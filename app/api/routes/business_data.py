# ~/Desktop/clean-code/app/api/routes/business_data.py

from flask import Blueprint, request, jsonify
import logging
from ...business.scrapers import WebsiteScraper, GBPScraper
from ...repositories.business_repository import BusinessRepository
from ...repositories.training_repository import TrainingRepository
from ...business.analytics import CallAnalytics
from ...call_management.call_handler import CallHandler

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
router = Blueprint('business_data', __name__, url_prefix='/api/business')

def get_current_user():
    """Get the current user from the request context."""
    return {
        'user_id': 'test_user_id',
        'business_id': 'test_business_id'
    }

@router.route("/scrape-website", methods=['POST'])
def scrape_website():
    try:
        current_user = get_current_user()
        data = request.get_json()
        website_url = data.get('website_url')
        
        if not website_url:
            return jsonify({
                "success": False,
                "error": "Website URL is required"
            }), 400
            
        scraper = WebsiteScraper()
        result = scraper.scrape_website(current_user['business_id'], website_url)
        
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        logger.error(f"Error in website scraping: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@router.route("/scrape-gbp", methods=['POST'])
def scrape_gbp():
    try:
        current_user = get_current_user()
        data = request.get_json()
        business_name = data.get('business_name')
        location = data.get('location')
        
        if not business_name:
            return jsonify({
                "success": False,
                "error": "Business name is required"
            }), 400
            
        logger.info(f"Starting GBP scrape for business name: {business_name}, location: {location}")
        scraper = GBPScraper()
        result = scraper.scrape_gbp(current_user['business_id'], business_name, location)
        
        # The scraper already returns a dict with success/error fields
        if not result.get("success", False):
            logger.error(f"GBP scraper returned an error: {result.get('error')}")
            return jsonify(result), 500
            
        logger.info(f"GBP scrape successful for business name: {business_name}")
        return jsonify(result)
    except ValueError as e:
        # Specifically catch the error related to missing API key
        logger.error(f"API key error in GBP scraping: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Google Maps API key not properly configured",
            "details": str(e)
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error in GBP scraping: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500

@router.route("/training-data", methods=['GET'])
def get_training_data():
    try:
        business_id = "test_business_id"
        source = request.args.get('source')
        
        repo = TrainingRepository()
        
        if source:
            data = repo.get_training_data(business_id, source)
        else:
            data = repo.get_combined_training_data(business_id)
            
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/training-data/qa", methods=['POST'])
def add_qa_pair():
    try:
        data = request.get_json()
        question = data.get('question')
        answer = data.get('answer')
        business_id = "test_business_id"
        
        if not question or not answer:
            return jsonify({
                "success": False,
                "error": "Question and answer are required"
            }), 400
            
        repo = TrainingRepository()
        success = repo.add_qa_pair(business_id, question, answer)
        
        if success:
            return jsonify({"success": True, "message": "Q&A pair added successfully"})
        else:
            return jsonify({"success": False, "message": "Failed to add Q&A pair"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/training-data/qa", methods=['DELETE'])
def delete_qa_pair():
    try:
        question = request.args.get('question')
        business_id = "test_business_id"
        
        if not question:
            return jsonify({
                "success": False,
                "error": "Question parameter is required"
            }), 400
            
        repo = TrainingRepository()
        success = repo.delete_qa_pair(business_id, question)
        
        if success:
            return jsonify({"success": True, "message": "Q&A pair deleted successfully"})
        else:
            return jsonify({"success": False, "message": "Q&A pair not found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/call", methods=['POST'])
def handle_call():
    try:
        data = request.get_json()
        caller_number = data.get('caller_number')
        caller_name = data.get('caller_name')
        forwarded_from = data.get('forwarded_from')
        twilio_sid = data.get('twilio_sid')
        business_id = "test_business_id"
        
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
        
        result = call_handler.handle_incoming_call(call_data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error handling call: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@router.route("/call/<call_id>/speech", methods=['POST'])
def process_speech(call_id):
    try:
        data = request.get_json()
        speech_text = data.get('speech_text')
        
        if not speech_text:
            return jsonify({
                "success": False,
                "error": "Speech text is required"
            }), 400
            
        call_handler = CallHandler()
        result = call_handler.process_user_speech(call_id, speech_text)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error processing speech: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@router.route("/call/<call_id>/end", methods=['POST'])
def end_call(call_id):
    try:
        data = request.get_json()
        duration = data.get('duration')
        recording_url = data.get('recording_url')
        
        call_handler = CallHandler()
        result = call_handler.end_call(call_id, duration, recording_url)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error ending call: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@router.route("/analytics/call-volume", methods=['GET'])
def get_call_volume():
    try:
        business_id = "test_business_id"
        days = int(request.args.get('days', 30))
        
        analytics = CallAnalytics()
        result = analytics.get_call_volume_by_day(business_id, days)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/analytics/duration-stats", methods=['GET'])
def get_call_duration_stats():
    try:
        business_id = "test_business_id"
        days = int(request.args.get('days', 30))
        
        analytics = CallAnalytics()
        result = analytics.get_call_duration_stats(business_id, days)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/analytics/top-intents", methods=['GET'])
def get_top_intents():
    try:
        business_id = "test_business_id"
        days = int(request.args.get('days', 30))
        limit = int(request.args.get('limit', 10))
        
        analytics = CallAnalytics()
        result = analytics.get_top_intents(business_id, days, limit)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/analytics/common-entities", methods=['GET'])
def get_common_entities():
    try:
        business_id = "test_business_id"
        days = int(request.args.get('days', 30))
        
        analytics = CallAnalytics()
        result = analytics.get_common_entities(business_id, days)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/analytics/action-metrics", methods=['GET'])
def get_action_metrics():
    try:
        business_id = "test_business_id"
        days = int(request.args.get('days', 30))
        
        analytics = CallAnalytics()
        result = analytics.get_call_action_metrics(business_id, days)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/analytics/keyword-frequency", methods=['GET'])
def get_keyword_frequency():
    try:
        business_id = "test_business_id"
        days = int(request.args.get('days', 30))
        top_n = int(request.args.get('top_n', 10))
        
        analytics = CallAnalytics()
        result = analytics.get_keyword_frequency(business_id, days, top_n)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@router.route("/analytics/dashboard", methods=['GET'])
def get_dashboard():
    try:
        business_id = "test_business_id"
        days = int(request.args.get('days', 30))
        
        analytics = CallAnalytics()
        result = analytics.get_business_dashboard(business_id, days)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500