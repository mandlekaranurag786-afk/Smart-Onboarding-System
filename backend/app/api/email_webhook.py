"""
Email Webhook API endpoints
Handles incoming email events from Azure Communication Services
"""
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import json

from app.database import get_db
from app.services.email_reply_processor import EmailReplyProcessor

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic schemas for Azure Communication Services email events
class EmailAddress(BaseModel):
    """Email address schema"""
    address: EmailStr
    displayName: Optional[str] = None


class EmailAttachment(BaseModel):
    """Email attachment schema"""
    name: str
    contentType: str
    contentId: Optional[str] = None
    contentInBytes: Optional[str] = None


class EmailContent(BaseModel):
    """Email content schema"""
    subject: str
    plainText: Optional[str] = None
    html: Optional[str] = None


class EmailReceivedEvent(BaseModel):
    """Azure Communication Services email received event"""
    id: str
    topic: str
    subject: str
    eventType: str
    eventTime: str
    data: Dict[str, Any]


class ManualEmailReplyRequest(BaseModel):
    """Manual email reply submission (for testing or manual processing)"""
    sender_email: EmailStr
    sender_name: str
    email_subject: str
    email_body: str


class EmailReplyResponse(BaseModel):
    """Response schema for email reply processing"""
    success: bool
    task_id: Optional[int] = None
    new_status: Optional[str] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None
    message: str
    idempotent: Optional[bool] = False


