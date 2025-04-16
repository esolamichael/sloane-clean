# mongodb_simple.py
import os
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
import json

# Load environment variables
load_dotenv()

# Get MongoDB connection info - try to load from Secret Manager in production
try:
    # Import the secrets utilities
    from app.utils.secrets import get_mongodb_connection_string, get_project_id, should_use_secret_manager
    
    # Check if we should use Secret Manager
    if should_use_secret_manager():
        # Get MongoDB credentials from Secret Manager
        project_id = get_project_id()
        mongo_conn_string = get_mongodb_connection_string(project_id)
        
        if mongo_conn_string:
            MONGODB_URL = mongo_conn_string
            print("Using MongoDB connection from Secret Manager")
        else:
            # Fall back to environment variable if secret not found
            MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
            print("Failed to load MongoDB URL from Secret Manager, using environment variable")
    else:
        # In development, use environment variables
        MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        print("Using MongoDB connection from environment variables")
except ImportError:
    # If Secret Manager is not available, use environment variables
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    print("Secret Manager not available, using environment variables for MongoDB connection")

# Get MongoDB database name from environment variables
MONGODB_NAME = os.getenv("MONGODB_NAME", "sloane_ai_service")

# Create a singleton client instance
client = None
db = None

def connect_to_mongodb():
    """Connect to MongoDB database."""
    global client, db
    try:
        # Add a connection timeout and retry configuration
        client = MongoClient(
            MONGODB_URL,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            retryWrites=True
        )
        # Test the connection with a server_info() call
        client.server_info()
        db = client[MONGODB_NAME]
        print(f"Connected to MongoDB at {MONGODB_URL} successfully.")
        return db
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        # Don't raise, just log the error
        db = None
        return None

def close_mongodb_connection():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        print("MongoDB connection closed successfully.")

# Basic CRUD operations (synchronous version)
def insert_document(collection_name, document):
    """Insert a document into a collection and return its ID."""
    result = db[collection_name].insert_one(document)
    return str(result.inserted_id)

def find_document(collection_name, query):
    """Find a single document that matches the query."""
    return db[collection_name].find_one(query)

def find_documents(collection_name, query):
    """Find all documents that match the query."""
    return list(db[collection_name].find(query))

def update_document(collection_name, query, update_data):
    """Update documents matching the query with the provided data."""
    result = db[collection_name].update_one(
        query, {"$set": update_data}
    )
    return result.modified_count

def delete_document(collection_name, query):
    """Delete documents matching the query."""
    result = db[collection_name].delete_one(query)
    return result.deleted_count