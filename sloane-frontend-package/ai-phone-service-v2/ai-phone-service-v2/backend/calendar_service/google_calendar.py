"""
Calendar service for appointment scheduling integration.
"""
import os
import logging
import datetime
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarService:
    """
    Service for integrating with Google Calendar.
    """
    
    def __init__(self, credentials_path: str = None, token_path: str = None):
        """
        Initialize the Google Calendar service.
        
        Args:
            credentials_path (str, optional): Path to the credentials.json file.
            token_path (str, optional): Path to the token.json file.
        """
        self.credentials_path = credentials_path or os.path.join(
            os.path.dirname(__file__), 'credentials', 'google_credentials.json'
        )
        self.token_path = token_path or os.path.join(
            os.path.dirname(__file__), 'credentials', 'google_token.json'
        )
        self.service = None
        
        # Ensure credentials directory exists
        os.makedirs(os.path.dirname(self.credentials_path), exist_ok=True)
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API.
        
        Returns:
            bool: True if authentication was successful, False otherwise.
        """
        creds = None
        
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_info(
                json.loads(open(self.token_path).read()), SCOPES
            )
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    logger.error(f"Credentials file not found at {self.credentials_path}")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            return True
        except Exception as e:
            logger.error(f"Failed to build Google Calendar service: {str(e)}")
            return False
    
    def get_calendars(self) -> List[Dict[str, Any]]:
        """
        Get a list of calendars for the authenticated user.
        
        Returns:
            List[Dict[str, Any]]: List of calendars.
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            calendars = []
            page_token = None
            
            while True:
                calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
                for calendar_list_entry in calendar_list['items']:
                    calendars.append({
                        'id': calendar_list_entry['id'],
                        'summary': calendar_list_entry['summary'],
                        'description': calendar_list_entry.get('description', ''),
                        'primary': calendar_list_entry.get('primary', False)
                    })
                
                page_token = calendar_list.get('nextPageToken')
                if not page_token:
                    break
            
            return calendars
        except HttpError as error:
            logger.error(f"An error occurred while getting calendars: {error}")
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
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            # Get events from the calendar
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_date.isoformat() + 'Z',  # 'Z' indicates UTC time
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            
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
                    if 'dateTime' not in event.get('start', {}) or 'dateTime' not in event.get('end', {}):
                        continue
                    
                    event_start = datetime.datetime.fromisoformat(
                        event['start']['dateTime'].replace('Z', '+00:00')
                    )
                    event_end = datetime.datetime.fromisoformat(
                        event['end']['dateTime'].replace('Z', '+00:00')
                    )
                    
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
        except HttpError as error:
            logger.error(f"An error occurred while getting available slots: {error}")
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
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            event = {
                'summary': summary,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                }
            }
            
            if description:
                event['description'] = description
            
            if location:
                event['location'] = location
            
            if attendees:
                event['attendees'] = attendees
            
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event,
                sendUpdates='all'
            ).execute()
            
            return {
                'id': created_event['id'],
                'summary': created_event['summary'],
                'start': created_event['start']['dateTime'],
                'end': created_event['end']['dateTime'],
                'link': created_event.get('htmlLink', '')
            }
        except HttpError as error:
            logger.error(f"An error occurred while creating appointment: {error}")
            return None
