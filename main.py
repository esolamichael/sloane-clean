from flask import Flask, jsonify, request
import os
import logging
import json
import datetime
import pandas as pd
import pymongo
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from google.cloud import secretmanager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Secret name mapping
SECRET_NAME_MAP = {
    "MONGODB_URL": "mongodb-connection",
    "GOOGLE_MAPS_API_KEY": "google-maps-api-key",
    "TWILIO_AUTH_TOKEN": "twilio-auth-token"
}

# Function to get secrets from Secret Manager
def get_secret(secret_name):
    """Retrieve a secret from Google Cloud Secret Manager."""
    # Use the mapped secret name if available
    actual_secret_name = SECRET_NAME_MAP.get(secret_name, secret_name)
    
    if os.environ.get('USE_SECRET_MANAGER', 'false').lower() == 'true':
        try:
            # Always use the correct project ID
            project_id = 'clean-code-app-1744825963'
            logger.info(f"Using project ID: {project_id}")
                
            # Create the Secret Manager client
            client = secretmanager.SecretManagerServiceClient()
            
            # Access the secret by name
            secret_path = f"projects/{project_id}/secrets/{actual_secret_name}/versions/latest"
            
            logger.info(f"Attempting to access secret: {secret_path}")
            
            # Get the secret value
            response = client.access_secret_version(request={"name": secret_path})
            secret_value = response.payload.data.decode("UTF-8")
            logger.info(f"Successfully retrieved secret: {actual_secret_name} for {secret_name}")
            return secret_value
        except Exception as e:
            logger.error(f"Error accessing Secret Manager for {actual_secret_name} (original: {secret_name}): {str(e)}")
            return os.environ.get(secret_name)
    else:
        # In development, get from environment variable
        return os.environ.get(secret_name)

# Initialize MongoDB connection
def init_mongodb():
    """Initialize MongoDB connection."""
    try:
        # Get MongoDB URL from Secret Manager
        secret_name = "MONGODB_URL"
        mongodb_url = get_secret(secret_name)
        
        if not mongodb_url:
            logger.warning("Could not retrieve MongoDB URL from any Secret Manager secrets")
            
            # Try environment variable as fallback
            mongodb_url = os.environ.get("MONGODB_URL")
            if mongodb_url:
                logger.info("Using MongoDB URL from environment variable")
            else:
                # Last resort fallback for development only
                logger.warning("Using localhost MongoDB URL as last resort fallback")
                mongodb_url = "mongodb://localhost:27017"
        
        # Basic validation of the connection string format
        if mongodb_url and ("mongodb://" in mongodb_url or "mongodb+srv://" in mongodb_url):
            # Mask the connection string for logging (don't log credentials)
            url_parts = mongodb_url.split('@')
            if len(url_parts) > 1:
                masked_url = f"...@{url_parts[1]}"
                logger.info(f"MongoDB connection string format appears valid: {masked_url}")
            else:
                logger.info("MongoDB connection string format appears valid (but couldn't be masked)")
        else:
            logger.error(f"MongoDB connection string doesn't appear to be in the correct format")
        
        # Set as environment variable for database modules to use
        os.environ["MONGODB_URL"] = mongodb_url
        
        # Get database name
        db_name = os.environ.get("MONGODB_NAME", "sloane_ai_service")
        logger.info(f"MongoDB configured with database: {db_name}")
        
        # Try to import and use the MongoDB client to verify connection
        try:
            logger.info("Testing MongoDB connection...")
            from pymongo import MongoClient
            client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
            # Force a connection to verify
            server_info = client.server_info()
            logger.info(f"MongoDB connection test successful! Server version: {server_info.get('version')}")
            client.close()
        except Exception as conn_err:
            logger.error(f"MongoDB connection test failed: {str(conn_err)}")
            logger.warning("Application may have limited functionality due to MongoDB connection issues")
            # Continue anyway - the app should handle failures gracefully
        
        return True
    except Exception as e:
        logger.error(f"Error initializing MongoDB: {str(e)}")
        logger.exception("Detailed exception info for MongoDB initialization:")
        return False

