from typing import Dict, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from .repository import BusinessProfileRepository, OAuthTokenRepository

class GoogleBusinessService:
    def __init__(self, business_repo: BusinessProfileRepository, oauth_repo: OAuthTokenRepository):
        self.business_repo = business_repo
        self.oauth_repo = oauth_repo
    
    def get_google_client(self, user_id: int) -> Any:
        """Get Google API client with user credentials"""
        # Get tokens from repository
        tokens = self.oauth_repo.get_tokens(user_id, 'google')
        
        if not tokens:
            raise Exception("User not authenticated with Google")
        
        # Create credentials
        credentials = Credentials(
            token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            token_uri='https://oauth2.googleapis.com/token',
            client_id=os.environ.get('GOOGLE_CLIENT_ID'),
            client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
            scopes=['https://www.googleapis.com/auth/business.manage']
        )
        
        # Build the service
        return build('mybusiness', 'v4', credentials=credentials)
    
    def get_business_accounts(self, user_id: int) -> Dict[str, Any]:
        """Get business accounts for a user"""
        service = self.get_google_client(user_id)
        accounts = service.accounts().list().execute()
        return accounts
    
    def get_business_locations(self, user_id: int, account_id: str) -> Dict[str, Any]:
        """Get business locations for an account"""
        service = self.get_google_client(user_id)
        locations = service.accounts().locations().list(parent=account_id).execute()
        return locations
    
    def get_business_details(self, user_id: int, location_name: str) -> Dict[str, Any]:
        """Get detailed information about a business location"""
        service = self.get_google_client(user_id)
        location = service.locations().get(name=location_name).execute()
        return location
    
    def import_business_profile(self, user_id: int, location_data: Dict[str, Any]) -> int:
        """Import Google Business Profile data into Sloane"""
        # Process the location data
        processed_data = self._process_location_data(location_data)
        
        # Save to database
        profile_id = self.business_repo.create_from_google_business(user_id, processed_data)
        
        return profile_id
    
    def _process_location_data(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Google Business location data for storage"""
        # Extract business name
        business_name = location_data.get('locationName', '')
        
        # Extract address
        address = {}
        if 'address' in location_data:
            address = {
                'street': location_data['address'].get('addressLines', [''])[0],
                'city': location_data['address'].get('locality', ''),
                'state': location_data['address'].get('administrativeArea', ''),
                'postalCode': location_data['address'].get('postalCode', ''),
                'country': location_data['address'].get('regionCode', '')
            }
        
        # Extract contact info
        contact_info = {
            'phone': location_data.get('primaryPhone', ''),
            'website': location_data.get('websiteUri', ''),
            'email': location_data.get('primaryEmail', '')
        }
        
        # Extract business hours
        business_hours = {}
        if 'regularHours' in location_data:
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            # Initialize all days as closed
            for day in days:
                business_hours[day] = {'isOpen': False}
            
            # Update with actual hours
            for period in location_data['regularHours'].get('periods', []):
                day_index = period.get('openDay', 0) - 1  # Google uses 1-7 for days
                if 0 <= day_index < 7:
                    day = days[day_index]
                    business_hours[day] = {
                        'isOpen': True,
                        'openTime': period.get('openTime', ''),
                        'closeTime': period.get('closeTime', '')
                    }
        
        # Extract services from categories
        services = []
        for category in location_data.get('categories', []):
            services.append({
                'name': category.get('displayName', ''),
                'description': '',  # Google doesn't provide service descriptions
                'price': ''  # Google doesn't provide pricing
            })
        
        # Prepare the complete data structure
        return {
            'googleBusinessId': location_data.get('name', ''),
            'businessName': business_name,
            'address': address,
            'contactInfo': contact_info,
            'businessHours': business_hours,
            'services': services,
            'description': location_data.get('profile', {}).get('description', ''),
            'attributes': location_data.get('attributes', {})
        }
