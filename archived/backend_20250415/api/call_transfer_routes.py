"""
API endpoints for call transfer functionality.
"""
import logging
from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..telephony_service.twilio_transfer import TwilioTransferHandler

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/call", tags=["call"])

# Initialize Twilio transfer handler
twilio_transfer_handler = TwilioTransferHandler()

# Models for API requests and responses
class TransferRequest(BaseModel):
    call_sid: str
    transfer_number: str
    message: Optional[str] = None

class TransferResponse(BaseModel):
    success: bool
    message: str

class TransferStatusRequest(BaseModel):
    call_sid: str

class TransferStatusResponse(BaseModel):
    status: Optional[Dict[str, Any]] = None
    success: bool
    message: str

@router.post("/transfer", response_model=TransferResponse)
async def transfer_call(request: TransferRequest):
    """
    Transfer an active call to another number.
    
    Args:
        request (TransferRequest): The request containing call SID and transfer number.
        
    Returns:
        TransferResponse: The response indicating success or failure.
    """
    try:
        success = twilio_transfer_handler.transfer_call(
            call_sid=request.call_sid,
            transfer_number=request.transfer_number
        )
        
        if success:
            return TransferResponse(
                success=True,
                message="Call transfer initiated successfully"
            )
        else:
            return TransferResponse(
                success=False,
                message="Failed to initiate call transfer"
            )
    except Exception as e:
        logger.error(f"Error transferring call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transfer-status", response_model=TransferStatusResponse)
async def get_transfer_status(request: TransferStatusRequest):
    """
    Get the status of a transferred call.
    
    Args:
        request (TransferStatusRequest): The request containing call SID.
        
    Returns:
        TransferStatusResponse: The response containing call status.
    """
    try:
        status = twilio_transfer_handler.get_call_status(request.call_sid)
        
        if status:
            return TransferStatusResponse(
                status=status,
                success=True,
                message="Call status retrieved successfully"
            )
        else:
            return TransferStatusResponse(
                success=False,
                message="Failed to retrieve call status"
            )
    except Exception as e:
        logger.error(f"Error getting call status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transfer-twiml")
async def get_transfer_twiml(request: Request):
    """
    Get TwiML for transferring a call.
    
    Args:
        request (Request): The request containing transfer details.
        
    Returns:
        str: The TwiML response.
    """
    try:
        data = await request.json()
        transfer_number = data.get("transfer_number")
        message = data.get("message")
        
        if not transfer_number:
            raise HTTPException(status_code=400, detail="Transfer number is required")
        
        twiml = twilio_transfer_handler.generate_transfer_twiml(
            transfer_number=transfer_number,
            message=message
        )
        
        return {"twiml": twiml}
    except Exception as e:
        logger.error(f"Error generating transfer TwiML: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transfer-in-progress")
async def transfer_in_progress():
    """
    Get TwiML for when a transfer is in progress.
    
    Returns:
        str: The TwiML response.
    """
    try:
        twiml = twilio_transfer_handler.transfer_in_progress_twiml()
        return {"twiml": twiml}
    except Exception as e:
        logger.error(f"Error generating transfer in progress TwiML: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transfer-complete")
async def transfer_complete(request: Request):
    """
    Handle transfer completion.
    
    Args:
        request (Request): The request containing transfer status.
        
    Returns:
        str: The TwiML response.
    """
    try:
        form_data = await request.form()
        status = form_data.get("DialCallStatus", "completed")
        
        twiml = twilio_transfer_handler.transfer_complete_twiml(status)
        return {"twiml": twiml}
    except Exception as e:
        logger.error(f"Error handling transfer completion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
