"""
Dashboard summary, forecasting, financial health score, and AI chat endpoints.
"""
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.expense import Expense
from app.models.budget import Budget, FinancialScore
from app.schemas.schemas import (
    DashboardSummary, ForecastResponse, FinancialScoreResponse, ChatMessage, ChatResponse
)
from app.services.forecasting import run_prophet_forecast
from app.services.health_score import compute_financial_health
from app.services.chat_assistant import get_chat_reply

router = APIRouter(tags=["Analytics"])


# ── Dashboard ─────────────────────────────────────────────────────────

@router.get("/dashboard", response_model=DashboardSummary)
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    this_month = f"{now.year}-{now.month:02d}"
    last_month_dt = date(now.year, now.month - 1, 1) if now.month > 1 else date(now.year - 1, 12, 1)
    last_month = f"{last_month_dt.year}-{last_month_dt.month:02d}"

    def monthly_total(month_str: str) -> float:
        yr, mo = map(int, month_str.split("-"))
        start = date(yr, mo, 1)
        end = date(yr, mo + 1, 1) if mo < 12 else date(yr + 1, 1, 1)
        result = db.query(func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            Expense.date >= start,
            Expense.date < end,
        ).scalar()
        return float(result or 0)

    this_total = monthly_total(this_month)
    last_total = monthly_total(last_month)
    mom_change = ((this_total - last_total) / last_total * 100) if last_total else 0.0

    # Category breakdown for this month
    yr, mo = map(int, this_month.split("-"))
    start = date(yr, mo, 1)
    end = date(yr, mo + 1, 1) if mo < 12 else date(yr + 1, 1, 1)

    cat_rows = db.query(Expense.category, func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        Expense.date >= start,
        Expense.date < end,
    ).group_by(Expense.category).all()
    category_breakdown = {cat: float(amt) for cat, amt in cat_rows}

    # Budget utilisation
    budgets = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.month == this_month,
    ).all()
    budget_util = {}
    for b in budgets:
        spent = category_breakdown.get(b.category, 0.0)
        budget_util[b.category] = round((spent / b.allocated_amount) * 100, 1) if b.allocated_amount else 0.0

    # Latest health score
    score_row = db.query(FinancialScore).filter(
        FinancialScore.user_id == current_user.id
    ).order_by(FinancialScore.created_at.desc()).first()
    health_score = score_row.score if score_row else None

    top_cats = sorted(category_breakdown, key=category_breakdown.get, reverse=True)[:3]

    return DashboardSummary(
        total_expenses_this_month=this_total,
        total_expenses_last_month=last_total,
        month_over_month_change_pct=round(mom_change, 2),
        category_breakdown=category_breakdown,
        financial_health_score=health_score,
        budget_utilization=budget_util,
        top_spending_categories=top_cats,
    )


# ── Forecasting ───────────────────────────────────────────────────────

@router.get("/forecast", response_model=ForecastResponse)
def forecast_expenses(
    category: Optional[str] = Query(None),
    periods: int = Query(3, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Predict the next `periods` months of spending using Facebook Prophet.
    Optionally filter by expense category.
    """
    query = db.query(Expense.date, Expense.amount).filter(
        Expense.user_id == current_user.id
    )
    if category:
        query = query.filter(Expense.category == category)
    rows = query.all()

    if len(rows) < 6:
        return ForecastResponse(
            model_used="prophet",
            forecast=[],
            category=category,
        )

    forecast_data = run_prophet_forecast(rows, periods=periods)
    return ForecastResponse(model_used="prophet", forecast=forecast_data, category=category)


# ── Financial Health Score ────────────────────────────────────────────

@router.post("/health-score", response_model=FinancialScoreResponse)
def generate_health_score(
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compute and persist the financial health score for a given month."""
    yr, mo = map(int, month.split("-"))
    start = date(yr, mo, 1)
    end = date(yr, mo + 1, 1) if mo < 12 else date(yr + 1, 1, 1)

    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.date >= start,
        Expense.date < end,
    ).all()
    budgets = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.month == month,
    ).all()

    score, breakdown, explanation = compute_financial_health(expenses, budgets)

    record = FinancialScore(
        user_id=current_user.id,
        month=month,
        score=score,
        breakdown=breakdown,
        explanation=explanation,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ── AI Chat Assistant ─────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    LLM-powered chat assistant. Fetches spending context and answers the user's
    financial question.
    """
    # Build a quick spending context for the model
    recent = db.query(Expense).filter(
        Expense.user_id == current_user.id
    ).order_by(Expense.date.desc()).limit(100).all()

    context_lines = [f"- {e.date}: {e.category} ₹{e.amount:.2f} @ {e.merchant_name}" for e in recent]
    context = "\n".join(context_lines)

    reply = get_chat_reply(payload.message, context)
    return ChatResponse(reply=reply)
