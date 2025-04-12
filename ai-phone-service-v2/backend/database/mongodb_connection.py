# backend/database/mongodb_connection.py
import os
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MongoDBConnection:
    """MongoDB connection manager for Sloane AI phone service."""
    
    def __init__(self):
        self.client = None
        self.db = None
        
    async def connect_to_mongodb(self):
        """Connect to MongoDB database."""
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_NAME", "sloane_ai_service")
        
        try:
            self.client = AsyncIOMotorClient(mongodb_url)
            # Verify connection is successful
            await self.client.admin.command('ping')
            self.db = self.client[db_name]
            print(f"Connected to MongoDB at {mongodb_url} successfully.")
            return self.db
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise
            
    async def close_mongodb_connection(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            print("MongoDB connection closed successfully.")
            
    # Basic CRUD operations
    async def insert_document(self, collection_name: str, document: Dict) -> str:
        """Insert a document into a collection and return its ID."""
        result = await self.db[collection_name].insert_one(document)
        return str(result.inserted_id)
    
    async def find_document(self, collection_name: str, query: Dict) -> Optional[Dict]:
        """Find a single document that matches the query."""
        return await self.db[collection_name].find_one(query)
    
    async def find_documents(self, collection_name: str, query: Dict) -> List[Dict]:
        """Find all documents that match the query."""
        cursor = self.db[collection_name].find(query)
        return [doc async for doc in cursor]
    
    async def update_document(self, collection_name: str, query: Dict, update_data: Dict) -> int:
        """Update documents matching the query with the provided data."""
        result = await self.db[collection_name].update_one(
            query, {"$set": update_data}
        )
        return result.modified_count
    
    async def delete_document(self, collection_name: str, query: Dict) -> int:
        """Delete documents matching the query."""
        result = await self.db[collection_name].delete_one(query)
        return result.deleted_count

# Create a singleton instance to be imported elsewhere
mongodb = MongoDBConnection()
