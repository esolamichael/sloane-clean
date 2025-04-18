"""
Integration of call transfer functionality with the conversation manager.
"""
import logging
from typing import Dict, Any, Optional
from .call_transfer import CallTransferService
from .conversation_manager import ConversationManager

logger = logging.getLogger(__name__)

def integrate_call_transfer(conversation_manager: ConversationManager):
    """
    Integrate call transfer functionality with the conversation manager.
    
    This function monkey patches the ConversationManager class to add call transfer functionality.
    
    Args:
        conversation_manager (ConversationManager): The conversation manager instance.
    """
    # Store the original generate_response method
    original_generate_response = conversation_manager.generate_response
    
    # Create a call transfer service
    call_transfer_service = CallTransferService()
    
    # Define the new generate_response method with call transfer functionality
    def generate_response_with_transfer(nlu_result):
        """
        Generate a response based on the NLU result, with call transfer functionality.
        
        Args:
            nlu_result (dict): The NLU processing result.
            
        Returns:
            dict: The response with text and audio.
        """
        # Check if this is a high-value call that should be transferred
        if call_transfer_service.should_transfer_call(
            conversation_history=conversation_manager.conversation_history,
            business_profile=conversation_manager.business_profile,
            nlu_result=nlu_result
        ):
            return handle_call_transfer()
        
        # If not, use the original method
        return original_generate_response(nlu_result)
    
    # Define the handle_call_transfer method
    def handle_call_transfer():
        """
        Handle transferring the call to a live person.
        
        Returns:
            dict: The response with text and audio.
        """
        if not conversation_manager.business_profile or "transferSettings" not in conversation_manager.business_profile:
            return conversation_manager.handle_fallback()
        
        transfer_number = call_transfer_service.get_transfer_number(conversation_manager.business_profile)
        if not transfer_number:
            return conversation_manager.handle_fallback()
        
        response_text = call_transfer_service.generate_transfer_message(conversation_manager.business_profile)
        
        # Add the transfer message to the conversation history
        conversation_manager.conversation_history.append({
            "role": "assistant",
            "text": response_text
        })
        
        return {
            "text": response_text,
            "audio": conversation_manager.speech_processor.text_to_speech(response_text),
            "action": {
                "type": "transfer",
                "number": transfer_number
            }
        }
    
    # Replace the original method with the new one
    conversation_manager.generate_response = generate_response_with_transfer
    
    # Add the handle_call_transfer method to the conversation manager
    conversation_manager.handle_call_transfer = handle_call_transfer
    
    return conversation_manager
