from fastapi import FastAPI
from business_profile_service.routes import router as google_business_router
from datetime import datetime
import pymongo

# Import MongoDB connection module (create this file next)
import os
import sys
# Add the project root to the Python path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database.mongodb_simple import connect_to_mongodb, close_mongodb_connection, insert_document, find_document, db

app = FastAPI()

# Register all routers
app.include_router(google_business_router)

@app.on_event("startup")
def startup_db_client():
    connect_to_mongodb()
    print("MongoDB connection initialized on startup")

@app.on_event("shutdown")
def shutdown_db_client():
    close_mongodb_connection()
    print("MongoDB connection closed on shutdown")

@app.get("/")
def read_root():
    return {"status": "online", "service": "AI Phone Service Backend"}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