# Initialize API keys
def init_api_keys():
    """Initialize API keys from Secret Manager."""
    try:
        # Get Google Maps API key
        maps_api_key = get_secret("GOOGLE_MAPS_API_KEY")
        if maps_api_key:
            os.environ["GOOGLE_MAPS_API_KEY"] = maps_api_key
            logger.info("Google Maps API key configured successfully")
        else:
            logger.error("Could not retrieve Google Maps API key")
        
        # Get Twilio auth token
        twilio_auth_token = get_secret("TWILIO_AUTH_TOKEN")
        if twilio_auth_token:
            os.environ["TWILIO_AUTH_TOKEN"] = twilio_auth_token
            logger.info("Twilio Auth Token configured successfully")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing API keys: {str(e)}")
        return False

# Create Flask app - ensure this is exposed as 'app' variable for gunicorn
app = Flask(__name__)
print("========== MAIN.PY APPLICATION STARTING ==========")
logger.info("Main.py Flask application initialized")

# Register blueprints for Flask - make this more robust to missing dependencies
# Register routes in blocks, so business_data routes can still work even if analytics fails
business_routes_registered = False

try:
    # Import and register business data routes without the analytics routes
    from app.api.routes.business_data import router as business_router
    app.register_blueprint(business_router)
    business_routes_registered = True
    logger.info("Registered core business data routes successfully")
    
    # Add direct testing routes on the main app
    @app.route('/api/business/test', methods=['GET'])
    def test_business_routes():
        return jsonify({
            "status": "Business routes registered", 
            "endpoints": [
                "/api/business/scrape-website",
                "/api/business/scrape-gbp"
            ]
        })
except Exception as e:
    logger.error(f"Error registering business routes: {str(e)}")

# Initialize MongoDB and API keys before first request
@app.before_request
def before_each_request():
    # In newer Flask versions, before_first_request is deprecated
    # So we use a flag in app.config to ensure initialization runs only once
    if not app.config.get('INITIALIZED', False):
        logger.info("Initializing application on first request")
        init_mongodb()
        init_api_keys()
        app.config['INITIALIZED'] = True

@app.route('/')
def home():
    return jsonify({"status": "online", "service": "Sloane AI Phone Service Backend"})

@app.route('/api/health')
def health_check():
    # Basic health check that doesn't expose environment details
    return jsonify({"status": "healthy"})

# Add a Google Maps API test endpoint
@app.route('/api/maps/test')
def maps_api_test():
    """Test endpoint to verify Google Maps API key is working"""
    maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY', 'Not configured')
    key_is_set = bool(maps_api_key and maps_api_key != 'Not configured')
    
    # Don't return the actual key for security
    return jsonify({
        "status": "Maps API configured" if key_is_set else "Maps API not configured",
        "key_exists": key_is_set
    })

# Add a GBP scraper test endpoint
@app.route('/api/gbp/test')
def gbp_test():
    """Test endpoint to verify GBP scraper is working"""
    try:
        from app.business.scrapers import GBPScraper
        
        # First check if the Google Maps API key is accessible
        api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
        from app.utils.secrets import get_secret
        secret_key = get_secret("GOOGLE_MAPS_API_KEY")
        
        # Log information about the API key availability
        logger.info(f"API Key in environment: {'Yes' if api_key else 'No'}")
        logger.info(f"API Key in Secret Manager: {'Yes' if secret_key else 'No'}")
        
        # Create a scraper instance
        scraper = GBPScraper()
        
        # Log information about the scraper's API key
        logger.info(f"Scraper API key available: {'Yes' if scraper.api_key else 'No'}")
        
        # Test the scraper with a known business
        result = scraper.scrape_gbp("test_business_id", "Starbucks", "San Francisco")
        
        # Add some diagnostic information to the response
        if not result.get("success", False):
            result["diagnostics"] = {
                "env_api_key_available": bool(api_key),
                "secret_manager_key_available": bool(secret_key),
                "scraper_key_available": bool(scraper.api_key)
            }
            
        return jsonify(result)
    except ValueError as e:
        # API key related errors
        logger.error(f"API key error in GBP scraper test: {str(e)}")
        return jsonify({
            "status": "error",
            "error": "Google Maps API key not properly configured",
            "details": str(e),
            "diagnostics": {
                "env_api_key_available": bool(os.environ.get('GOOGLE_MAPS_API_KEY')),
                "secret_manager_key_available": bool(get_secret("GOOGLE_MAPS_API_KEY") if 'get_secret' in locals() else None)
            }
        }), 500
    except Exception as e:
        # Other errors
        logger.error(f"Error testing GBP scraper: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # Initialize in development mode
    if os.environ.get('GAE_ENV', '') != 'standard':
        init_mongodb()
        init_api_keys()
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)