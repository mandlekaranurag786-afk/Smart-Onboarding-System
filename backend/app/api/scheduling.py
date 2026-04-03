"""
Scheduling routes backed by Excel availability data.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.activities import log_activity
from app.database import get_db
from app.llm_client import get_llm
from app.models.candidate import Candidate
from app.models.stakeholder import Stakeholder
from app.models.task import Task, TaskStatus
from app.services.excel_service import (
    ask_llm_for_slot,
    book_slot,
    get_all_available_slots,
    get_all_interviewers,
    get_first_available_slot,
    get_meetings_for_candidate,
)

router = APIRouter()


class BookMeetingRequest(BaseModel):
    candidate_name: str
    meeting_type: str
    interviewer_name: str
    date: str
    time: str
    booked_by: Optional[str] = "HR"


def _canonical_meeting_type(meeting_type: str) -> str:
    normalized = meeting_type.strip().lower()

    if normalized == "hr introduction" or "meeting: hr" in normalized or normalized == "hr":
        return "HR Introduction"

    if (
        normalized == "delivery head introduction"
        or "delivery head" in normalized
        or "practice head" in normalized
    ):
        return "Delivery Head Introduction"

    if (
        normalized == "manager introduction"
        or "manager" in normalized
        or "reporting manager" in normalized
        or "infrastructure" in normalized
    ):
        return "Manager Introduction"

    raise HTTPException(
        status_code=400,
        detail=(
            "Unsupported meeting_type. Use one of: "
            "HR Introduction, Manager Introduction, Delivery Head Introduction."
        ),
    )


def _role_filter_for_meeting_type(canonical_type: str) -> str:
    mapping = {
        "HR Introduction": "HR",
        "Manager Introduction": "Manager",
        "Delivery Head Introduction": "Delivery Head",
    }
    return mapping.get(canonical_type, "")


def _normalize_name(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def _find_candidate(db: Session, candidate_name: str) -> Candidate:
    candidate = (
        db.query(Candidate)
        .filter(func.lower(Candidate.name) == candidate_name.strip().lower())
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate '{candidate_name}' not found.")
    return candidate


def _candidate_field(candidate: Candidate, *names: str) -> str:
    for field_name in names:
        if hasattr(candidate, field_name):
            value = getattr(candidate, field_name)
            if isinstance(value, Enum):
                value = value.value
            if value:
                return str(value).strip()
    return ""


def _default_interviewer_name(role: str) -> str:
    interviewers = get_all_interviewers(role_filter=role)
    if not interviewers:
        return ""
    return interviewers[0]["name"]


def _resolve_interviewer_name(requested_name: str, role_filter: str) -> str:
    interviewers = get_all_interviewers(role_filter=role_filter)
    if not interviewers:
        return ""

    requested_normalized = _normalize_name(requested_name)
    if not requested_normalized:
        return interviewers[0]["name"]

    # 1) exact full-name match
    for person in interviewers:
        if _normalize_name(person["name"]) == requested_normalized:
            return person["name"]

    # 2) first-token match (for names like "Sumit Patil" -> "Sumit")
    requested_first = requested_normalized.split()[0]
    for person in interviewers:
        person_first = _normalize_name(person["name"]).split()[0]
        if person_first == requested_first:
            return person["name"]

    # 3) fallback to first interviewer of same role
    return interviewers[0]["name"]


def _assigned_person_for_meeting(candidate: Candidate, meeting_type: str) -> str:
    canonical_type = _canonical_meeting_type(meeting_type)

    if canonical_type == "HR Introduction":
        raw = _candidate_field(candidate, "assigned_hr", "hr_name")
        if raw:
            return _resolve_interviewer_name(raw, "HR")
        return _default_interviewer_name("HR")

    if canonical_type == "Manager Introduction":
        raw = _candidate_field(
            candidate,
            "assigned_manager",
            "reporting_to",
            "reporting_manager",
        )
        if raw:
            return _resolve_interviewer_name(raw, "Manager")
        return _default_interviewer_name("Manager")

    if canonical_type == "Delivery Head Introduction":
        raw = _candidate_field(
            candidate,
            "backup_manager",
            "assigned_delivery_head",
            "assigned_manager",
            "reporting_to",
            "reporting_manager",
        )
        if raw:
            return _resolve_interviewer_name(raw, "Delivery Head")
        return _default_interviewer_name("Delivery Head")

    return ""


def _set_candidate_meeting_status(candidate: Candidate) -> None:
    if not hasattr(candidate, "status"):
        return

    status_value = getattr(candidate, "status")
    if isinstance(status_value, Enum):
        status_enum = status_value.__class__
        if "IN_PROGRESS" in status_enum.__members__:
            candidate.status = status_enum.IN_PROGRESS
        return

    # Best effort for string-backed status fields
    if isinstance(candidate.status, str):
        candidate.status = "in_progress"


def _meeting_type_task_keywords(canonical_meeting_type: str) -> tuple[str, ...]:
    if canonical_meeting_type == "HR Introduction":
        return ("hr walkthrough", "meeting: hr", "hr")
    if canonical_meeting_type == "Manager Introduction":
        return ("reporting manager", "manager")
    return ("delivery head", "practice head")


def _find_candidate_meeting_task(candidate: Candidate, canonical_meeting_type: str) -> Optional[Task]:
    checklist = getattr(candidate, "checklist", None)
    if not checklist:
        return None

    keywords = _meeting_type_task_keywords(canonical_meeting_type)
    for task in checklist.tasks:
        if task.task_type != "meeting_scheduling":
            continue
        task_name = (task.name or "").lower()
        if any(keyword in task_name for keyword in keywords):
            return task
    return None


def _find_stakeholder_by_name(db: Session, interviewer_name: str) -> Optional[Stakeholder]:
    normalized = interviewer_name.strip().lower()
    if not normalized:
        return None

    # exact, case-insensitive
    stakeholder = (
        db.query(Stakeholder)
        .filter(func.lower(Stakeholder.name) == normalized)
        .first()
    )
    if stakeholder:
        return stakeholder

    # first token match
    first_token = normalized.split()[0]
    stakeholders = db.query(Stakeholder).all()
    for person in stakeholders:
        person_first = (person.name or "").strip().lower().split()
        if person_first and person_first[0] == first_token:
            return person
    return None


def _apply_task_booking_details(
    *,
    db: Session,
    candidate: Candidate,
    canonical_meeting_type: str,
    booking: Dict[str, str],
) -> None:
    task = _find_candidate_meeting_task(candidate, canonical_meeting_type)
    if not task:
        return

    task.status = TaskStatus.IN_PROGRESS
    task.meeting_scheduled_time = f"{booking.get('date', '')} {booking.get('time', '')}".strip()
    task.assigned_to_name = booking.get("interviewer_name")

    stakeholder = _find_stakeholder_by_name(db, booking.get("interviewer_name", ""))
    if stakeholder:
        task.assigned_to_id = stakeholder.id
        task.assigned_to_email = stakeholder.email


@router.get("/slots")
async def get_slots(
    candidate_name: str = Query(..., description="Candidate name from UI profile context"),
    meeting_type: str = Query(..., description="Meeting type"),
    interviewer_name: Optional[str] = Query(None, description="Optional interviewer override"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    candidate = _find_candidate(db, candidate_name)
    canonical_meeting_type = _canonical_meeting_type(meeting_type)
    role_filter = _role_filter_for_meeting_type(canonical_meeting_type)

    assigned_to = _assigned_person_for_meeting(candidate, canonical_meeting_type)
    if not assigned_to:
        raise HTTPException(
            status_code=404,
            detail=f"No assignee configured for '{meeting_type}' on candidate '{candidate.name}'.",
        )

    requested_name = (
        interviewer_name.strip()
        if isinstance(interviewer_name, str) and interviewer_name.strip()
        else assigned_to
    )
    effective_interviewer = _resolve_interviewer_name(requested_name, role_filter)
    if not effective_interviewer:
        raise HTTPException(
            status_code=404,
            detail=f"No interviewers found for role '{role_filter}'.",
        )

    available_slots = get_all_available_slots(effective_interviewer)
    smart_suggestion = get_first_available_slot(effective_interviewer)

    return {
        "candidate_name": candidate.name,
        "meeting_type": canonical_meeting_type,
        "assigned_to": assigned_to,
        "selected_interviewer": effective_interviewer,
        "smart_suggestion": smart_suggestion,
        "available_slots": available_slots,
        "all_interviewers": get_all_interviewers(role_filter=role_filter),
    }


@router.post("/book")
async def book_meeting(payload: BookMeetingRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    candidate = _find_candidate(db, payload.candidate_name)
    canonical_meeting_type = _canonical_meeting_type(payload.meeting_type)
    role_filter = _role_filter_for_meeting_type(canonical_meeting_type)
    resolved_interviewer = _resolve_interviewer_name(payload.interviewer_name, role_filter)

    booking_result = book_slot(
        candidate_name=candidate.name,
        meeting_type=canonical_meeting_type,
        interviewer_name=resolved_interviewer or payload.interviewer_name,
        date=payload.date,
        time=payload.time,
        booked_by=payload.booked_by or "HR",
    )

    if not booking_result.get("success"):
        error = booking_result.get("error")
        if error in {"slot_not_found", "slot_unavailable"}:
            raise HTTPException(status_code=409, detail=booking_result.get("message"))
        raise HTTPException(status_code=500, detail=booking_result.get("message", "Booking failed."))

    booking = booking_result["booking"]
    _set_candidate_meeting_status(candidate)
    _apply_task_booking_details(
        db=db,
        candidate=candidate,
        canonical_meeting_type=canonical_meeting_type,
        booking=booking,
    )
    db.commit()

    log_activity(
        db,
        user_name=payload.booked_by or "HR",
        user_role="HR",
        action_text=f"scheduled {canonical_meeting_type} for {candidate.name}.",
        target_object=f"{booking.get('date', '')} {booking.get('time', '')}".strip(),
        activity_type="meeting",
        icon_type="calendar",
    )

    return {"message": "Meeting booked successfully.", "booking": booking}


def _try_auto_booking(
    *,
    candidate_name: str,
    meeting_type: str,
    primary_person: str,
    backup_person: Optional[str],
    booked_by: str,
    llm,
) -> Dict[str, Any]:
    decision = ask_llm_for_slot(
        candidate_name=candidate_name,
        meeting_type=meeting_type,
        primary_person=primary_person,
        backup_person=backup_person,
        llm=llm,
    )

    if not decision.get("success"):
        return {
            "status": "PENDING",
            "reason": decision.get("reason", f"No available slots found for {primary_person}."),
            "fallback_note": decision.get("fallback_note", "N/A"),
        }

    booking_result = book_slot(
        candidate_name=candidate_name,
        meeting_type=meeting_type,
        interviewer_name=decision["interviewer"],
        date=decision["date"],
        time=decision["time"],
        booked_by=booked_by,
    )
    if not booking_result.get("success"):
        return {
            "status": "PENDING",
            "reason": booking_result.get("message", "Could not book selected slot."),
            "fallback_note": decision.get("fallback_note", "N/A"),
        }

    used_fallback = (
        bool(backup_person)
        and decision["interviewer"].strip().lower() == backup_person.strip().lower()
    )
    result: Dict[str, Any] = {
        "status": "CONFIRMED",
        "booking": booking_result["booking"],
        "reason": decision.get("reason", ""),
        "fallback_note": decision.get("fallback_note", "N/A"),
    }
    if used_fallback:
        result["fallback_used"] = True
        result["fallback_person"] = backup_person
    return result


@router.post("/auto")
async def auto_schedule(
    candidate_name: str = Query(..., description="Candidate name"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    candidate = _find_candidate(db, candidate_name)
    llm = get_llm(temperature=0.0)

    hr_assignee = _assigned_person_for_meeting(candidate, "HR Introduction")
    manager_assignee = _assigned_person_for_meeting(candidate, "Manager Introduction")
    backup_assignee = _assigned_person_for_meeting(candidate, "Delivery Head Introduction")

    if not hr_assignee:
        hr_result: Dict[str, Any] = {
            "status": "PENDING",
            "reason": "No HR interviewer configured for this candidate.",
        }
    else:
        hr_result = _try_auto_booking(
            candidate_name=candidate.name,
            meeting_type="HR Introduction",
            primary_person=hr_assignee,
            backup_person=None,
            booked_by="Scheduling Agent",
            llm=llm,
        )

    if not manager_assignee:
        manager_result: Dict[str, Any] = {
            "status": "PENDING",
            "reason": "No manager interviewer configured for this candidate.",
        }
    else:
        manager_result = _try_auto_booking(
            candidate_name=candidate.name,
            meeting_type="Manager Introduction",
            primary_person=manager_assignee,
            backup_person=backup_assignee,
            booked_by="Scheduling Agent",
            llm=llm,
        )

    if hr_result["status"] == "CONFIRMED":
        _apply_task_booking_details(
            db=db,
            candidate=candidate,
            canonical_meeting_type="HR Introduction",
            booking=hr_result["booking"],
        )
    if manager_result["status"] == "CONFIRMED":
        _apply_task_booking_details(
            db=db,
            candidate=candidate,
            canonical_meeting_type="Manager Introduction",
            booking=manager_result["booking"],
        )

    if hr_result["status"] == "CONFIRMED" or manager_result["status"] == "CONFIRMED":
        _set_candidate_meeting_status(candidate)
        db.commit()

    return {
        "candidate_name": candidate.name,
        "hr_meeting": hr_result,
        "manager_meeting": manager_result,
        "scheduled_by": "Groq LLM (llama-3.3-70b-versatile)",
    }


@router.get("/meetings")
async def get_meetings(
    candidate_name: str = Query(..., description="Candidate name"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    candidate = _find_candidate(db, candidate_name)
    meetings = get_meetings_for_candidate(candidate.name)
    return {"candidate_name": candidate.name, "meetings": meetings}
