# backend/repositories/ai_training_repository.py
from typing import Dict, List, Optional, Any
from datetime import datetime
from bson.objectid import ObjectId

from ..database.mongodb_connection import mongodb
from ..schemas.mongodb_schemas import AITrainingData

class AITrainingRepository:
    """Repository for AI training data operations using MongoDB."""
    
    collection_name = "ai_training_data"
    
    @classmethod
    async def store_training_data(cls, training_data: Dict) -> str:
        """Store new AI training data."""
        # Validate with Pydantic model
        validated_data = AITrainingData(**training_data)
        
        # Insert into MongoDB
        return await mongodb.insert_document(cls.collection_name, validated_data.dict())
    
    @classmethod
    async def get_training_data_by_id(cls, training_id: str) -> Optional[Dict]:
        """Get training data by its MongoDB ID."""
        return await mongodb.find_document(cls.collection_name, {"_id": ObjectId(training_id)})
    
    @classmethod
    async def get_training_data_by_business(cls, business_id: str, training_type: Optional[str] = None) -> List[Dict]:
        """Get all training data for a specific business, optionally filtered by type."""
        query = {"business_id": business_id}
        if training_type:
            query["training_type"] = training_type
            
        cursor = mongodb.db[cls.collection_name].find(query)
        return [doc async for doc in cursor]
    
    @classmethod
    async def update_training_data(cls, training_id: str, updated_data: Dict) -> bool:
        """Update existing training data."""
        # Update the updated_at timestamp
        if "updated_at" not in updated_data:
            updated_data["updated_at"] = datetime.utcnow()
            
        modified_count = await mongodb.update_document(
            cls.collection_name,
            {"_id": ObjectId(training_id)},
            updated_data
        )
        return modified_count > 0
    
    @classmethod
    async def delete_training_data(cls, training_id: str) -> bool:
        """Delete training data."""
        deleted_count = await mongodb.delete_document(
            cls.collection_name,
            {"_id": ObjectId(training_id)}
        )
        return deleted_count > 0
    
    @classmethod
    async def add_training_examples(cls, training_id: str, new_examples: List[Dict]) -> bool:
        """Add new examples to existing training data."""
        # Get existing document
        existing_doc = await cls.get_training_data_by_id(training_id)
        if not existing_doc:
            return False
            
        # Add examples using the $push operator
        result = await mongodb.db[cls.collection_name].update_one(
            {"_id": ObjectId(training_id)},
            {
                "$push": {"examples": {"$each": new_examples}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
