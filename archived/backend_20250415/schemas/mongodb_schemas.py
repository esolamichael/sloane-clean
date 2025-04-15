# backend/schemas/mongodb_schemas.py
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

class ScrapedWebsiteData(BaseModel):
    """Schema for scraped website data stored in MongoDB."""
    business_id: str
    url: str
    content: Dict[str, Any]  # Flexible structure for different webpage contents
    last_scraped: datetime = Field(default_factory=datetime.utcnow)
    sections: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None

class GoogleBusinessProfileData(BaseModel):
    """Schema for Google Business Profile data stored in MongoDB."""
    business_id: str
    google_place_id: Optional[str] = None
    business_name: str
    description: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    phone_number: Optional[str] = None
    categories: Optional[List[str]] = None
    services: Optional[List[Dict[str, Any]]] = None
    hours: Optional[Dict[str, List[str]]] = None
    photos_urls: Optional[List[str]] = None
    reviews: Optional[List[Dict[str, Any]]] = None
    attributes: Optional[Dict[str, Any]] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class CallTranscript(BaseModel):
    """Schema for call transcripts stored in MongoDB."""
    business_id: str
    call_id: str
    caller_phone: Optional[str] = None
    caller_name: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    full_transcript: str
    transcript_segments: List[Dict[str, Any]]  # Each segment with speaker, text, timestamp
    detected_intents: Optional[List[str]] = None
    entities: Optional[Dict[str, Any]] = None
    sentiment_score: Optional[float] = None
    action_items: Optional[List[str]] = None
    recording_url: Optional[str] = None

class AITrainingData(BaseModel):
    """Schema for AI training data stored in MongoDB."""
    business_id: str
    training_type: str  # e.g., "faq", "services", "call_handling"
    examples: List[Dict[str, Any]]  # Flexible structure for different training examples
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    source: Optional[str] = None  # Where this training data came from
    metadata: Optional[Dict[str, Any]] = None

class UserSession(BaseModel):
    """Schema for user session data stored in MongoDB."""
    user_id: str
    session_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None
