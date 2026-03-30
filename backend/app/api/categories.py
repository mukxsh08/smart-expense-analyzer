# backend/app/api/categories.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from app.schemas.category import CategoryCreate, CategoryResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    """Get all active categories."""
    return CategoryService.get_all_categories(db)


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new expense category."""
    try:
        return CategoryService.create_category(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/seed")
def seed_categories(db: Session = Depends(get_db)):
    """Seed the database with default categories."""
    seeded = CategoryService.seed_default_categories(db)
    if seeded:
        return {"message": "Default categories added successfully!"}
    return {"message": "Categories already exist, nothing was added."}