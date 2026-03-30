# backend/app/services/category_service.py

from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate
from typing import List, Optional


# Default categories to seed the database with
DEFAULT_CATEGORIES = [
    {"name": "Food & Dining", "icon": "🍔", "color": "#F59E0B", "description": "Restaurants, groceries, food delivery"},
    {"name": "Transport", "icon": "🚗", "color": "#3B82F6", "description": "Uber, Ola, fuel, metro, bus"},
    {"name": "Shopping", "icon": "🛍️", "color": "#EC4899", "description": "Online and offline shopping"},
    {"name": "Entertainment", "icon": "🎬", "color": "#8B5CF6", "description": "Movies, streaming, games"},
    {"name": "Health", "icon": "🏥", "color": "#10B981", "description": "Medical, pharmacy, gym"},
    {"name": "Utilities", "icon": "💡", "color": "#6B7280", "description": "Electricity, water, internet, phone"},
    {"name": "Education", "icon": "📚", "color": "#0EA5E9", "description": "Courses, books, subscriptions"},
    {"name": "Travel", "icon": "✈️", "color": "#F97316", "description": "Flights, hotels, trips"},
    {"name": "Miscellaneous", "icon": "📦", "color": "#94A3B8", "description": "Anything else"},
]


class CategoryService:

    @staticmethod
    def seed_default_categories(db: Session):
        """Add default categories if none exist."""
        existing = db.query(Category).count()
        if existing == 0:
            for cat_data in DEFAULT_CATEGORIES:
                cat = Category(**cat_data)
                db.add(cat)
            db.commit()
            return True
        return False

    @staticmethod
    def get_all_categories(db: Session) -> List[Category]:
        return db.query(Category).filter(Category.is_active == True).all()

    @staticmethod
    def create_category(db: Session, data: CategoryCreate) -> Category:
        existing = db.query(Category).filter(Category.name == data.name).first()
        if existing:
            raise ValueError(f"Category '{data.name}' already exists")
        category = Category(**data.dict())
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> Optional[Category]:
        return db.query(Category).filter(Category.id == category_id).first()