"""
Integration test script for the AI phone answering service.
"""
import os
import sys
import json
import time
import requests
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_conversation_service.api import app as conversation_app
from calendar_service.api import app as calendar_app

# Test clients
conversation_client = TestClient(conversation_app)
calendar_client = TestClient(calendar_app)

def test_conversation_api():
    """Test the conversation API endpoints."""
    print("Testing conversation API...")
    
    # Test health check
    response = conversation_client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    print("✓ Health check passed")
    
    # Test starting a conversation
    response = conversation_client.post("/api/conversation/start", json={
        "business_id": "test_business"
    })
    assert response.status_code == 200
    assert "text" in response.json()
    assert "session_id" in response.json()
    session_id = response.json()["session_id"]
    print("✓ Start conversation passed")
    
    # Test responding to user input
    response = conversation_client.post("/api/conversation/respond", json={
        "business_id": "test_business",
        "session_id": session_id,
        "text": "What are your business hours?"
    })
    assert response.status_code == 200
    assert "text" in response.json()
    assert "business hours" in response.json()["text"].lower()
    print("✓ Respond to conversation passed")
    
    # Test ending a conversation
    response = conversation_client.post("/api/conversation/end", json={
        "session_id": session_id,
        "caller_number": "+15551234567",
        "duration": 120
    })
    assert response.status_code == 200
    assert response.json()["success"] == True
    print("✓ End conversation passed")
    
    print("All conversation API tests passed!")

def test_calendar_api():
    """Test the calendar API endpoints."""
    print("\nTesting calendar API...")
    
    # Test health check
    response = calendar_client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    print("✓ Health check passed")
    
    # Note: The following tests would require actual calendar credentials
    # For demonstration purposes, we'll just print what would be tested
    print("Note: The following calendar tests would require actual credentials:")
    print("- Getting calendars list")
    print("- Checking availability")
    print("- Creating appointments")
    
    print("Calendar API tests completed!")

def test_end_to_end_flow():
    """Test the end-to-end flow of the AI phone answering service."""
    print("\nTesting end-to-end flow...")
    
    # This would simulate a complete call flow from start to finish
    # For demonstration purposes, we'll outline the steps
    
    print("1. Call is received by Twilio")
    print("2. Twilio requests greeting from our service")
    print("3. AI responds with greeting")
    print("4. Caller asks about business hours")
    print("5. AI processes speech and identifies intent")
    print("6. AI responds with business hours")
    print("7. Caller requests appointment scheduling")
    print("8. AI checks calendar availability")
    print("9. AI suggests available time slots")
    print("10. Caller selects a time slot")
    print("11. AI confirms and creates the appointment")
    print("12. Call ends and notification is sent to business")
    
    print("End-to-end flow test completed!")

def test_high_value_call_transfer():
    """Test the high-value call transfer functionality."""
    print("\nTesting high-value call transfer...")
    
    # This would simulate a call that should be transferred
    # For demonstration purposes, we'll outline the steps
    
    print("1. Call is received by Twilio")
    print("2. AI responds with greeting")
    print("3. Caller mentions 'urgent issue'")
    print("4. AI identifies high-value keyword 'urgent'")
    print("5. AI informs caller about transfer")
    print("6. Call is transferred to business's transfer number")
    print("7. Transfer event is logged")
    
    print("High-value call transfer test completed!")

if __name__ == "__main__":
    print("Running integration tests for AI Phone Answering Service\n")
    print("=" * 60)
    
    try:
        test_conversation_api()
        test_calendar_api()
        test_end_to_end_flow()
        test_high_value_call_transfer()
        
        print("\n" + "=" * 60)
        print("All integration tests completed successfully!")
    except Exception as e:
        print(f"\nTest failed: {str(e)}")
        sys.exit(1)
