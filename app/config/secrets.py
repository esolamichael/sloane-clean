"""
Centralized configuration for secrets management.
"""

import os
import logging
from typing import Dict, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Project ID constant
PROJECT_ID = "clean-code-app-1744825963"

# Secret name mappings
SECRET_MAPPINGS = {
    "TWILIO_AUTH_TOKEN": "twilio-auth-token",
    "MONGODB_URL": "mongodb-connection",
    "GOOGLE_MAPS_API_KEY": "google-maps-api-key",
    "OPENAI_API_KEY": "openai-api-key",
    "APP_ENGINE_API_KEY": "APP_ENGINE_API_KEY_SECRET"
}

# Environment variable fallbacks
ENV_FALLBACKS = {
    "TWILIO_AUTH_TOKEN": "TWILIO_AUTH_TOKEN",
    "MONGODB_URL": "MONGODB_URL",
    "GOOGLE_MAPS_API_KEY": "GOOGLE_MAPS_API_KEY",
    "OPENAI_API_KEY": "OPENAI_API_KEY"
}

def get_project_id() -> str:
    """
    Get the GCP project ID.
    
    Returns:
        The project ID as a string
    """
    # Always use the correct project ID
    logger.info(f"Using project ID: {PROJECT_ID}")
    return PROJECT_ID

def get_secret_name(env_name: str) -> Optional[str]:
    """Get the Secret Manager name for an environment variable."""
    return SECRET_MAPPINGS.get(env_name)

def get_env_fallback(env_name: str) -> Optional[str]:
    """Get the environment variable name to fall back to."""
    return ENV_FALLBACKS.get(env_name)

def should_use_secret_manager() -> bool:
    """Determine if we should use Secret Manager based on environment."""
    # Check for App Engine environment
    is_app_engine = os.environ.get('GAE_ENV', '') != ''
    
    # Check for explicit flag
    use_flag = os.environ.get('USE_SECRET_MANAGER', 'false').lower() == 'true'
    
    # Use Secret Manager in App Engine or if explicitly enabled
    return is_app_engine or use_flag 