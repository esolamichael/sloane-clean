# backend/database/db_manager.py
from typing import Dict, List, Optional, Any
from fastapi import Depends
from sqlalchemy.orm import Session

# Import our database connections
from .postgres_connection import get_postgres_db
from .mongodb_connection import mongodb

class DatabaseManager:
    """
    Database manager to handle interactions with both SQLite and MongoDB.
    This provides a unified interface for database operations.
    """
    
    def __init__(self, postgres_db: Session = None, mongo_db = None):
        self.postgres_db = postgres_db
        self.mongo_db = mongo_db
    
    # Methods for determining which database to use for different data types
    # [Same methods as before]

# Dependency to get the DatabaseManager with both connections
def get_db_manager(
    postgres_db: Session = Depends(get_postgres_db),
):
    """Dependency for getting a DatabaseManager instance with both database connections."""
    db_manager = DatabaseManager(postgres_db=postgres_db)
    return db_manager
