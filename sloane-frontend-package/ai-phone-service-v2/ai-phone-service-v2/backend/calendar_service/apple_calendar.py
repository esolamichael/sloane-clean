"""
Apple Calendar service for appointment scheduling integration.
"""
import os
import logging
import datetime
import json
import requests
from typing import List, Dict, Any, Optional
import caldav
from caldav.elements import dav, cdav

logger = logging.getLogger(__name__)

class AppleCalendarService:
    """
    Service for integrating with Apple Calendar via CalDAV.
    """
    
    def __init__(self, credentials_path: str = None):
        """
        Initialize the Apple Calendar service.
        
        Args:
            credentials_path (str, optional): Path to the credentials.json file.
        """
        self.credentials_path = credentials_path or os.path.join(
            os.path.dirname(__file__), 'credentials', 'apple_credentials.json'
        )
        self.client = None
        
        # Ensure credentials directory exists
        os.makedirs(os.path.dirname(self.credentials_path), exist_ok=True)
    
    def authenticate(self) -> bool:
        """
        Authenticate with Apple Calendar via CalDAV.
        
        Returns:
            bool: True if authentication was successful, False otherwise.
        """
        try:
            # Load credentials
            if not os.path.exists(self.credentials_path):
                logger.error(f"Credentials file not found at {self.credentials_path}")
                return False
            
            with open(self.credentials_path, 'r') as f:
                credentials = json.load(f)
            
            # Connect to CalDAV server
            self.client = caldav.DAVClient(
                url=credentials.get('url', 'https://caldav.icloud.com'),
                username=credentials.get('username'),
                password=credentials.get('password')
            )
            
            # Test connection by getting principal
            principal = self.client.principal()
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate with Apple Calendar: {str(e)}")
            return False
    
    def get_calendars(self) -> List[Dict[str, Any]]:
        """
        Get a list of calendars for the authenticated user.
        
        Returns:
            List[Dict[str, Any]]: List of calendars.
        """
        if not self.client:
            if not self.authenticate():
                return []
        
        try:
            # Get principal
            principal = self.client.principal()
            
            # Get calendars
            calendars = principal.calendars()
            
            # Format the response
            result = []
            for calendar in calendars:
                result.append({
                    'id': calendar.id,
                    'summary': calendar.name,
                    'description': '',  # CalDAV doesn't provide description
                    'primary': False  # CalDAV doesn't indicate primary calendar
                })
            
            return result
        except Exception as e:
            logger.error(f"An error occurred while getting calendars: {str(e)}")
            return []
    
    def get_available_slots(
        self, 
        calendar_id: str, 
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        duration_minutes: int = 60,
        business_hours: Dict[str, str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get available time slots for a calendar.
        
        Args:
            calendar_id (str): The ID of the calendar.
            start_date (datetime.datetime): The start date for the search.
            end_date (datetime.datetime): The end date for the search.
            duration_minutes (int, optional): The duration of the appointment in minutes.
            business_hours (Dict[str, str], optional): Business hours for each day of the week.
                Format: {'monday': '9:00 AM - 5:00 PM', ...}
        
        Returns:
            List[Dict[str, Any]]: List of available time slots.
        """
        if not self.client:
            if not self.authenticate():
                return []
        
        try:
            # Get principal
            principal = self.client.principal()
            
            # Get calendar
            calendars = principal.calendars()
            calendar = None
            for cal in calendars:
                if cal.id == calendar_id:
                    calendar = cal
                    break
            
            if not calendar:
                logger.error(f"Calendar not found: {calendar_id}")
                return []
            
            # Get events from the calendar
            events = calendar.date_search(
                start=start_date,
                end=end_date,
                expand=True
            )
            
            # Convert business hours to datetime objects
            business_hours_dict = {}
            if business_hours:
                for day, hours in business_hours.items():
                    if hours.lower() == 'closed':
                        business_hours_dict[day.lower()] = None
                        continue
                    
                    try:
                        start_time_str, end_time_str = hours.split('-')
                        start_time = datetime.datetime.strptime(start_time_str.strip(), '%I:%M %p').time()
                        end_time = datetime.datetime.strptime(end_time_str.strip(), '%I:%M %p').time()
                        business_hours_dict[day.lower()] = (start_time, end_time)
                    except Exception as e:
                        logger.error(f"Failed to parse business hours for {day}: {str(e)}")
                        business_hours_dict[day.lower()] = None
            
            # Generate available slots
            available_slots = []
            current_date = start_date
            
            while current_date <= end_date:
                day_name = current_date.strftime('%A').lower()
                
                # Skip if the business is closed on this day
                if business_hours and day_name in business_hours_dict and business_hours_dict[day_name] is None:
                    current_date += datetime.timedelta(days=1)
                    current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    continue
                
                # Use business hours if available
                if business_hours and day_name in business_hours_dict and business_hours_dict[day_name]:
                    start_time, end_time = business_hours_dict[day_name]
                    day_start = current_date.replace(
                        hour=start_time.hour, 
                        minute=start_time.minute, 
                        second=0, 
                        microsecond=0
                    )
                    day_end = current_date.replace(
                        hour=end_time.hour, 
                        minute=end_time.minute, 
                        second=0, 
                        microsecond=0
                    )
                else:
                    # Default to 9 AM - 5 PM
                    day_start = current_date.replace(hour=9, minute=0, second=0, microsecond=0)
                    day_end = current_date.replace(hour=17, minute=0, second=0, microsecond=0)
                
                # Skip if the day has already passed
                if day_end < datetime.datetime.now():
                    current_date += datetime.timedelta(days=1)
                    current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    continue
                
                # Get busy slots for the day
                busy_slots = []
                for event in events:
                    event_data = event.instance.vevent
                    
                    # Extract start and end times
                    event_start = event_data.dtstart.value
                    event_end = event_data.dtend.value
                    
                    # Convert to datetime if date
                    if isinstance(event_start, datetime.date) and not isinstance(event_start, datetime.datetime):
                        event_start = datetime.datetime.combine(event_start, datetime.time.min)
                    if isinstance(event_end, datetime.date) and not isinstance(event_end, datetime.datetime):
                        event_end = datetime.datetime.combine(event_end, datetime.time.max)
                    
                    # Check if the event is on the current day
                    if event_start.date() == current_date.date() or event_end.date() == current_date.date():
                        busy_slots.append((event_start, event_end))
                
                # Sort busy slots by start time
                busy_slots.sort(key=lambda x: x[0])
                
                # Generate available slots
                slot_start = day_start
                duration = datetime.timedelta(minutes=duration_minutes)
                
                while slot_start + duration <= day_end:
                    slot_end = slot_start + duration
                    is_available = True
                    
                    # Check if the slot overlaps with any busy slot
                    for busy_start, busy_end in busy_slots:
                        if (slot_start < busy_end and slot_end > busy_start):
                            is_available = False
                            # Move to the end of the busy slot
                            slot_start = busy_end
                            break
                    
                    if is_available:
                        available_slots.append({
                            'start': slot_start.isoformat(),
                            'end': slot_end.isoformat(),
                            'duration_minutes': duration_minutes
                        })
                        slot_start += duration
                    
                current_date += datetime.timedelta(days=1)
                current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            return available_slots
        except Exception as e:
            logger.error(f"An error occurred while getting available slots: {str(e)}")
            return []
    
    def create_appointment(
        self,
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
            calendar_id (str): The ID of the calendar.
            summary (str): The summary/title of the appointment.
            start_time (datetime.datetime): The start time of the appointment.
            end_time (datetime.datetime): The end time of the appointment.
            description (str, optional): The description of the appointment.
            location (str, optional): The location of the appointment.
            attendees (List[Dict[str, str]], optional): List of attendees.
                Format: [{'email': 'attendee@example.com'}, ...]
        
        Returns:
            Optional[Dict[str, Any]]: The created event if successful, None otherwise.
        """
        if not self.client:
            if not self.authenticate():
                return None
        
        try:
            # Get principal
            principal = self.client.principal()
            
            # Get calendar
            calendars = principal.calendars()
            calendar = None
            for cal in calendars:
                if cal.id == calendar_id:
                    calendar = cal
                    break
            
            if not calendar:
                logger.error(f"Calendar not found: {calendar_id}")
                return None
            
            # Create event
            event = calendar.save_event(
                dtstart=start_time,
                dtend=end_time,
                summary=summary,
                description=description or "",
                location=location or ""
            )
            
            # Add attendees if provided
            if attendees and event:
                # This would require modifying the iCalendar data directly
                # For simplicity, we'll skip this in the example
                pass
            
            # Get the created event
            if event:
                return {
                    'id': event.id,
                    'summary': summary,
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'link': ''  # CalDAV doesn't provide a web link
                }
            
            return None
        except Exception as e:
            logger.error(f"An error occurred while creating appointment: {str(e)}")
            return None
