"""
Meeting Scheduling API endpoints
Handles interview/meeting scheduling and availability management
"""
import logging
import random
import string
import threading
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, date, time, timedelta

from app.database import get_db
from app.email.email_factory import email_service
from app.email.email_templates import (
    send_meeting_confirmation_to_candidate,
    send_meeting_notification_to_interviewer,
)
from app.models.task import Task, TaskStatus
from app.models.stakeholder import Stakeholder
from app.models.candidate import Candidate
from app.services.excel_service import get_interviewer_email

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic Schemas
class MeetingScheduleRequest(BaseModel):
    candidate_id: int
    stakeholder_id: int
    meeting_type: str  # "interview", "onboarding", "orientation"
    scheduled_time: str  # ISO format datetime
    duration_minutes: int = 60
    meeting_link: Optional[str] = None
    notes: Optional[str] = None

class MeetingRescheduleRequest(BaseModel):
    scheduled_time: str
    reason: Optional[str] = None

class TimeSlot(BaseModel):
    start_time: str
    end_time: str
    available: bool

class MeetingResponse(BaseModel):
    id: int
    candidate_name: str
    stakeholder_name: str
    meeting_type: str
    scheduled_time: str
    duration_minutes: int
    status: str
    meeting_link: Optional[str]


def _generate_onboardiq_meeting_link() -> str:
    code = "".join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"https://meet.onboardiq.io/session/{code}"


def _meeting_type_for_email(meeting_type: str, stakeholder_role: str) -> str:
    normalized_type = (meeting_type or "").strip().lower()
    normalized_role = (stakeholder_role or "").strip().lower()

    if "hr" in normalized_type or normalized_role == "hr":
        return "Meeting: HR Walkthrough"
    if "delivery head" in normalized_type or "delivery head" in normalized_role:
        return "Meeting: Delivery Head"
    if "manager" in normalized_type or "manager" in normalized_role:
        return "Meeting: Reporting Manager"
    return meeting_type or "Meeting"


