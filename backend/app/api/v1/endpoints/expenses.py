"""
Expense management endpoints – CRUD, CSV upload, NLP categorization.
"""
import io
from typing import List, Optional
from datetime import date

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.expense import Expense
from app.schemas.schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.services.nlp_categorizer import categorize_expense

router = APIRouter(prefix="/expenses", tags=["Expenses"])


# ── Helpers ───────────────────────────────────────────────────────────

def _apply_category(expense: Expense, user_category: Optional[str], description: str):
    """Use NLP categorizer if the user did not supply a category."""
    if user_category:
        expense.category = user_category
        expense.category_confidence = 1.0
    else:
        predicted, confidence = categorize_expense(description)
        expense.category = predicted
        expense.category_confidence = round(confidence, 4)


# ── Endpoints ─────────────────────────────────────────────────────────

@router.post("/", response_model=ExpenseResponse, status_code=201)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a single expense. Category is auto-assigned by NLP if not provided."""
    text = f"{payload.merchant_name} {payload.description or ''}".strip()
    expense = Expense(
        user_id=current_user.id,
        amount=payload.amount,
        date=payload.date,
        merchant_name=payload.merchant_name,
        description=payload.description,
        payment_mode=payload.payment_mode or "UPI",
        notes=payload.notes,
    )
    _apply_category(expense, payload.category, text)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/", response_model=List[ExpenseResponse])
def list_expenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List expenses for the authenticated user with optional filters."""
    q = db.query(Expense).filter(Expense.user_id == current_user.id)
    if category:
        q = q.filter(Expense.category == category)
    if start_date:
        q = q.filter(Expense.date >= start_date)
    if end_date:
        q = q.filter(Expense.date <= end_date)
    return q.order_by(Expense.date.desc()).offset(skip).limit(limit).all()


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id, Expense.user_id == current_user.id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id, Expense.user_id == current_user.id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(expense, key, value)

    # Re-categorize if merchant or description changed but no category set
    if (payload.merchant_name or payload.description) and not payload.category:
        text = f"{expense.merchant_name} {expense.description or ''}".strip()
        _apply_category(expense, None, text)

    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=204)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id, Expense.user_id == current_user.id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()


@router.post("/upload/csv", response_model=List[ExpenseResponse], status_code=201)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a bank statement CSV.
    Expected columns: date, amount, description (merchant_name optional).
    All other columns are ignored.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    contents = await file.read()
    try:
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not parse CSV file")

    # Normalise column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    required = {"date", "amount"}
    if not required.issubset(set(df.columns)):
        raise HTTPException(
            status_code=400,
            detail=f"CSV must contain columns: {required}. Found: {list(df.columns)}",
        )

    created = []
    for _, row in df.iterrows():
        try:
            merchant = str(row.get("description", row.get("merchant_name", "Unknown")))
            expense = Expense(
                user_id=current_user.id,
                amount=abs(float(row["amount"])),
                date=pd.to_datetime(row["date"]).date(),
                merchant_name=merchant[:255],
                description=merchant[:500],
                payment_mode="Bank Transfer",
            )
            _apply_category(expense, None, merchant)
            db.add(expense)
            created.append(expense)
        except Exception:
            # Skip malformed rows
            continue

    db.commit()
    for e in created:
        db.refresh(e)
    return created
