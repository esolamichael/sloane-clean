import os
from sqlalchemy import create_engine
from backend.database.postgres_connection import Base
from backend.models.postgres_models import *  # Import all SQLAlchemy models

def create_tables():
    """Create all database tables."""
    # Get the database URL (using SQLite for now)
    DATABASE_URL = os.getenv(
        "SQLITE_URL", 
        "sqlite:///./sloane.db"  # SQLite file in current directory
    )
    
    # Create SQLAlchemy engine
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}  # Needed for SQLite
    )
    
    # Create all tables defined in the models
    Base.metadata.create_all(bind=engine)
    print("SQLite tables created successfully!")

if __name__ == "__main__":
    create_tables()
