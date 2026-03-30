# backend/app/rules/rule_engine.py

from sqlalchemy.orm import Session
from app.models.rule import Rule
from app.models.expense import Expense
from typing import Optional, List
import re


class RuleEngine:
    """
    The Rule Engine automatically assigns a category to an expense
    by checking a set of rules stored in the database.
    
    Rule Types:
    1. keyword     - Matches if the text CONTAINS one of the keywords
                     Example: condition="uber,ola,rapido" matches "Uber ride"
    
    2. merchant    - Matches if merchant name contains the value
                     Example: condition="amazon" matches merchant "Amazon India"
    
    3. amount_range - Matches if amount is within a range
                      Example: condition="0-500" matches amount 350
    """

    def __init__(self, db: Session):
        self.db = db
        # Load all active rules, sorted by priority (highest first)
        self.rules: List[Rule] = (
            db.query(Rule)
            .filter(Rule.is_active == True)
            .order_by(Rule.priority.desc())
            .all()
        )

    def apply_rules(self, expense: Expense) -> Optional[str]:
        """
        Check each rule against the expense.
        Return the category name of the FIRST matching rule.
        Returns None if no rule matches.
        """
        for rule in self.rules:
            if self._matches(rule, expense):
                return rule.category_name
        return None

    def _matches(self, rule: Rule, expense: Expense) -> bool:
        """Check if a single rule matches an expense."""
        
        if rule.rule_type == "keyword":
            return self._match_keyword(rule, expense)
        
        elif rule.rule_type == "merchant":
            return self._match_merchant(rule, expense)
        
        elif rule.rule_type == "amount_range":
            return self._match_amount_range(rule, expense)
        
        return False

    def _match_keyword(self, rule: Rule, expense: Expense) -> bool:
        """
        Check if any keyword in the condition appears in the target field.
        
        Example:
        condition = "uber,ola,rapido,taxi"
        apply_on = "title"
        expense.title = "Uber ride to airport"
        → Returns True because "uber" is in the title
        """
        keywords = [kw.strip().lower() for kw in rule.condition.split(",")]
        
        # Get the text field to check
        if rule.apply_on == "title":
            text = (expense.title or "").lower()
        elif rule.apply_on == "merchant":
            text = (expense.merchant or "").lower()
        elif rule.apply_on == "description":
            text = (expense.description or "").lower()
        else:
            text = (expense.title or "").lower()

        # Check if ANY keyword appears in the text
        for keyword in keywords:
            if keyword and keyword in text:
                return True
        
        return False

    def _match_merchant(self, rule: Rule, expense: Expense) -> bool:
        """
        Check if merchant name matches the condition.
        
        Example:
        condition = "swiggy,zomato,uber eats"
        expense.merchant = "Swiggy"
        → Returns True
        """
        if not expense.merchant:
            return False
        
        merchant_lower = expense.merchant.lower()
        merchants = [m.strip().lower() for m in rule.condition.split(",")]
        
        for merchant in merchants:
            if merchant and merchant in merchant_lower:
                return True
        
        return False

    def _match_amount_range(self, rule: Rule, expense: Expense) -> bool:
        """
        Check if expense amount is within the specified range.
        
        Example:
        condition = "0-500" means amount between 0 and 500
        condition = "1000+" means amount >= 1000
        condition = "500" means amount == 500 exactly
        """
        condition = rule.condition.strip()
        amount = expense.amount

        try:
            # Handle "1000+" format (greater than or equal)
            if condition.endswith("+"):
                min_val = float(condition[:-1])
                return amount >= min_val
            
            # Handle "0-500" range format
            elif "-" in condition:
                parts = condition.split("-")
                min_val = float(parts[0])
                max_val = float(parts[1])
                return min_val <= amount <= max_val
            
            # Handle exact value
            else:
                return amount == float(condition)
        
        except ValueError:
            # If condition can't be parsed, skip this rule
            return False

    def explain(self, expense: Expense) -> List[dict]:
        """
        Debug tool: Show which rules were checked and why they matched/didn't match.
        Useful for understanding why an expense got a certain category.
        """
        explanations = []
        for rule in self.rules:
            matched = self._matches(rule, expense)
            explanations.append({
                "rule_id": rule.id,
                "rule_name": rule.name,
                "rule_type": rule.rule_type,
                "condition": rule.condition,
                "category": rule.category_name,
                "matched": matched
            })
        return explanations