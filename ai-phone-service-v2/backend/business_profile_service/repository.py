import os
import json
from datetime import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List

from .models import BusinessProfile, BusinessHours, BusinessService, OAuthToken

class BusinessProfileRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def create_from_google_business(self, user_id: int, business_data: Dict[str, Any]) -> int:
        """Create a new business profile from Google Business data"""
        try:
            # Create the main business profile
            business_profile = BusinessProfile(
                user_id=user_id,
                google_business_id=business_data.get('googleBusinessId'),
                business_name=business_data.get('businessName'),
                street_address=business_data.get('address', {}).get('street'),
                city=business_data.get('address', {}).get('city'),
                state=business_data.get('address', {}).get('state'),
                postal_code=business_data.get('address', {}).get('postalCode'),
                country=business_data.get('address', {}).get('country'),
                phone=business_data.get('contactInfo', {}).get('phone'),
                website=business_data.get('contactInfo', {}).get('website'),
                email=business_data.get('contactInfo', {}).get('email'),
                description=business_data.get('description'),
                attributes=business_data.get('attributes', {})
            )
            
            self.db_session.add(business_profile)
            # Flush to get the ID without committing transaction
            self.db_session.flush()
            
            # Add business hours if available
            business_hours = business_data.get('businessHours', {})
            for day, hours in business_hours.items():
                if hours:
                    hour = BusinessHours(
                        business_profile_id=business_profile.id,
                        day_of_week=day,
                        is_open=hours.get('isOpen', True),
                        open_time=hours.get('openTime'),
                        close_time=hours.get('closeTime')
                    )
                    self.db_session.add(hour)
            
            # Add services if available
            services = business_data.get('services', [])
            for service_data in services:
                service = BusinessService(
                    business_profile_id=business_profile.id,
                    name=service_data.get('name', ''),
                    description=service_data.get('description', ''),
                    price=service_data.get('price', '')
                )
                self.db_session.add(service)
            
            self.db_session.commit()
            return business_profile.id
            
        except Exception as e:
            self.db_session.rollback()
            raise e
    
    def get_by_id(self, profile_id: int) -> Optional[Dict[str, Any]]:
        """Get business profile by ID"""
        profile = self.db_session.query(BusinessProfile).filter_by(id=profile_id).first()
        
        if not profile:
            return None
        
        return self._format_profile(profile)
    
    def get_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get business profile by user ID"""
        profile = self.db_session.query(BusinessProfile).filter_by(user_id=user_id).first()
        
        if not profile:
            return None
        
        return self._format_profile(profile)
    
    def _format_profile(self, profile: BusinessProfile) -> Dict[str, Any]:
        """Format business profile data"""
        # Convert business hours to dictionary format
        business_hours = {}
        for hour in profile.business_hours:
            business_hours[hour.day_of_week] = {
                'isOpen': hour.is_open,
                'openTime': hour.open_time,
                'closeTime': hour.close_time
            }
        
        # Format services
        services = []
        for service in profile.services:
            services.append({
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'price': service.price
            })
        
        return {
            'id': profile.id,
            'userId': profile.user_id,
            'googleBusinessId': profile.google_business_id,
            'businessName': profile.business_name,
            'address': {
                'street': profile.street_address,
                'city': profile.city,
                'state': profile.state,
                'postalCode': profile.postal_code,
                'country': profile.country
            },
            'contactInfo': {
                'phone': profile.phone,
                'website': profile.website,
                'email': profile.email
            },
            'businessHours': business_hours,
            'services': services,
            'description': profile.description,
            'attributes': profile.attributes,
            'createdAt': profile.created_at.isoformat() if profile.created_at else None,
            'updatedAt': profile.updated_at.isoformat() if profile.updated_at else None
        }


class OAuthTokenRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        # Get the encryption key from environment
        self.encryption_key = os.environ.get('TOKEN_ENCRYPTION_KEY').encode('utf-8')
    
    def save_tokens(self, user_id: int, provider: str, tokens: Dict[str, Any]) -> bool:
        """Save OAuth tokens for a user"""
        try:
            # Check if tokens already exist
            existing_token = self.db_session.query(OAuthToken).filter_by(
                user_id=user_id, provider=provider
            ).first()
            
            # Generate a random nonce (IV)
            nonce = os.urandom(12)
            
            # Encrypt access token
            aesgcm = AESGCM(self.encryption_key)
            access_token_bytes = tokens['access_token'].encode('utf-8')
            encrypted_access_token = aesgcm.encrypt(nonce, access_token_bytes, None)
            
            # Encrypt refresh token if provided
            encrypted_refresh_token = None
            if tokens.get('refresh_token'):
                refresh_token_bytes = tokens['refresh_token'].encode('utf-8')
                encrypted_refresh_token = aesgcm.encrypt(nonce, refresh_token_bytes, None)
            
            if existing_token:
                # Update existing token
                existing_token.encrypted_access_token = encrypted_access_token.hex()
                if encrypted_refresh_token:
                    existing_token.encrypted_refresh_token = encrypted_refresh_token.hex()
                existing_token.iv = nonce.hex()
                existing_token.expiry_date = datetime.fromtimestamp(tokens.get('expiry_date') / 1000) if tokens.get('expiry_date') else None
                existing_token.updated_at = datetime.now()
            else:
                # Create new token
                token = OAuthToken(
                    user_id=user_id,
                    provider=provider,
                    encrypted_access_token=encrypted_access_token.hex(),
                    encrypted_refresh_token=encrypted_refresh_token.hex() if encrypted_refresh_token else None,
                    iv=nonce.hex(),
                    expiry_date=datetime.fromtimestamp(tokens.get('expiry_date') / 1000) if tokens.get('expiry_date') else None
                )
                self.db_session.add(token)
            
            self.db_session.commit()
            return True
            
        except Exception as e:
            self.db_session.rollback()
            raise e
    
    def get_tokens(self, user_id: int, provider: str) -> Optional[Dict[str, Any]]:
        """Get OAuth tokens for a user"""
        token = self.db_session.query(OAuthToken).filter_by(
            user_id=user_id, provider=provider
        ).first()
        
        if not token:
            return None
        
        try:
            # Decrypt tokens
            aesgcm = AESGCM(self.encryption_key)
            nonce = bytes.fromhex(token.iv)
            
            # Decrypt access token
            encrypted_access_token = bytes.fromhex(token.encrypted_access_token)
            access_token = aesgcm.decrypt(nonce, encrypted_access_token, None).decode('utf-8')
            
            # Decrypt refresh token if exists
            refresh_token = None
            if token.encrypted_refresh_token:
                encrypted_refresh_token = bytes.fromhex(token.encrypted_refresh_token)
                refresh_token = aesgcm.decrypt(nonce, encrypted_refresh_token, None).decode('utf-8')
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expiry_date': int(token.expiry_date.timestamp() * 1000) if token.expiry_date else None
            }
            
        except Exception as e:
            print(f"Error decrypting tokens: {e}")
            return None
