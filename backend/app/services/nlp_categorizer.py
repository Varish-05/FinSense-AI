"""
NLP Expense Categorizer Service
---------------------------------
Primary approach : TF-IDF + Logistic Regression (fast, lightweight, no GPU needed)
Advanced approach: distilbert-base-uncased fine-tuning (see ml/bert_trainer.py)

At startup the service tries to load a pre-trained model from disk.
If no model exists, it falls back to a rule-based heuristic so the API
still works before training.
"""
import os
import re
import joblib
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Path where the trained sklearn pipeline is saved
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../ml_models/tfidf_lr_categorizer.pkl")

# ── Category keywords (fallback rule-based system) ────────────────────

RULES = {
    "Food": [
        "swiggy", "zomato", "mcdonalds", "kfc", "pizza", "burger", "cafe",
        "restaurant", "food", "eat", "meal", "dinner", "lunch", "breakfast",
        "biryani", "hotel", "canteen", "mess",
    ],
    "Transport": [
        "uber", "ola", "rapido", "namma yatri", "bus", "metro", "auto", "cab",
        "petrol", "diesel", "fuel", "toll", "parking", "train", "irctc",
    ],
    "Healthcare": [
        "apollo", "medplus", "pharmacy", "medicine", "doctor", "hospital",
        "clinic", "lab", "health", "dental", "optician",
    ],
    "Entertainment": [
        "netflix", "amazon prime", "hotstar", "spotify", "youtube premium",
        "movie", "pvr", "inox", "concert", "game", "steam",
    ],
    "Education": [
        "udemy", "coursera", "college", "university", "book", "stationery",
        "tuition", "coaching", "pen", "notebook", "fees",
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "ajio", "nykaa", "meesho",
        "clothes", "shirt", "shoe", "fashion", "mall",
    ],
    "Utilities": [
        "electricity", "water", "bescom", "bwssb", "airtel", "jio",
        "broadband", "internet", "gas", "lpg", "bbmp",
    ],
    "Investments": [
        "zerodha", "groww", "mutual fund", "sip", "fd", "gold", "stocks",
        "nps", "ppf", "insurance", "lic",
    ],
    "Travel": [
        "indigo", "air india", "spicejet", "flight", "hotel booking",
        "make my trip", "cleartrip", "goibibo", "oyo", "airbnb",
    ],
}


def _rule_based_predict(text: str) -> Tuple[str, float]:
    """Simple keyword-matching fallback categorizer."""
    text_lower = text.lower()
    for category, keywords in RULES.items():
        for kw in keywords:
            if kw in text_lower:
                return category, 0.75
    return "Miscellaneous", 0.5


# ── Load trained ML model (if available) ─────────────────────────────

_model = None

def _load_model():
    global _model
    if _model is not None:
        return _model
    if os.path.exists(MODEL_PATH):
        try:
            _model = joblib.load(MODEL_PATH)
            logger.info("NLP categorizer model loaded from disk.")
        except Exception as e:
            logger.warning(f"Could not load NLP model: {e}. Using rule-based fallback.")
    return _model


def categorize_expense(text: str) -> Tuple[str, float]:
    """
    Categorize an expense description.

    Returns
    -------
    (category: str, confidence: float)
    """
    text = re.sub(r"[^a-zA-Z0-9 ]", " ", str(text)).strip()
    if not text:
        return "Miscellaneous", 0.5

    model = _load_model()
    if model is not None:
        try:
            category = model.predict([text])[0]
            proba = model.predict_proba([text]).max()
            return category, float(proba)
        except Exception as e:
            logger.warning(f"Model prediction failed: {e}. Falling back to rules.")

    return _rule_based_predict(text)
