# backend/business_profile_service/__init__.py

"""
Google Business Profile integration service for Sloane.

This package provides functionality to import business profile data from 
Google Business Profile API, store it in the database, and use it for training Sloane.
"""

# You can optionally expose key classes/functions at the package level
from .models import BusinessProfile, BusinessHours, BusinessService, OAuthToken
from .repository import BusinessProfileRepository, OAuthTokenRepository
from .service import GoogleBusinessService
