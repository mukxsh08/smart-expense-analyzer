# backend/app/analytics/expense_analytics.py

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import date


class ExpenseAnalytics:
    """
    All SQL analytics queries for the expense data.
    We use raw SQL with SQLAlchemy's text() function for complex queries.
    """

    def __init__(self, db: Session):
        self.db = db

    def monthly_summary(self, year: int = None) -> List[dict]:
        """
        Monthly spending summary.
        Returns: total spent, count of expenses, and average per expense for each month.
        """
        year_filter = f"AND YEAR(e.date) = {year}" if year else ""
        
        query = text(f"""
            SELECT 
                YEAR(e.date) AS year,
                MONTH(e.date) AS month,
                MONTHNAME(e.date) AS month_name,
                COUNT(e.id) AS total_expenses,
                ROUND(SUM(e.amount), 2) AS total_amount,
                ROUND(AVG(e.amount), 2) AS avg_amount,
                ROUND(MAX(e.amount), 2) AS max_expense,
                ROUND(MIN(e.amount), 2) AS min_expense
            FROM expenses e
            WHERE 1=1 {year_filter}
            GROUP BY YEAR(e.date), MONTH(e.date), MONTHNAME(e.date)
            ORDER BY year DESC, month DESC
        """)
        
        result = self.db.execute(query)
        return [dict(row._mapping) for row in result]

    def category_wise_spending(self, month: int = None, year: int = None) -> List[dict]:
        """
        Spending broken down by category.
        Includes percentage of total spending.
        """
        conditions = []
        if month:
            conditions.append(f"MONTH(e.date) = {month}")
        if year:
            conditions.append(f"YEAR(e.date) = {year}")
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = text(f"""
            SELECT 
                COALESCE(c.name, 'Uncategorized') AS category,
                COALESCE(c.icon, '📦') AS icon,
                COALESCE(c.color, '#94A3B8') AS color,
                COUNT(e.id) AS expense_count,
                ROUND(SUM(e.amount), 2) AS total_amount,
                ROUND(AVG(e.amount), 2) AS avg_amount,
                ROUND(
                    (SUM(e.amount) / SUM(SUM(e.amount)) OVER ()) * 100, 
                    2
                ) AS percentage
            FROM expenses e
            LEFT JOIN categories c ON e.category_id = c.id
            {where_clause}
            GROUP BY c.id, c.name, c.icon, c.color
            ORDER BY total_amount DESC
        """)
        
        result = self.db.execute(query)
        return [dict(row._mapping) for row in result]

    def top_expenses(self, limit: int = 10, month: int = None, year: int = None) -> List[dict]:
        """
        Top N most expensive transactions.
        """
        conditions = []
        if month:
            conditions.append(f"MONTH(e.date) = {month}")
        if year:
            conditions.append(f"YEAR(e.date) = {year}")
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = text(f"""
            SELECT 
                e.id,
                e.title,
                e.amount,
                e.date,
                e.merchant,
                COALESCE(c.name, 'Uncategorized') AS category,
                COALESCE(c.icon, '📦') AS icon,
                e.is_anomaly
            FROM expenses e
            LEFT JOIN categories c ON e.category_id = c.id
            {where_clause}
            ORDER BY e.amount DESC
            LIMIT {limit}
        """)
        
        result = self.db.execute(query)
        return [dict(row._mapping) for row in result]

    def daily_spending_trend(self, month: int, year: int) -> List[dict]:
        """
        Day-by-day spending for a given month.
        Uses window function to show running total.
        """
        query = text(f"""
            SELECT 
                e.date,
                DAY(e.date) AS day,
                ROUND(SUM(e.amount), 2) AS daily_total,
                COUNT(e.id) AS transaction_count,
                ROUND(
                    SUM(SUM(e.amount)) OVER (ORDER BY e.date ROWS UNBOUNDED PRECEDING),
                    2
                ) AS running_total
            FROM expenses e
            WHERE MONTH(e.date) = {month} AND YEAR(e.date) = {year}
            GROUP BY e.date
            ORDER BY e.date ASC
        """)
        
        result = self.db.execute(query)
        return [dict(row._mapping) for row in result]

    def spending_rank_by_category(self, year: int = None) -> List[dict]:
        """
        Ranks categories by total spending using RANK() window function.
        """
        year_filter = f"AND YEAR(e.date) = {year}" if year else ""
        
        query = text(f"""
            SELECT 
                COALESCE(c.name, 'Uncategorized') AS category,
                ROUND(SUM(e.amount), 2) AS total_amount,
                COUNT(e.id) AS expense_count,
                RANK() OVER (ORDER BY SUM(e.amount) DESC) AS spending_rank
            FROM expenses e
            LEFT JOIN categories c ON e.category_id = c.id
            WHERE 1=1 {year_filter}
            GROUP BY c.id, c.name
            ORDER BY spending_rank ASC
        """)
        
        result = self.db.execute(query)
        return [dict(row._mapping) for row in result]

    def month_over_month_comparison(self) -> List[dict]:
        """
        Compare this month's spending to last month using LAG() window function.
        """
        query = text("""
            WITH monthly AS (
                SELECT 
                    YEAR(date) AS year,
                    MONTH(date) AS month,
                    MONTHNAME(date) AS month_name,
                    ROUND(SUM(amount), 2) AS total_amount
                FROM expenses
                GROUP BY YEAR(date), MONTH(date), MONTHNAME(date)
            )
            SELECT 
                year,
                month,
                month_name,
                total_amount,
                LAG(total_amount) OVER (ORDER BY year, month) AS prev_month_amount,
                ROUND(
                    total_amount - LAG(total_amount) OVER (ORDER BY year, month),
                    2
                ) AS difference,
                ROUND(
                    ((total_amount - LAG(total_amount) OVER (ORDER BY year, month)) 
                    / NULLIF(LAG(total_amount) OVER (ORDER BY year, month), 0)) * 100,
                    2
                ) AS pct_change
            FROM monthly
            ORDER BY year DESC, month DESC
        """)
        
        result = self.db.execute(query)
        return [dict(row._mapping) for row in result]

    def dashboard_summary(self) -> dict:
        """
        Single query to get everything needed for the dashboard.
        """
        # Current month stats
        current_month_query = text("""
            SELECT 
                ROUND(SUM(amount), 2) AS this_month_total,
                COUNT(id) AS this_month_count,
                ROUND(AVG(amount), 2) AS this_month_avg
            FROM expenses
            WHERE MONTH(date) = MONTH(CURDATE()) 
              AND YEAR(date) = YEAR(CURDATE())
        """)
        
        # Last month stats
        last_month_query = text("""
            SELECT 
                ROUND(SUM(amount), 2) AS last_month_total
            FROM expenses
            WHERE MONTH(date) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
              AND YEAR(date) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
        """)

        # Anomaly count
        anomaly_query = text("""
            SELECT COUNT(id) AS anomaly_count
            FROM expenses
            WHERE is_anomaly = TRUE
              AND MONTH(date) = MONTH(CURDATE())
              AND YEAR(date) = YEAR(CURDATE())
        """)

        # Total all time
        total_query = text("""
            SELECT 
                ROUND(SUM(amount), 2) AS all_time_total,
                COUNT(id) AS all_time_count
            FROM expenses
        """)

        current = dict(self.db.execute(current_month_query).fetchone()._mapping)
        last = dict(self.db.execute(last_month_query).fetchone()._mapping)
        anomaly = dict(self.db.execute(anomaly_query).fetchone()._mapping)
        total = dict(self.db.execute(total_query).fetchone()._mapping)

        # Calculate month-over-month change
        this_month = current.get("this_month_total") or 0
        last_month = last.get("last_month_total") or 0
        pct_change = 0
        if last_month and last_month > 0:
            pct_change = round(((this_month - last_month) / last_month) * 100, 2)

        return {
            "this_month_total": this_month,
            "this_month_count": current.get("this_month_count") or 0,
            "this_month_avg": current.get("this_month_avg") or 0,
            "last_month_total": last_month,
            "month_over_month_pct": pct_change,
            "anomaly_count_this_month": anomaly.get("anomaly_count") or 0,
            "all_time_total": total.get("all_time_total") or 0,
            "all_time_count": total.get("all_time_count") or 0,
        }