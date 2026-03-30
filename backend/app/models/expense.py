# backend/app/models/expense.py

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Expense(Base):
    """
    This table stores every expense entry.
    Each row = one expense.
    """
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Basic expense info
    title = Column(String(200), nullable=False)           # e.g., "Lunch at McDonald's"
    amount = Column(Float, nullable=False)                # e.g., 450.50
    date = Column(Date, nullable=False)                   # e.g., 2024-01-15
    merchant = Column(String(200), nullable=True)         # e.g., "McDonald's"
    description = Column(Text, nullable=True)             # Optional extra details
    
    # Category assigned by rule engine
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="expenses")
    
    # Source of expense
    source = Column(String(50), default="manual")         # "manual" or "csv"
    
    # Was this flagged as unusual?
    is_anomaly = Column(Boolean, default=False)
    anomaly_reason = Column(String(500), nullable=True)
    
    # Tags for extra filtering
    tags = Column(String(500), nullable=True)             # e.g., "work,travel"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Expense id={self.id} title={self.title} amount={self.amount}>"