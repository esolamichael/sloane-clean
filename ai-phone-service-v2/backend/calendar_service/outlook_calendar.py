"""
Outlook Calendar service for appointment scheduling integration.
"""
import os
import logging
import datetime
import json
from typing import List, Dict, Any, Optional
import msal
import requests

logger = logging.getLogger(__name__)

# Microsoft Graph API endpoints
GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'
AUTHORITY = 'https://login.microsoftonline.com/common'

# Scopes required for calendar access
SCOPES = ['Calendars.ReadWrite', 'Calendars.Read']

class OutlookCalendarService:
    """
    Service for integrating with Microsoft Outlook Calendar.
    """
    
    def __init__(self, credentials_path: str = None, token_path: str = None):
        """
        Initialize the Outlook Calendar service.
        
        Args:
            credentials_path (str, optional): Path to the credentials.json file.
            token_path (str, optional): Path to the token.json file.
        """
        self.credentials_path = credentials_path or os.path.join(
            os.path.dirname(__file__), 'credentials', 'outlook_credentials.json'
        )
        self.token_path = token_path or os.path.join(
            os.path.dirname(__file__), 'credentials', 'outlook_token.json'
        )
        self.app = None
        self.token = None
        
        # Ensure credentials directory exists
        os.makedirs(os.path.dirname(self.credentials_path), exist_ok=True)
    
    def authenticate(self) -> bool:
        """
        Authenticate with Microsoft Graph API.
        
        Returns:
            bool: True if authentication was successful, False otherwise.
        """
        try:
            # Load credentials
            if not os.path.exists(self.credentials_path):
                logger.error(f"Credentials file not found at {self.credentials_path}")
                return False
            
            with open(self.credentials_path, 'r') as f:
                config = json.load(f)
            
            # Initialize MSAL app
            self.app = msal.ConfidentialClientApplication(
                config['client_id'],
                authority=AUTHORITY,
                client_credential=config['client_secret']
            )
            
            # Load token from cache if available
            if os.path.exists(self.token_path):
                with open(self.token_path, 'r') as f:
                    self.token = json.load(f)
            
            # Check if token is valid
            if not self.token or 'access_token' not in self.token:
                # For a web app, you would redirect to the authorization URL
                # For this example, we'll simulate a device code flow
                flow = self.app.initiate_device_flow(scopes=SCOPES)
                
                if 'user_code' not in flow:
                    logger.error(f"Failed to initiate device flow: {flow.get('error_description', 'Unknown error')}")
                    return False
                
                print(f"Please visit {flow['verification_uri']} and enter the code {flow['user_code']}")
                
                # Wait for user to complete the flow
                self.token = self.app.acquire_token_by_device_flow(flow)
                
                # Save token for future use
                with open(self.token_path, 'w') as f:
                    json.dump(self.token, f)
            
            return 'access_token' in self.token
        except Exception as e:
            logger.error(f"Failed to authenticate with Outlook: {str(e)}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get the headers for API requests.
        
        Returns:
            Dict[str, str]: The headers.
        """
        return {
            'Authorization': f"Bearer {self.token['access_token']}",
            'Content-Type': 'application/json'
        }
    
    def get_calendars(self) -> List[Dict[str, Any]]:
        """
        Get a list of calendars for the authenticated user.
        
        Returns:
            List[Dict[str, Any]]: List of calendars.
        """
        if not self.token:
            if not self.authenticate():
                return []
        
        try:
            # Get calendars from Microsoft Graph API
            response = requests.get(
                f"{GRAPH_API_ENDPOINT}/me/calendars",
                headers=self._get_headers()
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get calendars: {response.text}")
                return []
            
            calendars_data = response.json()
            
            # Format the response
            calendars = []
            for calendar in calendars_data.get('value', []):
                calendars.append({
                    'id': calendar['id'],
                    'summary': calendar['name'],
                    'description': calendar.get('description', ''),
                    'primary': calendar.get('isDefaultCalendar', False)
                })
            
            return calendars
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
        if not self.token:
            if not self.authenticate():
                return []
        
        try:
            # Format dates for Microsoft Graph API
            start_date_str = start_date.isoformat() + 'Z'
            end_date_str = end_date.isoformat() + 'Z'
            
            # Get events from the calendar
            response = requests.get(
                f"{GRAPH_API_ENDPOINT}/me/calendars/{calendar_id}/events",
                headers=self._get_headers(),
                params={
                    'startDateTime': start_date_str,
                    'endDateTime': end_date_str,
                    '$select': 'subject,start,end,isAllDay'
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get events: {response.text}")
                return []
            
            events_data = response.json()
            events = events_data.get('value', [])
            
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
                    if 'start' not in event or 'end' not in event:
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
        if not self.token:
            if not self.authenticate():
                return None
        
        try:
            # Prepare the event data
            event_data = {
                'subject': summary,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC'
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC'
                }
            }
            
            if description:
                event_data['body'] = {
                    'contentType': 'text',
                    'content': description
                }
            
            if location:
                event_data['location'] = {
                    'displayName': location
                }
            
            if attendees:
                event_data['attendees'] = [
                    {
                        'emailAddress': {
                            'address': attendee['email']
                        },
                        'type': 'required'
                    }
                    for attendee in attendees
                ]
            
            # Create the event
            response = requests.post(
                f"{GRAPH_API_ENDPOINT}/me/calendars/{calendar_id}/events",
                headers=self._get_headers(),
                json=event_data
            )
            
            if response.status_code not in (200, 201):
                logger.error(f"Failed to create event: {response.text}")
                return None
            
            event = response.json()
            
            return {
                'id': event['id'],
                'summary': event['subject'],
                'start': event['start']['dateTime'],
                'end': event['end']['dateTime'],
                'link': event.get('webLink', '')
            }
        except Exception as e:
            logger.error(f"An error occurred while creating appointment: {str(e)}")
            return None
