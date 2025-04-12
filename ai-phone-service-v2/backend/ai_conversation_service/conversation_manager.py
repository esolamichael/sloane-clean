"""
Conversation manager for handling the flow of AI phone conversations.
"""
import json
import logging
from . import config
from .nlu_processor import NLUProcessor
from .speech_processor import SpeechProcessor
import requests

logger = logging.getLogger(__name__)

class ConversationManager:
    """
    Manages the conversation flow for AI phone calls.
    """
    
    def __init__(self, business_id=None):
        """
        Initialize the conversation manager.
        
        Args:
            business_id (str): The ID of the business for this conversation.
        """
        self.business_id = business_id
        self.nlu_processor = NLUProcessor()
        self.speech_processor = SpeechProcessor()
        self.conversation_history = []
        self.business_profile = None
        
        if business_id:
            self.load_business_profile(business_id)
    
    def load_business_profile(self, business_id):
        """
        Load the business profile from the Business Profile Service.
        
        Args:
            business_id (str): The ID of the business.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # In a real implementation, this would make an API call to the Business Profile Service
            # For demonstration, we'll create a mock business profile
            self.business_profile = {
                "id": business_id,
                "name": "Sample Business",
                "greeting": "Thank you for calling Sample Business. This is Rosie, how can I help you today?",
                "business_hours": {
                    "monday": "9:00 AM - 5:00 PM",
                    "tuesday": "9:00 AM - 5:00 PM",
                    "wednesday": "9:00 AM - 5:00 PM",
                    "thursday": "9:00 AM - 5:00 PM",
                    "friday": "9:00 AM - 5:00 PM",
                    "saturday": "Closed",
                    "sunday": "Closed"
                },
                "services": [
                    "Consultation",
                    "Installation",
                    "Repair",
                    "Maintenance"
                ],
                "faqs": [
                    {
                        "question": "What are your business hours?",
                        "answer": "We are open Monday through Friday from 9:00 AM to 5:00 PM. We are closed on weekends."
                    },
                    {
                        "question": "Do you offer free estimates?",
                        "answer": "Yes, we offer free estimates for all our services. You can schedule an estimate by booking an appointment."
                    },
                    {
                        "question": "What forms of payment do you accept?",
                        "answer": "We accept all major credit cards, cash, and checks."
                    }
                ],
                "appointment_scheduling": {
                    "enabled": True,
                    "calendar_id": "sample_calendar_id",
                    "duration_minutes": 60
                },
                "transfer_settings": {
                    "high_value_keywords": ["urgent", "emergency", "immediately", "right now", "premium"],
                    "transfer_number": "+15551234567"
                },
                "notification_settings": {
                    "email": "business@example.com",
                    "sms": "+15551234567",
                    "notify_on_all_calls": True
                }
            }
            return True
        except Exception as e:
            logger.error(f"Failed to load business profile: {str(e)}")
            return False
    
    def start_conversation(self):
        """
        Start a new conversation with a greeting.
        
        Returns:
            dict: The greeting response.
        """
        if not self.business_profile:
            greeting = "Hello, how can I help you today?"
        else:
            greeting = self.business_profile.get("greeting", "Hello, how can I help you today?")
        
        # Add greeting to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "text": greeting
        })
        
        return {
            "text": greeting,
            "audio": self.speech_processor.text_to_speech(greeting)
        }
    
    def process_user_input(self, audio_content=None, text=None):
        """
        Process user input and generate a response.
        
        Args:
            audio_content (bytes, optional): The audio content from the user.
            text (str, optional): The text input from the user (if already transcribed).
            
        Returns:
            dict: The response with text and audio.
        """
        # Convert audio to text if provided
        if audio_content and not text:
            text = self.speech_processor.recognize_speech(audio_content)
        
        if not text:
            # If we couldn't get text, ask the user to repeat
            response_text = "I'm sorry, I couldn't understand that. Could you please repeat?"
            return {
                "text": response_text,
                "audio": self.speech_processor.text_to_speech(response_text)
            }
        
        # Add user input to conversation history
        self.conversation_history.append({
            "role": "user",
            "text": text
        })
        
        # Process the text with NLU
        nlu_result = self.nlu_processor.process(text)
        
        # Generate response based on NLU result
        response = self.generate_response(nlu_result)
        
        # Add response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "text": response["text"]
        })
        
        return response
    
    def generate_response(self, nlu_result):
        """
        Generate a response based on the NLU result.
        
        Args:
            nlu_result (dict): The NLU processing result.
            
        Returns:
            dict: The response with text and audio.
        """
        intent = nlu_result["intent"]["intent"]
        entities = nlu_result["entities"]
        
        # Check if this is a high-value call that should be transferred
        if self.should_transfer_call(nlu_result):
            return self.handle_call_transfer()
        
        # Handle different intents
        if intent == "greeting":
            return self.handle_greeting()
        elif intent == "appointment_scheduling":
            return self.handle_appointment_scheduling(entities)
        elif intent == "business_hours":
            return self.handle_business_hours()
        elif intent == "service_inquiry":
            return self.handle_service_inquiry(entities)
        elif intent == "pricing":
            return self.handle_pricing(entities)
        elif intent == "complaint":
            return self.handle_complaint(entities)
        elif intent == "urgent_request":
            return self.handle_urgent_request(entities)
        elif intent == "general_question":
            return self.handle_general_question(nlu_result["text"])
        elif intent == "contact_request":
            return self.handle_contact_request(entities)
        elif intent == "goodbye":
            return self.handle_goodbye()
        else:
            # Default fallback response
            return self.handle_fallback()
    
    def should_transfer_call(self, nlu_result):
        """
        Determine if the call should be transferred to a live person.
        
        Args:
            nlu_result (dict): The NLU processing result.
            
        Returns:
            bool: True if the call should be transferred, False otherwise.
        """
        if not self.business_profile or "transfer_settings" not in self.business_profile:
            return False
        
        # Check for high-value keywords
        high_value_keywords = self.business_profile["transfer_settings"].get("high_value_keywords", [])
        text_lower = nlu_result["text"].lower()
        
        # Check if any high-value keywords are in the text
        for keyword in high_value_keywords:
            if keyword.lower() in text_lower:
                return True
        
        # Check for urgent intent with high confidence
        if nlu_result["intent"]["intent"] == "urgent_request" and nlu_result["intent"]["confidence"] > 0.6:
            return True
        
        # Check for complaint intent with high confidence
        if nlu_result["intent"]["intent"] == "complaint" and nlu_result["intent"]["confidence"] > 0.7:
            return True
        
        return False
    
    def handle_call_transfer(self):
        """
        Handle transferring the call to a live person.
        
        Returns:
            dict: The response with text and audio.
        """
        if not self.business_profile or "transfer_settings" not in self.business_profile:
            return self.handle_fallback()
        
        transfer_number = self.business_profile["transfer_settings"].get("transfer_number")
        if not transfer_number:
            return self.handle_fallback()
        
        response_text = "I'll transfer you to a representative who can help you with this. Please hold while I connect you."
        
        # In a real implementation, this would trigger the call transfer via Twilio
        # For demonstration, we'll just return the response
        
        return {
            "text": response_text,
            "audio": self.speech_processor.text_to_speech(response_text),
            "action": {
                "type": "transfer",
                "number": transfer_number
            }
        }
    
    def handle_greeting(self):
        """Handle greeting intent."""
        response_text = "Hello! How can I assist you today?"
        return {
            "text": response_text,
            "audio": self.speech_processor.text_to_speech(response_text)
        }
    
    def handle_appointment_scheduling(self, entities):
        """Handle appointment scheduling intent."""
        # Extract date and time entities if available
        date_entity = next((e for e in entities if e["type"] == "DATE"), None)
        time_entity = next((e for e in entities if e["type"] == "TIME"), None)
        
        if date_entity and time_entity:
            response_text = f"I'd be happy to schedule an appointment for {date_entity['text']} at {time_entity['text']}. Let me check availability."
            # In a real implementation, this would check calendar availability
            # For demonstration, we'll just return a confirmation
            response_text += " That time is available. Would you like me to book this appointment for you?"
        else:
            response_text = "I'd be happy to help you schedule an appointment. What day and time works best for you?"
        
        return {
            "text": response_text,
            "audio": self.speech_processor.text_to_speech(response_text)
        }
    
    def handle_business_hours(self):
        """Handle business hours intent."""
        if not self.business_profile or "business_hours" not in self.business_profile:
            response_text = "I'm sorry, I don't have information about the business hours. Would you like me to take a message for someone to get back to you?"
        else:
            hours = self.business_profile["business_hours"]
            response_text = "Our business hours are: "
            for day, time in hours.items():
                response_text += f"{day.capitalize()}: {time}. "
        
        return {
            "text": response_text,
            "audio": self.speech_processor.text_to_speech(response_text)
        }
    
    def handle_service_inquiry(self, entities):
        """Handle service inquiry intent."""
        if not self.business_profile or "services" not in self.business_profile:
            response_text = "I'm sorry, I don't have detailed information about our services. Would you like me to take a message for someone to get back to you?"
        else:
            services = self.business_profile["services"]
            response_text = "We offer the following services: " + ", ".join(services) + ". Would you like more information about any specific service?"
        
        return {
            "text": response_text,
            "audio": self.speech_processor.text_to_speech(response_text)
        }
    
    def handle_pricing(self, entities):
        """Handle pricing intent."""
        response_text = "Our pricing varies depending on the specific service you're interested in. Would you like me to take your contact information so someone can provide you with a detailed quote?"
        
        return {
            "text": response_text,
            "audio": self.speech_processor.text_to_speech(response_text)
        }
    
    def handle_complaint(self, entities):
        """Handle complaint intent."""
        response_text = "I'm sorry to hear you're experiencing an issue. I'd like to make sure this gets addressed properly. Could you provide me with some details about your concern, and I'll make sure the right person gets back to you as soon as possible."
        
        return {
            "text": response_text,
            "audio": self.speech_processor.text_to_speech(response_text)
        }
    
    def handle_urgent_request(self, entities):
        """Handle urgent request intent."""
        response_text = "I understand this is urgent. Let me collect some information so we can address this right away. Could you briefly describe the situation and provide your contact details?"
        
        return {
            "text": response_text,
            "audio": self.speech_processor.text_to_speech(response_text)
        }
    
    def handle_general_question(self, question_text):
        """Handle general question intent."""
        if not self.business_profile or "faqs" not in self.business_profile:
            response_text = "I'll do my best to answer your question. Could you provide more details so I can help you better?"
        else:
            # Simple FAQ matching
            faqs = self.business_profile["faqs"]
            best_match = None
            best_match_score = 0
            
            # Very simple keyword matching for demonstration
            # In a real implementation, this would use more sophisticated matching
            for faq in faqs:
                question_lower = faq["question"].lower()
                user_question_lower = question_text.lower()
                
                # Count matching words
                question_words = set(question_lower.split())
                user_words = set(user_question_lower.split())
                matching_words = question_words.intersection(user_words)
                
                score = len(matching_words) / len(question_words) if question_words else 0
                
                if score > best_match_score and score > 0.3:  # Threshold for matching
                    best_match = faq
                    best_match_score = score
            
            if best_match:
                response_text = best_match["answer"]
            else:
                response_text = "I don't have a specific answer to that question. Would you like me to take a message for someone to get back to you with more information?"
        
        return {
            "text": response_text,
            "audio": self.speech_processor.text_to_speech(response_text)
        }
    
    def handle_contact_request(self, entities):
        """Handle contact request intent."""
        response_text = "I'd be happy to have someone contact you. Could you please provide your name, phone number, and a brief message about what you'd like to discuss?"
        
        return {
            "text": response_text,
            "audio": self.speech_processor.text_to_speech(response_text)
        }
    
    def handle_goodbye(self):
        """Handle goodbye intent."""
        response_text = "Thank you for calling. Have a great day!"
        
        return {
            "text": response_text,
            "audio": self.speech_processor.text_to_speech(response_text),
            "action": {
                "type": "end_call"
            }
        }
    
    def handle_fallback(self):
        """Handle fallback for unrecognized intents."""
        response_text = "I'm not sure I understood that correctly. Could you please rephrase or let me know how else I can assist you today?"
        
        return {
            "text": response_text,
            "audio": self.speech_processor.text_to_speech(response_text)
        }
    
    def send_notification(self, call_data):
        """
        Send a notification about the call to the business.
        
        Args:
            call_data (dict): Data about the call.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.business_profile or "notification_settings" not in self.business_profile:
            return False
        
        notification_settings = self.business_profile["notification_settings"]
        
        # Prepare notification data
        notification = {
            "business_id": self.business_id,
            "call_id": call_data.get("call_id"),
            "caller_number": call_data.get("caller_number"),
            "timestamp": call_data.get("timestamp"),
            "duration": call_data.get("duration"),
            "transcription": self.get_conversation_transcript(),
            "notification_type": "call_completed",
            "email": notification_settings.get("email"),
            "sms": notification_settings.get("sms")
        }
        
        try:
            # In a real implementation, this would make an API call to the Notification Service
            # For demonstration, we'll just log the notification
            logger.info(f"Sending notification: {json.dumps(notification)}")
            return True
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return False
    
    def get_conversation_transcript(self):
        """
        Get a formatted transcript of the conversation.
        
        Returns:
            str: The conversation transcript.
        """
        transcript = ""
        for message in self.conversation_history:
            role = "AI" if message["role"] == "assistant" else "Caller"
            transcript += f"{role}: {message['text']}\n"
        
        return transcript
