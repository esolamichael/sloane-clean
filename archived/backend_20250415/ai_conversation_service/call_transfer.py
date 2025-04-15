"""
Call transfer functionality for the AI Conversation Service.
"""
import os
import logging
import json
from typing import List, Dict, Any, Optional
from .conversation_manager import ConversationManager

logger = logging.getLogger(__name__)

class CallTransferService:
    """
    Service for handling call transfers to live agents.
    """
    
    def __init__(self):
        """Initialize the call transfer service."""
        pass
    
    def should_transfer_call(
        self,
        conversation_history: List[Dict[str, str]],
        business_profile: Dict[str, Any],
        nlu_result: Dict[str, Any]
    ) -> bool:
        """
        Determine if a call should be transferred to a live agent.
        
        Args:
            conversation_history (List[Dict[str, str]]): The conversation history.
            business_profile (Dict[str, Any]): The business profile.
            nlu_result (Dict[str, Any]): The NLU processing result.
            
        Returns:
            bool: True if the call should be transferred, False otherwise.
        """
        # Check if transfer settings are configured
        if not business_profile or "transferSettings" not in business_profile:
            return False
        
        transfer_settings = business_profile["transferSettings"]
        
        # Check for high-value keywords
        high_value_keywords = transfer_settings.get("highValueKeywords", [])
        text = nlu_result["text"].lower()
        
        # Check if any high-value keywords are in the text
        for keyword in high_value_keywords:
            if keyword.lower() in text:
                logger.info(f"High-value keyword detected: {keyword}")
                return True
        
        # Check for urgent intent with high confidence
        if nlu_result["intent"]["intent"] == "urgent_request" and nlu_result["intent"]["confidence"] > 0.6:
            logger.info("Urgent request detected with high confidence")
            return True
        
        # Check for complaint intent with high confidence
        if nlu_result["intent"]["intent"] == "complaint" and nlu_result["intent"]["confidence"] > 0.7:
            logger.info("Complaint detected with high confidence")
            return True
        
        # Check for high-value entities (e.g., large monetary amounts)
        for entity in nlu_result["entities"]:
            if entity["type"] == "MONEY":
                # Try to extract the amount
                try:
                    # Remove currency symbols and commas
                    amount_str = entity["text"].replace("$", "").replace(",", "")
                    
                    # Check if there's a word "dollars" after the amount
                    if "dollars" in amount_str:
                        amount_str = amount_str.split("dollars")[0].strip()
                    
                    amount = float(amount_str)
                    
                    # If the amount is large (e.g., over $1000), consider it high-value
                    if amount > 1000:
                        logger.info(f"High-value monetary amount detected: ${amount}")
                        return True
                except (ValueError, TypeError):
                    pass
        
        # Check for multiple questions or complex requests
        question_count = 0
        for message in conversation_history:
            if message["role"] == "user" and "?" in message["text"]:
                question_count += 1
        
        if question_count >= 3:
            logger.info(f"Multiple questions detected: {question_count}")
            return True
        
        # Check for repeated clarification requests from the AI
        clarification_count = 0
        for message in conversation_history:
            if message["role"] == "assistant" and any(phrase in message["text"].lower() for phrase in [
                "could you clarify", "i'm not sure i understood", "could you please explain",
                "i didn't quite catch", "could you be more specific"
            ]):
                clarification_count += 1
        
        if clarification_count >= 2:
            logger.info(f"Multiple clarification requests detected: {clarification_count}")
            return True
        
        return False
    
    def get_transfer_number(self, business_profile: Dict[str, Any]) -> Optional[str]:
        """
        Get the phone number to transfer the call to.
        
        Args:
            business_profile (Dict[str, Any]): The business profile.
            
        Returns:
            Optional[str]: The phone number to transfer to, or None if not configured.
        """
        if not business_profile or "transferSettings" not in business_profile:
            return None
        
        transfer_settings = business_profile["transferSettings"]
        return transfer_settings.get("transferNumber")
    
    def generate_transfer_message(self, business_profile: Dict[str, Any]) -> str:
        """
        Generate a message to inform the caller about the transfer.
        
        Args:
            business_profile (Dict[str, Any]): The business profile.
            
        Returns:
            str: The transfer message.
        """
        business_name = business_profile.get("name", "our business")
        
        return (
            f"I'll transfer you to a representative at {business_name} who can help you with this. "
            "Please hold while I connect you."
        )
    
    def log_transfer(
        self,
        business_id: str,
        call_id: str,
        caller_number: str,
        transfer_number: str,
        reason: str,
        conversation_history: List[Dict[str, str]]
    ) -> bool:
        """
        Log a call transfer for analytics and reporting.
        
        Args:
            business_id (str): The ID of the business.
            call_id (str): The ID of the call.
            caller_number (str): The caller's phone number.
            transfer_number (str): The number the call was transferred to.
            reason (str): The reason for the transfer.
            conversation_history (List[Dict[str, str]]): The conversation history.
            
        Returns:
            bool: True if the log was successful, False otherwise.
        """
        try:
            # In a real implementation, this would store the log in a database
            # For demonstration, we'll just log it
            transfer_log = {
                "business_id": business_id,
                "call_id": call_id,
                "caller_number": caller_number,
                "transfer_number": transfer_number,
                "reason": reason,
                "conversation_history": conversation_history,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            logger.info(f"Call transfer logged: {json.dumps(transfer_log)}")
            return True
        except Exception as e:
            logger.error(f"Failed to log call transfer: {str(e)}")
            return False
