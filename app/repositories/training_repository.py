# ~/Desktop/clean-code/app/repositories/training_repository.py

import logging
from datetime import datetime
from bson.objectid import ObjectId

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainingRepository:
    """Repository for AI training data storage and retrieval in MongoDB"""
    
    def __init__(self, db_uri=None):
        """
        Initialize the repository
        
        Args:
            db_uri: MongoDB connection string (will use env if not provided)
        """
        from ..database.mongo_db import get_mongo_db
        self.db = get_mongo_db()
    
    async def save_training_data(self, business_id, training_data):
        """
        Save business training data for AI
        
        Args:
            business_id: ID of the business
            training_data: Training data dictionary
            
        Returns:
            str: ID of the inserted document
        """
        try:
            # Add metadata
            training_data.update({
                "business_id": business_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            # Check if we already have training data from this source for this business
            existing = await self.db.ai_training.find_one({
                "business_id": business_id,
                "source": training_data.get("source")
            })
            
            if existing:
                # Update existing document
                training_data["updated_at"] = datetime.utcnow()
                
                # Merge existing example_qa with new ones
                if "example_qa" in training_data and "example_qa" in existing:
                    # Create a set of existing questions (lowercase for comparison)
                    existing_questions = {q.get("question", "").lower() for q in existing["example_qa"]}
                    
                    # Only add new QA pairs that don't have a similar question
                    new_qa_pairs = [
                        qa for qa in training_data["example_qa"] 
                        if qa.get("question", "").lower() not in existing_questions
                    ]
                    
                    # Combine existing and new QA pairs
                    combined_qa = existing["example_qa"] + new_qa_pairs
                    training_data["example_qa"] = combined_qa
                
                result = await self.db.ai_training.update_one(
                    {"_id": existing["_id"]},
                    {"$set": training_data}
                )
                return str(existing["_id"])
            else:
                # Insert new document
                result = await self.db.ai_training.insert_one(training_data)
                return str(result.inserted_id)
                
        except Exception as e:
            logger.error(f"Error saving training data: {str(e)}")
            raise
    
    async def get_training_data(self, business_id, source=None):
        """
        Get training data for a business
        
        Args:
            business_id: The business ID
            source: Optional source filter (website, gbp, manual, etc.)
            
        Returns:
            list: Training data documents
        """
        try:
            query = {"business_id": business_id}
            
            if source:
                query["source"] = source
            
            cursor = self.db.ai_training.find(query)
            
            # Convert MongoDB cursor to list
            data = await cursor.to_list(length=100)
            
            # Convert ObjectIds to strings for JSON serialization
            for item in data:
                item["_id"] = str(item["_id"])
                
            return data
            
        except Exception as e:
            logger.error(f"Error getting training data: {str(e)}")
            return []
    
    async def get_combined_training_data(self, business_id):
        """
        Get all training data combined for a business
        
        Args:
            business_id: The business ID
            
        Returns:
            dict: Combined training data
        """
        try:
            all_data = await self.get_training_data(business_id)
            
            # Initialize combined data structure
            combined = {
                "business_id": business_id,
                "business_name": "",
                "business_description": "",
                "services": [],
                "contact_info": {},
                "hours": {},
                "example_qa": []
            }
            
            # Prioritize sources (manual entries take precedence over website/gbp)
            sources_priority = ["gbp", "website", "manual"]
            
            # Sort by source priority
            all_data.sort(key=lambda x: sources_priority.index(x.get("source", "")) 
                          if x.get("source", "") in sources_priority else 999)
            
            # Combine data with priority consideration
            for data in all_data:
                # Business name - take first non-empty
                if not combined["business_name"] and data.get("business_name"):
                    combined["business_name"] = data["business_name"]
                    
                # Business description - take first non-empty
                if not combined["business_description"] and data.get("business_description"):
                    combined["business_description"] = data["business_description"]
                
                # Services - add unique items
                if "services" in data:
                    combined["services"].extend([
                        service for service in data["services"] 
                        if service not in combined["services"]
                    ])
                
                # Contact info - update if available
                if "contact_info" in data:
                    combined["contact_info"].update(data["contact_info"])
                
                # Hours - update if available
                if "hours" in data:
                    combined["hours"].update(data["hours"])
                
                # Example Q&A - add all
                if "example_qa" in data:
                    # Avoid duplicates by comparing questions
                    existing_questions = {q.get("question", "").lower() for q in combined["example_qa"]}
                    for qa in data["example_qa"]:
                        if qa.get("question", "").lower() not in existing_questions:
                            combined["example_qa"].append(qa)
                            existing_questions.add(qa.get("question", "").lower())
            
            return combined
            
        except Exception as e:
            logger.error(f"Error getting combined training data: {str(e)}")
            return {}
    
    async def save_manual_training_data(self, business_id, training_data):
        """
        Save manually entered training data
        
        Args:
            business_id: The business ID
            training_data: The training data
            
        Returns:
            str: ID of the inserted document
        """
        try:
            # Mark as manual source
            training_data["source"] = "manual"
            return await self.save_training_data(business_id, training_data)
            
        except Exception as e:
            logger.error(f"Error saving manual training data: {str(e)}")
            raise
    
    async def add_qa_pair(self, business_id, question, answer):
        """
        Add a single Q&A pair to the training data
        
        Args:
            business_id: The business ID
            question: The question
            answer: The answer
            
        Returns:
            bool: Success status
        """
        try:
            # Find or create manual training data
            manual_data = await self.db.ai_training.find_one({
                "business_id": business_id,
                "source": "manual"
            })
            
            qa_pair = {"question": question, "answer": answer}
            
            if manual_data:
                # Add to existing
                if "example_qa" not in manual_data:
                    manual_data["example_qa"] = []
                
                # Check if question already exists
                existing_questions = [q.get("question", "").lower() for q in manual_data["example_qa"]]
                
                if question.lower() not in existing_questions:
                    manual_data["example_qa"].append(qa_pair)
                    manual_data["updated_at"] = datetime.utcnow()
                    
                    await self.db.ai_training.update_one(
                        {"_id": manual_data["_id"]},
                        {"$set": {
                            "example_qa": manual_data["example_qa"],
                            "updated_at": manual_data["updated_at"]
                        }}
                    )
                else:
                    # Update existing answer
                    for i, qa in enumerate(manual_data["example_qa"]):
                        if qa.get("question", "").lower() == question.lower():
                            manual_data["example_qa"][i]["answer"] = answer
                            break
                    
                    manual_data["updated_at"] = datetime.utcnow()
                    
                    await self.db.ai_training.update_one(
                        {"_id": manual_data["_id"]},
                        {"$set": {
                            "example_qa": manual_data["example_qa"],
                            "updated_at": manual_data["updated_at"]
                        }}
                    )
            else:
                # Create new manual training data
                await self.save_manual_training_data(business_id, {
                    "example_qa": [qa_pair]
                })
                
            return True
            
        except Exception as e:
            logger.error(f"Error adding Q&A pair: {str(e)}")
            return False
    
    async def delete_qa_pair(self, business_id, question):
        """
        Delete a Q&A pair from the training data
        
        Args:
            business_id: The business ID
            question: The question to delete
            
        Returns:
            bool: Success status
        """
        try:
            # Find manual training data
            manual_data = await self.db.ai_training.find_one({
                "business_id": business_id,
                "source": "manual"
            })
            
            if manual_data and "example_qa" in manual_data:
                # Filter out the question
                updated_qa = [
                    qa for qa in manual_data["example_qa"] 
                    if qa.get("question", "").lower() != question.lower()
                ]
                
                if len(updated_qa) != len(manual_data["example_qa"]):
                    # Question was found and removed
                    manual_data["updated_at"] = datetime.utcnow()
                    
                    await self.db.ai_training.update_one(
                        {"_id": manual_data["_id"]},
                        {"$set": {
                            "example_qa": updated_qa,
                            "updated_at": manual_data["updated_at"]
                        }}
                    )
                    return True
            
            return False
                
        except Exception as e:
            logger.error(f"Error deleting Q&A pair: {str(e)}")
            return False
