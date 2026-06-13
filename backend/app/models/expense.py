"""
SQLAlchemy ORM model for the expenses table.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.core.database import Base

EXPENSE_CATEGORIES = [
    "Food", "Transport", "Healthcare", "Entertainment",
    "Education", "Shopping", "Utilities", "Investments",
    "Travel", "Miscellaneous",
]

PAYMENT_MODES = ["Cash", "UPI", "Credit Card", "Debit Card", "Net Banking", "Wallet"]


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False, index=True)
    merchant_name = Column(String(255), nullable=False)
    description = Column(String(500))
    payment_mode = Column(String(50), default="UPI")

    # AI-assigned category
    category = Column(String(100), nullable=False, default="Miscellaneous")
    # Confidence from the NLP model (0.0 – 1.0)
    category_confidence = Column(Float, default=1.0)

    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    owner = relationship("User", back_populates="expenses")
