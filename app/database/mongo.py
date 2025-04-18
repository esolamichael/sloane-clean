# app/database/mongo.py
import os
import logging
import certifi
from flask import current_app, g
from pymongo import MongoClient
from bson.objectid import ObjectId
from app.utils.secrets import get_secret

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    """
    Configure the MongoDB connection and return the database.
    Uses Google Cloud Secret Manager for the connection string.
    """
    if 'db' not in g:
        try:
            # Use the project ID from secrets.py
            from ..utils.secrets import PROJECT_ID
            logger.info(f"Using project ID: {PROJECT_ID}")
            
            # Get the connection string from Secret Manager
            mongodb_url = get_secret("MONGODB_URL")
            
            if not mongodb_url:
                logger.error("Failed to get MongoDB connection string")
                raise ConnectionError("Could not retrieve MongoDB connection string")
                
            logger.info("Successfully retrieved MongoDB connection string")
            
            # Get database name from environment
            db_name = os.getenv("MONGODB_NAME", "sloane_ai_service")
            
            # Create client with timeout settings and SSL certificate verification
            g.client = MongoClient(
                mongodb_url,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                retryWrites=True,
                tlsCAFile=certifi.where()  # Use certifi for SSL certificate verification
            )
            
            # Test the connection
            g.client.server_info()
            
            # Set up the database
            g.db = g.client[db_name]
            
            # Create indexes
            _ensure_indexes(g.db)
            
            logger.info(f"Successfully connected to MongoDB database: {db_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    return g.db

def _ensure_indexes(db):
    """Create necessary indexes for collections."""
    try:
        # Add indexes for business profiles
        db.business_profiles.create_index("business_id", unique=True)
        
        # Add indexes for GBP scraping data
        db.gbp_data.create_index("business_id")
        db.gbp_data.create_index("scraped_at")
        
        # Add indexes for call transcripts
        db.call_transcripts.create_index("call_id", unique=True)
        db.call_transcripts.create_index("business_id")
        db.call_transcripts.create_index("timestamp")
        
        logger.info("MongoDB indexes created/verified successfully")
    except Exception as e:
        logger.error(f"Failed to create MongoDB indexes: {str(e)}")

def close_db(e=None):
    """Close the MongoDB connection."""
    client = g.pop('client', None)
    if client is not None:
        client.close()
        logger.info("MongoDB connection closed")

def init_app(app):
    """
    Initialize MongoDB with the Flask app.
    """
    app.teardown_appcontext(close_db)

def get_mongo_client():
    """Get MongoDB client instance."""
    if 'client' not in g:
        try:
            # Get MongoDB connection string from Secret Manager or environment
            mongodb_url = get_secret("MONGODB_URL")
            if not mongodb_url:
                logger.error("Failed to get MongoDB connection string")
                raise ConnectionError("Could not retrieve MongoDB connection string")
                
            g.client = MongoClient(
                mongodb_url, 
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                retryWrites=True,
                tlsCAFile=certifi.where()  # Use certifi for SSL certificate verification
            )
            
            # Test the connection
            g.client.server_info()
            logger.info("MongoDB client connection successful")
        except Exception as e:
            logger.error(f"Error creating MongoDB client: {str(e)}")
            raise
    
    return g.client
