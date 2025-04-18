"""
Main application for the AI Phone Answering Service.
"""
import os
import sys
import logging
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the backend directory to the Python path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Initialize FastAPI app
app = FastAPI(
    title="AI Phone Answering Service",
    description="An AI-powered phone answering service for small businesses",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import API routers
from backend.ai_conversation_service.api import router as conversation_router
from backend.calendar_service.api import router as calendar_router
from backend.api.call_transfer_routes import router as call_transfer_router

# Include routers
app.include_router(conversation_router)
app.include_router(calendar_router)
app.include_router(call_transfer_router)

# Serve static files for the frontend
app.mount("/static", StaticFiles(directory="frontend/build"), name="static")

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "status": "ok",
        "service": "AI Phone Answering Service",
        "version": "1.0.0"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )

def start_server():
    """Start the FastAPI server."""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    start_server()
