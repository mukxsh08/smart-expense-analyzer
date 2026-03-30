# backend/app/schemas/rule.py

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class RuleCreate(BaseModel):
    name: str = Field(..., min_length=1)
    rule_type: str = Field(..., description="One of: keyword, amount_range, merchant")
    condition: str = Field(..., min_length=1)
    category_name: str = Field(..., min_length=1)
    priority: Optional[int] = 1
    apply_on: Optional[str] = "title"

    @validator('rule_type')
    def validate_rule_type(cls, v):
        allowed = ["keyword", "amount_range", "merchant"]
        if v not in allowed:
            raise ValueError(f"rule_type must be one of {allowed}")
        return v

    @validator('apply_on')
    def validate_apply_on(cls, v):
        allowed = ["title", "merchant", "description"]
        if v not in allowed:
            raise ValueError(f"apply_on must be one of {allowed}")
        return v


class RuleResponse(BaseModel):
    id: int
    name: str
    rule_type: str
    condition: str
    category_name: str
    priority: int
    is_active: bool
    apply_on: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True