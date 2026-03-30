# backend/app/schemas/category.py

from pydantic import BaseModel, Field
from typing import Optional


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = "#3B82F6"
    icon: Optional[str] = "💰"


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    color: str
    icon: str
    is_active: bool

    class Config:
        from_attributes = True