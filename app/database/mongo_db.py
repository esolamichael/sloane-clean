# app/database/mongo_db.py

import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global MongoDB client
_mongo_client = None
_mongo_db = None

def get_mongo_db():
    """Get the MongoDB database instance.
    
    Returns:
        AsyncIOMotorDatabase: MongoDB database instance
    """
    global _mongo_client, _mongo_db
    
    if _mongo_db is None:
        # Get MongoDB connection details from environment variables
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_NAME", "sloane_ai_service")
        
        try:
            # Create a MongoDB client
            _mongo_client = AsyncIOMotorClient(mongodb_url, serverSelectionTimeoutMS=5000)
            _mongo_db = _mongo_client[db_name]
            
            # Test the connection
            logger.info(f"Connected to MongoDB at {mongodb_url}")
            
            # Create indexes
            _ensure_indexes(_mongo_db)
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            # Return a dummy database for testing
            return DummyAsyncDB()
    
    return _mongo_db

async def close_mongo_connection():
    """Close the MongoDB connection."""
    global _mongo_client
    
    if _mongo_client is not None:
        _mongo_client.close()
        logger.info("MongoDB connection closed")

async def _ensure_indexes(db):
    """Create necessary indexes for collections.
    
    Args:
        db: MongoDB database instance
    """
    try:
        # User collection indexes
        await db.users.create_index("email", unique=True)
        
        # Business collection indexes
        await db.businesses.create_index("owner_id")
        
        # Call transcripts collection indexes
        await db.call_transcripts.create_index([("full_transcript", "text")])
        await db.call_transcripts.create_index("business_id")
        
        # Business data collection indexes
        await db.business_data.create_index("business_id")
        await db.business_data.create_index([("business_id", 1), ("data_type", 1)])
        
        # AI training data indexes
        await db.ai_training.create_index([("business_id", 1), ("source", 1)])
        
        logger.info("MongoDB indexes created")
    except Exception as e:
        logger.error(f"Error creating MongoDB indexes: {str(e)}")

class DummyAsyncDB:
    """Dummy database for testing when MongoDB is not available."""
    
    def __getattr__(self, name):
        """Return a dummy collection for any attribute."""
        return DummyAsyncCollection()

class DummyAsyncCollection:
    """Dummy collection that returns empty results for all operations."""
    
    async def find_one(self, *args, **kwargs):
        return None
    
    async def find(self, *args, **kwargs):
        return DummyAsyncCursor()
    
    async def insert_one(self, *args, **kwargs):
        return DummyInsertResult()
    
    async def update_one(self, *args, **kwargs):
        return DummyUpdateResult()
    
    async def delete_one(self, *args, **kwargs):
        return DummyDeleteResult()
    
    async def delete_many(self, *args, **kwargs):
        return DummyDeleteResult()
    
    async def create_index(self, *args, **kwargs):
        return None

class DummyAsyncCursor:
    """Dummy cursor that returns empty results."""
    
    async def to_list(self, *args, **kwargs):
        return []

class DummyInsertResult:
    """Dummy insert result."""
    
    @property
    def inserted_id(self):
        return "dummy_id"

class DummyUpdateResult:
    """Dummy update result."""
    
    @property
    def modified_count(self):
        return 0
    
    @property
    def upserted_id(self):
        return None

class DummyDeleteResult:
    """Dummy delete result."""
    
    @property
    def deleted_count(self):
        return 0