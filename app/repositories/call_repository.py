# ~/Desktop/clean-code/app/repositories/call_repository.py

import logging
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
import os
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CallRepository:
    """Repository for managing call transcripts and data"""
    
    def __init__(self):
        """Initialize the repository with MongoDB connection"""
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
        
    def create_call_transcript(self, transcript_data: Dict[str, Any]) -> bool:
        """Create a new call transcript."""
        try:
            # Add timestamps
            transcript_data["created_at"] = datetime.utcnow()
            transcript_data["updated_at"] = datetime.utcnow()
            
            # Insert the transcript
            result = self.db.call_transcripts.insert_one(transcript_data)
            return bool(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating call transcript: {str(e)}")
            return False
            
    def get_call_transcript(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get a call transcript by ID."""
        try:
            # Get the transcript
            doc = self.db.call_transcripts.find_one({"call_id": call_id})
            return doc
            
        except Exception as e:
            logger.error(f"Error getting call transcript: {str(e)}")
            return None
            
    def add_to_transcript(self, call_id: str, speaker: str, text: str) -> bool:
        """Add a message to the call transcript."""
        try:
            # Get current transcript
            doc = self.db.call_transcripts.find_one({"call_id": call_id})
            if not doc:
                logger.error(f"No transcript found for call ID: {call_id}")
                return False
                
            # Create message entry
            message = {
                "speaker": speaker,
                "text": text,
                "timestamp": datetime.utcnow()
            }
            
            # Add to transcript array
            self.db.call_transcripts.update_one(
                {"call_id": call_id},
                {
                    "$push": {"transcript": message},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding to transcript: {str(e)}")
            return False
            
    def update_transcript(self, call_id: str, transcript: List[Dict[str, Any]]) -> bool:
        """Update the entire transcript."""
        try:
            # Update the transcript
            result = self.db.call_transcripts.update_one(
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
            
    def update_full_recording_transcript(self, call_id: str, full_transcript: str) -> bool:
        """Update the full recording transcript."""
        try:
            # Update the full transcript
            result = self.db.call_transcripts.update_one(
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
            
    def update_summary(self, call_id: str, summary: str) -> bool:
        """Update the call summary."""
        try:
            # Update the summary
            result = self.db.call_transcripts.update_one(
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
            
    def update_detected_intents(self, call_id: str, intents: List[Dict[str, Any]]) -> bool:
        """Update detected intents."""
        try:
            # Get current intents
            doc = self.db.call_transcripts.find_one(
                {"call_id": call_id},
                {"detected_intents": 1}
            )
            
            if not doc:
                logger.error(f"No transcript found for call ID: {call_id}")
                return False
                
            # Merge with existing intents
            current_intents = doc.get("detected_intents", [])
            updated_intents = current_intents + intents
            
            # Update in database
            result = self.db.call_transcripts.update_one(
                {"call_id": call_id},
                {
                    "$set": {
                        "detected_intents": updated_intents,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating detected intents: {str(e)}")
            return False
            
    def update_extracted_entities(self, call_id: str, entities: List[Dict[str, Any]]) -> bool:
        """Update extracted entities."""
        try:
            # Get current entities
            doc = self.db.call_transcripts.find_one(
                {"call_id": call_id},
                {"extracted_entities": 1}
            )
            
            if not doc:
                logger.error(f"No transcript found for call ID: {call_id}")
                return False
                
            # Merge with existing entities
            current_entities = doc.get("extracted_entities", [])
            updated_entities = current_entities + entities
            
            # Update in database
            result = self.db.call_transcripts.update_one(
                {"call_id": call_id},
                {
                    "$set": {
                        "extracted_entities": updated_entities,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating extracted entities: {str(e)}")
            return False
            
    def update_sentiment_analysis(self, call_id: str, sentiment: Dict[str, Any]) -> bool:
        """Update sentiment analysis results."""
        try:
            # Update sentiment analysis
            result = self.db.call_transcripts.update_one(
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
            
    def update_call_transcript(self, call_id: str, data: Dict[str, Any]) -> bool:
        """Update multiple fields in the call transcript."""
        try:
            # Add updated timestamp
            data["updated_at"] = datetime.utcnow()
            
            # Update the document
            result = self.db.call_transcripts.update_one(
                {"call_id": call_id},
                {"$set": data}
            )
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating call transcript: {str(e)}")
            return False
            
    def get_calls_by_business(self, business_id: str, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Get call transcripts for a business."""
        try:
            # Get calls with pagination
            cursor = self.db.call_transcripts.find(
                {"business_id": business_id}
            ).sort("created_at", -1).skip(skip).limit(limit)
            
            calls = list(cursor)
            return calls
            
        except Exception as e:
            logger.error(f"Error getting calls by business: {str(e)}")
            return []
            
    def delete_call_transcript(self, call_id: str) -> bool:
        """Delete a call transcript."""
        try:
            # Delete the transcript
            result = self.db.call_transcripts.delete_one({"call_id": call_id})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting call transcript: {str(e)}")
            return False