def _send_meeting_emails_background(
    *,
    candidate_name: str,
    candidate_email: Optional[str],
    interviewer_name: str,
    interviewer_role: str,
    meeting_type: str,
    date: str,
    time: str,
    meeting_link: str,
) -> None:
    interviewer_email = get_interviewer_email(interviewer_name)

    if not candidate_email:
        logger.warning("[MEETINGS] Candidate email not found for %s; skipping candidate meeting email.", candidate_name)
    if not interviewer_email:
        logger.warning("[MEETINGS] Interviewer email not found for %s; skipping interviewer meeting email.", interviewer_name)

    def _send() -> None:
        try:
            if candidate_email:
                candidate_payload = send_meeting_confirmation_to_candidate(
                    candidate_name=candidate_name,
                    interviewer_name=interviewer_name,
                    interviewer_role=interviewer_role or "Interviewer",
                    meeting_type=meeting_type,
                    date=date,
                    time=time,
                    meeting_link=meeting_link,
                )
                email_service.email_service._send_email(
                    to_email=candidate_email,
                    subject=candidate_payload["subject"],
                    html_content=candidate_payload["html_content"],
                    to_name=candidate_name,
                )

            if interviewer_email:
                interviewer_payload = send_meeting_notification_to_interviewer(
                    interviewer_name=interviewer_name,
                    candidate_name=candidate_name,
                    candidate_email=candidate_email or "Not available",
                    meeting_type=meeting_type,
                    date=date,
                    time=time,
                    meeting_link=meeting_link,
                )
                email_service.email_service._send_email(
                    to_email=interviewer_email,
                    subject=interviewer_payload["subject"],
                    html_content=interviewer_payload["html_content"],
                    to_name=interviewer_name,
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("[MEETING EMAIL ERROR] %s", exc)

    thread = threading.Thread(target=_send, daemon=True)
    thread.start()

@router.post("/schedule", response_model=MeetingResponse)
async def schedule_meeting(
    meeting_data: MeetingScheduleRequest,
    db: Session = Depends(get_db)
):
    """
    Schedule a new interview or meeting
    Creates a task entry for the meeting
    """
    # Validate candidate exists
    candidate = db.query(Candidate).filter_by(id=meeting_data.candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Validate stakeholder exists and is available
    stakeholder = db.query(Stakeholder).filter_by(id=meeting_data.stakeholder_id).first()
    if not stakeholder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stakeholder not found"
        )
    
    if not stakeholder.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stakeholder {stakeholder.name} is not available"
        )
    
    # Parse scheduled time
    try:
        scheduled_datetime = datetime.fromisoformat(meeting_data.scheduled_time.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )
    
    # Create or update meeting task
    checklist = candidate.checklist
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate checklist not found"
        )
    
    # Find existing meeting task or create new one
    meeting_task = None
    for task in checklist.tasks:
        if task.task_type == "meeting_scheduling" and task.assigned_to_id == meeting_data.stakeholder_id:
            meeting_task = task
            break
    
    if not meeting_task:
        # Create new meeting task
        from app.models.task import TaskOwner
        meeting_task = Task(
            checklist_id=checklist.id,
            name=f"{meeting_data.meeting_type.title()} with {stakeholder.name}",
            description=meeting_data.notes or f"Scheduled {meeting_data.meeting_type}",
            task_type="meeting_scheduling",
            owner=TaskOwner.SYSTEM,
            assigned_to_id=stakeholder.id,
            assigned_to_name=stakeholder.name,
            assigned_to_email=stakeholder.email,
            status=TaskStatus.IN_PROGRESS,
            meeting_scheduled_time=meeting_data.scheduled_time,
            due_date=scheduled_datetime.date()
        )
        db.add(meeting_task)
    else:
        # Update existing task
        meeting_task.meeting_scheduled_time = meeting_data.scheduled_time
        meeting_task.status = TaskStatus.IN_PROGRESS
        meeting_task.due_date = scheduled_datetime.date()
    
    db.commit()
    db.refresh(meeting_task)

    meeting_link = meeting_data.meeting_link or _generate_onboardiq_meeting_link()
    formatted_date = scheduled_datetime.strftime("%d %b")
    formatted_time = scheduled_datetime.strftime("%I:%M %p")
    meeting_type_for_email = _meeting_type_for_email(meeting_data.meeting_type, stakeholder.role or "")

    _send_meeting_emails_background(
        candidate_name=candidate.name,
        candidate_email=candidate.email,
        interviewer_name=stakeholder.name,
        interviewer_role=stakeholder.role or "Interviewer",
        meeting_type=meeting_type_for_email,
        date=formatted_date,
        time=formatted_time,
        meeting_link=meeting_link,
    )
    
    return MeetingResponse(
        id=meeting_task.id,
        candidate_name=candidate.name,
        stakeholder_name=stakeholder.name,
        meeting_type=meeting_data.meeting_type,
        scheduled_time=meeting_data.scheduled_time,
        duration_minutes=meeting_data.duration_minutes,
        status=meeting_task.status.value,
        meeting_link=meeting_link
    )

@router.get("/slots")
async def get_available_slots(
    stakeholder_id: int,
    date_str: str,  # Format: YYYY-MM-DD
    db: Session = Depends(get_db)
):
    """
    Get available time slots for a stakeholder on a specific date
    Returns hourly slots from 9 AM to 6 PM
    """
    stakeholder = db.query(Stakeholder).filter_by(id=stakeholder_id).first()
    if not stakeholder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stakeholder not found"
        )
    
    # Parse date
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Check if stakeholder is available
    if not stakeholder.is_available:
        return {
            "stakeholder_id": stakeholder_id,
            "stakeholder_name": stakeholder.name,
            "date": date_str,
            "available": False,
            "reason": f"On leave until {stakeholder.on_leave_until}",
            "slots": []
        }
    
    # Generate time slots (9 AM to 6 PM, hourly)
    slots = []
    start_hour = 9
    end_hour = 18
    
    for hour in range(start_hour, end_hour):
        start_time = datetime.combine(target_date, time(hour, 0))
        end_time = start_time + timedelta(hours=1)
        
        # Check if slot is already booked
        booked = db.query(Task).filter(
            Task.assigned_to_id == stakeholder_id,
            Task.task_type == "meeting_scheduling",
            Task.meeting_scheduled_time.like(f"{date_str}T{hour:02d}:%")
        ).first()
        
        slots.append(TimeSlot(
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            available=not bool(booked)
        ))
    
    return {
        "stakeholder_id": stakeholder_id,
        "stakeholder_name": stakeholder.name,
        "date": date_str,
        "available": True,
        "slots": slots
    }

