# backend/repositories/business_data_repository.py
from typing import Dict, List, Optional, Any
from datetime import datetime
from bson.objectid import ObjectId

from ..database.mongodb_connection import mongodb
from ..schemas.mongodb_schemas import ScrapedWebsiteData, GoogleBusinessProfileData

class BusinessDataRepository:
    """Repository for business data operations using MongoDB."""
    
    website_collection = "scraped_website_data"
    gbp_collection = "google_business_profiles"
    
    @classmethod
    async def store_website_data(cls, website_data: Dict) -> str:
        """Store scraped website data."""
        # Validate with Pydantic model
        validated_data = ScrapedWebsiteData(**website_data)
        
        # Insert into MongoDB
        return await mongodb.insert_document(cls.website_collection, validated_data.dict())
    
    @classmethod
    async def store_gbp_data(cls, gbp_data: Dict) -> str:
        """Store Google Business Profile data."""
        # Validate with Pydantic model
        validated_data = GoogleBusinessProfileData(**gbp_data)
        
        # Insert into MongoDB
        return await mongodb.insert_document(cls.gbp_collection, validated_data.dict())
    
    @classmethod
    async def get_website_data(cls, business_id: str) -> List[Dict]:
        """Get all scraped website data for a business."""
        cursor = mongodb.db[cls.website_collection].find(
            {"business_id": business_id}
        ).sort("last_scraped", -1)
        return [doc async for doc in cursor]
    
    @classmethod
    async def get_latest_website_data(cls, business_id: str) -> Optional[Dict]:
        """Get the most recent scraped website data for a business."""
        cursor = mongodb.db[cls.website_collection].find(
            {"business_id": business_id}
        ).sort("last_scraped", -1).limit(1)
        
        documents = [doc async for doc in cursor]
        return documents[0] if documents else None
    
    @classmethod
    async def get_gbp_data(cls, business_id: str) -> Optional[Dict]:
        """Get Google Business Profile data for a business."""
        return await mongodb.find_document(cls.gbp_collection, {"business_id": business_id})
    
    @classmethod
    async def update_website_data(cls, data_id: str, updated_data: Dict) -> bool:
        """Update scraped website data."""
        # Update the last_scraped timestamp
        if "last_scraped" not in updated_data:
            updated_data["last_scraped"] = datetime.utcnow()
            
        modified_count = await mongodb.update_document(
            cls.website_collection,
            {"_id": ObjectId(data_id)},
            updated_data
        )
        return modified_count > 0
    
    @classmethod
    async def update_gbp_data(cls, data_id: str, updated_data: Dict) -> bool:
        """Update Google Business Profile data."""
        # Update the last_updated timestamp
        if "last_updated" not in updated_data:
            updated_data["last_updated"] = datetime.utcnow()
            
        modified_count = await mongodb.update_document(
            cls.gbp_collection,
            {"_id": ObjectId(data_id)},
            updated_data
        )
        return modified_count > 0
    
    @classmethod
    async def extract_business_services(cls, business_id: str) -> List[Dict]:
        """
        Extract services information from both website and GBP data.
        This is useful for training the AI conversation service.
        """
        # Get data from both sources
        gbp_data = await cls.get_gbp_data(business_id)
        website_data = await cls.get_latest_website_data(business_id)
        
        services = []
        
        # Extract from GBP if available
        if gbp_data and "services" in gbp_data and gbp_data["services"]:
            services.extend(gbp_data["services"])
            
        # Extract from website if available (assuming a specific structure)
        if website_data and "sections" in website_data:
            for section in website_data["sections"]:
                if section.get("type") == "services" or "service" in section.get("title", "").lower():
                    # Structure depends on your scraping implementation
                    if "items" in section:
                        services.extend(section["items"])
        
        return services
