# ~/Desktop/clean-code/app/repositories/business_repository.py

import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson.objectid import ObjectId

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BusinessRepository:
    """Repository for business data storage in MongoDB"""
    
    def __init__(self, db_uri=None):
        """
        Initialize the repository
        
        Args:
            db_uri: MongoDB connection string (will use env if not provided)
        """
        from ..database.mongo_db import get_mongo_db
        self.db = get_mongo_db()
    
    async def save_website_data(self, business_id, website_data):
        """
        Save website scraped data to MongoDB
        
        Args:
            business_id: The business ID
            website_data: The scraped website data
            
        Returns:
            str: ID of the inserted document
        """
        try:
            # Add metadata
            website_data.update({
                "business_id": business_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "data_type": "website_data"
            })
            
            # Check if we already have data for this business URL
            existing = await self.db.business_data.find_one({
                "business_id": business_id,
                "data_type": "website_data",
                "url": website_data.get("url")
            })
            
            if existing:
                # Update the existing document
                website_data["updated_at"] = datetime.utcnow()
                result = await self.db.business_data.update_one(
                    {"_id": existing["_id"]},
                    {"$set": website_data}
                )
                return str(existing["_id"])
            else:
                # Insert new document
                result = await self.db.business_data.insert_one(website_data)
                return str(result.inserted_id)
                
        except Exception as e:
            logger.error(f"Error saving website data: {str(e)}")
            raise
    
    async def save_gbp_data(self, business_id, gbp_data):
        """
        Save Google Business Profile data to MongoDB
        
        Args:
            business_id: The business ID
            gbp_data: The GBP data
            
        Returns:
            str: ID of the inserted document
        """
        try:
            # Add metadata
            gbp_data.update({
                "business_id": business_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "data_type": "gbp_data"
            })
            
            # Check if we already have GBP data for this business
            existing = await self.db.business_data.find_one({
                "business_id": business_id,
                "data_type": "gbp_data"
            })
            
            if existing:
                # Update the existing document
                gbp_data["updated_at"] = datetime.utcnow()
                result = await self.db.business_data.update_one(
                    {"_id": existing["_id"]},
                    {"$set": gbp_data}
                )
                return str(existing["_id"])
            else:
                # Insert new document
                result = await self.db.business_data.insert_one(gbp_data)
                return str(result.inserted_id)
                
        except Exception as e:
            logger.error(f"Error saving GBP data: {str(e)}")
            raise
    
    async def get_business_data(self, business_id, data_type=None):
        """
        Get all data for a business
        
        Args:
            business_id: The business ID
            data_type: Optional filter for data_type (website_data or gbp_data)
            
        Returns:
            list: List of data documents
        """
        try:
            query = {"business_id": business_id}
            
            if data_type:
                query["data_type"] = data_type
                
            cursor = self.db.business_data.find(query)
            
            # Convert MongoDB cursor to list
            data = await cursor.to_list(length=100)
            
            # Convert ObjectIds to strings for JSON serialization
            for item in data:
                item["_id"] = str(item["_id"])
                
            return data
            
        except Exception as e:
            logger.error(f"Error getting business data: {str(e)}")
            return []
    
    async def get_website_data(self, business_id):
        """
        Get website data for a business
        
        Args:
            business_id: The business ID
            
        Returns:
            dict: Website data or None
        """
        try:
            return await self.get_business_data(business_id, "website_data")
        except Exception as e:
            logger.error(f"Error getting website data: {str(e)}")
            return None
    
    async def get_gbp_data(self, business_id):
        """
        Get GBP data for a business
        
        Args:
            business_id: The business ID
            
        Returns:
            dict: GBP data or None
        """
        try:
            return await self.get_business_data(business_id, "gbp_data")
        except Exception as e:
            logger.error(f"Error getting GBP data: {str(e)}")
            return None

    async def delete_business_data(self, business_id, data_type=None):
        """
        Delete business data
        
        Args:
            business_id: The business ID
            data_type: Optional filter for data_type
            
        Returns:
            int: Number of deleted documents
        """
        try:
            query = {"business_id": business_id}
            
            if data_type:
                query["data_type"] = data_type
                
            result = await self.db.business_data.delete_many(query)
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting business data: {str(e)}")
            return 0
