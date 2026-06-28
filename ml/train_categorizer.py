"""
NLP Expense Categorizer – Training Script
==========================================
Trains a TF-IDF + Logistic Regression pipeline on the synthetic dataset
and saves the model to ml/models/tfidf_lr_categorizer.pkl.

Usage
-----
    cd FinSense-AI
    python ml/train_categorizer.py
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# ── Configuration ─────────────────────────────────────────────────────

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "transactions.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "tfidf_lr_categorizer.pkl")
REPORT_PATH = os.path.join(os.path.dirname(__file__), "models", "eval_report.json")

os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

# ── Load Data ─────────────────────────────────────────────────────────

print("Loading dataset ...")
df = pd.read_csv(DATA_PATH)
df = df.dropna(subset=["description", "category"])
df["text"] = df["description"].str.lower().str.replace(r"[^a-z0-9 ]", " ", regex=True).str.strip()
df = df[df["text"].str.len() > 0]

print(f"  Total samples : {len(df)}")
print(f"  Categories    : {sorted(df['category'].unique())}")

X = df["text"].values
y = df["category"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── Build Pipeline ────────────────────────────────────────────────────

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=30_000,
        sublinear_tf=True,
        min_df=2,
    )),
    ("clf", LogisticRegression(
        C=5.0,
        max_iter=1000,
        solver="lbfgs",
        random_state=42,
    )),
])

# ── Train ─────────────────────────────────────────────────────────────

print("\nTraining TF-IDF + Logistic Regression ...")
pipeline.fit(X_train, y_train)

# ── Evaluate ──────────────────────────────────────────────────────────

y_pred = pipeline.predict(X_test)
acc = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred, output_dict=True)

print(f"\nTest Accuracy : {acc:.4f}")
print(classification_report(y_test, y_pred))

# ── Save ──────────────────────────────────────────────────────────────

joblib.dump(pipeline, MODEL_PATH)
print(f"Model saved -> {MODEL_PATH}")

with open(REPORT_PATH, "w") as f:
    json.dump({"accuracy": acc, "report": report}, f, indent=2)
print(f"Eval report saved -> {REPORT_PATH}")
