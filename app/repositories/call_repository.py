# ~/Desktop/clean-code/app/repositories/call_repository.py

import logging
from datetime import datetime
from bson.objectid import ObjectId

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CallRepository:
    """Repository for call transcripts and analysis in MongoDB"""
    
    def __init__(self, db_uri=None):
        """
        Initialize the repository
        
        Args:
            db_uri: MongoDB connection string (will use env if not provided)
        """
        from ..database.mongo_db import get_mongo_db
        self.db = get_mongo_db()
    
    async def create_call_transcript(self, transcript_data):
        """
        Create a new call transcript document
        
        Args:
            transcript_data: Initial transcript data
            
        Returns:
            str: ID of the inserted document
        """
        try:
            # Add metadata
            transcript_data.update({
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            result = await self.db.call_transcripts.insert_one(transcript_data)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating call transcript: {str(e)}")
            raise
    
    async def get_call_transcript(self, call_id):
        """
        Get call transcript document
        
        Args:
            call_id: The call ID
            
        Returns:
            dict: Transcript document or None
        """
        try:
            doc = await self.db.call_transcripts.find_one({"call_id": call_id})
            
            if doc:
                # Convert ObjectId to string for JSON serialization
                doc["_id"] = str(doc["_id"])
                
            return doc
            
        except Exception as e:
            logger.error(f"Error getting call transcript: {str(e)}")
            return None
    
    async def add_to_transcript(self, call_id, speaker, text):
        """
        Add a transcript entry
        
        Args:
            call_id: The call ID
            speaker: Who is speaking (user/ai)
            text: The spoken text
            
        Returns:
            bool: Success status
        """
        try:
            # Get current transcript
            doc = await self.db.call_transcripts.find_one({"call_id": call_id})
            
            if not doc:
                return False
                
            # Create transcript entry
            entry = {
                "timestamp": datetime.utcnow(),
                "speaker": speaker,
                "text": text
            }
            
            # Add to transcript array
            await self.db.call_transcripts.update_one(
                {"call_id": call_id},
                {
                    "$push": {"transcript": entry},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            # Add to call flow
            if speaker == "ai":
                flow_type = "response"
            else:
                flow_type = "input"
                
            flow_entry = {
                "timestamp": datetime.utcnow(),
                "type": flow_type,
                "content": text
            }
            
            await self.db.call_transcripts.update_one(
                {"call_id": call_id},
                {
                    "$push": {"call_flow": flow_entry}
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding to transcript: {str(e)}")
            return False
    
    async def update_transcript(self, call_id, transcript):
        """
        Update the entire transcript
        
        Args:
            call_id: The call ID
            transcript: New transcript array
            
        Returns:
            bool: Success status
        """
        try:
            result = await self.db.call_transcripts.update_one(
                {"call_id": call_id},
                {
                    "$set": {
                        "transcript": transcript,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating transcript: {str(e)}")
            return False
    
    async def update_full_recording_transcript(self, call_id, full_transcript):
        """
        Update the full recording transcript
        
        Args:
            call_id: The call ID
            full_transcript: Full recording transcript text
            
        Returns:
            bool: Success status
        """
        try:
            result = await self.db.call_transcripts.update_one(
                {"call_id": call_id},
                {
                    "$set": {
                        "full_recording_transcript": full_transcript,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating full recording transcript: {str(e)}")
            return False
    
    async def update_summary(self, call_id, summary):
        """
        Update call summary
        
        Args:
            call_id: The call ID
            summary: Call summary text
            
        Returns:
            bool: Success status
        """
        try:
            result = await self.db.call_transcripts.update_one(
                {"call_id": call_id},
                {
                    "$set": {
                        "summary": summary,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating summary: {str(e)}")
            return False
    
    async def update_detected_intents(self, call_id, intents):
        """
        Update detected intents
        
        Args:
            call_id: The call ID
            intents: List of detected intents
            
        Returns:
            bool: Success status
        """
        try:
            # Get current intents
            doc = await self.db.call_transcripts.find_one(
                {"call_id": call_id},
                {"detected_intents": 1}
            )
            
            current_intents = doc.get("detected_intents", []) if doc else []
            
            # Add new intents (avoid duplicates)
            for intent in intents:
                if intent not in current_intents:
                    current_intents.append(intent)
            
            # Update document
            result = await self.db.call_transcripts.update_one(
                {"call_id": call_id},
                {
                    "$set": {
                        "detected_intents": current_intents,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating detected intents: {str(e)}")
            return False
    
    async def update_extracted_entities(self, call_id, entities):
        """
        Update extracted entities
        
        Args:
            call_id: The call ID
            entities: Dictionary of extracted entities
            
        Returns:
            bool: Success status
        """
        try:
            # Get current entities
            doc = await self.db.call_transcripts.find_one(
                {"call_id": call_id},
                {"extracted_entities": 1}
            )
            
            current_entities = doc.get("extracted_entities", {}) if doc else {}
            
            # Merge entities
            for entity_type, values in entities.items():
                if entity_type in current_entities:
                    # If list, extend
                    if isinstance(values, list) and isinstance(current_entities[entity_type], list):
                        for value in values:
                            if value not in current_entities[entity_type]:
                                current_entities[entity_type].append(value)
                    # If dictionary, update
                    elif isinstance(values, dict) and isinstance(current_entities[entity_type], dict):
                        current_entities[entity_type].update(values)
                    # Otherwise replace
                    else:
                        current_entities[entity_type] = values
                else:
                    current_entities[entity_type] = values
            
            # Update document
            result = await self.db.call_transcripts.update_one(
                {"call_id": call_id},
                {
                    "$set": {
                        "extracted_entities": current_entities,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating extracted entities: {str(e)}")
            return False
    
    async def update_sentiment_analysis(self, call_id, sentiment):
        """
        Update sentiment analysis
        
        Args:
            call_id: The call ID
            sentiment: Sentiment analysis result
            
        Returns:
            bool: Success status
        """
        try:
            result = await self.db.call_transcripts.update_one(
                {"call_id": call_id},
                {
                    "$set": {
                        "sentiment_analysis": sentiment,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating sentiment analysis: {str(e)}")
            return False
    
    async def update_call_transcript(self, call_id, data):
        """
        Update call transcript document with arbitrary data
        
        Args:
            call_id: The call ID
            data: Data to update
            
        Returns:
            bool: Success status
        """
        try:
            # Add updated timestamp
            data["updated_at"] = datetime.utcnow()
            
            result = await self.db.call_transcripts.update_one(
                {"call_id": call_id},
                {"$set": data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating call transcript: {str(e)}")
            return False
    
    async def get_calls_by_business(self, business_id, limit=100, skip=0):
        """
        Get calls for a business
        
        Args:
            business_id: The business ID
            limit: Maximum number of records
            skip: Number of records to skip
            
        Returns:
            list: Call transcript documents
        """
        try:
            cursor = self.db.call_transcripts.find(
                {"business_id": business_id}
            ).sort("created_at", -1).skip(skip).limit(limit)
            
            # Convert MongoDB cursor to list
            calls = await cursor.to_list(length=limit)
            
            # Convert ObjectIds to strings for JSON serialization
            for call in calls:
                call["_id"] = str(call["_id"])
                
            return calls
            
        except Exception as e:
            logger.error(f"Error getting calls by business: {str(e)}")
            return []
    
    async def delete_call_transcript(self, call_id):
        """
        Delete call transcript
        
        Args:
            call_id: The call ID
            
        Returns:
            bool: Success status
        """
        try:
            result = await self.db.call_transcripts.delete_one({"call_id": call_id})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting call transcript: {str(e)}")
            return False
