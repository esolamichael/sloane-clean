"""
Twilio integration for call transfer functionality.
"""
import os
import logging
from typing import Dict, Any, Optional
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Dial

logger = logging.getLogger(__name__)

class TwilioTransferHandler:
    """
    Handler for Twilio call transfers.
    """
    
    def __init__(self):
        """Initialize the Twilio transfer handler."""
        # In a production environment, these would be loaded from environment variables
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            logger.warning("Twilio credentials not provided. Some functionality will be limited.")
    
    def generate_transfer_twiml(self, transfer_number: str, message: str = None) -> str:
        """
        Generate TwiML for transferring a call.
        
        Args:
            transfer_number (str): The phone number to transfer to.
            message (str, optional): A message to say before transferring.
            
        Returns:
            str: The TwiML response as a string.
        """
        response = VoiceResponse()
        
        if message:
            response.say(message)
            
            # Add a brief pause after the message
            response.pause(length=1)
        
        # Dial the transfer number
        dial = Dial(
            caller_id=os.getenv("TWILIO_PHONE_NUMBER", ""),
            timeout=30,
            record="record-from-answer",
            action="/api/call/transfer-complete"
        )
        dial.number(transfer_number)
        
        response.append(dial)
        
        # If the dial fails (e.g., no answer), provide a message and take a voicemail
        response.say("I'm sorry, but we couldn't reach a representative. Please leave a message after the tone.")
        response.record(
            max_length=300,
            play_beep=True,
            timeout=5,
            transcribe=True,
            transcribe_callback="/api/call/voicemail-transcription"
        )
        
        return str(response)
    
    def transfer_in_progress_twiml(self) -> str:
        """
        Generate TwiML for when a transfer is in progress.
        
        Returns:
            str: The TwiML response as a string.
        """
        response = VoiceResponse()
        response.say("Please hold while we connect you to a representative.")
        response.play("https://api.twilio.com/cowbell.mp3")  # Hold music
        return str(response)
    
    def transfer_complete_twiml(self, status: str) -> str:
        """
        Generate TwiML for when a transfer is complete.
        
        Args:
            status (str): The status of the transfer (e.g., "completed", "no-answer").
            
        Returns:
            str: The TwiML response as a string.
        """
        response = VoiceResponse()
        
        if status == "completed":
            response.say("Thank you for calling. Goodbye.")
            response.hangup()
        else:
            response.say("I'm sorry, but we couldn't reach a representative. Please try calling back later.")
            response.hangup()
        
        return str(response)
    
    def transfer_call(self, call_sid: str, transfer_number: str) -> bool:
        """
        Transfer an active call using Twilio's API.
        
        Args:
            call_sid (str): The Twilio call SID.
            transfer_number (str): The phone number to transfer to.
            
        Returns:
            bool: True if the transfer was successful, False otherwise.
        """
        if not self.client:
            logger.error("Twilio client not initialized. Cannot transfer call.")
            return False
        
        try:
            # Update the call with a new TwiML URL that will handle the transfer
            self.client.calls(call_sid).update(
                twiml=self.generate_transfer_twiml(transfer_number)
            )
            
            logger.info(f"Call {call_sid} transferred to {transfer_number}")
            return True
        except Exception as e:
            logger.error(f"Failed to transfer call: {str(e)}")
            return False
    
    def get_call_status(self, call_sid: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a call.
        
        Args:
            call_sid (str): The Twilio call SID.
            
        Returns:
            Optional[Dict[str, Any]]: The call status if successful, None otherwise.
        """
        if not self.client:
            logger.error("Twilio client not initialized. Cannot get call status.")
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
            logger.error(f"Failed to get call status: {str(e)}")
            return None
