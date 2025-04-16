from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from datetime import datetime
import uvicorn
import logging
import pymongo
import os
import sys

# Add the project root to the Python path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import MongoDB connection module
from mongodb_simple import connect_to_mongodb, close_mongodb_connection, insert_document, find_document, db

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create app
app = FastAPI(title="Sloane AI Phone Service", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Changed to False to work with allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-Business-ID", "Accept"]
)

# Include existing routers
try:
    from business_profile_service.routes import router as google_business_router
    app.include_router(google_business_router)
except ImportError:
    print("Business profile service routes not found")

# Include new routers if they exist
try:
    # Only include these if the modules exist
    # If they don't exist yet, the app will still run without them
    from app.api.routes import auth, businesses, calls, users, twilio
    app.include_router(auth.router)
    app.include_router(businesses.router)
    app.include_router(calls.router)
    app.include_router(users.router)
    app.include_router(twilio.router)

    # Include our new business data router
    from app.api.routes.business_data import router as business_data_router
    app.include_router(business_data_router)
    
    logger.info("Successfully loaded new API routes")
except ImportError as e:
    # Log the import error but continue
    logger.warning(f"Could not import some new modules: {e}")
    logger.warning("Some new features may not be available until directory structure is updated")

# Mount static files if directories exist
if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    
if os.path.exists("sloane-frontend-package/build"):
    app.mount("/frontend", StaticFiles(directory="sloane-frontend-package/build"), name="frontend")

@app.on_event("startup")
def startup_db_client():
    connect_to_mongodb()
    logger.info("MongoDB connection initialized on startup")
    
@app.on_event("shutdown")
def shutdown_db_client():
    close_mongodb_connection()
    logger.info("MongoDB connection closed on shutdown")

@app.get("/")
def read_root():  
    return {"status": "online", "service": "Sloane AI Phone Service Backend"}

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "mongodb_connected": db is not None
    }

@app.get("/api/mongo/test")
def test_mongo():
    # Insert a test document
    doc_id = insert_document("test_collection", {"test": "data", "timestamp": str(datetime.now())})
    # Retrieve the document
    doc = find_document("test_collection", {"_id": pymongo.ObjectId(doc_id)})
    return {"message": "MongoDB test successful", "document": str(doc)}

@app.get("/api/twilio/webhook")
def twilio_webhook():
    return {"message": "Twilio webhook endpoint"}

@app.get("/api/calendar/availability")
def calendar_availability():
    return {"message": "Calendar availability endpoint"}

@app.middleware("http")
async def cors_and_log_middleware(request: Request, call_next):
    """Add CORS headers and log requests"""
    # Log the request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Handle CORS preflight requests
    if request.method == "OPTIONS":
        # Create a response with appropriate CORS headers
        from fastapi.responses import JSONResponse
        response = JSONResponse(
            content={"message": "CORS preflight handled"},
            status_code=200,
        )
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, X-Business-ID, Accept'
        response.headers['Access-Control-Max-Age'] = '86400'  # 24 hours cache for preflight requests
        return response
    
    # Continue with normal request
    response = await call_next(request)
    
    # Add CORS headers to all responses
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    
    return response

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))
    
    # Run the application
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
