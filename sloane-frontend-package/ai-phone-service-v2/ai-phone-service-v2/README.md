# AI Phone Answering Service - README

## Overview

This AI-powered phone answering service is designed for small businesses, providing an automated solution for handling incoming calls. The service is modeled after "Rosie" (https://heyrosie.com/) and includes all key features such as automated call answering, business profile customization, appointment scheduling, and high-value call transfers.

## Key Features

1. **Automated AI Call Answering**
   - Natural language understanding for caller intents
   - Custom responses based on business profile
   - Speech recognition and synthesis using Google Cloud Speech API

2. **Business Onboarding**
   - Conversational AI-guided setup process
   - Business profile creation and configuration
   - AI training on business-specific information

3. **Appointment Scheduling**
   - Integration with Google Calendar, Microsoft Outlook, and Apple Calendar
   - Intelligent time slot suggestions based on business hours
   - Automatic appointment creation and confirmation

4. **High-Value Call Transfer**
   - Identification of high-value customers through keywords and patterns
   - Seamless transfer to live representatives
   - Fallback to voicemail with transcription

5. **Telephony Integration**
   - Complete Twilio integration for call handling
   - TwiML generation for call flow control
   - Call recording and analytics

## System Architecture

The system consists of several key components:

1. **AI Conversation Service**
   - Speech processing (recognition and synthesis)
   - Natural language understanding
   - Conversation management

2. **Calendar Service**
   - Multiple calendar provider integrations
   - Availability checking
   - Appointment creation

3. **Telephony Service**
   - Call handling with Twilio
   - Call transfer functionality
   - Voicemail and transcription

4. **Business Onboarding Interface**
   - React.js frontend with Material UI
   - Conversational setup wizard
   - Business profile management

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- Twilio account
- Google Cloud account (for Speech API)
- Calendar provider accounts (Google, Microsoft, or Apple)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/esolamichael/ai-phone-service.git
   cd ai-phone-service
   ```

2. Run the deployment script:
   ```
   python deploy.py
   ```

   This script will:
   - Check and install dependencies
   - Build the frontend
   - Run tests
   - Start all services

3. Access the application:
   - Frontend: http://localhost:8000/static
   - API: http://localhost:8000/api

### Configuration

1. Set up environment variables:
   ```
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number
   GOOGLE_APPLICATION_CREDENTIALS=path/to/google_credentials.json
   ```

2. Configure calendar credentials:
   - Place Google Calendar credentials in `backend/calendar_service/credentials/google_credentials.json`
   - Place Outlook Calendar credentials in `backend/calendar_service/credentials/outlook_credentials.json`
   - Place Apple Calendar credentials in `backend/calendar_service/credentials/apple_credentials.json`

## Usage

### Business Onboarding

1. Access the onboarding interface at http://localhost:8000/static
2. Follow the conversational setup process
3. Configure business profile, hours, services, and FAQs
4. Set up calendar integration and call transfer settings

### Testing the Service

1. Run the test suite:
   ```
   python tests/test_ai_phone_service.py
   python tests/integration_test.py
   ```

2. Make a test call to your Twilio number
3. Interact with the AI assistant
4. Test appointment scheduling and call transfer functionality

## Development

### Project Structure

```
ai_phone_service/
├── backend/
│   ├── ai_conversation_service/
│   ├── calendar_service/
│   ├── telephony_service/
│   └── api/
├── frontend/
│   ├── public/
│   └── src/
├── tests/
├── main.py
└── deploy.py
```

### Adding New Features

1. Implement the feature in the appropriate service
2. Add API endpoints in the corresponding router
3. Update the frontend if necessary
4. Add tests for the new feature
5. Update documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by Rosie (https://heyrosie.com/)
- Built with FastAPI, React, Twilio, and Google Cloud services
