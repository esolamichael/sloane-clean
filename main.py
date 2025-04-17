from flask import Flask, jsonify, request
import os
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to get secrets from Secret Manager
def get_secret(secret_name):
    """Retrieve a secret from Google Cloud Secret Manager."""
    if os.environ.get('USE_SECRET_MANAGER', 'false').lower() == 'true':
        try:
            from google.cloud import secretmanager
            
            # Try to get project ID from metadata server
            project_id = None
            try:
                import requests
                metadata_url = "http://metadata.google.internal/computeMetadata/v1/project/project-id"
                project_id = requests.get(
                    metadata_url, 
                    headers={"Metadata-Flavor": "Google"}
                ).text
                logger.info(f"Retrieved project ID from metadata: {project_id}")
            except Exception as e:
                logger.warning(f"Could not get project ID from metadata server: {str(e)}")
            
            # If metadata doesn't work, try to get from App Engine environment
            if not project_id:
                project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'clean-code-app-1744825963')
                logger.info(f"Using project ID from environment: {project_id}")
                
            # Create the Secret Manager client
            client = secretmanager.SecretManagerServiceClient()
            
            # Access the secret by name
            secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
            
            logger.info(f"Attempting to access secret: {secret_path}")
            
            # Get the secret value
            response = client.access_secret_version(request={"name": secret_path})
            secret_value = response.payload.data.decode("UTF-8")
            logger.info(f"Successfully retrieved secret: {secret_name}")
            return secret_value
        except Exception as e:
            logger.error(f"Error accessing Secret Manager for {secret_name}: {str(e)}")
            return os.environ.get(secret_name)
    else:
        # In development, get from environment variable
        return os.environ.get(secret_name)

# Initialize MongoDB connection
def init_mongodb():
    """Initialize MongoDB connection using Secret Manager."""
    try:
        # Get MongoDB connection string from Secret Manager
        mongodb_url = get_secret("MONGODB_URL")
        
        if not mongodb_url:
            logger.warning("Could not retrieve MongoDB URL from Secret Manager or environment variables")
            mongodb_url = "mongodb://localhost:27017"  # Fallback for development
        
        # Set as environment variable for database modules to use
        os.environ["MONGODB_URL"] = mongodb_url
        
        # Get database name
        db_name = os.environ.get("MONGODB_NAME", "sloane_ai_service")
        logger.info(f"MongoDB configured with database: {db_name}")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing MongoDB: {str(e)}")
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

# Create Flask app
app = Flask(__name__)

# Register blueprints for Flask
try:
    from app.api.routes.business_data import router as business_router
    app.register_blueprint(business_router)
    logger.info("Registered business data routes")
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

if __name__ == '__main__':
    # Initialize in development mode
    if os.environ.get('GAE_ENV', '') != 'standard':
        init_mongodb()
        init_api_keys()
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)