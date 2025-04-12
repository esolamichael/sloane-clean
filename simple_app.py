# simple_app.py - A simplified app without FastAPI to test MongoDB
from flask import Flask, jsonify
import pymongo
from bson.objectid import ObjectId  # Add this import for ObjectId
from datetime import datetime
import os

app = Flask(__name__)

# MongoDB connection information
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_NAME = os.getenv("MONGODB_NAME", "sloane_ai_service")

# MongoDB client
client = None
db = None

def connect_to_mongodb():
    """Connect to MongoDB database."""
    global client, db
    try:
        client = pymongo.MongoClient(MONGODB_URL)
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

# Connect to MongoDB when starting the app
connect_to_mongodb()

@app.route('/')
def home():
    return jsonify({"status": "online", "service": "AI Phone Service Backend"})

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "mongodb_connected": db is not None
    })

@app.route('/api/mongo/test')
def test_mongo():
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

if __name__ == '__main__':
    try:
        app.run(debug=True, port=8000)
    finally:
        close_mongodb_connection()
