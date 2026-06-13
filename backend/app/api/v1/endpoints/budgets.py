"""
Budget management endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.budget import Budget
from app.schemas.schemas import BudgetCreate, BudgetResponse

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.post("/", response_model=BudgetResponse, status_code=201)
def create_budget(
    payload: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budget = Budget(
        user_id=current_user.id,
        month=payload.month,
        category=payload.category,
        allocated_amount=payload.allocated_amount,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


@router.get("/", response_model=List[BudgetResponse])
def list_budgets(
    month: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Budget).filter(Budget.user_id == current_user.id)
    if month:
        q = q.filter(Budget.month == month)
    return q.all()


@router.delete("/{budget_id}", status_code=204)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budget = db.query(Budget).filter(
        Budget.id == budget_id, Budget.user_id == current_user.id
    ).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    db.delete(budget)
    db.commit()
