# ~/Desktop/clean-code/app/api/routes/business_data.py

from flask import Blueprint, request, jsonify
from typing import Optional
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

# Create blueprint
router = Blueprint('business_data', __name__, url_prefix='/api/business')

# Routes
@router.route("/scrape-website", methods=['POST'])
async def scrape_website():
    """Scrape a website for business data"""
    try:
        # Get request data
        data = request.get_json()
        url = data.get('url')
        
        # Get business ID from dependency
        business_id = "test_business_id"  # For now, use a test ID until proper auth is implemented
        
        # Check required parameters
        if not url:
            return jsonify({
                "success": False,
                "error": "URL is required"
            }), 400
            
        scraper = WebsiteScraper()
        result = await scraper.scrape_website(business_id, url)
        
        # Check for error in result
        if "error" in result:
            # Return a structured error response but with a 200 status code
            return jsonify({
                "success": False, 
                "error": result.get("error"), 
                "url": result.get("url", url)
            })
            
        return jsonify({"success": True, "data": result})
    except Exception as e:
        # Log the exception
        logging.error(f"Error in website scraping endpoint: {str(e)}")
        # Return structured error without raising an exception
        return jsonify({
            "success": False,
            "error": str(e),
            "url": url if 'url' in locals() else None
        })

@router.route("/scrape-gbp", methods=['POST'])
async def scrape_gbp():
    """Scrape Google Business Profile for business data"""
    try:
        # Get request data
        data = request.get_json()
        business_name = data.get('business_name')
        location = data.get('location')
        
        # Get business ID from dependency
        business_id = "test_business_id"  # For now, use a test ID until proper auth is implemented
        
        # Check required parameters
        if not business_name:
            return jsonify({
                "success": False,
                "error": "Business name is required"
            }), 400
            
        scraper = GBPScraper()
        result = await scraper.scrape_gbp(business_id, business_name, location)
        
        # Check for error in result
        if "error" in result:
            # Return a structured error response with details
            return jsonify({
                "success": False, 
                "error": result.get("error"), 
                "details": result.get("details", ""),
                "business_name": result.get("business_name", business_name)
            })
        
        # Return successful response with data
        return jsonify({"success": True, "data": result})
    except Exception as e:
        # Log the exception
        logging.error(f"Error in GBP scraping endpoint: {str(e)}")
        # Return structured error
        return jsonify({
            "success": False,
            "error": str(e),
            "business_name": business_name if 'business_name' in locals() else None
        })

