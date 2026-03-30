# backend/app/api/analytics.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from app.analytics.expense_analytics import ExpenseAnalytics
from app.services.anomaly_service import AnomalyDetector
from app.schemas.expense import ExpenseResponse
from typing import List

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    """Get all key metrics for the main dashboard."""
    analytics = ExpenseAnalytics(db)
    return analytics.dashboard_summary()


@router.get("/monthly")
def get_monthly_summary(
    year: Optional[int] = Query(None, description="Filter by year, e.g. 2024"),
    db: Session = Depends(get_db)
):
    """Get monthly spending summary."""
    analytics = ExpenseAnalytics(db)
    return analytics.monthly_summary(year=year)


@router.get("/by-category")
def get_category_spending(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get spending broken down by category."""
    analytics = ExpenseAnalytics(db)
    return analytics.category_wise_spending(month=month, year=year)


@router.get("/top-expenses")
def get_top_expenses(
    limit: int = Query(10, ge=1, le=50),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get top N most expensive transactions."""
    analytics = ExpenseAnalytics(db)
    return analytics.top_expenses(limit=limit, month=month, year=year)


@router.get("/daily-trend")
def get_daily_trend(
    month: int = Query(..., ge=1, le=12, description="Month number (1-12)"),
    year: int = Query(..., description="Year, e.g. 2024"),
    db: Session = Depends(get_db)
):
    """Get day-by-day spending trend for a month."""
    analytics = ExpenseAnalytics(db)
    return analytics.daily_spending_trend(month=month, year=year)


@router.get("/month-comparison")
def get_month_comparison(db: Session = Depends(get_db)):
    """Compare spending month over month."""
    analytics = ExpenseAnalytics(db)
    return analytics.month_over_month_comparison()


@router.get("/category-rank")
def get_category_rank(
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Rank categories by total spending."""
    analytics = ExpenseAnalytics(db)
    return analytics.spending_rank_by_category(year=year)


@router.get("/anomalies", response_model=List[ExpenseResponse])
def get_anomalies(db: Session = Depends(get_db)):
    """Get all expenses flagged as anomalies."""
    detector = AnomalyDetector(db)
    return detector.get_all_anomalies()