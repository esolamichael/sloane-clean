# simple_app.py - A simplified app to test the GBP scraper functionality
from flask import Flask, jsonify, request
import pymongo
from bson.objectid import ObjectId
from datetime import datetime
import os
import logging
import json
import requests
from google.cloud import secretmanager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Project ID constant
PROJECT_ID = "clean-code-app-1744825963"

def get_secret(secret_id: str) -> str:
    """
    Get a secret from Google Cloud Secret Manager.
    
    Args:
        secret_id: The ID of the secret to retrieve
        
    Returns:
        The secret value as a string
    """
    try:
        # Always use the correct project ID
        project_id = PROJECT_ID
        logger.info(f"Using project ID: {project_id}")
        
        # Create the Secret Manager client
        client = secretmanager.SecretManagerServiceClient()
        
        # Build the resource name of the secret version
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        
        # Access the secret version
        response = client.access_secret_version(request={"name": name})
        
        # Return the decoded payload
        return response.payload.data.decode("UTF-8")
        
    except Exception as e:
        logger.error(f"Error accessing secret {secret_id}: {str(e)}")
        raise

# Create Flask app
app = Flask(__name__)

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

@app.route('/api/gbp/test')
def test_gbp_scraper():
    """Test the GBP scraper with a known business name"""
    if not maps_api_key:
        return jsonify({"error": "Google Maps API key not configured"}), 500
    
    try:
        business_name = "Starbucks"
        location = "San Francisco"
        
        # Use the Places API to search for the business
        search_query = f"{business_name} {location}"
        search_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={search_query}&key={maps_api_key}"
        
        logger.info(f"Searching for business: {search_query}")
        response = requests.get(search_url)
        response.raise_for_status()
        search_data = response.json()
        
        if search_data.get('status') != 'OK':
            return jsonify({
                "success": False, 
                "error": f"Places API error: {search_data.get('status')}",
                "details": search_data.get('error_message', '')
            }), 500
        
        if not search_data.get('results'):
            return jsonify({
                "success": False,
                "error": "No results found for the business"
            }), 404
        
        # Get the first result
        place = search_data['results'][0]
        place_id = place['place_id']
        
        # Get detailed information
        fields = [
            "name",
            "formatted_address",
            "formatted_phone_number",
            "website",
            "rating",
            "opening_hours"
        ]
        
        details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields={','.join(fields)}&key={maps_api_key}"
        
        logger.info(f"Getting details for place_id: {place_id}")
        response = requests.get(details_url)
        response.raise_for_status()
        details_data = response.json()
        
        if details_data.get('status') != 'OK':
            return jsonify({
                "success": False,
                "error": f"Places API error: {details_data.get('status')}",
                "details": details_data.get('error_message', '')
            }), 500
        
        result = details_data['result']
        
        # Return relevant details
        business_data = {
            'name': result.get('name'),
            'address': result.get('formatted_address'),
            'phone': result.get('formatted_phone_number'),
            'website': result.get('website'),
            'rating': result.get('rating')
        }
        
        return jsonify({
            "success": True,
            "data": business_data,
            "message": "GBP scraper test successful"
        })
    except Exception as e:
        logger.error(f"GBP scraper test error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port)
    finally:
        close_mongodb_connection()
