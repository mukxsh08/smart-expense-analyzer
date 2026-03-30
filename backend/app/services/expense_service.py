# backend/app/services/expense_service.py

from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.expense import Expense
from app.models.category import Category
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.rules.rule_engine import RuleEngine
from app.services.anomaly_service import AnomalyDetector
from typing import List, Optional
import pandas as pd
from datetime import date
import io


class ExpenseService:
    """Handles all business logic for expenses."""

    @staticmethod
    def create_expense(db: Session, expense_data: ExpenseCreate, source: str = "manual") -> Expense:
        """
        Create a single expense.
        After creating, we automatically:
        1. Apply rule engine to find category
        2. Check for anomalies
        """
        # Create expense object
        expense = Expense(
            title=expense_data.title,
            amount=expense_data.amount,
            date=expense_data.date,
            merchant=expense_data.merchant,
            description=expense_data.description,
            tags=expense_data.tags,
            source=source
        )

        # Apply rule engine to auto-categorize
        rule_engine = RuleEngine(db)
        category_name = rule_engine.apply_rules(expense)

        if category_name:
            # Find the category in DB
            category = db.query(Category).filter(
                Category.name == category_name,
                Category.is_active == True
            ).first()
            if category:
                expense.category_id = category.id

        # Save to database
        db.add(expense)
        db.commit()
        db.refresh(expense)

        # Check for anomaly AFTER saving (we need historical data)
        detector = AnomalyDetector(db)
        is_anomaly, reason = detector.check_expense(expense)
        if is_anomaly:
            expense.is_anomaly = True
            expense.anomaly_reason = reason
            db.commit()
            db.refresh(expense)

        return expense

    @staticmethod
    def get_expenses(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        category_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        is_anomaly: Optional[bool] = None
    ) -> dict:
        """Get list of expenses with optional filters."""
        query = db.query(Expense)

        if category_id:
            query = query.filter(Expense.category_id == category_id)
        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)
        if is_anomaly is not None:
            query = query.filter(Expense.is_anomaly == is_anomaly)

        total = query.count()
        expenses = query.order_by(desc(Expense.date)).offset(skip).limit(limit).all()

        return {
            "total": total,
            "page": skip // limit + 1,
            "per_page": limit,
            "expenses": expenses
        }

    @staticmethod
    def get_expense_by_id(db: Session, expense_id: int) -> Optional[Expense]:
        """Get a single expense by ID."""
        return db.query(Expense).filter(Expense.id == expense_id).first()

    @staticmethod
    def update_expense(db: Session, expense_id: int, update_data: ExpenseUpdate) -> Optional[Expense]:
        """Update an existing expense."""
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            return None

        # Only update fields that were provided
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(expense, field, value)

        db.commit()
        db.refresh(expense)
        return expense

    @staticmethod
    def delete_expense(db: Session, expense_id: int) -> bool:
        """Delete an expense. Returns True if deleted, False if not found."""
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            return False
        db.delete(expense)
        db.commit()
        return True

    @staticmethod
    def process_csv(db: Session, file_content: bytes) -> dict:
        """
        Process a CSV file and create multiple expenses.
        
        Expected CSV columns:
        title, amount, date, merchant (optional), description (optional), tags (optional)
        """
        results = {
            "total_rows": 0,
            "success_count": 0,
            "error_count": 0,
            "errors": []
        }

        try:
            # Read CSV from bytes
            df = pd.read_csv(io.BytesIO(file_content))
            results["total_rows"] = len(df)

            # Clean column names (remove spaces, lowercase)
            df.columns = df.columns.str.strip().str.lower()

            # Validate required columns
            required_cols = ["title", "amount", "date"]
            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                return {
                    "error": f"CSV is missing required columns: {missing}",
                    "required_columns": required_cols,
                    "your_columns": list(df.columns)
                }

            for index, row in df.iterrows():
                row_num = index + 2  # +2 because row 1 is header, and index starts at 0
                try:
                    # Parse date
                    expense_date = pd.to_datetime(row["date"]).date()

                    expense_data = ExpenseCreate(
                        title=str(row["title"]).strip(),
                        amount=float(row["amount"]),
                        date=expense_date,
                        merchant=str(row.get("merchant", "")).strip() or None,
                        description=str(row.get("description", "")).strip() or None,
                        tags=str(row.get("tags", "")).strip() or None
                    )

                    ExpenseService.create_expense(db, expense_data, source="csv")
                    results["success_count"] += 1

                except Exception as e:
                    results["error_count"] += 1
                    results["errors"].append({
                        "row": row_num,
                        "data": row.to_dict(),
                        "error": str(e)
                    })

        except Exception as e:
            results["error"] = f"Failed to read CSV: {str(e)}"

        return results