# ~/Desktop/clean-code/app/api/routes/business_data.py

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
from ...business.scrapers import WebsiteScraper, GBPScraper
from ...repositories.business_repository import BusinessRepository
from ...repositories.training_repository import TrainingRepository
from ...business.analytics import CallAnalytics
from ...call_management.call_handler import CallHandler
from ..dependencies import get_current_business_id

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/business",
    tags=["business_data"]
)

# Models
class ScrapeWebsiteRequest(BaseModel):
    url: str

class ScrapeGBPRequest(BaseModel):
    business_name: str
    location: Optional[str] = None

class QAPairRequest(BaseModel):
    question: str
    answer: str

class CallRequest(BaseModel):
    caller_number: str
    caller_name: Optional[str] = None
    forwarded_from: Optional[str] = None
    twilio_sid: str

class SpeechInput(BaseModel):
    call_id: str
    speech_text: str

class EndCallRequest(BaseModel):
    call_id: str
    duration: Optional[int] = None
    recording_url: Optional[str] = None


# Routes
@router.post("/scrape-website", response_model=Dict[str, Any])
async def scrape_website(
    request: ScrapeWebsiteRequest,
    business_id: str = Depends(get_current_business_id)
):
    """Scrape a website for business data"""
    try:
        scraper = WebsiteScraper()
        result = await scraper.scrape_website(business_id, request.url)
        
        # Check for error in result
        if "error" in result:
            # Return a structured error response but with a 200 status code
            return {
                "success": False, 
                "error": result.get("error"), 
                "url": result.get("url", request.url)
            }
            
        return {"success": True, "data": result}
    except Exception as e:
        # Log the exception
        logging.error(f"Error in website scraping endpoint: {str(e)}")
        # Return structured error without raising an exception
        return {
            "success": False,
            "error": str(e),
            "url": request.url
        }

@router.post("/scrape-gbp", response_model=Dict[str, Any])
async def scrape_gbp(
    request: ScrapeGBPRequest,
    business_id: str = Depends(get_current_business_id)
):
    """Scrape Google Business Profile for business data"""
    try:
        scraper = GBPScraper()
        result = await scraper.scrape_gbp(business_id, request.business_name, request.location)
        
        # Check for error in result
        if "error" in result:
            # Return a structured error response but with a 200 status code
            # This allows the frontend to handle the error gracefully
            return {
                "success": False, 
                "error": result.get("error"), 
                "details": result.get("details", ""),
                "business_name": result.get("business_name", request.business_name)
            }
        
        # Return successful response with data
        return {"success": True, "data": result}
    except Exception as e:
        # Log the exception
        logging.error(f"Error in GBP scraping endpoint: {str(e)}")
        # Return structured error
        return {
            "success": False,
            "error": str(e),
            "business_name": request.business_name
        }

@router.get("/training-data", response_model=Dict[str, Any])
async def get_training_data(
    business_id: str = Depends(get_current_business_id),
    source: Optional[str] = None
):
    """Get AI training data for a business"""
    try:
        repo = TrainingRepository()
        
        if source:
            data = await repo.get_training_data(business_id, source)
        else:
            data = await repo.get_combined_training_data(business_id)
            
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/training-data/qa", response_model=Dict[str, Any])
async def add_qa_pair(
    request: QAPairRequest,
    business_id: str = Depends(get_current_business_id)
):
    """Add a Q&A pair to the training data"""
    try:
        repo = TrainingRepository()
        success = await repo.add_qa_pair(business_id, request.question, request.answer)
        
        if success:
            return {"success": True, "message": "Q&A pair added successfully"}
        else:
            return {"success": False, "message": "Failed to add Q&A pair"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/training-data/qa", response_model=Dict[str, Any])
async def delete_qa_pair(
    question: str,
    business_id: str = Depends(get_current_business_id)
):
    """Delete a Q&A pair from the training data"""
    try:
        repo = TrainingRepository()
        success = await repo.delete_qa_pair(business_id, question)
        
        if success:
            return {"success": True, "message": "Q&A pair deleted successfully"}
        else:
            return {"success": False, "message": "Q&A pair not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/call", response_model=Dict[str, Any])
async def handle_call(
    request: CallRequest,
    business_id: str = Depends(get_current_business_id)
):
    """Handle an incoming call"""
    try:
        call_handler = CallHandler()
        
        call_data = {
            "business_id": business_id,
            "caller_number": request.caller_number,
            "caller_name": request.caller_name,
            "forwarded_from": request.forwarded_from,
            "twilio_sid": request.twilio_sid
        }
        
        result = await call_handler.handle_incoming_call(call_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/call/speech", response_model=Dict[str, Any])
async def process_speech(
    request: SpeechInput
):
    """Process user speech in a call"""
    try:
        call_handler = CallHandler()
        result = await call_handler.process_user_speech(request.call_id, request.speech_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/call/end", response_model=Dict[str, Any])
async def end_call(
    request: EndCallRequest
):
    """End a call and generate summary"""
    try:
        call_handler = CallHandler()
        result = await call_handler.end_call(
            request.call_id, 
            request.duration, 
            request.recording_url
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/call-volume", response_model=Dict[str, Any])
async def get_call_volume(
    days: int = Query(30, ge=1, le=365),
    business_id: str = Depends(get_current_business_id)
):
    """Get call volume analytics"""
    try:
        analytics = CallAnalytics()
        result = await analytics.get_call_volume_by_day(business_id, days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/call-duration", response_model=Dict[str, Any])
async def get_call_duration_stats(
    days: int = Query(30, ge=1, le=365),
    business_id: str = Depends(get_current_business_id)
):
    """Get call duration statistics"""
    try:
        analytics = CallAnalytics()
        result = await analytics.get_call_duration_stats(business_id, days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/top-intents", response_model=Dict[str, Any])
async def get_top_intents(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50),
    business_id: str = Depends(get_current_business_id)
):
    """Get top detected intents"""
    try:
        analytics = CallAnalytics()
        result = await analytics.get_top_intents(business_id, days, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/common-entities", response_model=Dict[str, Any])
async def get_common_entities(
    days: int = Query(30, ge=1, le=365),
    business_id: str = Depends(get_current_business_id)
):
    """Get commonly extracted entities"""
    try:
        analytics = CallAnalytics()
        result = await analytics.get_common_entities(business_id, days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/action-metrics", response_model=Dict[str, Any])
async def get_action_metrics(
    days: int = Query(30, ge=1, le=365),
    business_id: str = Depends(get_current_business_id)
):
    """Get call action metrics"""
    try:
        analytics = CallAnalytics()
        result = await analytics.get_call_action_metrics(business_id, days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/keyword-frequency", response_model=Dict[str, Any])
async def get_keyword_frequency(
    days: int = Query(30, ge=1, le=365),
    top_n: int = Query(20, ge=1, le=100),
    business_id: str = Depends(get_current_business_id)
):
    """Get keyword frequency analysis"""
    try:
        analytics = CallAnalytics()
        result = await analytics.get_keyword_frequency(business_id, days, top_n)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/dashboard", response_model=Dict[str, Any])
async def get_dashboard(
    days: int = Query(30, ge=1, le=365),
    business_id: str = Depends(get_current_business_id)
):
    """Get comprehensive dashboard data"""
    try:
        analytics = CallAnalytics()
        result = await analytics.get_business_dashboard(business_id, days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
