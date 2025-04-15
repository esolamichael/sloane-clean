# ~/Desktop/clean-code/app/call_management/call_handler.py

import logging
import json
from datetime import datetime
import uuid
from ..repositories.training_repository import TrainingRepository
from ..ai_conversation.ai_processor import AIProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CallHandler:
    """
    Core class for handling incoming calls, processing with AI, and managing call data
    """
    
    def __init__(self, db_session=None, training_repo=None, ai_processor=None):
        """
        Initialize the call handler
        
        Args:
            db_session: SQL database session for call metadata
            training_repo: Training repository instance
            ai_processor: AI processor instance
        """
        self.db_session = db_session
        self.training_repo = training_repo or TrainingRepository()
        self.ai_processor = ai_processor or AIProcessor()
        
        # Import here to avoid circular imports
        from ..database.sql_db import get_db_session
        if self.db_session is None:
            self.db_session = get_db_session()
    
    async def handle_incoming_call(self, call_data):
        """
        Handle an incoming call
        
        Args:
            call_data: Dictionary with call information
                - business_id: ID of the business
                - caller_number: Phone number of the caller
                - caller_name: Name of the caller (if available)
                - forwarded_from: Original number the call was forwarded from
                - twilio_sid: Twilio call SID
                
        Returns:
            dict: Response with call handling instructions
        """
        try:
            # Generate a call ID
            call_id = str(uuid.uuid4())
            
            # Get business training data
            business_training = await self.training_repo.get_combined_training_data(call_data["business_id"])
            
            # Create initial call record in PostgreSQL
            call_record = {
                "id": call_id,
                "business_id": call_data["business_id"],
                "caller_number": call_data["caller_number"],
                "caller_name": call_data.get("caller_name", "Unknown"),
                "forwarded_from": call_data.get("forwarded_from"),
                "twilio_sid": call_data["twilio_sid"],
                "start_time": datetime.utcnow(),
                "status": "in-progress",
                "duration": 0,
                "recording_url": None,
                "summary": None,
                "action_required": False
            }
            
            # Store in SQL database
            from ..models.call import Call
            new_call = Call(**call_record)
            self.db_session.add(new_call)
            self.db_session.commit()
            
            # Create initial call transcript document in MongoDB
            from ..repositories.call_repository import CallRepository
            call_repo = CallRepository()
            transcript_doc = {
                "call_id": call_id,
                "business_id": call_data["business_id"],
                "twilio_sid": call_data["twilio_sid"],
                "transcript": [],
                "full_recording_transcript": None,
                "summary": None,
                "detected_intents": [],
                "extracted_entities": {},
                "sentiment_analysis": None,
                "call_flow": []
            }
            await call_repo.create_call_transcript(transcript_doc)
            
            # Prepare AI response for greeting
            business_name = business_training.get("business_name", "our business")
            greeting = await self.ai_processor.generate_greeting(business_training)
            
            # Add to transcript
            await call_repo.add_to_transcript(call_id, "ai", greeting)
            
            # Return response with call ID and greeting
            return {
                "call_id": call_id,
                "business_id": call_data["business_id"],
                "greeting": greeting,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error handling incoming call: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def process_user_speech(self, call_id, speech_text):
        """
        Process speech from the user
        
        Args:
            call_id: The call ID
            speech_text: Transcribed speech text
            
        Returns:
            dict: Response with AI response
        """
        try:
            # Get call data
            from ..repositories.call_repository import CallRepository
            call_repo = CallRepository()
            
            # Add user speech to transcript
            await call_repo.add_to_transcript(call_id, "user", speech_text)
            
            # Get call data including business_id
            call_data = await call_repo.get_call_transcript(call_id)
            business_id = call_data.get("business_id")
            
            if not business_id:
                # Fallback to SQL database
                from ..models.call import Call
                call_record = self.db_session.query(Call).filter(Call.id == call_id).first()
                if call_record:
                    business_id = call_record.business_id
                else:
                    return {"success": False, "error": "Call not found"}
            
            # Get business training data
            business_training = await self.training_repo.get_combined_training_data(business_id)
            
            # Get existing transcript for context
            transcript = call_data.get("transcript", [])
            
            # Generate AI response
            ai_response = await self.ai_processor.generate_response(
                business_training, 
                speech_text, 
                transcript
            )
            
            # Add AI response to transcript
            await call_repo.add_to_transcript(call_id, "ai", ai_response)
            
            # Detect intents
            intents = await self.ai_processor.detect_intents(speech_text, business_training)
            
            # Extract entities
            entities = await self.ai_processor.extract_entities(speech_text)
            
            # Update detected intents and entities
            if intents:
                await call_repo.update_detected_intents(call_id, intents)
            
            if entities:
                await call_repo.update_extracted_entities(call_id, entities)
            
            # Check for appointment scheduling
            if any(intent.get("name") == "schedule_appointment" for intent in intents):
                # Process appointment scheduling
                appointment_data = self._extract_appointment_data(entities)
                
                if appointment_data:
                    # Would integrate with calendar here
                    pass
            
            # Return AI response
            return {
                "call_id": call_id,
                "response": ai_response,
                "intents": intents,
                "entities": entities,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error processing user speech: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _extract_appointment_data(self, entities):
        """Extract appointment data from entities"""
        appointment_data = {}
        
        if "datetime" in entities:
            appointment_data["datetime"] = entities["datetime"]
            
        if "duration" in entities:
            appointment_data["duration"] = entities["duration"]
            
        if "service" in entities:
            appointment_data["service"] = entities["service"]
            
        return appointment_data if appointment_data else None
    
    async def end_call(self, call_id, duration=None, recording_url=None):
        """
        End a call and generate summary
        
        Args:
            call_id: The call ID
            duration: Call duration in seconds
            recording_url: URL to the call recording
            
        Returns:
            dict: Response with status
        """
        try:
            # Update SQL database
            from ..models.call import Call
            call_record = self.db_session.query(Call).filter(Call.id == call_id).first()
            
            if call_record:
                call_record.status = "completed"
                call_record.end_time = datetime.utcnow()
                
                if duration:
                    call_record.duration = duration
                    
                if recording_url:
                    call_record.recording_url = recording_url
                
                self.db_session.commit()
            
            # Get transcript for summary
            from ..repositories.call_repository import CallRepository
            call_repo = CallRepository()
            call_data = await call_repo.get_call_transcript(call_id)
            
            if call_data and "transcript" in call_data:
                # Generate summary
                transcript_text = "\n".join([
                    f"{item['speaker']}: {item['text']}" 
                    for item in call_data["transcript"]
                ])
                
                summary = await self.ai_processor.generate_summary(transcript_text)
                
                # Update summary in both databases
                if call_record:
                    call_record.summary = summary
                    self.db_session.commit()
                
                await call_repo.update_summary(call_id, summary)
                
                # Analyze call for required actions
                action_required, action_items = await self.ai_processor.analyze_for_actions(
                    transcript_text, summary
                )
                
                # Update action required flag
                if call_record and action_required:
                    call_record.action_required = True
                    call_record.action_items = json.dumps(action_items)
                    self.db_session.commit()
                
                # Store action items in MongoDB
                if action_required and action_items:
                    await call_repo.update_call_transcript(
                        call_id, 
                        {"action_required": True, "action_items": action_items}
                    )
                
                return {
                    "call_id": call_id,
                    "summary": summary,
                    "action_required": action_required,
                    "action_items": action_items if action_required else [],
                    "success": True
                }
            
            return {"call_id": call_id, "success": True}
            
        except Exception as e:
            logger.error(f"Error ending call: {str(e)}")
            return {"success": False, "error": str(e)}
