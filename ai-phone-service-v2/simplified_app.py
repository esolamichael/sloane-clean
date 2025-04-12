import os
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Phone Answering Service",
    description="An AI-powered phone answering service for small businesses",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create basic API routes
@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "AI Phone Answering Service",
        "version": "1.0.0"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# Serve static files for the frontend
try:
    app.mount("/static", StaticFiles(directory="frontend/build", html=True), name="static")
    logger.info("Static files mounted successfully")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

# Mock conversation endpoint
@app.post("/api/conversation")
async def process_conversation(request: dict):
    return {
        "response": "Thank you for contacting our business. This is a simplified version of the AI phone answering service.",
        "intent": "greeting",
        "confidence": 0.9
    }

# Mock appointment endpoint
@app.post("/api/calendar/check-availability")
async def check_availability():
    return {
        "available_slots": [
            {"date": "2025-04-02", "time": "10:00 AM"},
            {"date": "2025-04-02", "time": "2:00 PM"},
            {"date": "2025-04-03", "time": "11:00 AM"}
        ]
    }

# Run the application
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

