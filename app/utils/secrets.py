"""
Utility module for accessing secrets from Google Cloud Secret Manager.
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from google.cloud import secretmanager
from google.api_core import exceptions

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Project ID constant
PROJECT_ID = "clean-code-app-1744825963"

# Secret name mapping - use the actual secret names in Secret Manager
SECRET_NAME_MAP = {
    "MONGODB_URL": "mongodb-connection",
    "GOOGLE_MAPS_API_KEY": "google-maps-api-key",
    "TWILIO_AUTH_TOKEN": "twilio-auth-token",
    "APP_ENGINE_API_KEY": "APP_ENGINE_API_KEY_SECRET"
}

def get_secret(secret_id: str) -> Optional[str]:
    """
    Get a secret from Google Cloud Secret Manager.
    
    Args:
        secret_id: The ID of the secret to retrieve
        
    Returns:
        The secret value as a string, or None if not found
    """
    try:
        # Always use the correct secret names directly
        # mongodb-connection, google-maps-api-key, twilio-auth-token, APP_ENGINE_API_KEY_SECRET
        
        # Always use the correct project ID
        project_id = PROJECT_ID
        logger.info(f"Using project ID: {project_id} to get secret {secret_id}")
        
        # Create the Secret Manager client
        client = secretmanager.SecretManagerServiceClient()
        
        # Build the resource name of the secret version using the exact name
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        
        # Access the secret version
        response = client.access_secret_version(request={"name": name})
        
        # Return the decoded payload
        return response.payload.data.decode("UTF-8")
        
    except Exception as e:
        logger.error(f"Error accessing secret {secret_id}: {str(e)}")
        return None


def get_service_account_credentials(project_id: str, secret_id: str = "app-service-account-key") -> Dict[str, Any]:
    """
    Get service account credentials from Secret Manager.
    
    Args:
        project_id: The GCP project ID
        secret_id: The secret ID storing the service account key, defaults to "app-service-account-key"
        
    Returns:
        The service account credentials as a dictionary
    """
    try:
        # Get the secret payload
        secret_payload = get_secret(secret_id)
        
        # Parse the JSON payload
        credentials = json.loads(secret_payload)
        return credentials
    except Exception as e:
        print(f"Error getting service account credentials: {e}")
        # Return empty dict if error
        return {}


def get_mongodb_connection_string(project_id: str = PROJECT_ID) -> str:
    """
    Get MongoDB connection string from Secret Manager.
    
    Args:
        project_id: The GCP project ID (defaults to clean-code-app-1744825963)
        
    Returns:
        The MongoDB connection string
    """
    try:
        # Use the EXACT hyphenated name
        return get_secret("mongodb-connection")
    except Exception as e:
        logger.error(f"Error getting MongoDB connection string: {e}")
        raise


def get_twilio_auth_token(project_id: str, secret_id: str = "twilio-auth-token") -> str:
    """
    Get Twilio auth token from Secret Manager.
    
    Args:
        project_id: The GCP project ID
        secret_id: The secret ID storing the Twilio auth token, defaults to using exact hyphenated name
        
    Returns:
        The Twilio auth token
    """
    try:
        # Use the EXACT hyphenated name
        return get_secret("twilio-auth-token")
    except Exception as e:
        print(f"Error getting Twilio auth token: {e}")
        # Return empty string if error
        return ""


def get_project_id() -> str:
    """
    Get the GCP project ID.
    
    Returns:
        The project ID as a string
    """
    # Always use the correct project ID
    return PROJECT_ID


def should_use_secret_manager() -> bool:
    """
    Determine if we should use Secret Manager based on environment.
    
    Returns:
        Boolean indicating whether to use Secret Manager
    """
    # Check for App Engine environment
    is_app_engine = os.environ.get('GAE_ENV', '') != ''
    
    # Check for explicit flag
    use_flag = os.environ.get('USE_SECRET_MANAGER', 'false').lower() == 'true'
    
    # Use Secret Manager in App Engine or if explicitly enabled
    return is_app_engine or use_flag