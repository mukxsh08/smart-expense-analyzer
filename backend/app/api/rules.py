# backend/app/api/rules.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from app.schemas.rule import RuleCreate, RuleResponse
from app.models.rule import Rule
from app.rules.default_rules import seed_default_rules
from app.rules.rule_engine import RuleEngine
from app.schemas.expense import ExpenseCreate
from app.models.expense import Expense

router = APIRouter(prefix="/rules", tags=["Rules"])


@router.get("/", response_model=List[RuleResponse])
def list_rules(db: Session = Depends(get_db)):
    """List all rules."""
    return db.query(Rule).order_by(Rule.priority.desc()).all()


@router.post("/", response_model=RuleResponse, status_code=201)
def create_rule(data: RuleCreate, db: Session = Depends(get_db)):
    """Create a new categorization rule."""
    rule = Rule(**data.dict())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete a rule."""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"message": f"Rule {rule_id} deleted"}


@router.put("/{rule_id}/toggle")
def toggle_rule(rule_id: int, db: Session = Depends(get_db)):
    """Enable or disable a rule."""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    rule.is_active = not rule.is_active
    db.commit()
    return {"message": f"Rule {'enabled' if rule.is_active else 'disabled'}", "is_active": rule.is_active}


@router.post("/seed")
def seed_rules(db: Session = Depends(get_db)):
    """Seed default categorization rules."""
    seeded = seed_default_rules(db)
    if seeded:
        return {"message": "Default rules seeded successfully!"}
    return {"message": "Rules already exist."}


@router.post("/test")
def test_rule_engine(expense: ExpenseCreate, db: Session = Depends(get_db)):
    """
    Test what category the rule engine would assign to an expense WITHOUT saving it.
    Useful for debugging rules.
    """
    # Create a fake expense object (not saved to DB)
    temp_expense = Expense(
        title=expense.title,
        amount=expense.amount,
        date=expense.date,
        merchant=expense.merchant,
        description=expense.description
    )
    
    engine = RuleEngine(db)
    category = engine.apply_rules(temp_expense)
    explanation = engine.explain(temp_expense)
    
    return {
        "expense": {
            "title": expense.title,
            "amount": expense.amount,
            "merchant": expense.merchant
        },
        "assigned_category": category or "Uncategorized (no rule matched)",
        "rule_explanations": [r for r in explanation if r["matched"]]  # Only show matching rules
    }