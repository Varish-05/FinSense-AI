"""
Pydantic schemas for User, Expense, Budget, FinancialScore, Auth.
"""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator


# ── Auth ─────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None


# ── User ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None


# ── Expense ───────────────────────────────────────────────────────────

class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0)
    date: date
    merchant_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    payment_mode: Optional[str] = "UPI"
    category: Optional[str] = None   # if None → NLP model assigns it
    notes: Optional[str] = None

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    date: Optional[date] = None
    merchant_name: Optional[str] = None
    description: Optional[str] = None
    payment_mode: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None

class ExpenseResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    date: date
    merchant_name: str
    description: Optional[str]
    payment_mode: str
    category: str
    category_confidence: float
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Budget ────────────────────────────────────────────────────────────

class BudgetCreate(BaseModel):
    month: str = Field(..., pattern=r"^\d{4}-\d{2}$")   # YYYY-MM
    category: str
    allocated_amount: float = Field(..., gt=0)

class BudgetResponse(BaseModel):
    id: int
    user_id: int
    month: str
    category: str
    allocated_amount: float
    spent_amount: float
    created_at: datetime

    class Config:
        from_attributes = True


# ── Financial Score ───────────────────────────────────────────────────

class FinancialScoreResponse(BaseModel):
    id: int
    user_id: int
    month: str
    score: float
    breakdown: Optional[Dict[str, Any]]
    explanation: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Dashboard ─────────────────────────────────────────────────────────

class DashboardSummary(BaseModel):
    total_expenses_this_month: float
    total_expenses_last_month: float
    month_over_month_change_pct: float
    category_breakdown: Dict[str, float]
    financial_health_score: Optional[float]
    budget_utilization: Dict[str, float]  # category → % used
    top_spending_categories: List[str]


# ── Forecast ──────────────────────────────────────────────────────────

class ForecastResponse(BaseModel):
    model_used: str
    forecast: List[Dict[str, Any]]   # [{ds, yhat, yhat_lower, yhat_upper}, ...]
    category: Optional[str]


# ── Chat ─────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)

class ChatResponse(BaseModel):
    reply: str
