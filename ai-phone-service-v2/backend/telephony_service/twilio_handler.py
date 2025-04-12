"""
Twilio integration for handling phone calls.
"""
import os
import logging
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from . import config
from .conversation_manager import ConversationManager

logger = logging.getLogger(__name__)

class TwilioHandler:
    """
    Handles Twilio integration for phone calls.
    """
    
    def __init__(self):
        """Initialize the Twilio client."""
        # In a production environment, these would be loaded from environment variables
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.twilio_number = os.getenv("TWILIO_PHONE_NUMBER", "")
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            logger.warning("Twilio credentials not provided. Some functionality will be limited.")
    
    def generate_welcome_twiml(self, business_id):
        """
        Generate TwiML for the initial welcome message.
        
        Args:
            business_id (str): The ID of the business.
            
        Returns:
            str: The TwiML response as a string.
        """
        conversation_manager = ConversationManager(business_id)
        greeting_response = conversation_manager.start_conversation()
        
        response = VoiceResponse()
        
        # Add a brief pause to ensure the call is connected
        response.pause(length=1)
        
        # Add the greeting message
        response.say(greeting_response["text"])
        
        # Gather the caller's input
        gather = Gather(
            input='speech',
            action=f'/api/call/respond?business_id={business_id}',
            method='POST',
            speech_timeout='auto',
            language='en-US'
        )
        
        # Add the gather to the response
        response.append(gather)
        
        # If the caller doesn't say anything, retry
        response.redirect(f'/api/call/welcome?business_id={business_id}')
        
        return str(response)
    
    def generate_response_twiml(self, business_id, speech_result):
        """
        Generate TwiML for responding to the caller's input.
        
        Args:
            business_id (str): The ID of the business.
            speech_result (str): The speech recognition result.
            
        Returns:
            str: The TwiML response as a string.
        """
        conversation_manager = ConversationManager(business_id)
        ai_response = conversation_manager.process_user_input(text=speech_result)
        
        response = VoiceResponse()
        
        # Check if there's a special action to take
        if "action" in ai_response:
            action = ai_response["action"]
            
            if action["type"] == "transfer":
                # Transfer the call
                response.say(ai_response["text"])
                response.dial(action["number"])
                return str(response)
            
            elif action["type"] == "end_call":
                # End the call
                response.say(ai_response["text"])
                response.hangup()
                return str(response)
        
        # Standard response
        response.say(ai_response["text"])
        
        # Gather the caller's next input
        gather = Gather(
            input='speech',
            action=f'/api/call/respond?business_id={business_id}',
            method='POST',
            speech_timeout='auto',
            language='en-US'
        )
        
        # Add the gather to the response
        response.append(gather)
        
        # If the caller doesn't say anything, retry
        response.redirect(f'/api/call/respond?business_id={business_id}&retry=true')
        
        return str(response)
    
    def make_outbound_call(self, to_number, from_number=None, url=None):
        """
        Make an outbound call using Twilio.
        
        Args:
            to_number (str): The number to call.
            from_number (str, optional): The number to call from. Defaults to the Twilio number.
            url (str, optional): The URL for Twilio to request when the call connects.
            
        Returns:
            dict: The call details if successful, None otherwise.
        """
        if not self.client:
            logger.error("Twilio client not initialized. Cannot make outbound call.")
            return None
        
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=from_number or self.twilio_number,
                url=url or f"{config.API_HOST}/api/call/outbound"
            )
            
            return {
                "call_sid": call.sid,
                "status": call.status
            }
        except Exception as e:
            logger.error(f"Failed to make outbound call: {str(e)}")
            return None
    
    def get_call_details(self, call_sid):
        """
        Get details about a call from Twilio.
        
        Args:
            call_sid (str): The Twilio call SID.
            
        Returns:
            dict: The call details if successful, None otherwise.
        """
        if not self.client:
            logger.error("Twilio client not initialized. Cannot get call details.")
            return None
        
        try:
            call = self.client.calls(call_sid).fetch()
            
            return {
                "call_sid": call.sid,
                "status": call.status,
                "direction": call.direction,
                "from_number": call.from_,
                "to_number": call.to,
                "duration": call.duration,
                "start_time": call.start_time,
                "end_time": call.end_time
            }
        except Exception as e:
            logger.error(f"Failed to get call details: {str(e)}")
            return None
    
    def record_call(self, call_sid, recording_status_callback=None):
        """
        Start recording a call.
        
        Args:
            call_sid (str): The Twilio call SID.
            recording_status_callback (str, optional): URL to receive recording status callbacks.
            
        Returns:
            dict: The recording details if successful, None otherwise.
        """
        if not self.client:
            logger.error("Twilio client not initialized. Cannot record call.")
            return None
        
        try:
            recording = self.client.calls(call_sid).recordings.create(
                recording_status_callback=recording_status_callback
            )
            
            return {
                "recording_sid": recording.sid,
                "status": recording.status
            }
        except Exception as e:
            logger.error(f"Failed to start recording: {str(e)}")
            return None
