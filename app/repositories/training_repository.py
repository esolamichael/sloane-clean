# ~/Desktop/clean-code/app/repositories/training_repository.py

import logging
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainingRepository:
    """Repository for managing AI training data"""
    
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
        
    def save_training_data(self, business_id: str, training_data: Dict[str, Any]) -> bool:
        """Save training data for a business."""
        try:
            # Add business ID to training data
            training_data["business_id"] = business_id
            
            # Check if training data already exists for this business
            existing = self.db.ai_training.find_one({
                "business_id": business_id,
                "source": training_data.get("source")
            })
            
            if existing:
                # Update existing training data
                result = self.db.ai_training.update_one(
                    {"_id": existing["_id"]},
                    {"$set": training_data}
                )
                return result.modified_count > 0
            else:
                # Insert new training data
                result = self.db.ai_training.insert_one(training_data)
                return bool(result.inserted_id)
                
        except Exception as e:
            logger.error(f"Error saving training data: {str(e)}")
            return False
            
    def get_training_data(self, business_id: str, source: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get training data for a business."""
        try:
            # Build query
            query = {"business_id": business_id}
            if source:
                query["source"] = source
                
            # Get training data
            cursor = self.db.ai_training.find(query)
            data = list(cursor)
            
            if not data:
                logger.warning(f"No training data found for business {business_id}")
                return []
                
            return data
            
        except Exception as e:
            logger.error(f"Error getting training data: {str(e)}")
            return []
            
    def get_combined_training_data(self, business_id: str) -> Dict[str, Any]:
        """Get combined training data from all sources for a business."""
        try:
            # Get all training data for the business
            all_data = self.get_training_data(business_id)
            
            # Combine data from different sources
            combined_data = {
                "business_id": business_id,
                "business_info": {},
                "example_qa": [],
                "common_phrases": [],
                "keywords": [],
                "services": [],
                "products": [],
                "policies": [],
                "hours": {},
                "contact_info": {}
            }
            
            for data in all_data:
                # Update business info
                if data.get("business_info"):
                    combined_data["business_info"].update(data["business_info"])
                    
                # Extend lists
                if data.get("example_qa"):
                    combined_data["example_qa"].extend(data["example_qa"])
                if data.get("common_phrases"):
                    combined_data["common_phrases"].extend(data["common_phrases"])
                if data.get("keywords"):
                    combined_data["keywords"].extend(data["keywords"])
                if data.get("services"):
                    combined_data["services"].extend(data["services"])
                if data.get("products"):
                    combined_data["products"].extend(data["products"])
                if data.get("policies"):
                    combined_data["policies"].extend(data["policies"])
                    
                # Update hours if present
                if data.get("hours"):
                    combined_data["hours"].update(data["hours"])
                    
                # Update contact info if present
                if data.get("contact_info"):
                    combined_data["contact_info"].update(data["contact_info"])
                    
            # Remove duplicates from lists
            combined_data["example_qa"] = list({str(qa): qa for qa in combined_data["example_qa"]}.values())
            combined_data["common_phrases"] = list(set(combined_data["common_phrases"]))
            combined_data["keywords"] = list(set(combined_data["keywords"]))
            combined_data["services"] = list(set(combined_data["services"]))
            combined_data["products"] = list(set(combined_data["products"]))
            combined_data["policies"] = list(set(combined_data["policies"]))
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Error getting combined training data: {str(e)}")
            return {
                "business_id": business_id,
                "error": str(e)
            }
            
    def save_manual_training_data(self, business_id: str, training_data: Dict[str, Any]) -> bool:
        """Save manually entered training data."""
        try:
            # Set source as manual
            training_data["source"] = "manual"
            
            # Save the training data
            return self.save_training_data(business_id, training_data)
            
        except Exception as e:
            logger.error(f"Error saving manual training data: {str(e)}")
            return False
            
    def add_qa_pair(self, business_id: str, question: str, answer: str) -> bool:
        """Add a Q&A pair to the manual training data."""
        try:
            # Get existing manual training data
            manual_data = self.db.ai_training.find_one({
                "business_id": business_id,
                "source": "manual"
            })
            
            qa_pair = {
                "question": question,
                "answer": answer
            }
            
            if manual_data:
                # Add to existing manual data
                example_qa = manual_data.get("example_qa", [])
                
                # Check if question already exists
                for qa in example_qa:
                    if qa["question"] == question:
                        # Update answer if question exists
                        qa["answer"] = answer
                        self.db.ai_training.update_one(
                            {"_id": manual_data["_id"]},
                            {"$set": {"example_qa": example_qa}}
                        )
                        return True
                        
                # Add new Q&A pair
                example_qa.append(qa_pair)
                self.db.ai_training.update_one(
                    {"_id": manual_data["_id"]},
                    {"$set": {"example_qa": example_qa}}
                )
                return True
            else:
                # Create new manual training data
                return self.save_manual_training_data(business_id, {
                    "example_qa": [qa_pair]
                })
                
        except Exception as e:
            logger.error(f"Error adding Q&A pair: {str(e)}")
            return False
            
    def delete_qa_pair(self, business_id: str, question: str) -> bool:
        """Delete a Q&A pair from the manual training data."""
        try:
            # Get existing manual training data
            manual_data = self.db.ai_training.find_one({
                "business_id": business_id,
                "source": "manual"
            })
            
            if not manual_data:
                logger.warning(f"No manual training data found for business {business_id}")
                return False
                
            # Remove Q&A pair with matching question
            example_qa = manual_data.get("example_qa", [])
            original_length = len(example_qa)
            example_qa = [qa for qa in example_qa if qa["question"] != question]
            
            if len(example_qa) == original_length:
                logger.warning(f"Q&A pair with question '{question}' not found")
                return False
                
            # Update manual training data
            self.db.ai_training.update_one(
                {"_id": manual_data["_id"]},
                {"$set": {"example_qa": example_qa}}
            )
            return True
            
        except Exception as e:
            logger.error(f"Error deleting Q&A pair: {str(e)}")
            return False
