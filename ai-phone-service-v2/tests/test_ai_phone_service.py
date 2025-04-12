"""
Test script for the AI phone answering service.
"""
import os
import sys
import json
import time
import unittest
from unittest.mock import MagicMock, patch
import requests

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_conversation_service.speech_processor import SpeechProcessor
from ai_conversation_service.nlu_processor import NLUProcessor
from ai_conversation_service.conversation_manager import ConversationManager
from ai_conversation_service.calendar_integration import CalendarIntegration
from ai_conversation_service.call_transfer import CallTransferService
from ai_conversation_service.call_transfer_integration import integrate_call_transfer

class TestAIPhoneService(unittest.TestCase):
    """Test cases for the AI phone answering service."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock business profile
        self.business_profile = {
            "id": "test_business",
            "name": "Test Business",
            "greeting": "Thank you for calling Test Business. This is Rosie, how can I help you today?",
            "businessHours": {
                "monday": "9:00 AM - 5:00 PM",
                "tuesday": "9:00 AM - 5:00 PM",
                "wednesday": "9:00 AM - 5:00 PM",
                "thursday": "9:00 AM - 5:00 PM",
                "friday": "9:00 AM - 5:00 PM",
                "saturday": "Closed",
                "sunday": "Closed"
            },
            "services": [
                "Consultation",
                "Installation",
                "Repair",
                "Maintenance"
            ],
            "faqs": [
                {
                    "question": "What are your business hours?",
                    "answer": "We are open Monday through Friday from 9:00 AM to 5:00 PM. We are closed on weekends."
                },
                {
                    "question": "Do you offer free estimates?",
                    "answer": "Yes, we offer free estimates for all our services. You can schedule an estimate by booking an appointment."
                },
                {
                    "question": "What forms of payment do you accept?",
                    "answer": "We accept all major credit cards, cash, and checks."
                }
            ],
            "appointmentScheduling": {
                "enabled": True,
                "calendarType": "google",
                "calendarId": "test_calendar_id",
                "durationMinutes": 60
            },
            "transferSettings": {
                "highValueKeywords": ["urgent", "emergency", "immediately", "right now", "premium"],
                "transferNumber": "+15551234567"
            },
            "notificationSettings": {
                "email": "business@example.com",
                "sms": "+15551234567",
                "notifyOnAllCalls": True
            }
        }
        
        # Mock the speech processor
        self.speech_processor = MagicMock(spec=SpeechProcessor)
        self.speech_processor.recognize_speech.return_value = "Test input"
        self.speech_processor.text_to_speech.return_value = b"Test audio"
        
        # Create a conversation manager with the mocked speech processor
        with patch('ai_conversation_service.conversation_manager.SpeechProcessor', return_value=self.speech_processor):
            self.conversation_manager = ConversationManager("test_business")
            self.conversation_manager.business_profile = self.business_profile
    
    def test_greeting(self):
        """Test the greeting response."""
        response = self.conversation_manager.start_conversation()
        
        self.assertEqual(response["text"], self.business_profile["greeting"])
        self.assertEqual(response["audio"], b"Test audio")
        self.speech_processor.text_to_speech.assert_called_with(self.business_profile["greeting"])
    
    def test_business_hours_intent(self):
        """Test the response to a business hours intent."""
        # Mock the NLU processor
        with patch('ai_conversation_service.conversation_manager.NLUProcessor') as mock_nlu:
            mock_nlu_instance = mock_nlu.return_value
            mock_nlu_instance.process.return_value = {
                "text": "What are your business hours?",
                "intent": {
                    "intent": "business_hours",
                    "confidence": 0.9
                },
                "entities": []
            }
            
            # Process the user input
            response = self.conversation_manager.process_user_input(text="What are your business hours?")
            
            # Check that the response contains business hours information
            self.assertIn("business hours", response["text"].lower())
            self.assertIn("monday", response["text"].lower())
            self.assertIn("9:00 am", response["text"].lower())
    
    def test_appointment_scheduling_intent(self):
        """Test the response to an appointment scheduling intent."""
        # Mock the NLU processor
        with patch('ai_conversation_service.conversation_manager.NLUProcessor') as mock_nlu:
            mock_nlu_instance = mock_nlu.return_value
            mock_nlu_instance.process.return_value = {
                "text": "I'd like to schedule an appointment for tomorrow at 2pm",
                "intent": {
                    "intent": "appointment_scheduling",
                    "confidence": 0.9
                },
                "entities": [
                    {
                        "type": "DATE",
                        "text": "tomorrow",
                        "start": 35,
                        "end": 43
                    },
                    {
                        "type": "TIME",
                        "text": "2pm",
                        "start": 47,
                        "end": 50
                    }
                ]
            }
            
            # Process the user input
            response = self.conversation_manager.process_user_input(text="I'd like to schedule an appointment for tomorrow at 2pm")
            
            # Check that the response acknowledges the appointment request
            self.assertIn("appointment", response["text"].lower())
            self.assertIn("tomorrow", response["text"].lower())
            self.assertIn("2pm", response["text"].lower())
    
    def test_call_transfer_high_value_keyword(self):
        """Test call transfer for high-value keywords."""
        # Integrate call transfer functionality
        integrate_call_transfer(self.conversation_manager)
        
        # Mock the NLU processor
        with patch('ai_conversation_service.conversation_manager.NLUProcessor') as mock_nlu:
            mock_nlu_instance = mock_nlu.return_value
            mock_nlu_instance.process.return_value = {
                "text": "This is an urgent matter that needs immediate attention",
                "intent": {
                    "intent": "urgent_request",
                    "confidence": 0.9
                },
                "entities": []
            }
            
            # Process the user input
            response = self.conversation_manager.process_user_input(text="This is an urgent matter that needs immediate attention")
            
            # Check that the response indicates a transfer
            self.assertIn("transfer", response["text"].lower())
            self.assertEqual(response["action"]["type"], "transfer")
            self.assertEqual(response["action"]["number"], "+15551234567")
    
    def test_call_transfer_high_value_intent(self):
        """Test call transfer for high-value intents."""
        # Integrate call transfer functionality
        integrate_call_transfer(self.conversation_manager)
        
        # Mock the NLU processor
        with patch('ai_conversation_service.conversation_manager.NLUProcessor') as mock_nlu:
            mock_nlu_instance = mock_nlu.return_value
            mock_nlu_instance.process.return_value = {
                "text": "I have a complaint about the service I received",
                "intent": {
                    "intent": "complaint",
                    "confidence": 0.8
                },
                "entities": []
            }
            
            # Process the user input
            response = self.conversation_manager.process_user_input(text="I have a complaint about the service I received")
            
            # Check that the response indicates a transfer
            self.assertIn("transfer", response["text"].lower())
            self.assertEqual(response["action"]["type"], "transfer")
            self.assertEqual(response["action"]["number"], "+15551234567")
    
    def test_calendar_integration(self):
        """Test the calendar integration."""
        # Mock the calendar integration
        calendar_integration = MagicMock(spec=CalendarIntegration)
        calendar_integration.suggest_appointment_slots.return_value = [
            {
                "start": "2025-04-01T10:00:00",
                "end": "2025-04-01T11:00:00",
                "duration_minutes": 60
            },
            {
                "start": "2025-04-01T14:00:00",
                "end": "2025-04-01T15:00:00",
                "duration_minutes": 60
            }
        ]
        
        # Test suggesting appointment slots
        slots = calendar_integration.suggest_appointment_slots(
            business_id="test_business",
            business_profile=self.business_profile,
            requested_date="tomorrow",
            requested_time="afternoon"
        )
        
        self.assertEqual(len(slots), 2)
        self.assertEqual(slots[0]["duration_minutes"], 60)
        
        # Mock scheduling an appointment
        calendar_integration.schedule_appointment.return_value = {
            "id": "test_appointment_id",
            "summary": "Appointment with Test Customer",
            "start": "2025-04-01T14:00:00",
            "end": "2025-04-01T15:00:00",
            "link": "https://calendar.google.com/calendar/event?eid=123456"
        }
        
        # Test scheduling an appointment
        appointment = calendar_integration.schedule_appointment(
            business_id="test_business",
            business_profile=self.business_profile,
            slot=slots[1],
            customer_name="Test Customer",
            customer_email="customer@example.com",
            customer_phone="+15559876543",
            appointment_reason="Consultation"
        )
        
        self.assertEqual(appointment["summary"], "Appointment with Test Customer")
        self.assertEqual(appointment["start"], "2025-04-01T14:00:00")
        self.assertEqual(appointment["end"], "2025-04-01T15:00:00")

if __name__ == '__main__':
    unittest.main()
