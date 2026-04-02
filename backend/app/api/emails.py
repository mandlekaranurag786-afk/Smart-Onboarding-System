"""
Email API endpoints
Handles email sending operations
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.models.candidate import Candidate, CandidateAccountStatus
from app.email.email_service import email_service
from app.email.email_schemas import (
    WelcomeEmailData,
    ITNotificationData,
    ManagerNotificationData,
    LaptopConfirmationData,
    HRAlertData,
    EmailResponse
)
from app import config
from app.security import generate_temporary_password, hash_password

logger = logging.getLogger(__name__)
router = APIRouter()


# Default onboarding tasks
DEFAULT_ONBOARDING_TASKS = [
    "Complete personal information form",
    "Upload required documents (ID, certificates)",
    "Review and sign company policies",
    "Complete IT security training",
    "Setup email and communication tools",
    "Meet with reporting manager",
    "Complete department orientation",
    "Setup workstation and tools",
    "Complete compliance training"
]


def issue_candidate_temporary_password(candidate: Candidate, db: Session) -> str:
    """
    Generate and persist a new temporary password before emailing it.
    """
    temporary_password = generate_temporary_password()
    candidate.password_hash = hash_password(temporary_password)
    candidate.password_reset_required = 1
    candidate.account_status = CandidateAccountStatus.INVITED
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return temporary_password


@router.post("/send-welcome", response_model=EmailResponse)
async def send_welcome_email(
    candidate_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Send welcome email to a candidate
    Triggered when HR adds a new joiner
    """
    # Get candidate from database
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    login_password = issue_candidate_temporary_password(candidate, db)
    
    # Prepare email data
    email_data = WelcomeEmailData(
        candidate_name=candidate.name,
        candidate_email=candidate.email,
        role=candidate.role or "Team Member",
        department=candidate.department,
        joining_date=candidate.joining_date,
        reporting_manager=candidate.reporting_manager or "TBD",
        login_email=candidate.email,
        login_password=login_password,
        tasks=DEFAULT_ONBOARDING_TASKS
    )
    
    # Send email in background
    background_tasks.add_task(email_service.send_welcome_email, email_data)
    
    logger.info(f"Welcome email queued for {candidate.name}")
    
    return EmailResponse(
        success=True,
        message=f"Welcome email queued for {candidate.name}"
    )


