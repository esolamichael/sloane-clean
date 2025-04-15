"""
FastAPI application for the AI Conversation Service.
"""
import logging
from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import json
import base64
from datetime import datetime

from .conversation_manager import ConversationManager
from .speech_processor import SpeechProcessor
from . import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Conversation Service",
    description="API for handling AI-powered phone conversations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize speech processor
speech_processor = SpeechProcessor()

# Models for API requests and responses
class ConversationRequest(BaseModel):
    business_id: str
    audio_content: Optional[str] = None  # Base64 encoded audio
    text: Optional[str] = None
    session_id: Optional[str] = None

class ConversationResponse(BaseModel):
    text: str
    audio_content: Optional[str] = None  # Base64 encoded audio
    action: Optional[Dict[str, Any]] = None
    session_id: str

class BusinessProfileRequest(BaseModel):
    business_id: str
    name: str
    greeting: Optional[str] = None
    business_hours: Optional[Dict[str, str]] = None
    services: Optional[List[str]] = None
    faqs: Optional[List[Dict[str, str]]] = None
    appointment_scheduling: Optional[Dict[str, Any]] = None
    transfer_settings: Optional[Dict[str, Any]] = None
    notification_settings: Optional[Dict[str, Any]] = None

# Conversation sessions storage (in-memory for demonstration)
# In production, this would be stored in a database
conversation_sessions = {}

def get_conversation_manager(business_id: str, session_id: Optional[str] = None):
    """
    Get or create a conversation manager for the given business and session.
    
    Args:
        business_id (str): The business ID.
        session_id (str, optional): The session ID.
        
    Returns:
        tuple: (ConversationManager, session_id)
    """
    if session_id and session_id in conversation_sessions:
        return conversation_sessions[session_id], session_id
    
    # Create a new conversation manager
    conversation_manager = ConversationManager(business_id)
    
    # Generate a new session ID if not provided
    if not session_id:
        session_id = f"{business_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Store the conversation manager
    conversation_sessions[session_id] = conversation_manager
    
    return conversation_manager, session_id

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "AI Conversation Service"}

@app.post("/api/conversation/start", response_model=ConversationResponse)
async def start_conversation(request: ConversationRequest):
    """
    Start a new conversation.
    
    Args:
        request (ConversationRequest): The request containing business ID.
        
    Returns:
        ConversationResponse: The response with greeting.
    """
    try:
        conversation_manager, session_id = get_conversation_manager(
            request.business_id, request.session_id
        )
        
        response = conversation_manager.start_conversation()
        
        # Convert audio to base64 for API response
        audio_base64 = None
        if "audio" in response:
            audio_base64 = base64.b64encode(response["audio"]).decode("utf-8")
        
        return ConversationResponse(
            text=response["text"],
            audio_content=audio_base64,
            action=response.get("action"),
            session_id=session_id
        )
    except Exception as e:
        logger.error(f"Error starting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversation/respond", response_model=ConversationResponse)
async def respond_to_conversation(request: ConversationRequest):
    """
    Respond to user input in a conversation.
    
    Args:
        request (ConversationRequest): The request containing user input.
        
    Returns:
        ConversationResponse: The AI response.
    """
    try:
        if not request.session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        conversation_manager, session_id = get_conversation_manager(
            request.business_id, request.session_id
        )
        
        # Process audio content if provided
        audio_content = None
        if request.audio_content:
            audio_content = base64.b64decode(request.audio_content)
        
        response = conversation_manager.process_user_input(
            audio_content=audio_content,
            text=request.text
        )
        
        # Convert audio to base64 for API response
        audio_base64 = None
        if "audio" in response:
            audio_base64 = base64.b64encode(response["audio"]).decode("utf-8")
        
        return ConversationResponse(
            text=response["text"],
            audio_content=audio_base64,
            action=response.get("action"),
            session_id=session_id
        )
    except Exception as e:
        logger.error(f"Error responding to conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/business/profile")
async def update_business_profile(profile: BusinessProfileRequest):
    """
    Update or create a business profile.
    
    Args:
        profile (BusinessProfileRequest): The business profile data.
        
    Returns:
        dict: Success message.
    """
    try:
        # In a real implementation, this would store the profile in a database
        # For demonstration, we'll just log the profile
        logger.info(f"Updating business profile: {profile.business_id}")
        
        # Create a conversation manager to test loading the profile
        conversation_manager = ConversationManager(profile.business_id)
        
        # Mock successful profile update
        return {"status": "success", "message": "Business profile updated successfully"}
    except Exception as e:
        logger.error(f"Error updating business profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversation/end")
async def end_conversation(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    End a conversation and clean up resources.
    
    Args:
        request (Request): The request containing session ID.
        background_tasks (BackgroundTasks): FastAPI background tasks.
        
    Returns:
        dict: Success message.
    """
    try:
        data = await request.json()
        session_id = data.get("session_id")
        
        if not session_id or session_id not in conversation_sessions:
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        # Get the conversation manager
        conversation_manager = conversation_sessions[session_id]
        
        # Send notification in the background
        call_data = {
            "call_id": session_id,
            "caller_number": data.get("caller_number", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "duration": data.get("duration", 0)
        }
        background_tasks.add_task(conversation_manager.send_notification, call_data)
        
        # Clean up the session
        del conversation_sessions[session_id]
        
        return {"status": "success", "message": "Conversation ended successfully"}
    except Exception as e:
        logger.error(f"Error ending conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def start_server():
    """Start the FastAPI server."""
    uvicorn.run(
        "ai_conversation_service.api:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.API_DEBUG
    )

if __name__ == "__main__":
    start_server()
