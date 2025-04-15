"""
Configuration settings for the AI Conversation Service.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Cloud API settings
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "")

# TensorFlow/PyTorch model settings
MODEL_DIR = os.getenv("MODEL_DIR", "models")
INTENT_MODEL_PATH = os.path.join(MODEL_DIR, "intent_model")
ENTITY_MODEL_PATH = os.path.join(MODEL_DIR, "entity_model")
RESPONSE_MODEL_PATH = os.path.join(MODEL_DIR, "response_model")

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_DEBUG = os.getenv("API_DEBUG", "False").lower() == "true"

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/ai_phone_service")

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Service integration endpoints
BUSINESS_PROFILE_SERVICE_URL = os.getenv("BUSINESS_PROFILE_SERVICE_URL", "http://localhost:8001")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8002")
