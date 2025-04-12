# backend/repositories/call_transcript_repository.py
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from bson.objectid import ObjectId

from ..database.mongodb_connection import mongodb
from ..schemas.mongodb_schemas import CallTranscript

class CallTranscriptRepository:
    """Repository for call transcript operations using MongoDB."""
    
    collection_name = "call_transcripts"
    
    @classmethod
    async def create_transcript(cls, transcript_data: Dict) -> str:
        """Create a new call transcript."""
        # Validate with Pydantic model
        transcript = CallTranscript(**transcript_data)
        
        # Insert into MongoDB
        return await mongodb.insert_document(cls.collection_name, transcript.dict())
    
    @classmethod
    async def get_transcript_by_id(cls, transcript_id: str) -> Optional[Dict]:
        """Get a transcript by its MongoDB ID."""
        return await mongodb.find_document(cls.collection_name, {"_id": ObjectId(transcript_id)})
    
    @classmethod
    async def get_transcripts_by_business(cls, business_id: str, limit: int = 100, skip: int = 0) -> List[Dict]:
        """Get call transcripts for a specific business."""
        query = {"business_id": business_id}
        cursor = mongodb.db[cls.collection_name].find(query).sort("start_time", -1).skip(skip).limit(limit)
        return [doc async for doc in cursor]
    
    @classmethod
    async def get_recent_transcripts(cls, business_id: str, days: int = 7) -> List[Dict]:
        """Get recent call transcripts for a business."""
        date_threshold = datetime.utcnow() - timedelta(days=days)
        query = {
            "business_id": business_id,
            "start_time": {"$gte": date_threshold}
        }
        cursor = mongodb.db[cls.collection_name].find(query).sort("start_time", -1)
        return [doc async for doc in cursor]
    
    @classmethod
    async def search_transcripts(cls, business_id: str, search_text: str) -> List[Dict]:
        """Search for transcripts containing specific text."""
        query = {
            "business_id": business_id,
            "$text": {"$search": search_text}
        }
        # Note: This requires a text index on the full_transcript field
        cursor = mongodb.db[cls.collection_name].find(query).sort("start_time", -1)
        return [doc async for doc in cursor]
    
    @classmethod
    async def get_transcript_by_call_id(cls, call_id: str) -> Optional[Dict]:
        """Get a transcript by the associated call_id."""
        return await mongodb.find_document(cls.collection_name, {"call_id": call_id})
    
    @classmethod
    async def update_transcript(cls, transcript_id: str, update_data: Dict) -> bool:
        """Update a call transcript."""
        modified_count = await mongodb.update_document(
            cls.collection_name, 
            {"_id": ObjectId(transcript_id)}, 
            update_data
        )
        return modified_count > 0
    
    @classmethod
    async def create_text_index(cls):
        """Create a text index on the full_transcript field for text search."""
        await mongodb.db[cls.collection_name].create_index([("full_transcript", "text")])
        print(f"Created text index on {cls.collection_name}.full_transcript")
