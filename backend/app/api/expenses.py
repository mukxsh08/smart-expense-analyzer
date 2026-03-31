# backend/app/api/expenses.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from database import get_db
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseListResponse
from app.services.expense_service import ExpenseService

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/", response_model=ExpenseResponse, status_code=201)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    """
    Create a single expense manually.
    
    Example body:
    {
        "title": "Lunch at Swiggy",
        "amount": 350.00,
        "date": "2024-01-15",
        "merchant": "Swiggy"
    }
    """
    return ExpenseService.create_expense(db, expense)


@router.get("/", response_model=ExpenseListResponse)
def list_expenses(
    skip: int = Query(0, ge=0, description="How many records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    category_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    is_anomaly: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get list of expenses with optional filters."""
    result = ExpenseService.get_expenses(
        db, skip=skip, limit=limit,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
        is_anomaly=is_anomaly
    )
    return result


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    """Get a single expense by its ID."""
    expense = ExpenseService.get_expense_by_id(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail=f"Expense {expense_id} not found")
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(expense_id: int, update_data: ExpenseUpdate, db: Session = Depends(get_db)):
    """Update an existing expense."""
    expense = ExpenseService.update_expense(db, expense_id, update_data)
    if not expense:
        raise HTTPException(status_code=404, detail=f"Expense {expense_id} not found")
    return expense


@router.delete("/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    """Delete an expense."""
    deleted = ExpenseService.delete_expense(db, expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Expense {expense_id} not found")
    return {"message": f"Expense {expense_id} deleted successfully"}


@router.post("/upload/csv")
def upload_csv(
    file: UploadFile = File(..., description="CSV file with expense data"),
    db: Session = Depends(get_db)
):
    """
    Upload a CSV file to bulk-import expenses.
    
    Required CSV columns: title, amount, date
    Optional columns: merchant, description, tags
    
    Date format: YYYY-MM-DD (e.g., 2024-01-15)
    """
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only .csv files are allowed"
        )
    
    # Read file content
    content = file.file.read()
    
    # Process CSV
    result = ExpenseService.process_csv(db, content)
    
    return {
        "filename": file.filename,
        "processing_result": result
    }