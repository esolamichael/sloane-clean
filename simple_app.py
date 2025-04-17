# simple_app.py - A simplified app to securely connect to MongoDB and Google Maps API
from flask import Flask, jsonify, request
import pymongo
from bson.objectid import ObjectId
from datetime import datetime
import os
import logging
import json
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Function to get secrets from Secret Manager
def get_secret(secret_name):
    """Retrieve a secret from Google Cloud Secret Manager."""
    if os.environ.get('USE_SECRET_MANAGER', 'false').lower() == 'true':
        try:
            from google.cloud import secretmanager
            
            # Try to get project ID from metadata server
            project_id = None
            try:
                metadata_url = "http://metadata.google.internal/computeMetadata/v1/project/project-id"
                project_id = requests.get(
                    metadata_url, 
                    headers={"Metadata-Flavor": "Google"}
                ).text
                logger.info(f"Retrieved project ID from metadata: {project_id}")
            except Exception as e:
                logger.warning(f"Could not get project ID from metadata server: {str(e)}")
            
            # Create the Secret Manager client
            client = secretmanager.SecretManagerServiceClient()
            
            # Get the secret
            parent = f"projects/{project_id}"
            secret_path = f"{parent}/secrets/{secret_name}/versions/latest"
            
            logger.info(f"Accessing secret: {secret_name}")
            response = client.access_secret_version(request={"name": secret_path})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.error(f"Secret Manager error: {str(e)}")
            return None
    return os.environ.get(secret_name)

# MongoDB client
client = None
db = None

def connect_to_mongodb():
    """Connect to MongoDB database."""
    global client, db
    try:
        # Get MongoDB connection string from Secret Manager or environment
        mongodb_url = get_secret("MONGODB_URL")
        if not mongodb_url:
            logger.warning("Using fallback MongoDB connection")
            mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        
        # Get database name from environment
        mongodb_name = os.getenv("MONGODB_NAME", "sloane_ai_service")
        
        client = pymongo.MongoClient(mongodb_url)
        db = client[mongodb_name]
        logger.info(f"Connected to MongoDB successfully (db: {mongodb_name})")
        return db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        return None

def close_mongodb_connection():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")

# Connect to MongoDB when starting the app
connect_to_mongodb()

# Get Google Maps API key
maps_api_key = get_secret("GOOGLE_MAPS_API_KEY")
if maps_api_key:
    logger.info("Google Maps API key retrieved successfully")
else:
    logger.warning("Google Maps API key not found")

@app.route('/')
def home():
    return jsonify({
        "status": "online", 
        "service": "Sloane AI Phone Service Backend",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "mongodb_connected": db is not None,
        "google_maps_api": maps_api_key is not None,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/mongo/test')
def test_mongo():
    if not db:
        return jsonify({"error": "MongoDB not connected"}), 500
        
    try:
        # Insert a test document
        doc = {"test": "data", "timestamp": str(datetime.now())}
        result = db["test_collection"].insert_one(doc)
        doc_id = str(result.inserted_id)
        
        # Retrieve the document
        retrieved_doc = db["test_collection"].find_one({"_id": ObjectId(doc_id)})
        
        # Convert ObjectId to string for JSON serialization
        retrieved_doc["_id"] = str(retrieved_doc["_id"])
        
        return jsonify({
            "message": "MongoDB test successful", 
            "document": retrieved_doc
        })
    except Exception as e:
        logger.error(f"MongoDB test error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/maps/test')
def test_maps_api():
    if not maps_api_key:
        return jsonify({"error": "Google Maps API key not configured"}), 500
    
    try:
        # Test a simple Places API call
        location = "New York"
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={location}&key={maps_api_key}"
        
        response = requests.get(url)
        data = response.json()
        
        # Return only status and result count for security
        return jsonify({
            "message": "Google Maps API test successful",
            "status": data.get("status"),
            "results_count": len(data.get("results", [])),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Google Maps API test error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port)
    finally:
        close_mongodb_connection()
