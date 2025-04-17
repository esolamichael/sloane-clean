# ~/Desktop/clean-code/app/api/routes/business_data.py

from flask import Blueprint, request, jsonify
import logging
from ...business.scrapers import WebsiteScraper, GBPScraper
from ...repositories.business_repository import BusinessRepository
from ...repositories.training_repository import TrainingRepository
from ...business.analytics import CallAnalytics
from ...call_management.call_handler import CallHandler
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
router = Blueprint('business_data', __name__, url_prefix='/api/business')

def get_current_user():
    """Get the current user from the request context."""
    # For now, return a test user until proper auth is implemented
    return {
        'user_id': 'test_user_id',
        'business_id': 'test_business_id'
    }

# Routes
@router.route("/scrape-website", methods=['POST'])
def scrape_website():
    """Scrape business data from a website."""
    try:
        # Get current user for authorization
        current_user = get_current_user()
        
        # Get request data
        data = request.get_json()
        website_url = data.get('website_url')
        
        if not website_url:
            return jsonify({
                "success": False,
                "error": "Website URL is required"
            }), 400
            
        # TODO: Implement website scraping
        return jsonify({
            "success": True,
            "message": "Website scraping not yet implemented"
        })
    except Exception as e:
        logger.error(f"Error in website scraping: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@router.route("/scrape-gbp", methods=['POST'])
def scrape_gbp():
    """Scrape business data from Google Business Profile."""
    try:
        # Get current user for authorization
        current_user = get_current_user()
        
        # Get request data
        data = request.get_json()
        business_name = data.get('business_name')
        location = data.get('location')
        
        if not business_name:
            return jsonify({
                "success": False,
                "error": "Business name is required"
            }), 400
            
        # Create scraper and run it
        scraper = GBPScraper()
        
        # Run the async function with asyncio
        result = asyncio.run(scraper.scrape_gbp(current_user.get('user_id'), business_name, location))
        
        # Check for error in result
        if isinstance(result, dict) and "error" in result:
            return jsonify({
                "success": False,
                "error": result.get("error"),
                "details": result.get("details", "")
            }), 500
            
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        logger.error(f"Error in GBP scraping: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@router.route("/training-data", methods=['GET'])
def get_training_data():
    """Get AI training data for a business"""
    try:
        # Get business ID from dependency
        business_id = "test_business_id"  # For now, use a test ID until proper auth is implemented
        source = request.args.get('source')
        
        repo = TrainingRepository()
        
        if source:
            data = asyncio.run(repo.get_training_data(business_id, source))
        else:
            data = asyncio.run(repo.get_combined_training_data(business_id))
            
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/training-data/qa", methods=['POST'])
def add_qa_pair():
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
        success = asyncio.run(repo.add_qa_pair(business_id, question, answer))
        
        if success:
            return jsonify({"success": True, "message": "Q&A pair added successfully"})
        else:
            return jsonify({"success": False, "message": "Failed to add Q&A pair"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/training-data/qa", methods=['DELETE'])
def delete_qa_pair():
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
        success = asyncio.run(repo.delete_qa_pair(business_id, question))
        
        if success:
            return jsonify({"success": True, "message": "Q&A pair deleted successfully"})
        else:
            return jsonify({"success": False, "message": "Q&A pair not found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/call", methods=['POST'])
def handle_call():
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
        
        # Handle the call
        result = asyncio.run(call_handler.handle_call(call_data))
        
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        logger.error(f"Error handling call: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@router.route("/call/speech", methods=['POST'])
def process_speech():
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
        result = asyncio.run(call_handler.process_user_speech(call_id, speech_text))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/call/end", methods=['POST'])
def end_call():
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
        result = asyncio.run(call_handler.end_call(call_id, duration, recording_url))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/analytics/call-volume", methods=['GET'])
def get_call_volume():
    """Get call volume analytics"""
    try:
        # Get query parameter
        days = request.args.get('days', 30, type=int)
        
        # Validate parameters
        days = max(1, min(days, 365))
        
        # Get business ID from dependency
        business_id = "test_business_id"  # For now, use a test ID until proper auth is implemented
        
        analytics = CallAnalytics()
        result = asyncio.run(analytics.get_call_volume_by_day(business_id, days))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/analytics/call-duration", methods=['GET'])
def get_call_duration_stats():
    """Get call duration statistics"""
    try:
        # Get query parameter
        days = request.args.get('days', 30, type=int)
        
        # Validate parameters
        days = max(1, min(days, 365))
        
        # Get business ID from dependency
        business_id = "test_business_id"  # For now, use a test ID until proper auth is implemented
        
        analytics = CallAnalytics()
        result = asyncio.run(analytics.get_call_duration_stats(business_id, days))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/analytics/top-intents", methods=['GET'])
def get_top_intents():
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
        result = asyncio.run(analytics.get_top_intents(business_id, days, limit))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/analytics/dashboard", methods=['GET'])
def get_dashboard():
    """Get comprehensive dashboard data"""
    try:
        # Get query parameter
        days = request.args.get('days', 30, type=int)
        
        # Validate parameters
        days = max(1, min(days, 365))
        
        # Get business ID from dependency
        business_id = "test_business_id"  # For now, use a test ID until proper auth is implemented
        
        analytics = CallAnalytics()
        result = asyncio.run(analytics.get_business_dashboard(business_id, days))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500