# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from database import engine, Base
from app.models.expense import Expense
from app.models.category import Category
from app.models.rule import Rule

# Import API routers
from app.api.expenses import router as expenses_router
from app.api.categories import router as categories_router
from app.api.rules import router as rules_router
from app.api.analytics import router as analytics_router

# Create all tables in MySQL
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=os.getenv("APP_NAME", "Smart Expense Analyzer"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="""
    ## Smart Expense Analyzer API
    
    An intelligent expense tracking system with:
    - 📊 Automatic categorization via Rule Engine
    - 🔍 SQL-powered analytics
    - 🚨 Anomaly detection
    - 📁 CSV bulk import
    """
)

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(expenses_router)
app.include_router(categories_router)
app.include_router(rules_router)
app.include_router(analytics_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Smart Expense Analyzer API is running!",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "docs": "/docs",
        "endpoints": {
            "expenses": "/expenses",
            "categories": "/categories",
            "rules": "/rules",
            "analytics": "/analytics"
        }
    }


@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"message": "Backend is running"}