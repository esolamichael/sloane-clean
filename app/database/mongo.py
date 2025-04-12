# app/database/mongo.py
import os
from flask import current_app, g
from pymongo import MongoClient
from bson.objectid import ObjectId

def get_db():
    """
    Configure the MongoDB connection and return the database.
    """
    if 'db' not in g:
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_NAME", "sloane_ai_service")
        
        g.client = MongoClient(mongodb_url)
        g.db = g.client[db_name]
        
        # Create indexes if they don't exist
        _ensure_indexes(g.db)
        
    return g.db

def close_db(e=None):
    """
    Close the MongoDB connection.
    """
    client = g.pop('client', None)
    if client is not None:
        client.close()

def _ensure_indexes(db):
    """
    Create necessary indexes for our collections.
    """
    # User collection indexes
    db.users.create_index("email", unique=True)
    
    # Business collection indexes
    db.businesses.create_index("owner_id")
    
    # Call transcripts collection indexes
    db.call_transcripts.create_index([("full_transcript", "text")])
    db.call_transcripts.create_index("business_id")
    
    # Business data collection indexes
    db.website_data.create_index("business_id")
    db.google_business_profiles.create_index("business_id", unique=True)

def init_app(app):
    """
    Initialize MongoDB with the Flask app.
    """
    app.teardown_appcontext(close_db)
