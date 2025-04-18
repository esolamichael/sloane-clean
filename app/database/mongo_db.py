# app/database/mongo_db.py

import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from ..utils.secrets import get_secret

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global MongoDB client
_mongo_client = None

def get_mongo_client():
    """Get MongoDB client instance."""
    global _mongo_client
    if _mongo_client is None:
        try:
            # Get MongoDB connection string from Secret Manager or environment
            mongodb_url = get_secret("MONGODB_URL")
            if not mongodb_url:
                logger.error("Failed to get MongoDB connection string")
                raise ConnectionError("Could not retrieve MongoDB connection string")
                
            _mongo_client = MongoClient(
                mongodb_url, 
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                retryWrites=True
            )
            # Test connection to fail fast if there's an issue
            _mongo_client.server_info()
            logger.info("MongoDB client connection successful")
        except Exception as e:
            logger.error(f"Error creating MongoDB client: {str(e)}")
            raise
    return _mongo_client

def get_database():
    """Get MongoDB database instance."""
    try:
        client = get_mongo_client()
        db_name = os.environ.get("MONGODB_NAME", "sloane_ai_service")
        db = client[db_name]
        # Perform a quick operation to verify database connection
        db.command('ping')
        logger.info(f"Successfully connected to MongoDB database: {db_name}")
        return db
    except Exception as e:
        logger.error(f"Error getting database: {str(e)}")
        raise

def close_mongo_connection():
    """Close MongoDB connection."""
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None

def _ensure_indexes(db):
    """Ensure required indexes exist."""
    try:
        # Create indexes
        db.users.create_index("email", unique=True)
        db.businesses.create_index("owner_id")
        db.call_transcripts.create_index([("full_transcript", "text")])
        db.call_transcripts.create_index("business_id")
        db.business_data.create_index("business_id")
        db.business_data.create_index([("business_id", 1), ("data_type", 1)])
        db.ai_training.create_index([("business_id", 1), ("source", 1)])
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")

class DummyDB:
    """Dummy database for testing."""
    def __getitem__(self, name):
        return DummyCollection()

class DummyCollection:
    """Dummy collection for testing."""
    def find_one(self, *args, **kwargs):
        return None
    
    def find(self, *args, **kwargs):
        return DummyCursor()
    
    def insert_one(self, *args, **kwargs):
        return {"inserted_id": "dummy_id"}
    
    def update_one(self, *args, **kwargs):
        return {"matched_count": 0, "modified_count": 0}
    
    def delete_one(self, *args, **kwargs):
        return {"deleted_count": 0}
    
    def delete_many(self, *args, **kwargs):
        return {"deleted_count": 0}
    
    def create_index(self, *args, **kwargs):
        return None

class DummyCursor:
    """Dummy cursor for testing."""
    def to_list(self, *args, **kwargs):
        return []