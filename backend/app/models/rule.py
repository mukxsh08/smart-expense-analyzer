# backend/app/models/rule.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class Rule(Base):
    """
    This table stores categorization rules.
    Rules are checked against each expense to auto-assign a category.
    
    Example rule:
    - rule_type: "keyword"
    - condition: "uber,ola,rapido"
    - category_name: "Transport"
    - priority: 1
    """
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    name = Column(String(200), nullable=False)          # Human-friendly name
    rule_type = Column(String(50), nullable=False)      # "keyword", "amount_range", "merchant"
    
    # The condition to match
    condition = Column(Text, nullable=False)            # e.g., "uber,ola" or "0-500" or "amazon"
    
    # What to do when rule matches
    category_name = Column(String(100), nullable=False) # e.g., "Transport"
    
    # Higher priority rules are checked first
    priority = Column(Integer, default=1)
    
    is_active = Column(Boolean, default=True)
    
    # Optional: apply rule only to specific fields
    apply_on = Column(String(50), default="title")      # "title", "merchant", "description"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Rule id={self.id} type={self.rule_type} condition={self.condition}>"