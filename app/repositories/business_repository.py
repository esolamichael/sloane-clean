# ~/Desktop/clean-code/app/repositories/business_repository.py

import logging
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
import os
from datetime import datetime
from bson.objectid import ObjectId
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BusinessRepository:
    """Repository for managing business data"""
    
    def __init__(self):
        """Initialize the repository with MongoDB connection"""
        # Try to use get_secret for direct access to secret with correct name
        try:
            from ..utils.secrets import get_secret
            mongodb_url = get_secret("mongodb-connection")
            if not mongodb_url:
                mongodb_url = os.environ.get("MONGODB_URL", "mongodb://localhost:27017")
        except (ImportError, ModuleNotFoundError):
            # Fall back to environment variable
            mongodb_url = os.environ.get("MONGODB_URL", "mongodb://localhost:27017")
        
        self.client = MongoClient(mongodb_url)
        self.db = self.client.sloane_ai_service
        
    def create_business(self, business_data: Dict[str, Any]) -> Optional[str]:
        """Create a new business."""
        try:
            # Add timestamps
            business_data["created_at"] = datetime.utcnow()
            business_data["updated_at"] = datetime.utcnow()
            
            # Insert the business
            result = self.db.businesses.insert_one(business_data)
            return str(result.inserted_id) if result.inserted_id else None
            
        except Exception as e:
            logger.error(f"Error creating business: {str(e)}")
            return None
            
    def get_business(self, business_id: str) -> Optional[Dict[str, Any]]:
        """Get a business by ID."""
        try:
            # Get the business
            business = self.db.businesses.find_one({"business_id": business_id})
            return business
            
        except Exception as e:
            logger.error(f"Error getting business: {str(e)}")
            return None
            
    def update_business(self, business_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a business."""
        try:
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            # Update the business
            result = self.db.businesses.update_one(
                {"business_id": business_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating business: {str(e)}")
            return False
            
    def delete_business(self, business_id: str) -> bool:
        """Delete a business."""
        try:
            # Delete the business
            result = self.db.businesses.delete_one({"business_id": business_id})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting business: {str(e)}")
            return False
            
    def list_businesses(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List all businesses with pagination."""
        try:
            # Get businesses with pagination
            cursor = self.db.businesses.find().sort(
                "created_at", -1
            ).skip(skip).limit(limit)
            
            businesses = list(cursor)
            return businesses
            
        except Exception as e:
            logger.error(f"Error listing businesses: {str(e)}")
            return []
            
    def search_businesses(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for businesses based on criteria."""
        try:
            # Search for businesses
            cursor = self.db.businesses.find(query)
            businesses = list(cursor)
            return businesses
            
        except Exception as e:
            logger.error(f"Error searching businesses: {str(e)}")
            return []
            
    def update_business_settings(self, business_id: str, settings: Dict[str, Any]) -> bool:
        """Update business settings."""
        try:
            # Update settings
            result = self.db.businesses.update_one(
                {"business_id": business_id},
                {
                    "$set": {
                        "settings": settings,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating business settings: {str(e)}")
            return False
            
    def get_business_settings(self, business_id: str) -> Optional[Dict[str, Any]]:
        """Get business settings."""
        try:
            # Get business with settings
            business = self.db.businesses.find_one(
                {"business_id": business_id},
                {"settings": 1}
            )
            return business.get("settings") if business else None
            
        except Exception as e:
            logger.error(f"Error getting business settings: {str(e)}")
            return None

    def save_website_data(self, business_id, website_data):
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
            existing = self.db.business_data.find_one({
                "business_id": business_id,
                "data_type": "website_data",
                "url": website_data.get("url")
            })
            
            if existing:
                # Update the existing document
                website_data["updated_at"] = datetime.utcnow()
                result = self.db.business_data.update_one(
                    {"_id": existing["_id"]},
                    {"$set": website_data}
                )
                return str(existing["_id"])
            else:
                # Insert new document
                result = self.db.business_data.insert_one(website_data)
                return str(result.inserted_id)
                
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB connection error while saving website data: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error saving website data: {str(e)}")
            raise
    
    def save_gbp_data(self, business_id, gbp_data):
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
            existing = self.db.business_data.find_one({
                "business_id": business_id,
                "data_type": "gbp_data"
            })
            
            if existing:
                # Update the existing document
                gbp_data["updated_at"] = datetime.utcnow()
                result = self.db.business_data.update_one(
                    {"_id": existing["_id"]},
                    {"$set": gbp_data}
                )
                return str(existing["_id"])
            else:
                # Insert new document
                result = self.db.business_data.insert_one(gbp_data)
                return str(result.inserted_id)
                
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB connection error while saving GBP data: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error saving GBP data: {str(e)}")
            raise
    
    def get_business_data(self, business_id, data_type=None):
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
            return list(cursor)
                
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB connection error while getting business data: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting business data: {str(e)}")
            raise
    
    def get_website_data(self, business_id):
        """
        Get website data for a business
        
        Args:
            business_id: The business ID
            
        Returns:
            dict: Website data document
        """
        try:
            return self.get_business_data(business_id, "website_data")
        except Exception as e:
            logger.error(f"Error getting website data: {str(e)}")
            raise
    
    def get_gbp_data(self, business_id):
        """
        Get Google Business Profile data for a business
        
        Args:
            business_id: The business ID
            
        Returns:
            dict: GBP data document
        """
        try:
            return self.get_business_data(business_id, "gbp_data")
        except Exception as e:
            logger.error(f"Error getting GBP data: {str(e)}")
            raise
    
    def delete_business_data(self, business_id, data_type=None):
        """
        Delete business data
        
        Args:
            business_id: The business ID
            data_type: Optional filter for data_type (website_data or gbp_data)
            
        Returns:
            int: Number of documents deleted
        """
        try:
            query = {"business_id": business_id}
            
            if data_type:
                query["data_type"] = data_type
                
            result = self.db.business_data.delete_many(query)
            return result.deleted_count
                
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB connection error while deleting business data: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error deleting business data: {str(e)}")
            raise