@router.route("/training-data", methods=['GET'])
async def get_training_data():
    """Get AI training data for a business"""
    try:
        # Get business ID from dependency
        business_id = "test_business_id"  # For now, use a test ID until proper auth is implemented
        source = request.args.get('source')
        
        repo = TrainingRepository()
        
        if source:
            data = await repo.get_training_data(business_id, source)
        else:
            data = await repo.get_combined_training_data(business_id)
            
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/training-data/qa", methods=['POST'])
async def add_qa_pair():
    """Add a Q&A pair to the training data"""
    try:
        # Get request data
        data = request.get_json()
        question = data.get('question')
        answer = data.get('answer')
        
        # Get business ID from dependency
        business_id = "test_business_id"  # For now, use a test ID until proper auth is implemented
        
        # Check required parameters
        if not question or not answer:
            return jsonify({
                "success": False,
                "error": "Question and answer are required"
            }), 400
            
        repo = TrainingRepository()
        success = await repo.add_qa_pair(business_id, question, answer)
        
        if success:
            return jsonify({"success": True, "message": "Q&A pair added successfully"})
        else:
            return jsonify({"success": False, "message": "Failed to add Q&A pair"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/training-data/qa", methods=['DELETE'])
async def delete_qa_pair():
    """Delete a Q&A pair from the training data"""
    try:
        # Get query parameter
        question = request.args.get('question')
        
        # Get business ID from dependency
        business_id = "test_business_id"  # For now, use a test ID until proper auth is implemented
        
        # Check required parameters
        if not question:
            return jsonify({
                "success": False,
                "error": "Question parameter is required"
            }), 400
            
        repo = TrainingRepository()
        success = await repo.delete_qa_pair(business_id, question)
        
        if success:
            return jsonify({"success": True, "message": "Q&A pair deleted successfully"})
        else:
            return jsonify({"success": False, "message": "Q&A pair not found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/call", methods=['POST'])
async def handle_call():
    """Handle an incoming call"""
    try:
        # Get request data
        data = request.get_json()
        caller_number = data.get('caller_number')
        caller_name = data.get('caller_name')
        forwarded_from = data.get('forwarded_from')
        twilio_sid = data.get('twilio_sid')
        
        # Get business ID from dependency
        business_id = "test_business_id"  # For now, use a test ID until proper auth is implemented
        
        # Check required parameters
        if not caller_number or not twilio_sid:
            return jsonify({
                "success": False,
                "error": "Caller number and Twilio SID are required"
            }), 400
            
        call_handler = CallHandler()
        
        call_data = {
            "business_id": business_id,
            "caller_number": caller_number,
            "caller_name": caller_name,
            "forwarded_from": forwarded_from,
            "twilio_sid": twilio_sid
        }
        
        result = await call_handler.handle_incoming_call(call_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/call/speech", methods=['POST'])
async def process_speech():
    """Process user speech in a call"""
    try:
        # Get request data
        data = request.get_json()
        call_id = data.get('call_id')
        speech_text = data.get('speech_text')
        
        # Check required parameters
        if not call_id or not speech_text:
            return jsonify({
                "success": False,
                "error": "Call ID and speech text are required"
            }), 400
            
        call_handler = CallHandler()
        result = await call_handler.process_user_speech(call_id, speech_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/call/end", methods=['POST'])
async def end_call():
    """End a call and generate summary"""
    try:
        # Get request data
        data = request.get_json()
        call_id = data.get('call_id')
        duration = data.get('duration')
        recording_url = data.get('recording_url')
        
        # Check required parameters
        if not call_id:
            return jsonify({
                "success": False,
                "error": "Call ID is required"
            }), 400
            
        call_handler = CallHandler()
        result = await call_handler.end_call(call_id, duration, recording_url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/analytics/call-volume", methods=['GET'])
async def get_call_volume():
    """Get call volume analytics"""
    try:
        # Get query parameter
        days = request.args.get('days', 30, type=int)
        
        # Validate parameters
        days = max(1, min(days, 365))
        
        # Get business ID from dependency
        business_id = "test_business_id"  # For now, use a test ID until proper auth is implemented
        
        analytics = CallAnalytics()
        result = await analytics.get_call_volume_by_day(business_id, days)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/analytics/call-duration", methods=['GET'])
async def get_call_duration_stats():
    """Get call duration statistics"""
    try:
        # Get query parameter
        days = request.args.get('days', 30, type=int)
        
        # Validate parameters
        days = max(1, min(days, 365))
        
        # Get business ID from dependency
        business_id = "test_business_id"  # For now, use a test ID until proper auth is implemented
        
        analytics = CallAnalytics()
        result = await analytics.get_call_duration_stats(business_id, days)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/analytics/top-intents", methods=['GET'])
async def get_top_intents():
    """Get top detected intents"""
    try:
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Validate parameters
        days = max(1, min(days, 365))
        limit = max(1, min(limit, 50))
        
        # Get business ID from dependency
        business_id = "test_business_id"  # For now, use a test ID until proper auth is implemented
        
        analytics = CallAnalytics()
        result = await analytics.get_top_intents(business_id, days, limit)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/analytics/dashboard", methods=['GET'])
async def get_dashboard():
    """Get comprehensive dashboard data"""
    try:
        # Get query parameter
        days = request.args.get('days', 30, type=int)
        
        # Validate parameters
        days = max(1, min(days, 365))
        
        # Get business ID from dependency
        business_id = "test_business_id"  # For now, use a test ID until proper auth is implemented
        
        analytics = CallAnalytics()
        result = await analytics.get_business_dashboard(business_id, days)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500