# backend/app/models/category.py

from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base


class Category(Base):
    """
    This table stores expense categories.
    e.g., Food, Transport, Entertainment, etc.
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)       # e.g., "Food"
    description = Column(Text, nullable=True)
    color = Column(String(20), default="#3B82F6")                 # Hex color for UI
    icon = Column(String(50), default="💰")                      # Emoji icon
    is_active = Column(Boolean, default=True)
    
    # One category has many expenses
    expenses = relationship("Expense", back_populates="category")

    def __repr__(self):
        return f"<Category id={self.id} name={self.name}>"