"""
LSTM Time-Series Forecasting
==============================
Trains an LSTM on monthly expense sequences per user.
For comparison with Prophet.

Usage
-----
    python ml/lstm_forecaster.py --user_id 1 --category Food
"""
import argparse
import os
import numpy as np
import pandas as pd

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping
except ImportError:
    print("Install TensorFlow: pip install tensorflow")
    exit(1)

LOOK_BACK = 3   # months of history used as features


def create_sequences(data, look_back=3):
    X, y = [], []
    for i in range(look_back, len(data)):
        X.append(data[i - look_back:i])
        y.append(data[i])
    return np.array(X), np.array(y)


def train_lstm(monthly_amounts: list, periods: int = 3):
    """
    Train LSTM on monthly totals and forecast `periods` months ahead.

    Parameters
    ----------
    monthly_amounts : list of floats (monthly totals, chronological order)
    periods         : number of future months to forecast

    Returns
    -------
    list of predicted amounts
    """
    data = np.array(monthly_amounts, dtype=np.float32)

    # Normalise
    max_val = data.max() or 1.0
    data_norm = data / max_val

    X, y = create_sequences(data_norm, LOOK_BACK)
    if len(X) < 4:
        print("Not enough data for LSTM training (need at least 7 months).")
        return []

    X = X.reshape((X.shape[0], X.shape[1], 1))

    # Build model
    model = Sequential([
        LSTM(64, activation="tanh", return_sequences=True, input_shape=(LOOK_BACK, 1)),
        Dropout(0.2),
        LSTM(32, activation="tanh"),
        Dropout(0.2),
        Dense(1),
    ])
    model.compile(optimizer="adam", loss="mse")

    es = EarlyStopping(monitor="loss", patience=10, restore_best_weights=True)
    model.fit(X, y, epochs=100, batch_size=min(8, len(X)), verbose=0, callbacks=[es])

    # Forecast
    last_seq = data_norm[-LOOK_BACK:].tolist()
    predictions = []
    for _ in range(periods):
        seq = np.array(last_seq[-LOOK_BACK:]).reshape(1, LOOK_BACK, 1)
        pred = model.predict(seq, verbose=0)[0][0]
        predictions.append(float(pred) * max_val)
        last_seq.append(pred)

    return [round(p, 2) for p in predictions]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data",    default="ml/data/transactions.csv")
    parser.add_argument("--user_id", type=int, default=1)
    parser.add_argument("--category", default=None)
    parser.add_argument("--periods", type=int, default=3)
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["user_id"] == args.user_id]
    if args.category:
        df = df[df["category"] == args.category]

    monthly = df.set_index("date")["amount"].resample("MS").sum().values.tolist()
    print(f"Monthly totals ({len(monthly)} months): {monthly}")

    preds = train_lstm(monthly, periods=args.periods)
    print(f"\nLSTM Forecast for next {args.periods} months: {preds}")
