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

def get_secret(secret_id: str, project_id: str = PROJECT_ID) -> str:
    """
    Get a secret from Google Cloud Secret Manager.
    
    Args:
        secret_id: The ID of the secret to retrieve
        project_id: The GCP project ID (defaults to clean-code-app-1744825963)
        
    Returns:
        The secret value as a string
    """
    try:
        # Create the Secret Manager client
        client = secretmanager.SecretManagerServiceClient()
        
        # Build the resource name of the secret version
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        
        # Access the secret version
        response = client.access_secret_version(request={"name": name})
        
        # Return the decoded payload
        return response.payload.data.decode("UTF-8")
        
    except exceptions.PermissionDenied:
        logger.error(f"Permission denied when accessing secret {secret_id}")
        raise
    except exceptions.NotFound:
        logger.error(f"Secret {secret_id} not found in project {project_id}")
        raise
    except Exception as e:
        logger.error(f"Error accessing secret {secret_id}: {str(e)}")
        raise


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
        secret_payload = get_secret(secret_id, project_id)
        
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
        return get_secret("mongodb-connection", project_id)
    except Exception as e:
        logger.error(f"Error getting MongoDB connection string: {e}")
        raise


def get_twilio_auth_token(project_id: str, secret_id: str = "twilio-auth-token") -> str:
    """
    Get Twilio auth token from Secret Manager.
    
    Args:
        project_id: The GCP project ID
        secret_id: The secret ID storing the Twilio auth token
        
    Returns:
        The Twilio auth token
    """
    try:
        return get_secret(secret_id, project_id)
    except Exception as e:
        print(f"Error getting Twilio auth token: {e}")
        # Return empty string if error
        return ""


def get_project_id() -> str:
    """
    Get the GCP project ID from environment variable or App Engine environment.
    
    Returns:
        The project ID as a string
    """
    # First try to get from environment variable
    project_id = os.environ.get('GCP_PROJECT')
    
    # If not set, try to get from App Engine environment
    if not project_id:
        # On App Engine, project ID is available in the environment
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    
    # If still not found, use the one from your configuration
    if not project_id:
        project_id = PROJECT_ID
    
    return project_id


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