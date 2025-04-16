# test_server.py - A minimal mocked server for testing
from fastapi import FastAPI, Header, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
from pydantic import BaseModel
import uvicorn
import logging
import json
import os
from datetime import datetime, timedelta
import random

# Set Google Maps API key for local testing
os.environ["GOOGLE_MAPS_API_KEY"] = "AIzaSyAVQNhMwjrnWGmwFZTQvVMBHgdB_IGdZt4"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create app
app = FastAPI(title="Mock Test API Server", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ScrapeWebsiteRequest(BaseModel):
    url: str

class ScrapeGBPRequest(BaseModel):
    business_name: str
    location: Optional[str] = None

class CallRequest(BaseModel):
    caller_number: str
    twilio_sid: str
    caller_name: Optional[str] = None
    forwarded_from: Optional[str] = None

# Helper function for dependency
async def get_current_business_id(x_business_id: Optional[str] = Header(None)):
    """
    Get the current business ID from the request header.
    For test implementation, we'll accept any header or use a test ID.
    """
    if not x_business_id:
        return "test-business-123"
    return x_business_id

@app.get("/")
def read_root():
    return {"status": "online", "service": "Mock Test API Server"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

# --- Mock API endpoints ---

@app.post("/api/business/scrape-website")
async def scrape_website(
    request: ScrapeWebsiteRequest,
    business_id: str = Depends(get_current_business_id)
):
    """Mock scrape a website for business data"""
    logger.info(f"Scraping website: {request.url} for business_id: {business_id}")
    
    # Return mock data
    return {
        "success": True,
        "data": {
            "business_id": business_id,
            "source": "website",
            "url": request.url,
            "title": "Sample Business Name",
            "description": "A sample business description for testing purposes",
            "services": ["Service 1", "Service 2", "Service 3"],
            "contact_info": {
                "email": ["contact@example.com"],
                "phone": ["(555) 123-4567"],
                "address": "123 Business St, Sample City, CA 94000"
            },
            "hours": {
                "monday": "9:00 AM - 5:00 PM",
                "tuesday": "9:00 AM - 5:00 PM",
                "wednesday": "9:00 AM - 5:00 PM",
                "thursday": "9:00 AM - 5:00 PM",
                "friday": "9:00 AM - 5:00 PM",
                "saturday": "10:00 AM - 3:00 PM",
                "sunday": "Closed"
            }
        }
    }

@app.post("/api/business/scrape-gbp")
async def scrape_gbp(
    request: ScrapeGBPRequest,
    business_id: str = Depends(get_current_business_id)
):
    """Mock scrape Google Business Profile for business data"""
    logger.info(f"Scraping GBP for: {request.business_name} in {request.location or 'any location'} for business_id: {business_id}")
    
    # For test server, we'll always use our real GBP scraper implementation to test
    try:
        # Import the real GBPScraper
        import sys
        import os
        
        # Add parent directory to system path if needed
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.append(current_dir)
        
        from app.business.scrapers import GBPScraper
        
        # Create scraper instance
        scraper = GBPScraper()
        
        # Scrape with real implementation
        result = await scraper.scrape_gbp(business_id, request.business_name, request.location)
        
        # Return the result directly (which could be an error or real data)
        if "error" in result:
            return {
                "success": False, 
                "error": result.get("error"),
                "details": result.get("details", "")
            }
        else:
            return {
                "success": True,
                "data": result
            }
    except Exception as e:
        logger.error(f"Error in test server GBP scraping: {str(e)}")
        
        # Return mock data as fallback
        return {
            "success": True,
            "data": {
                "business_id": business_id,
                "source": "gbp",
                "name": request.business_name,
                "formatted_address": f"123 Business St, {request.location or 'Sample City'}, CA 94000",
                "phone": "(555) 123-4567",
                "website": f"https://www.{request.business_name.lower().replace(' ', '')}.com",
                "rating": 4.5,
                "reviews_count": 42,
                "categories": ["Service Business", "Local Business"],
                "opening_hours": {
                    "monday": { "isOpen": True, "openTime": "9:00 AM", "closeTime": "5:00 PM" },
                    "tuesday": { "isOpen": True, "openTime": "9:00 AM", "closeTime": "5:00 PM" },
                    "wednesday": { "isOpen": True, "openTime": "9:00 AM", "closeTime": "5:00 PM" },
                    "thursday": { "isOpen": True, "openTime": "9:00 AM", "closeTime": "5:00 PM" },
                    "friday": { "isOpen": True, "openTime": "9:00 AM", "closeTime": "5:00 PM" },
                    "saturday": { "isOpen": True, "openTime": "10:00 AM", "closeTime": "3:00 PM" },
                    "sunday": { "isOpen": False, "openTime": "", "closeTime": "" }
                },
                "services": [
                    { "name": "Service 1", "description": "Description of service 1", "price": "Contact for pricing" },
                    { "name": "Service 2", "description": "Description of service 2", "price": "Contact for pricing" },
                    { "name": "Service 3", "description": "Description of service 3", "price": "Contact for pricing" }
                ]
            }
        }

@app.get("/api/business/training-data")
async def get_training_data(
    business_id: str = Depends(get_current_business_id),
    source: Optional[str] = None
):
    """Mock get AI training data for a business"""
    logger.info(f"Getting training data for business_id: {business_id}, source: {source}")
    
    # Return mock data
    return {
        "success": True,
        "data": {
            "business_id": business_id,
            "business_name": "Sample Business",
            "business_description": "A sample business for testing purposes",
            "services": ["Service 1", "Service 2", "Service 3"],
            "hours": {
                "monday": "9:00 AM - 5:00 PM",
                "tuesday": "9:00 AM - 5:00 PM",
                "wednesday": "9:00 AM - 5:00 PM",
                "thursday": "9:00 AM - 5:00 PM",
                "friday": "9:00 AM - 5:00 PM",
                "saturday": "10:00 AM - 3:00 PM",
                "sunday": "Closed"
            },
            "contact_info": {
                "email": ["contact@example.com"],
                "phone": ["(555) 123-4567"],
                "address": "123 Business St, Sample City, CA 94000"
            },
            "example_qa": [
                {
                    "question": "What are your hours?",
                    "answer": "We're open 9:00 AM - 5:00 PM Monday through Friday, 10:00 AM - 3:00 PM on Saturday, and closed on Sunday."
                },
                {
                    "question": "Do you offer Service 1?",
                    "answer": "Yes, we offer Service 1."
                },
                {
                    "question": "What's your phone number?",
                    "answer": "You can reach us at (555) 123-4567."
                }
            ]
        }
    }

@app.post("/api/business/call")
async def handle_call(
    request: CallRequest,
    business_id: str = Depends(get_current_business_id)
):
    """Mock handle an incoming call"""
    logger.info(f"Handling call from {request.caller_number} for business_id: {business_id}")
    
    # Return mock data
    return {
        "success": True,
        "call_id": "call_" + str(random.randint(10000, 99999)),
        "business_id": business_id,
        "caller_number": request.caller_number,
        "greeting": "Thank you for calling Sample Business. How can I help you today?",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/business/analytics/dashboard")
async def get_dashboard(
    days: int = Query(30, ge=1, le=365),
    business_id: str = Depends(get_current_business_id)
):
    """Mock comprehensive dashboard data"""
    logger.info(f"Getting dashboard for business_id: {business_id}, days: {days}")
    
    # Generate dates for the past N days
    today = datetime.now().date()
    dates = [(today - timedelta(days=i)).isoformat() for i in range(days)]
    
    # Generate random call volumes
    call_volumes = [random.randint(3, 15) for _ in range(days)]
    
    # Generate random intent distribution
    intents = ["booking", "hours", "pricing", "location", "services"]
    intent_counts = {intent: random.randint(10, 50) for intent in intents}
    total_intents = sum(intent_counts.values())
    intent_percentages = {k: round(v / total_intents * 100, 1) for k, v in intent_counts.items()}
    
    # Return mock data
    return {
        "success": True,
        "business_id": business_id,
        "period_days": days,
        "total_calls": sum(call_volumes),
        "call_volume_by_date": dict(zip(dates, call_volumes)),
        "avg_call_duration": random.randint(120, 300),
        "top_intents": intent_percentages,
        "call_outcomes": {
            "resolved": random.randint(60, 90),
            "transferred": random.randint(5, 20),
            "voicemail": random.randint(5, 20)
        },
        "peak_call_times": {
            "day_of_week": "Monday",
            "time_of_day": "10:00 AM - 12:00 PM"
        }
    }

if __name__ == "__main__":
    # Use port 8000 for testing
    port = 8000
    
    # Run the application
    logger.info(f"Starting mock test server on port {port}")
    uvicorn.run("test_server:app", host="0.0.0.0", port=port, reload=True)