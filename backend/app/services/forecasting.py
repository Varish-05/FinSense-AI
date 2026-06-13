"""
Time-Series Forecasting Service using Facebook Prophet.
Also includes an LSTM skeleton for comparison (requires more data).
"""
from typing import List, Tuple, Any, Dict
from datetime import date
import logging

logger = logging.getLogger(__name__)


def run_prophet_forecast(rows: List[Tuple[date, float]], periods: int = 3) -> List[Dict[str, Any]]:
    """
    Build a Prophet model on monthly aggregated expense data and return
    `periods` months of forecast.

    Parameters
    ----------
    rows    : list of (date, amount) tuples from the DB
    periods : number of future months to forecast

    Returns
    -------
    List of dicts with keys: ds, yhat, yhat_lower, yhat_upper
    """
    try:
        import pandas as pd
        from prophet import Prophet

        # Aggregate to monthly level
        df = pd.DataFrame(rows, columns=["ds", "y"])
        df["ds"] = pd.to_datetime(df["ds"])
        df = df.set_index("ds").resample("MS").sum().reset_index()   # Month-Start frequency
        df.columns = ["ds", "y"]

        if len(df) < 3:
            logger.warning("Not enough monthly data for Prophet (need ≥ 3 months).")
            return []

        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            interval_width=0.80,
        )
        model.fit(df)

        future = model.make_future_dataframe(periods=periods, freq="MS")
        forecast = model.predict(future)

        result = []
        for _, row in forecast.tail(periods).iterrows():
            result.append({
                "ds": row["ds"].strftime("%Y-%m"),
                "yhat": round(float(row["yhat"]), 2),
                "yhat_lower": round(float(row["yhat_lower"]), 2),
                "yhat_upper": round(float(row["yhat_upper"]), 2),
            })
        return result

    except ImportError:
        logger.error("Prophet is not installed. Run: pip install prophet")
        return []
    except Exception as e:
        logger.error(f"Prophet forecast failed: {e}")
        return []