@router.get("/{stakeholder_id}/availability")
async def check_stakeholder_availability(
    stakeholder_id: int,
    db: Session = Depends(get_db)
):
    """
    Check if a stakeholder is available for meetings
    """
    stakeholder = db.query(Stakeholder).filter_by(id=stakeholder_id).first()
    if not stakeholder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stakeholder not found"
        )
    
    return {
        "stakeholder_id": stakeholder.id,
        "name": stakeholder.name,
        "email": stakeholder.email,
        "role": stakeholder.role,
        "is_available": stakeholder.is_available,
        "on_leave_until": stakeholder.on_leave_until,
        "fallback_stakeholder_id": stakeholder.fallback_stakeholder_id
    }

@router.patch("/{meeting_id}", response_model=MeetingResponse)
async def reschedule_meeting(
    meeting_id: int,
    reschedule_data: MeetingRescheduleRequest,
    db: Session = Depends(get_db)
):
    """
    Reschedule an existing meeting
    """
    meeting_task = db.query(Task).filter_by(
        id=meeting_id,
        task_type="meeting_scheduling"
    ).first()
    
    if not meeting_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    # Parse new scheduled time
    try:
        scheduled_datetime = datetime.fromisoformat(reschedule_data.scheduled_time.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format"
        )
    
    # Update meeting
    meeting_task.meeting_scheduled_time = reschedule_data.scheduled_time
    meeting_task.due_date = scheduled_datetime.date()
    if reschedule_data.reason:
        meeting_task.fallback_reason = reschedule_data.reason
    
    db.commit()
    db.refresh(meeting_task)
    
    # Get candidate info
    candidate = meeting_task.checklist.candidate
    interviewer_name = meeting_task.assigned_to_name or "Interviewer"
    interviewer_role = "Interviewer"
    stakeholder = db.query(Stakeholder).filter_by(id=meeting_task.assigned_to_id).first() if meeting_task.assigned_to_id else None
    if stakeholder and stakeholder.role:
        interviewer_role = stakeholder.role

    meeting_link = _generate_onboardiq_meeting_link()
    formatted_date = scheduled_datetime.strftime("%d %b")
    formatted_time = scheduled_datetime.strftime("%I:%M %p")
    meeting_type_for_email = _meeting_type_for_email(meeting_task.name or "Meeting", interviewer_role)

    _send_meeting_emails_background(
        candidate_name=candidate.name,
        candidate_email=candidate.email,
        interviewer_name=interviewer_name,
        interviewer_role=interviewer_role,
        meeting_type=meeting_type_for_email,
        date=formatted_date,
        time=formatted_time,
        meeting_link=meeting_link,
    )
    
    return MeetingResponse(
        id=meeting_task.id,
        candidate_name=candidate.name,
        stakeholder_name=interviewer_name,
        meeting_type="meeting",
        scheduled_time=meeting_task.meeting_scheduled_time,
        duration_minutes=60,
        status=meeting_task.status.value,
        meeting_link=meeting_link
    )

@router.get("/", response_model=List[MeetingResponse])
async def get_all_meetings(
    candidate_id: Optional[int] = None,
    stakeholder_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get all scheduled meetings with optional filters
    """
    query = db.query(Task).filter(Task.task_type == "meeting_scheduling")
    
    if candidate_id:
        query = query.join(Task.checklist).filter(
            Task.checklist.has(candidate_id=candidate_id)
        )
    
    if stakeholder_id:
        query = query.filter(Task.assigned_to_id == stakeholder_id)
    
    meetings = query.all()
    
    result = []
    for meeting in meetings:
        candidate = meeting.checklist.candidate
        result.append(MeetingResponse(
            id=meeting.id,
            candidate_name=candidate.name,
            stakeholder_name=meeting.assigned_to_name,
            meeting_type="meeting",
            scheduled_time=meeting.meeting_scheduled_time or "",
            duration_minutes=60,
            status=meeting.status.value,
            meeting_link=None
        ))
    
    return result
