"""
Database configuration - SQLite for local deployment
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os

# Database path in user's home directory
DB_PATH = os.path.join(os.path.expanduser("~"), ".thamarat", "thamarat.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# SQLite connection string
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine with special settings for SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
