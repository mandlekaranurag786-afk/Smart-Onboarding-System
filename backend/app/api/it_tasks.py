"""
IT Tasks API endpoints for equipment allocation workflow
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.services import ITTaskService
from app.models import Task
from app.services.it_task_events import it_task_event_bus
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic schemas
class ButtonResponseRequest(BaseModel):
    """Request schema for button click responses"""
    token: str
    response: str  # "complete" or "need_time"
    responder_email: EmailStr
    responder_name: str
    message: Optional[str] = None


class ButtonResponseResponse(BaseModel):
    """Response schema for button click responses"""
    success: bool
    task_id: Optional[int] = None
    new_status: Optional[str] = None
    message: str
    idempotent: Optional[bool] = False


class TaskStatusResponse(BaseModel):
    """Response schema for task status queries"""
    task_id: int
    candidate_id: int
    candidate_name: str
    status: str
    created_at: str
    response_received_at: Optional[str] = None
    responder_name: Optional[str] = None
    responder_email: Optional[str] = None
    days_pending: int


@router.get("/response/button")
async def handle_button_click_get(
    token: str = Query(..., description="Task response token"),
    response: str = Query(..., description="Response type: complete or need_time"),
    db: Session = Depends(get_db)
):
    """
    Handle IT team button click via GET request (for email links)
    
    This endpoint is called when IT team clicks action buttons in the email.
    It validates the token, verifies authorization, and updates task status.
    
    Query Parameters:
    - token: Unique task response token
    - response: "complete" or "need_time"
    
    Returns:
    - HTML page confirming the action
    """
    try:
        # Validate token first
        task = ITTaskService.validate_token(token, db)
        if not task:
            return """
            <html>
                <head><title>Invalid Token</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1>❌ Invalid or Expired Token</h1>
                    <p>This link is no longer valid. Please contact HR directly.</p>
                </body>
            </html>
            """
        
        # Get candidate info for display
        candidate = task.checklist.candidate if task.checklist else None
        candidate_name = candidate.name if candidate else "Unknown"
        
        # For GET requests from email links, we need to extract responder info
        # Since we can't get it from the link, we'll use the IT_EMAIL from config
        from app.config import IT_EMAIL
        
        # Process the response
        result = ITTaskService.process_button_response(
            token=token,
            response=response,
            responder_email=IT_EMAIL or "it@company.com",
            responder_name="IT Team",
            message=None,
            db=db
        )
        
        if result["success"]:
            status_text = "✅ Allocation Complete" if response == "complete" else "⏰ Need More Time"
            status_color = "#4CAF50" if response == "complete" else "#FF9800"
            
            return f"""
            <html>
                <head>
                    <title>Response Recorded</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            text-align: center;
                            padding: 50px;
                            background-color: #f5f5f5;
                        }}
                        .container {{
                            background: white;
                            padding: 40px;
                            border-radius: 10px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                            max-width: 600px;
                            margin: 0 auto;
                        }}
                        .status {{
                            color: {status_color};
                            font-size: 48px;
                            margin-bottom: 20px;
                        }}
                        h1 {{
                            color: #333;
                            margin-bottom: 10px;
                        }}
                        p {{
                            color: #666;
                            font-size: 16px;
                            line-height: 1.6;
                        }}
                        .info-box {{
                            background: #f9f9f9;
                            padding: 20px;
                            border-radius: 5px;
                            margin: 20px 0;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="status">{status_text}</div>
                        <h1>Response Recorded Successfully</h1>
                        <div class="info-box">
                            <p><strong>Candidate:</strong> {candidate_name}</p>
                            <p><strong>Task ID:</strong> {task.id}</p>
                            <p><strong>Status:</strong> {result["new_status"].title()}</p>
                        </div>
                        <p>Thank you for your response. The HR team has been notified.</p>
                        {"<p><em>Note: This task was already processed earlier.</em></p>" if result.get("idempotent") else ""}
                    </div>
                </body>
            </html>
            """
        else:
            error_msg = result.get("error", "Unknown error")
            return f"""
            <html>
                <head><title>Error</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1>❌ Error Processing Response</h1>
                    <p>{error_msg}</p>
                    <p>Please contact HR directly if you need assistance.</p>
                </body>
            </html>
            """
            
    except Exception as e:
        logger.error(f"Error handling button click: {e}")
        return f"""
        <html>
            <head><title>Error</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>❌ Server Error</h1>
                <p>An unexpected error occurred. Please contact HR directly.</p>
            </body>
        </html>
        """


@router.post("/response/button", response_model=ButtonResponseResponse)
async def handle_button_click_post(
    request: ButtonResponseRequest,
    db: Session = Depends(get_db)
):
    """
    Handle IT team button click via POST request (for API calls)
    
    This endpoint processes button responses from IT team members.
    It validates the token, verifies authorization, and updates task status.
    
    Request Body:
    - token: Unique task response token
    - response: "complete" or "need_time"
    - responder_email: Email of IT team member
    - responder_name: Name of IT team member
    - message: Optional message from IT team
    
    Returns:
    - ButtonResponseResponse with success status and details
    """
    try:
        result = ITTaskService.process_button_response(
            token=request.token,
            response=request.response,
            responder_email=request.responder_email,
            responder_name=request.responder_name,
            message=request.message,
            db=db
        )
        
        if result["success"]:
            return ButtonResponseResponse(
                success=True,
                task_id=result.get("task_id"),
                new_status=result.get("new_status"),
                message=result.get("message", "Task status updated successfully"),
                idempotent=result.get("idempotent", False)
            )
        else:
            error_code = result.get("error_code", "UNKNOWN_ERROR")
            if error_code == "INVALID_TOKEN":
                raise HTTPException(status_code=400, detail=result.get("error"))
            elif error_code == "UNAUTHORIZED":
                raise HTTPException(status_code=403, detail=result.get("error"))
            else:
                raise HTTPException(status_code=500, detail=result.get("error"))
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing button response: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    Get current status of an IT equipment allocation task
    
    Path Parameters:
    - task_id: ID of the task
    
    Returns:
    - TaskStatusResponse with current status and details
    """
    try:
        # Get task
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Get candidate info
        candidate = task.checklist.candidate if task.checklist else None
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found for task")
        
        payload = ITTaskService._build_task_update_payload(task)
        return TaskStatusResponse(**payload)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{task_id}/stream")
async def stream_task_status(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Server-sent event stream for live IT task updates."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    async def event_generator():
        async for chunk in it_task_event_bus.subscribe(task_id):
            if await request.is_disconnected():
                break
            yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
