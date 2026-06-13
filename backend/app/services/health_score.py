"""
Financial Health Score Engine
-------------------------------
Computes a score 0–100 from four dimensions:

  1. Savings Ratio        (25 pts) – how much is not spent vs income proxy
  2. Budget Adherence     (30 pts) – how well user stays within set budgets
  3. Essential Ratio      (25 pts) – essential vs discretionary spending
  4. Expense Consistency  (20 pts) – month-over-month spend stability

The score and a plain-English explanation are returned.
"""
from typing import List, Tuple, Dict, Any

ESSENTIAL_CATEGORIES = {"Food", "Transport", "Healthcare", "Utilities", "Education"}
DISCRETIONARY_CATEGORIES = {"Entertainment", "Shopping", "Travel", "Miscellaneous", "Investments"}


def compute_financial_health(
    expenses: list,
    budgets: list,
    assumed_monthly_income: float = 30_000,
) -> Tuple[float, Dict[str, Any], str]:
    """
    Parameters
    ----------
    expenses  : list of Expense ORM objects for the target month
    budgets   : list of Budget ORM objects for the target month

    Returns
    -------
    (score: float, breakdown: dict, explanation: str)
    """
    total_spent = sum(e.amount for e in expenses)

    # ── 1. Savings Ratio (25 pts) ────────────────────────────────────
    savings_ratio = max(0.0, (assumed_monthly_income - total_spent) / assumed_monthly_income)
    savings_score = min(25.0, savings_ratio * 50)   # 50% savings → full 25 pts

    # ── 2. Budget Adherence (30 pts) ─────────────────────────────────
    if budgets:
        adherence_scores = []
        cat_spend = {}
        for e in expenses:
            cat_spend[e.category] = cat_spend.get(e.category, 0) + e.amount

        for b in budgets:
            spent = cat_spend.get(b.category, 0)
            if b.allocated_amount > 0:
                ratio = spent / b.allocated_amount
                # Full marks if under 90%, sliding penalty above
                adherence_scores.append(max(0, 1 - max(0, ratio - 0.9)))
        adherence_score = (sum(adherence_scores) / len(adherence_scores)) * 30
    else:
        adherence_score = 15.0   # Neutral if no budgets set

    # ── 3. Essential vs Discretionary (25 pts) ────────────────────────
    essential_spent = sum(e.amount for e in expenses if e.category in ESSENTIAL_CATEGORIES)
    disc_spent = sum(e.amount for e in expenses if e.category in DISCRETIONARY_CATEGORIES)
    if total_spent > 0:
        essential_ratio = essential_spent / total_spent
        essential_score = min(25.0, essential_ratio * 35)   # ~70% essential → full marks
    else:
        essential_score = 12.5

    # ── 4. Expense Consistency (20 pts) ──────────────────────────────
    # Approximated here as 15/20 (would need prior-month data for a real diff)
    consistency_score = 15.0

    score = round(savings_score + adherence_score + essential_score + consistency_score, 1)
    score = max(0.0, min(100.0, score))

    breakdown = {
        "savings_ratio": round(savings_score, 1),
        "budget_adherence": round(adherence_score, 1),
        "essential_ratio": round(essential_score, 1),
        "expense_consistency": round(consistency_score, 1),
        "total_spent": round(total_spent, 2),
    }

    # Plain-English explanation
    parts = []
    if savings_ratio < 0.1:
        parts.append("Your savings rate is very low – try to keep at least 20% of income unspent.")
    elif savings_ratio >= 0.3:
        parts.append("Great savings rate this month!")

    if budgets and adherence_score < 20:
        parts.append("You exceeded your budget in one or more categories.")
    if disc_spent > essential_spent:
        parts.append("Discretionary spending outpaced essentials – consider reviewing non-essential expenses.")
    if not parts:
        parts.append("Your finances look healthy this month. Keep it up!")

    explanation = " ".join(parts)
    return score, breakdown, explanation
