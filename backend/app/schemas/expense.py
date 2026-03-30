# backend/app/schemas/expense.py

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import datetime


class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0)
    date: datetime.date = Field(..., description="YYYY-MM-DD format")
    merchant: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    tags: Optional[str] = None

    @field_validator('amount')
    def amount_must_be_positive(cls, v):
        return round(v, 2)

    @field_validator('title')
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()


class ExpenseUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[datetime.date] = None
    merchant: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: int
    title: str
    amount: float
    date: datetime.date
    merchant: Optional[str]
    description: Optional[str]
    category_id: Optional[int]
    source: str
    is_anomaly: bool
    anomaly_reason: Optional[str]
    tags: Optional[str]
    created_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True


class ExpenseListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    expenses: List[ExpenseResponse]