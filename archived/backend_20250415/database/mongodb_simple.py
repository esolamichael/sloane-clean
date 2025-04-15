# backend/database/mongodb_simple.py
import os
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_NAME = os.getenv("MONGODB_NAME", "sloane_ai_service")

# Create a singleton client instance
client = None
db = None

def connect_to_mongodb():
    """Connect to MongoDB database."""
    global client, db
    try:
        client = MongoClient(MONGODB_URL)
        db = client[MONGODB_NAME]
        print(f"Connected to MongoDB at {MONGODB_URL} successfully.")
        return db
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise

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
