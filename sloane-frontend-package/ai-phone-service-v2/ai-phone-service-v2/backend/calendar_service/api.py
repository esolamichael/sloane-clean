"""
Calendar service API for appointment scheduling integration.
"""
import os
import logging
import datetime
import json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .google_calendar import GoogleCalendarService
from .outlook_calendar import OutlookCalendarService
from .apple_calendar import AppleCalendarService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Calendar Service API",
    description="API for appointment scheduling integration",
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

# Models for API requests and responses
class CalendarRequest(BaseModel):
    business_id: str
    calendar_type: str
    calendar_id: Optional[str] = None

class AvailabilityRequest(BaseModel):
    business_id: str
    calendar_type: str
    calendar_id: str
    start_date: str  # ISO format
    end_date: str  # ISO format
    duration_minutes: int = 60
    business_hours: Optional[Dict[str, str]] = None

class AppointmentRequest(BaseModel):
    business_id: str
    calendar_type: str
    calendar_id: str
    summary: str
    start_time: str  # ISO format
    end_time: str  # ISO format
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[List[Dict[str, str]]] = None

class CalendarResponse(BaseModel):
    calendars: List[Dict[str, Any]]

class AvailabilityResponse(BaseModel):
    slots: List[Dict[str, Any]]

class AppointmentResponse(BaseModel):
    appointment: Optional[Dict[str, Any]] = None
    success: bool
    message: str

# Calendar service factory
def get_calendar_service(calendar_type: str):
    """
    Get the appropriate calendar service based on the type.
    
    Args:
        calendar_type (str): The type of calendar service.
        
    Returns:
        The calendar service instance.
    """
    if calendar_type.lower() == 'google':
        return GoogleCalendarService()
    elif calendar_type.lower() == 'outlook':
        return OutlookCalendarService()
    elif calendar_type.lower() == 'apple':
        return AppleCalendarService()
    else:
        raise ValueError(f"Unsupported calendar type: {calendar_type}")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Calendar Service"}

@app.post("/api/calendars", response_model=CalendarResponse)
async def get_calendars(request: CalendarRequest):
    """
    Get a list of calendars for the authenticated user.
    
    Args:
        request (CalendarRequest): The request containing business ID and calendar type.
        
    Returns:
        CalendarResponse: The response containing the list of calendars.
    """
    try:
        calendar_service = get_calendar_service(request.calendar_type)
        calendars = calendar_service.get_calendars()
        
        return CalendarResponse(calendars=calendars)
    except Exception as e:
        logger.error(f"Error getting calendars: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/availability", response_model=AvailabilityResponse)
async def get_availability(request: AvailabilityRequest):
    """
    Get available time slots for a calendar.
    
    Args:
        request (AvailabilityRequest): The request containing calendar details and date range.
        
    Returns:
        AvailabilityResponse: The response containing the list of available slots.
    """
    try:
        calendar_service = get_calendar_service(request.calendar_type)
        
        start_date = datetime.datetime.fromisoformat(request.start_date)
        end_date = datetime.datetime.fromisoformat(request.end_date)
        
        slots = calendar_service.get_available_slots(
            calendar_id=request.calendar_id,
            start_date=start_date,
            end_date=end_date,
            duration_minutes=request.duration_minutes,
            business_hours=request.business_hours
        )
        
        return AvailabilityResponse(slots=slots)
    except Exception as e:
        logger.error(f"Error getting availability: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/appointments", response_model=AppointmentResponse)
async def create_appointment(request: AppointmentRequest):
    """
    Create an appointment on the calendar.
    
    Args:
        request (AppointmentRequest): The request containing appointment details.
        
    Returns:
        AppointmentResponse: The response containing the created appointment.
    """
    try:
        calendar_service = get_calendar_service(request.calendar_type)
        
        start_time = datetime.datetime.fromisoformat(request.start_time)
        end_time = datetime.datetime.fromisoformat(request.end_time)
        
        appointment = calendar_service.create_appointment(
            calendar_id=request.calendar_id,
            summary=request.summary,
            start_time=start_time,
            end_time=end_time,
            description=request.description,
            location=request.location,
            attendees=request.attendees
        )
        
        if appointment:
            return AppointmentResponse(
                appointment=appointment,
                success=True,
                message="Appointment created successfully"
            )
        else:
            return AppointmentResponse(
                success=False,
                message="Failed to create appointment"
            )
    except Exception as e:
        logger.error(f"Error creating appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def start_server():
    """Start the FastAPI server."""
    import uvicorn
    uvicorn.run(
        "calendar_service.api:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )

if __name__ == "__main__":
    start_server()
