"""
SQLAlchemy ORM models for budgets and financial health scores.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Month/year this budget applies to (e.g., 2024-03)
    month = Column(String(7), nullable=False)   # YYYY-MM
    category = Column(String(100), nullable=False)
    allocated_amount = Column(Float, nullable=False)
    spent_amount = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="budgets")


class FinancialScore(Base):
    __tablename__ = "financial_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    month = Column(String(7), nullable=False)   # YYYY-MM
    score = Column(Float, nullable=False)        # 0 – 100

    # JSON breakdown of sub-scores
    breakdown = Column(JSON)  # {"savings_ratio": 20, "budget_adherence": 30, ...}
    explanation = Column(String(1000))

    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="financial_scores")
