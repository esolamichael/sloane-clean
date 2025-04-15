# ~/Desktop/clean-code/app/ai_conversation/ai_processor.py

import logging
import json
import os
from datetime import datetime
import requests
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProcessor:
    """
    Handles all AI conversation processing for the phone service
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the AI processor
        
        Args:
            api_key: API key for the AI service (uses env if not provided)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.api_base = os.getenv("AI_API_BASE", "https://api.openai.com/v1")
        self.model = os.getenv("AI_MODEL", "gpt-4")
        self.provider = os.getenv("AI_PROVIDER", "openai").lower()
        
        # Ensure API key is set
        if not self.api_key:
            logger.warning("No AI API key provided. Using dummy responses for development.")
    
    async def generate_greeting(self, business_data):
        """
        Generate an initial greeting for a call
        
        Args:
            business_data: Business training data
            
        Returns:
            str: Greeting message
        """
        try:
            if not self.api_key:
                return self._get_dummy_greeting(business_data)
                
            business_name = business_data.get("business_name", "our business")
            
            # Create prompt for greeting
            prompt = f"""
            You are an AI phone assistant for {business_name}. Generate a friendly and professional 
            greeting for someone who has just called. The greeting should:
            1. Welcome the caller
            2. Identify as an AI assistant for {business_name}
            3. Offer to help
            
            Keep it concise (1-2 sentences) and natural sounding.
            """
            
            response = await self._call_ai_api(prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating greeting: {str(e)}")
            return self._get_dummy_greeting(business_data)
    
    def _get_dummy_greeting(self, business_data):
        """Get a dummy greeting for development"""
        business_name = business_data.get("business_name", "our business")
        greetings = [
            f"Hello! Thank you for calling {business_name}. I'm Sloane, the AI assistant. How can I help you today?",
            f"Hi there! This is Sloane, the virtual assistant for {business_name}. What can I do for you?",
            f"Welcome to {business_name}. I'm Sloane, an AI assistant ready to help. How may I assist you?"
        ]
        return random.choice(greetings)
    
    async def generate_response(self, business_data, user_message, conversation_history):
        """
        Generate a response to a user message
        
        Args:
            business_data: Business training data
            user_message: The user's message
            conversation_history: List of previous messages
            
        Returns:
            str: AI response
        """
        try:
            if not self.api_key:
                return self._get_dummy_response(business_data, user_message)
                
            business_name = business_data.get("business_name", "our business")
            
            # Extract relevant business info
            business_info = ""
            if business_data.get("services"):
                business_info += f"Services: {', '.join(business_data['services'])}\n"
                
            if business_data.get("hours"):
                business_info += f"Hours: {json.dumps(business_data['hours'])}\n"
                
            if business_data.get("contact_info"):
                contact = business_data["contact_info"]
                if contact.get("phone"):
                    business_info += f"Phone: {contact['phone'][0] if isinstance(contact['phone'], list) else contact['phone']}\n"
                if contact.get("email"):
                    business_info += f"Email: {contact['email'][0] if isinstance(contact['email'], list) else contact['email']}\n"
                if contact.get("address"):
                    business_info += f"Address: {contact['address']}\n"
            
            # Extract example Q&A for zero-shot learning
            qa_examples = ""
            if business_data.get("example_qa"):
                for i, qa in enumerate(business_data["example_qa"][:10]):  # Limit to 10 examples
                    qa_examples += f"Q: {qa.get('question', '')}\nA: {qa.get('answer', '')}\n\n"
            
            # Format conversation history
            formatted_history = ""
            for i, msg in enumerate(conversation_history[-10:]):  # Limit to last 10 messages
                speaker = "Customer" if msg.get("speaker") == "user" else "Assistant"
                formatted_history += f"{speaker}: {msg.get('text', '')}\n"
            
            # Build the prompt
            prompt = f"""
            You are Sloane, an AI phone assistant for {business_name}. You are speaking with a customer on the phone.
            
            Business Information:
            {business_info}
            
            If you don't know the answer to a question, say that you'll need to check with the team and someone will get back to them.
            
            Here are some example Q&A pairs for this business:
            {qa_examples}
            
            Recent conversation:
            {formatted_history}
            
            Customer: {user_message}
            
            Assistant:
            """
            
            response = await self._call_ai_api(prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._get_dummy_response(business_data, user_message)
    
    def _get_dummy_response(self, business_data, user_message):
        """Get a dummy response for development"""
        business_name = business_data.get("business_name", "our business")
        
        # Check for common intents in the message
        user_message_lower = user_message.lower()
        
        # Hours request
        if "hour" in user_message_lower or "open" in user_message_lower or "when" in user_message_lower:
            return f"Our normal business hours are Monday to Friday from 9 AM to 5 PM, and Saturday from 10 AM to 3 PM. We're closed on Sundays."
        
        # Location request
        if "where" in user_message_lower or "location" in user_message_lower or "address" in user_message_lower:
            return f"We're located at 123 Business Street, Suite 101, in downtown. Would you like directions?"
        
        # Appointment request
        if "appointment" in user_message_lower or "schedule" in user_message_lower or "book" in user_message_lower:
            return f"I'd be happy to help you schedule an appointment. What day and time works best for you?"
        
        # Generic responses
        generic_responses = [
            f"Thank you for your question. At {business_name}, we strive to provide excellent service. Can you provide more details so I can better assist you?",
            "I understand what you're asking. Let me help you with that. Could you tell me a bit more about your specific needs?",
            "That's a great question. I'd be happy to help with that. Could you give me some more information?"
        ]
        return random.choice(generic_responses)
    
    async def detect_intents(self, user_message, business_data):
        """
        Detect intents in user message
        
        Args:
            user_message: User's message
            business_data: Business training data
            
        Returns:
            list: Detected intents with confidence scores
        """
        try:
            if not self.api_key:
                return self._get_dummy_intents(user_message)
                
            services = business_data.get("services", [])
            
            # Create prompt for intent detection
            prompt = f"""
            Analyze the following customer message and detect the primary intent.
            Choose from these possible intents:
            - greeting: Customer is greeting or starting conversation
            - information: Customer is asking for general information
            - hours: Customer is asking about business hours
            - location: Customer is asking about business location
            - services: Customer is asking about services offered
            - pricing: Customer is asking about pricing
            - schedule_appointment: Customer wants to schedule an appointment
            - reschedule_appointment: Customer wants to reschedule an appointment
            - cancel_appointment: Customer wants to cancel an appointment
            - speak_to_human: Customer wants to speak to a human
            - complaint: Customer has a complaint
            - emergency: Customer has an emergency situation
            - other: Any other intent not listed above
            
            Available services: {', '.join(services)}
            
            Customer message: "{user_message}"
            
            Respond in the following JSON format:
            {{
                "intents": [
                    {{
                        "name": "intent_name",
                        "confidence": 0.XX,
                        "entities": ["entity1", "entity2"]
                    }}
                ]
            }}
            
            Include up to 2 most likely intents with confidence scores between 0 and 1.
            """
            
            response = await self._call_ai_api(prompt)
            
            try:
                # Extract JSON from response
                json_str = response.strip()
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0].strip()
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].strip()
                    
                intent_data = json.loads(json_str)
                return intent_data.get("intents", [])
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse intent JSON: {response}")
                return self._get_dummy_intents(user_message)
                
        except Exception as e:
            logger.error(f"Error detecting intents: {str(e)}")
            return self._get_dummy_intents(user_message)
    
    def _get_dummy_intents(self, user_message):
        """Get dummy intents for development"""
        user_message_lower = user_message.lower()
        
        if "appointment" in user_message_lower or "schedule" in user_message_lower or "book" in user_message_lower:
            return [
                {"name": "schedule_appointment", "confidence": 0.9, "entities": ["appointment"]}
            ]
            
        if "hour" in user_message_lower or "open" in user_message_lower:
            return [
                {"name": "hours", "confidence": 0.8, "entities": ["hours"]}
            ]
            
        if "where" in user_message_lower or "location" in user_message_lower or "address" in user_message_lower:
            return [
                {"name": "location", "confidence": 0.85, "entities": ["location"]}
            ]
            
        if "hi" in user_message_lower or "hello" in user_message_lower or "hey" in user_message_lower:
            return [
                {"name": "greeting", "confidence": 0.95, "entities": []}
            ]
            
        return [
            {"name": "information", "confidence": 0.6, "entities": []}
        ]
    
    async def extract_entities(self, user_message):
        """
        Extract entities from user message
        
        Args:
            user_message: User's message
            
        Returns:
            dict: Extracted entities by type
        """
        try:
            if not self.api_key:
                return self._get_dummy_entities(user_message)
                
            # Create prompt for entity extraction
            prompt = f"""
            Extract entities from the following customer message. Look for these entity types:
            - datetime: Any date or time mentioned
            - duration: Any duration mentioned
            - service: Any service mentioned
            - name: Any person name mentioned
            - phone: Any phone number
            - email: Any email address
            - location: Any location mentioned
            
            Customer message: "{user_message}"
            
            Respond in the following JSON format:
            {{
                "entities": {{
                    "datetime": ["2023-05-15 14:00", "tomorrow at 3pm"],
                    "duration": ["1 hour", "30 minutes"],
                    "service": ["haircut", "color treatment"],
                    "name": ["John Smith"],
                    "phone": ["555-123-4567"],
                    "email": ["john@example.com"],
                    "location": ["downtown office"]
                }}
            }}
            
            Only include entity types that are found in the message. If none are found for a type, omit that type.
            """
            
            response = await self._call_ai_api(prompt)
            
            try:
                # Extract JSON from response
                json_str = response.strip()
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0].strip()
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].strip()
                    
                entity_data = json.loads(json_str)
                return entity_data.get("entities", {})
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse entity JSON: {response}")
                return self._get_dummy_entities(user_message)
                
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return self._get_dummy_entities(user_message)
    
    def _get_dummy_entities(self, user_message):
        """Get dummy entities for development"""
        user_message_lower = user_message.lower()
        entities = {}
        
        # Simple regex-like checks
        import re
        
        # Time patterns
        time_patterns = [
            r'\b\d{1,2}(?::\d{2})?\s*(?:am|pm)\b',
            r'\b(?:tomorrow|today|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b'
        ]
        
        time_entities = []
        for pattern in time_patterns:
            matches = re.findall(pattern, user_message_lower)
            time_entities.extend(matches)
            
        if time_entities:
            entities["datetime"] = time_entities
            
        # Duration patterns
        duration_patterns = [
            r'\b\d+\s*(?:hour|minute|min|hr)s?\b'
        ]
        
        duration_entities = []
        for pattern in duration_patterns:
            matches = re.findall(pattern, user_message_lower)
            duration_entities.extend(matches)
            
        if duration_entities:
            entities["duration"] = duration_entities
            
        # Name pattern (simplistic)
        name_pattern = r'\bmy name is (\w+)\b'
        name_match = re.search(name_pattern, user_message_lower)
        if name_match:
            entities["name"] = [name_match.group(1)]
            
        return entities
    
    async def generate_summary(self, transcript):
        """
        Generate a summary of the call transcript
        
        Args:
            transcript: Full call transcript
            
        Returns:
            str: Call summary
        """
        try:
            if not self.api_key:
                return self._get_dummy_summary(transcript)
                
            # Create prompt for summary
            prompt = f"""
            Summarize the following phone call transcript between a customer and an AI assistant.
            Focus on:
            1. The customer's main reason for calling
            2. Key information exchanged
            3. Any decisions or next steps agreed upon
            4. Any unresolved issues
            
            Keep the summary concise (3-5 sentences).
            
            Transcript:
            {transcript}
            
            Summary:
            """
            
            response = await self._call_ai_api(prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return self._get_dummy_summary(transcript)
    
    def _get_dummy_summary(self, transcript):
        """Get dummy summary for development"""
        # Count the length of transcript for simple summary
        lines = transcript.split('\n')
        word_count = len(transcript.split())
        
        if word_count < 50:
            return "Brief call with customer asking initial questions. No specific requests were made."
        elif "appointment" in transcript.lower():
            return "Customer called to schedule an appointment. Details were collected and the appointment was confirmed."
        elif "price" in transcript.lower() or "cost" in transcript.lower():
            return "Customer inquired about pricing information. Pricing details were provided for the requested services."
        else:
            return "Customer called seeking information about services. Basic details were provided and the customer was encouraged to follow up for more specific information."
    
    async def analyze_for_actions(self, transcript, summary):
        """
        Analyze call for required actions
        
        Args:
            transcript: Call transcript
            summary: Call summary
            
        Returns:
            tuple: (action_required bool, action_items list)
        """
        try:
            if not self.api_key:
                return self._get_dummy_actions(transcript, summary)
                
            # Create prompt for action analysis
            prompt = f"""
            Analyze this phone call transcript and determine if any follow-up actions are required by the business staff.
            
            Transcript:
            {transcript}
            
            Summary:
            {summary}
            
            Respond in the following JSON format:
            {{
                "action_required": true/false,
                "action_items": [
                    {{
                        "action": "Brief description of action needed",
                        "priority": "high/medium/low",
                        "context": "Relevant context from the call"
                    }}
                ]
            }}
            
            Only include action_items if action_required is true.
            """
            
            response = await self._call_ai_api(prompt)
            
            try:
                # Extract JSON from response
                json_str = response.strip()
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0].strip()
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].strip()
                    
                action_data = json.loads(json_str)
                action_required = action_data.get("action_required", False)
                action_items = action_data.get("action_items", []) if action_required else []
                
                return action_required, action_items
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse action JSON: {response}")
                return self._get_dummy_actions(transcript, summary)
                
        except Exception as e:
            logger.error(f"Error analyzing for actions: {str(e)}")
            return self._get_dummy_actions(transcript, summary)
    
    def _get_dummy_actions(self, transcript, summary):
        """Get dummy actions for development"""
        # Look for indicators of needed follow-up
        transcript_lower = transcript.lower()
        
        action_required = False
        action_items = []
        
        # Check for common action triggers
        if "call me back" in transcript_lower or "get back to me" in transcript_lower:
            action_required = True
            action_items.append({
                "action": "Call customer back",
                "priority": "high",
                "context": "Customer explicitly requested a callback"
            })
            
        if "speak to a person" in transcript_lower or "speak to someone" in transcript_lower or "talk to a human" in transcript_lower:
            action_required = True
            action_items.append({
                "action": "Have a staff member call customer",
                "priority": "medium",
                "context": "Customer requested to speak with a human staff member"
            })
            
        if "complaint" in transcript_lower or "not satisfied" in transcript_lower or "unhappy" in transcript_lower:
            action_required = True
            action_items.append({
                "action": "Address customer complaint",
                "priority": "high",
                "context": "Customer expressed dissatisfaction"
            })
            
        if "price" in transcript_lower and "quote" in transcript_lower:
            action_required = True
            action_items.append({
                "action": "Provide price quote",
                "priority": "medium",
                "context": "Customer requested pricing information"
            })
            
        return action_required, action_items
    
    async def _call_ai_api(self, prompt):
        """
        Call the appropriate AI API based on the provider
        
        Args:
            prompt: The prompt to send
            
        Returns:
            str: API response text
        """
        if self.provider == "openai":
            return await self._call_openai_api(prompt)
        elif self.provider == "anthropic":
            return await self._call_anthropic_api(prompt)
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
    
    async def _call_openai_api(self, prompt):
        """Call OpenAI API"""
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "system", "content": "You are a helpful AI assistant."}, {"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    
    async def _call_anthropic_api(self, prompt):
        """Call Anthropic API"""
        url = "https://api.anthropic.com/v1/messages"
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        response_data = response.json()
        return response_data["content"][0]["text"]
