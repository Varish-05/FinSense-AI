"""
Advanced NLP Trainer – DistilBERT Fine-Tuning
=============================================
Fine-tunes distilbert-base-uncased on the expense categorization task.
Requires a GPU (or will be very slow on CPU – ~2h vs ~5min on GPU).

Usage
-----
    cd FinSense-AI
    python ml/bert_trainer.py

Output
------
    ml/models/distilbert_expense_categorizer/   (HuggingFace model dir)
"""
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

# Check for transformers
try:
    import torch
    from transformers import (
        DistilBertTokenizerFast,
        DistilBertForSequenceClassification,
        Trainer,
        TrainingArguments,
    )
    from torch.utils.data import Dataset as TorchDataset
except ImportError:
    print("Install transformers and torch: pip install transformers torch")
    exit(1)

# ── Config ─────────────────────────────────────────────────────────────
DATA_PATH  = os.path.join(os.path.dirname(__file__), "data", "transactions.csv")
MODEL_OUT  = os.path.join(os.path.dirname(__file__), "models", "distilbert_expense_categorizer")
MODEL_NAME = "distilbert-base-uncased"
MAX_LEN    = 64
BATCH_SIZE = 32
EPOCHS     = 3

os.makedirs(MODEL_OUT, exist_ok=True)

# ── Load & Prepare Data ────────────────────────────────────────────────
print("Loading data …")
df = pd.read_csv(DATA_PATH).dropna(subset=["description", "category"])
df["text"] = df["description"].str.lower().str.strip()

le = LabelEncoder()
df["label"] = le.fit_transform(df["category"])

X_train, X_val, y_train, y_val = train_test_split(
    df["text"].tolist(), df["label"].tolist(),
    test_size=0.15, stratify=df["label"], random_state=42
)

print(f"  Train: {len(X_train)} | Val: {len(X_val)}")
print(f"  Classes ({len(le.classes_)}): {list(le.classes_)}")

# ── Tokenize ────────────────────────────────────────────────────────────
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)

class ExpenseDataset(TorchDataset):
    def __init__(self, texts, labels):
        self.enc = tokenizer(texts, truncation=True, padding="max_length", max_length=MAX_LEN)
        self.labels = labels

    def __len__(self): return len(self.labels)

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.enc.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

train_ds = ExpenseDataset(X_train, y_train)
val_ds   = ExpenseDataset(X_val,   y_val)

# ── Model ───────────────────────────────────────────────────────────────
model = DistilBertForSequenceClassification.from_pretrained(
    MODEL_NAME, num_labels=len(le.classes_)
)

# ── Training ────────────────────────────────────────────────────────────
args = TrainingArguments(
    output_dir=MODEL_OUT,
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    logging_steps=50,
    report_to="none",
)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = logits.argmax(axis=-1)
    return {"accuracy": accuracy_score(labels, preds)}

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_ds,
    eval_dataset=val_ds,
    compute_metrics=compute_metrics,
)

print("\nFine-tuning DistilBERT …")
trainer.train()

# Save model + tokenizer + label encoder
trainer.save_model(MODEL_OUT)
tokenizer.save_pretrained(MODEL_OUT)

import joblib
joblib.dump(le, os.path.join(MODEL_OUT, "label_encoder.pkl"))

print(f"\nModel saved → {MODEL_OUT}")
print("To use this model, update nlp_categorizer.py to load from this path.")