@router.post("/webhook/azure-email-events")
async def handle_azure_email_events(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for Azure Communication Services email events
    
    This endpoint receives email events from Azure, including:
    - EmailReceived: When an email is received
    - EmailDeliveryReportReceived: Delivery status updates
    
    Azure Event Grid sends events in this format:
    [
        {
            "id": "unique-event-id",
            "topic": "/subscriptions/.../resourceGroups/.../providers/Microsoft.Communication/...",
            "subject": "sender/recipient",
            "eventType": "Microsoft.Communication.EmailReceived",
            "eventTime": "2024-01-15T10:30:00Z",
            "data": {
                "sender": "it@company.com",
                "recipient": "onboardiq@company.com",
                "subject": "Re: IT Setup Required",
                "receivedTimestamp": "2024-01-15T10:30:00Z",
                ...
            }
        }
    ]
    """
    try:
        # Parse request body
        body = await request.json()
        logger.info(f"Received Azure email webhook: {json.dumps(body, indent=2)}")
        
        # Azure sends events as an array
        if not isinstance(body, list):
            body = [body]
        
        results = []
        
        for event in body:
            event_type = event.get("eventType", "")
            
            # Handle email received events
            if event_type == "Microsoft.Communication.EmailReceived":
                result = await _process_email_received_event(event, db, background_tasks)
                results.append(result)
            
            # Handle validation events (Azure Event Grid subscription validation)
            elif event_type == "Microsoft.EventGrid.SubscriptionValidationEvent":
                validation_code = event.get("data", {}).get("validationCode")
                logger.info(f"Received subscription validation request: {validation_code}")
                return {"validationResponse": validation_code}
            
            else:
                logger.info(f"Ignoring event type: {event_type}")
        
        return {
            "success": True,
            "processed_events": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error processing Azure email webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def _process_email_received_event(
    event: Dict[str, Any],
    db: Session,
    background_tasks: BackgroundTasks
) -> Dict:
    """
    Process email received event from Azure
    
    Args:
        event: Azure email event data
        db: Database session
        background_tasks: FastAPI background tasks
        
    Returns:
        Processing result dictionary
    """
    try:
        data = event.get("data", {})
        
        # Extract email details
        sender_email = data.get("sender", "")
        sender_name = data.get("senderDisplayName", sender_email.split("@")[0])
        subject = data.get("subject", "")
        
        # Get email body (prefer plain text, fallback to HTML)
        body_plain = data.get("plainTextBody", "")
        body_html = data.get("htmlBody", "")
        email_body = body_plain if body_plain else body_html
        
        if not email_body:
            logger.warning("Email has no body content")
            return {
                "success": False,
                "error": "Email has no body content"
            }
        
        logger.info(
            f"Processing email from {sender_name} ({sender_email}): {subject}"
        )
        
        # Process email reply in background
        result = EmailReplyProcessor.process_email_reply(
            sender_email=sender_email,
            sender_name=sender_name,
            email_subject=subject,
            email_body=email_body,
            db=db
        )
        
        # If successful, send confirmation email to IT team
        if result.get("success"):
            background_tasks.add_task(
                _send_confirmation_email,
                sender_email=sender_email,
                sender_name=sender_name,
                task_id=result.get("task_id"),
                new_status=result.get("new_status")
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing email received event: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/webhook/manual-email-reply", response_model=EmailReplyResponse)
async def handle_manual_email_reply(
    request: ManualEmailReplyRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manual endpoint for processing email replies (for testing or manual submission)
    
    This endpoint allows manual submission of email replies for processing.
    Useful for testing the email reply processing logic without Azure webhook.
    
    Request Body:
    - sender_email: Email address of IT team member
    - sender_name: Name of IT team member
    - email_subject: Email subject line
    - email_body: Email body content
    
    Returns:
    - EmailReplyResponse with processing result
    """
    try:
        logger.info(
            f"Processing manual email reply from {request.sender_name} "
            f"({request.sender_email})"
        )
        
        result = EmailReplyProcessor.process_email_reply(
            sender_email=request.sender_email,
            sender_name=request.sender_name,
            email_subject=request.email_subject,
            email_body=request.email_body,
            db=db
        )
        
        if result.get("success"):
            # Send confirmation email in background
            background_tasks.add_task(
                _send_confirmation_email,
                sender_email=request.sender_email,
                sender_name=request.sender_name,
                task_id=result.get("task_id"),
                new_status=result.get("new_status")
            )
            
            return EmailReplyResponse(
                success=True,
                task_id=result.get("task_id"),
                new_status=result.get("new_status"),
                intent=result.get("intent"),
                confidence=result.get("confidence"),
                message=result.get("message", "Email processed successfully"),
                idempotent=result.get("idempotent", False)
            )
        else:
            error_code = result.get("error_code", "UNKNOWN_ERROR")
            if error_code == "UNAUTHORIZED":
                raise HTTPException(status_code=403, detail=result.get("error"))
            elif error_code == "TASK_NOT_FOUND":
                raise HTTPException(status_code=404, detail=result.get("error"))
            else:
                raise HTTPException(status_code=500, detail=result.get("error"))
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing manual email reply: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def _send_confirmation_email(
    sender_email: str,
    sender_name: str,
    task_id: int,
    new_status: str
):
    """
    Send confirmation email to IT team member
    
    Args:
        sender_email: Email of IT team member
        sender_name: Name of IT team member
        task_id: ID of the task
        new_status: New status of the task
    """
    try:
        from app.email.azure_email_service import AzureEmailService
        from app.database import create_db_session
        from app.models import Task
        
        # Get task details
        db = create_db_session()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                logger.warning(f"Task {task_id} not found for confirmation email")
                return
            
            candidate = task.checklist.candidate if task.checklist else None
            if not candidate:
                logger.warning(f"Candidate not found for task {task_id}")
                return
            
            # Prepare confirmation email
            status_emoji = "✅" if new_status == "completed" else "⏰"
            status_text = "Completed" if new_status == "completed" else "Delayed"
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 600px;
            margin: auto;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            background-color: #ffffff;
        }}
        .header {{
            background-color: #4CAF50;
            color: white;
            padding: 15px;
            border-radius: 6px 6px 0 0;
            text-align: center;
        }}
        .info-box {{
            background-color: #f9f9f9;
            padding: 15px;
            border-left: 4px solid #4CAF50;
            margin: 20px 0;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>{status_emoji} Response Recorded</h2>
        </div>
        
        <p>Hi {sender_name},</p>
        
        <p>Thank you for your response. We have recorded your update for the IT equipment allocation task.</p>
        
        <div class="info-box">
            <p><strong>Candidate:</strong> {candidate.name}</p>
            <p><strong>Task ID:</strong> {task_id}</p>
            <p><strong>Status:</strong> {status_text}</p>
        </div>
        
        <p>The HR team has been notified of this update.</p>
        
        <p>Best regards,<br><strong>OnboardIQ System</strong></p>
    </div>
</body>
</html>
"""
            
            # Send confirmation email
            email_service = AzureEmailService()
            result = email_service._send_email(
                to_email=sender_email,
                subject=f"{status_emoji} IT Task Response Confirmed - {candidate.name}",
                html_content=html_content,
                to_name=sender_name
            )
            
            if result.success:
                logger.info(f"Confirmation email sent to {sender_email}")
            else:
                logger.error(f"Failed to send confirmation email: {result.message}")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error sending confirmation email: {e}")


@router.get("/webhook/test")
async def test_webhook():
    """
    Test endpoint to verify webhook is accessible
    """
    return {
        "status": "online",
        "service": "Email Webhook",
        "timestamp": datetime.now().isoformat()
    }
