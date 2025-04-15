# backend/business_profile_service/routes.py

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from typing import Dict, Any, Optional
from google_auth_oauthlib.flow import Flow
import os
import json

from .schema import (
    GoogleAuthResponseSchema, 
    GoogleBusinessAccountSchema,
    GoogleBusinessLocationSchema,
    GoogleBusinessImportSchema,
    ImportResponseSchema
)
from .service import GoogleBusinessService
from .repository import BusinessProfileRepository, OAuthTokenRepository
# Import your dependency injection system or database session
from your_app_module import get_db_session

# Create Router
router = APIRouter(prefix="/api/google-business", tags=["Google Business"])

# OAuth configuration
CLIENT_CONFIG = {
    "web": {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [os.environ.get("GOOGLE_REDIRECT_URI")]
    }
}

# Dependency to get repositories and service
def get_service(request: Request):
    # Get database session
    db_session = get_db_session()
    
    # Initialize repositories
    business_repo = BusinessProfileRepository(db_session)
    oauth_repo = OAuthTokenRepository(db_session)
    
    # Initialize service
    service = GoogleBusinessService(business_repo, oauth_repo)
    
    return service

# Start OAuth flow
@router.get("/auth", response_model=GoogleAuthResponseSchema)
async def start_auth(request: Request, response: Response):
    # Create flow instance
    flow = Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=['https://www.googleapis.com/auth/business.manage'],
        redirect_uri=os.environ.get("GOOGLE_REDIRECT_URI")
    )
    
    # Generate authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    # Store state in session or cookie
    # For FastAPI, you need to handle sessions via cookies or another session middleware
    response.set_cookie(key="google_auth_state", value=state, httponly=True)
    
    # Return redirect URL
    return RedirectResponse(url=authorization_url)

# OAuth callback
@router.get("/auth/callback", response_model=GoogleAuthResponseSchema)
async def auth_callback(request: Request, response: Response, service: GoogleBusinessService = Depends(get_service)):
    # Get state from cookie
    state = request.cookies.get("google_auth_state")
    
    if not state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Create flow instance
    flow = Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=['https://www.googleapis.com/auth/business.manage'],
        redirect_uri=os.environ.get("GOOGLE_REDIRECT_URI"),
        state=state
    )
    
    # Exchange authorization code for tokens
    flow.fetch_token(authorization_response=str(request.url))
    
    # Get credentials
    credentials = flow.credentials
    tokens = {
        'access_token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'expiry_date': credentials.expiry
    }
    
    # Get user ID from request (implement your authentication method)
    user_id = request.state.user_id  # Adjust based on your auth system
    
    try:
        # Save tokens using service
        service.save_tokens(user_id, "google", tokens)
        
        # Clear the state cookie
        response.delete_cookie(key="google_auth_state")
        
        # Redirect to frontend
        return RedirectResponse(url="/dashboard/profile?google_connected=true")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get business accounts
@router.get("/accounts", response_model=Dict[str, Any])
async def get_accounts(service: GoogleBusinessService = Depends(get_service), request: Request = None):
    # Get user ID from request (implement your authentication method)
    user_id = request.state.user_id  # Adjust based on your auth system
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        accounts = service.get_business_accounts(user_id)
        return accounts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get business locations
@router.get("/locations", response_model=Dict[str, Any])
async def get_locations(account_id: str, request: Request = None, service: GoogleBusinessService = Depends(get_service)):
    # Get user ID from request (implement your authentication method)
    user_id = request.state.user_id  # Adjust based on your auth system
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not account_id:
        raise HTTPException(status_code=400, detail="Account ID is required")
    
    try:
        locations = service.get_business_locations(user_id, account_id)
        return locations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get detailed business information
@router.get("/details", response_model=Dict[str, Any])
async def get_details(location_id: str, request: Request = None, service: GoogleBusinessService = Depends(get_service)):
    # Get user ID from request (implement your authentication method)
    user_id = request.state.user_id  # Adjust based on your auth system
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not location_id:
        raise HTTPException(status_code=400, detail="Location ID is required")
    
    try:
        details = service.get_business_details(user_id, location_id)
        return {"profile": details}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Import business profile to Sloane
@router.post("/import", response_model=ImportResponseSchema)
async def import_profile(data: GoogleBusinessImportSchema, request: Request = None, service: GoogleBusinessService = Depends(get_service)):
    # Get user ID from request (implement your authentication method)
    user_id = request.state.user_id  # Adjust based on your auth system
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Get location details
        location_data = service.get_business_details(user_id, data.location_id)
        
        # Import to database
        profile_id = service.import_business_profile(user_id, location_data)
        
        return {
            "success": True,
            "profile_id": profile_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
