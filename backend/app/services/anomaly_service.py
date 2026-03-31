# backend/app/services/anomaly_service.py

from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.models.expense import Expense
from typing import Tuple, Optional
from datetime import date, timedelta


class AnomalyDetector:
    """
    Detects unusual spending patterns.
    
    Detection Methods:
    1. Amount Spike   — This expense is much higher than your average
    2. Daily Spike    — You spent much more today than your usual daily amount
    3. Duplicate      — Same title and amount within 24 hours
    4. Category Spike — You spent unusually high in a category this month
    """

    # How many times above average is considered "unusual"
    AMOUNT_SPIKE_THRESHOLD = 3.0    # 3x your average = unusual
    DAILY_SPIKE_THRESHOLD = 2.5     # 2.5x your daily average = unusual
    
    def __init__(self, db: Session):
        self.db = db

    def check_expense(self, expense: Expense) -> Tuple[bool, Optional[str]]:
        """
        Run all anomaly checks on a single expense.
        Returns (is_anomaly: bool, reason: str or None)
        """
        # Check 1: Is this amount way higher than usual?
        is_spike, spike_reason = self._check_amount_spike(expense)
        if is_spike:
            return True, spike_reason

        # Check 2: Is this a duplicate transaction?
        is_dup, dup_reason = self._check_duplicate(expense)
        if is_dup:
            return True, dup_reason

        # Check 3: Daily spending spike?
        is_daily, daily_reason = self._check_daily_spike(expense)
        if is_daily:
            return True, daily_reason

        # Check 4: Category overspending?
        is_cat, cat_reason = self._check_category_spike(expense)
        if is_cat:
            return True, cat_reason

        return False, None

    def _check_amount_spike(self, expense: Expense) -> Tuple[bool, Optional[str]]:
        """
        Check if this single expense is much higher than the user's average expense.
        """
        # Get average and stddev of all expenses (excluding this one)
        result = self.db.query(
            func.avg(Expense.amount).label("avg"),
            func.stddev(Expense.amount).label("stddev"),
            func.count(Expense.id).label("count")
        ).filter(Expense.id != expense.id).first()

        if not result or not result.count or result.count < 5:
            # Not enough data to detect anomaly
            return False, None

        avg = float(result.avg or 0)
        stddev = float(result.stddev or 0)
        count = result.count

        if avg == 0:
            return False, None

        # If this expense is more than threshold times the average
        if expense.amount > avg * self.AMOUNT_SPIKE_THRESHOLD:
            ratio = round(expense.amount / avg, 1)
            return True, (
                f"Amount spike: ₹{expense.amount:.0f} is {ratio}x your average "
                f"expense of ₹{avg:.0f} (based on {count} transactions)"
            )

        return False, None

    def _check_duplicate(self, expense: Expense) -> Tuple[bool, Optional[str]]:
        """
        Check if a similar expense was created within 24 hours.
        Same title + similar amount = likely duplicate.
        """
        # Look for expenses with same title within ±1 day
        date_start = expense.date - timedelta(days=1)
        date_end = expense.date + timedelta(days=1)

        duplicate = self.db.query(Expense).filter(
            Expense.id != expense.id,
            Expense.title.ilike(expense.title),  # Case-insensitive match
            Expense.amount == expense.amount,
            Expense.date.between(date_start, date_end)
        ).first()

        if duplicate:
            return True, (
                f"Possible duplicate: Similar expense '{expense.title}' "
                f"for ₹{expense.amount} found on {duplicate.date}"
            )

        return False, None

    def _check_daily_spike(self, expense: Expense) -> Tuple[bool, Optional[str]]:
        """
        Check if today's total spending is much higher than the usual daily spending.
        """
        # Get average daily spending (excluding today)
        result = self.db.execute(text("""
            SELECT AVG(daily_total) as avg_daily
            FROM (
                SELECT date, SUM(amount) as daily_total
                FROM expenses
                WHERE date != :today
                GROUP BY date
            ) daily_sums
        """), {"today": expense.date}).fetchone()

        if not result or not result.avg_daily:
            return False, None

        avg_daily = float(result.avg_daily)

        # Get today's total INCLUDING this expense
        today_total_result = self.db.query(
            func.sum(Expense.amount)
        ).filter(Expense.date == expense.date).scalar() or 0
        
        today_total = float(today_total_result) + expense.amount

        if avg_daily > 0 and today_total > avg_daily * self.DAILY_SPIKE_THRESHOLD:
            ratio = round(today_total / avg_daily, 1)
            return True, (
                f"Daily spending spike: Today's total ₹{today_total:.0f} is "
                f"{ratio}x your average daily spending of ₹{avg_daily:.0f}"
            )

        return False, None

    def _check_category_spike(self, expense: Expense) -> Tuple[bool, Optional[str]]:
        """
        Check if this category's spending this month is unusually high.
        Compare this month vs average monthly spending in that category.
        """
        if not expense.category_id:
            return False, None

        # Average monthly spending in this category (excluding current month)
        result = self.db.execute(text("""
            SELECT AVG(monthly_total) AS avg_monthly, COUNT(*) AS months
            FROM (
                SELECT YEAR(date) AS yr, MONTH(date) AS mo, SUM(amount) AS monthly_total
                FROM expenses
                WHERE category_id = :cat_id
                  AND NOT (YEAR(date) = YEAR(CURDATE()) AND MONTH(date) = MONTH(CURDATE()))
                GROUP BY YEAR(date), MONTH(date)
            ) monthly_totals
        """), {"cat_id": expense.category_id}).fetchone()

        if not result or not result.avg_monthly or result.months < 2:
            return False, None

        avg_monthly = float(result.avg_monthly)

        # This month's total in this category
        this_month_result = self.db.execute(text("""
            SELECT ROUND(SUM(amount), 2) AS this_month_total
            FROM expenses
            WHERE category_id = :cat_id
              AND YEAR(date) = YEAR(CURDATE())
              AND MONTH(date) = MONTH(CURDATE())
        """), {"cat_id": expense.category_id}).fetchone()

        this_month = float(this_month_result.this_month_total or 0) + expense.amount

        if avg_monthly > 0 and this_month > avg_monthly * 2.0:
            ratio = round(this_month / avg_monthly, 1)
            return True, (
                f"Category spike: This month's spending is {ratio}x your usual "
                f"monthly amount in this category (₹{this_month:.0f} vs avg ₹{avg_monthly:.0f})"
            )

        return False, None

    def get_all_anomalies(self) -> list:
        """Get all flagged anomaly expenses."""
        return self.db.query(Expense).filter(
            Expense.is_anomaly == True
        ).order_by(Expense.date.desc()).all()