"""
Calendar integration for the AI Conversation Service.
"""
import os
import logging
import datetime
import json
import requests
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class CalendarIntegration:
    """
    Integration with the Calendar Service API for the AI Conversation Service.
    """
    
    def __init__(self, api_base_url: str = None):
        """
        Initialize the calendar integration.
        
        Args:
            api_base_url (str, optional): Base URL for the Calendar Service API.
        """
        self.api_base_url = api_base_url or "http://localhost:8001"
    
    def get_calendars(self, business_id: str, calendar_type: str) -> List[Dict[str, Any]]:
        """
        Get a list of calendars for a business.
        
        Args:
            business_id (str): The ID of the business.
            calendar_type (str): The type of calendar (google, outlook, apple).
            
        Returns:
            List[Dict[str, Any]]: List of calendars.
        """
        try:
            response = requests.post(
                f"{self.api_base_url}/api/calendars",
                json={
                    "business_id": business_id,
                    "calendar_type": calendar_type
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get calendars: {response.text}")
                return []
            
            return response.json().get("calendars", [])
        except Exception as e:
            logger.error(f"An error occurred while getting calendars: {str(e)}")
            return []
    
    def get_available_slots(
        self,
        business_id: str,
        calendar_type: str,
        calendar_id: str,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        duration_minutes: int = 60,
        business_hours: Dict[str, str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get available time slots for a calendar.
        
        Args:
            business_id (str): The ID of the business.
            calendar_type (str): The type of calendar (google, outlook, apple).
            calendar_id (str): The ID of the calendar.
            start_date (datetime.datetime): The start date for the search.
            end_date (datetime.datetime): The end date for the search.
            duration_minutes (int, optional): The duration of the appointment in minutes.
            business_hours (Dict[str, str], optional): Business hours for each day of the week.
                Format: {'monday': '9:00 AM - 5:00 PM', ...}
            
        Returns:
            List[Dict[str, Any]]: List of available time slots.
        """
        try:
            response = requests.post(
                f"{self.api_base_url}/api/availability",
                json={
                    "business_id": business_id,
                    "calendar_type": calendar_type,
                    "calendar_id": calendar_id,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "duration_minutes": duration_minutes,
                    "business_hours": business_hours
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get availability: {response.text}")
                return []
            
            return response.json().get("slots", [])
        except Exception as e:
            logger.error(f"An error occurred while getting availability: {str(e)}")
            return []
    
    def create_appointment(
        self,
        business_id: str,
        calendar_type: str,
        calendar_id: str,
        summary: str,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        description: str = None,
        location: str = None,
        attendees: List[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create an appointment on the calendar.
        
        Args:
            business_id (str): The ID of the business.
            calendar_type (str): The type of calendar (google, outlook, apple).
            calendar_id (str): The ID of the calendar.
            summary (str): The summary/title of the appointment.
            start_time (datetime.datetime): The start time of the appointment.
            end_time (datetime.datetime): The end time of the appointment.
            description (str, optional): The description of the appointment.
            location (str, optional): The location of the appointment.
            attendees (List[Dict[str, str]], optional): List of attendees.
                Format: [{'email': 'attendee@example.com'}, ...]
            
        Returns:
            Optional[Dict[str, Any]]: The created appointment if successful, None otherwise.
        """
        try:
            response = requests.post(
                f"{self.api_base_url}/api/appointments",
                json={
                    "business_id": business_id,
                    "calendar_type": calendar_type,
                    "calendar_id": calendar_id,
                    "summary": summary,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "description": description,
                    "location": location,
                    "attendees": attendees
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to create appointment: {response.text}")
                return None
            
            result = response.json()
            
            if not result.get("success"):
                logger.error(f"Failed to create appointment: {result.get('message')}")
                return None
            
            return result.get("appointment")
        except Exception as e:
            logger.error(f"An error occurred while creating appointment: {str(e)}")
            return None
    
    def suggest_appointment_slots(
        self,
        business_id: str,
        business_profile: Dict[str, Any],
        requested_date: Optional[str] = None,
        requested_time: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Suggest appointment slots based on user request and business profile.
        
        Args:
            business_id (str): The ID of the business.
            business_profile (Dict[str, Any]): The business profile.
            requested_date (str, optional): The requested date (e.g., "tomorrow", "next Monday").
            requested_time (str, optional): The requested time (e.g., "morning", "afternoon").
            
        Returns:
            List[Dict[str, Any]]: List of suggested appointment slots.
        """
        try:
            # Check if appointment scheduling is enabled
            appointment_settings = business_profile.get("appointmentScheduling", {})
            if not appointment_settings.get("enabled", False):
                logger.info("Appointment scheduling is not enabled for this business")
                return []
            
            # Get calendar settings
            calendar_type = appointment_settings.get("calendarType", "google")
            calendar_id = appointment_settings.get("calendarId")
            duration_minutes = appointment_settings.get("durationMinutes", 60)
            
            if not calendar_id:
                logger.error("Calendar ID not found in business profile")
                return []
            
            # Parse requested date
            start_date = datetime.datetime.now()
            end_date = start_date + datetime.timedelta(days=7)  # Default to next 7 days
            
            if requested_date:
                # Parse common date expressions
                requested_date = requested_date.lower()
                
                if "today" in requested_date:
                    start_date = datetime.datetime.now()
                    end_date = start_date.replace(hour=23, minute=59, second=59)
                elif "tomorrow" in requested_date:
                    start_date = datetime.datetime.now() + datetime.timedelta(days=1)
                    start_date = start_date.replace(hour=0, minute=0, second=0)
                    end_date = start_date.replace(hour=23, minute=59, second=59)
                elif "next week" in requested_date:
                    # Start from next Monday
                    days_until_monday = 7 - start_date.weekday()
                    start_date = start_date + datetime.timedelta(days=days_until_monday)
                    start_date = start_date.replace(hour=0, minute=0, second=0)
                    end_date = start_date + datetime.timedelta(days=6, hours=23, minutes=59, seconds=59)
                elif any(day in requested_date for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]):
                    # Find the next occurrence of the requested day
                    day_map = {
                        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                        "friday": 4, "saturday": 5, "sunday": 6
                    }
                    
                    for day, day_num in day_map.items():
                        if day in requested_date:
                            days_until_day = (day_num - start_date.weekday()) % 7
                            if days_until_day == 0 and start_date.hour >= 12:  # If it's already afternoon, go to next week
                                days_until_day = 7
                            
                            start_date = start_date + datetime.timedelta(days=days_until_day)
                            start_date = start_date.replace(hour=0, minute=0, second=0)
                            end_date = start_date.replace(hour=23, minute=59, second=59)
                            break
            
            # Parse requested time
            if requested_time:
                requested_time = requested_time.lower()
                
                if "morning" in requested_time:
                    start_date = start_date.replace(hour=8, minute=0, second=0)
                    end_date = start_date.replace(hour=12, minute=0, second=0)
                elif "afternoon" in requested_time:
                    start_date = start_date.replace(hour=12, minute=0, second=0)
                    end_date = start_date.replace(hour=17, minute=0, second=0)
                elif "evening" in requested_time:
                    start_date = start_date.replace(hour=17, minute=0, second=0)
                    end_date = start_date.replace(hour=20, minute=0, second=0)
            
            # Get business hours
            business_hours = business_profile.get("businessHours", {})
            
            # Get available slots
            available_slots = self.get_available_slots(
                business_id=business_id,
                calendar_type=calendar_type,
                calendar_id=calendar_id,
                start_date=start_date,
                end_date=end_date,
                duration_minutes=duration_minutes,
                business_hours=business_hours
            )
            
            # Limit to a reasonable number of suggestions
            return available_slots[:5]
        except Exception as e:
            logger.error(f"An error occurred while suggesting appointment slots: {str(e)}")
            return []
    
    def schedule_appointment(
        self,
        business_id: str,
        business_profile: Dict[str, Any],
        slot: Dict[str, Any],
        customer_name: str,
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None,
        appointment_reason: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Schedule an appointment using a selected slot.
        
        Args:
            business_id (str): The ID of the business.
            business_profile (Dict[str, Any]): The business profile.
            slot (Dict[str, Any]): The selected time slot.
            customer_name (str): The name of the customer.
            customer_email (str, optional): The email of the customer.
            customer_phone (str, optional): The phone number of the customer.
            appointment_reason (str, optional): The reason for the appointment.
            
        Returns:
            Optional[Dict[str, Any]]: The created appointment if successful, None otherwise.
        """
        try:
            # Check if appointment scheduling is enabled
            appointment_settings = business_profile.get("appointmentScheduling", {})
            if not appointment_settings.get("enabled", False):
                logger.info("Appointment scheduling is not enabled for this business")
                return None
            
            # Get calendar settings
            calendar_type = appointment_settings.get("calendarType", "google")
            calendar_id = appointment_settings.get("calendarId")
            
            if not calendar_id:
                logger.error("Calendar ID not found in business profile")
                return None
            
            # Parse slot times
            start_time = datetime.datetime.fromisoformat(slot["start"])
            end_time = datetime.datetime.fromisoformat(slot["end"])
            
            # Create appointment summary
            summary = f"Appointment with {customer_name}"
            
            # Create appointment description
            description = f"Appointment with {customer_name}\n\n"
            if customer_email:
                description += f"Email: {customer_email}\n"
            if customer_phone:
                description += f"Phone: {customer_phone}\n"
            if appointment_reason:
                description += f"\nReason: {appointment_reason}\n"
            
            # Create attendees list
            attendees = []
            if customer_email:
                attendees.append({"email": customer_email})
            
            # Create the appointment
            appointment = self.create_appointment(
                business_id=business_id,
                calendar_type=calendar_type,
                calendar_id=calendar_id,
                summary=summary,
                start_time=start_time,
                end_time=end_time,
                description=description,
                attendees=attendees
            )
            
            return appointment
        except Exception as e:
            logger.error(f"An error occurred while scheduling appointment: {str(e)}")
            return None