@router.post("/send-it-notification", response_model=EmailResponse)
async def send_it_notification(
    candidate_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Send IT team notification for new joiner
    Triggered automatically when candidate is added
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    email_data = ITNotificationData(
        candidate_name=candidate.name,
        candidate_email=candidate.email,
        role=candidate.role or "Team Member",
        department=candidate.department,
        joining_date=candidate.joining_date,
        reporting_manager=candidate.reporting_manager or "TBD"
    )
    
    background_tasks.add_task(email_service.send_it_notification, email_data)
    
    logger.info(f"IT notification queued for {candidate.name}")
    
    return EmailResponse(
        success=True,
        message=f"IT notification queued for {candidate.name}"
    )


@router.post("/send-manager-notification", response_model=EmailResponse)
async def send_manager_notification(
    candidate_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Send notification to reporting manager
    Triggered automatically when candidate is added
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if not candidate.reporting_manager_email:
        raise HTTPException(
            status_code=400,
            detail="Reporting manager email not configured"
        )
    
    email_data = ManagerNotificationData(
        manager_name=candidate.reporting_manager or "Manager",
        manager_email=candidate.reporting_manager_email,
        candidate_name=candidate.name,
        candidate_email=candidate.email,
        role=candidate.role or "Team Member",
        department=candidate.department,
        joining_date=candidate.joining_date
    )
    
    background_tasks.add_task(email_service.send_manager_notification, email_data)
    
    logger.info(f"Manager notification queued for {candidate.name}")
    
    return EmailResponse(
        success=True,
        message=f"Manager notification queued for {candidate.name}"
    )


@router.post("/send-laptop-confirmation", response_model=EmailResponse)
async def send_laptop_confirmation(
    candidate_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Send laptop delivery confirmation request
    Can be triggered manually or automatically after X days
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Generate confirmation links
    base_url = config.FRONTEND_URL
    confirmation_link_yes = f"{base_url}/api/emails/laptop-confirm/{candidate_id}/yes"
    confirmation_link_no = f"{base_url}/api/emails/laptop-confirm/{candidate_id}/no"
    
    email_data = LaptopConfirmationData(
        candidate_name=candidate.name,
        candidate_email=candidate.email,
        candidate_id=candidate_id,
        confirmation_link_yes=confirmation_link_yes,
        confirmation_link_no=confirmation_link_no
    )
    
    background_tasks.add_task(email_service.send_laptop_confirmation, email_data)
    
    logger.info(f"Laptop confirmation queued for {candidate.name}")
    
    return EmailResponse(
        success=True,
        message=f"Laptop confirmation email queued for {candidate.name}"
    )


@router.get("/laptop-confirm/{candidate_id}/{response}")
async def laptop_confirmation_response(
    candidate_id: int,
    response: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Handle laptop confirmation response (Yes/No)
    Webhook endpoint for candidate clicks
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if response.lower() == "yes":
        # Laptop received - notify HR
        alert_data = HRAlertData(
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            alert_type="laptop_received",
            message=f"{candidate.name} has confirmed receiving their laptop and IT assets.",
            additional_info={
                "Confirmed At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Status": "✅ Delivered"
            }
        )
        
        background_tasks.add_task(email_service.send_hr_alert, alert_data)
        
        return {
            "message": "Thank you for confirming! HR has been notified.",
            "status": "confirmed"
        }
    
    elif response.lower() == "no":
        # Laptop not received - alert HR with SLA
        alert_data = HRAlertData(
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            alert_type="laptop_not_received",
            message=f"⚠️ {candidate.name} has NOT received their laptop yet. Please follow up with IT team.",
            additional_info={
                "Reported At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Joining Date": candidate.joining_date.strftime("%Y-%m-%d"),
                "Status": "❌ Not Delivered",
                "Action Required": "Contact IT team immediately"
            }
        )
        
        background_tasks.add_task(email_service.send_hr_alert, alert_data)
        
        return {
            "message": "Thank you for letting us know. HR will follow up shortly.",
            "status": "not_confirmed"
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid response")


@router.post("/trigger-onboarding-flow", response_model=dict)
async def trigger_complete_onboarding_flow(
    candidate_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger complete onboarding email flow
    Sends all automated emails in parallel:
    1. Welcome email to candidate
    2. IT team notification
    3. Manager notification
    
    This is the main endpoint HR calls when adding a new joiner
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    logger.info(f"Triggering complete onboarding flow for {candidate.name}")
    
    # 1. Send welcome email to candidate
    login_password = issue_candidate_temporary_password(candidate, db)
    welcome_data = WelcomeEmailData(
        candidate_name=candidate.name,
        candidate_email=candidate.email,
        role=candidate.role or "Team Member",
        department=candidate.department,
        joining_date=candidate.joining_date,
        reporting_manager=candidate.reporting_manager or "TBD",
        login_email=candidate.email,
        login_password=login_password,
        tasks=DEFAULT_ONBOARDING_TASKS
    )
    background_tasks.add_task(email_service.send_welcome_email, welcome_data)
    
    # 2. Send IT notification
    it_data = ITNotificationData(
        candidate_name=candidate.name,
        candidate_email=candidate.email,
        role=candidate.role or "Team Member",
        department=candidate.department,
        joining_date=candidate.joining_date,
        reporting_manager=candidate.reporting_manager or "TBD"
    )
    background_tasks.add_task(email_service.send_it_notification, it_data)
    
    # 3. Send manager notification (if manager email exists)
    if candidate.reporting_manager_email:
        manager_data = ManagerNotificationData(
            manager_name=candidate.reporting_manager or "Manager",
            manager_email=candidate.reporting_manager_email,
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            role=candidate.role or "Team Member",
            department=candidate.department,
            joining_date=candidate.joining_date
        )
        background_tasks.add_task(email_service.send_manager_notification, manager_data)
    
    return {
        "success": True,
        "message": f"Complete onboarding flow triggered for {candidate.name}",
        "emails_queued": {
            "welcome_email": True,
            "it_notification": True,
            "manager_notification": bool(candidate.reporting_manager_email)
        }
    }


@router.post("/send-hr-alert", response_model=EmailResponse)
async def send_hr_alert(
    alert_data: HRAlertData,
    background_tasks: BackgroundTasks
):
    """
    Send custom alert to HR team
    Can be used for various notifications
    """
    background_tasks.add_task(email_service.send_hr_alert, alert_data)
    
    return EmailResponse(
        success=True,
        message="HR alert queued"
    )


@router.get("/test-email")
async def test_email_service():
    """
    Test endpoint to verify email service configuration
    """
    if not email_service.client:
        return {
            "status": "error",
            "message": "SendGrid API key not configured",
            "configured": False
        }
    
    return {
        "status": "ok",
        "message": "Email service is configured",
        "configured": True,
        "from_email": email_service.from_email,
        "hr_email": email_service.hr_email,
        "it_email": email_service.it_email
    }
