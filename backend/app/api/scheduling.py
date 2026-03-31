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

from app.database import get_db
from app.llm_client import get_llm
from app.models.candidate import Candidate
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


def _assigned_person_for_meeting(candidate: Candidate, meeting_type: str) -> str:
    canonical_type = _canonical_meeting_type(meeting_type)

    if canonical_type == "HR Introduction":
        return _candidate_field(candidate, "assigned_hr") or _default_interviewer_name("HR")

    if canonical_type == "Manager Introduction":
        return _candidate_field(
            candidate, "assigned_manager", "reporting_to", "reporting_manager"
        ) or _default_interviewer_name("Manager")

    if canonical_type == "Delivery Head Introduction":
        return _candidate_field(
            candidate, "backup_manager", "assigned_manager", "reporting_to", "reporting_manager"
        ) or _default_interviewer_name("Delivery Head")
    return ""


def _set_candidate_meeting_status(candidate: Candidate) -> None:
    if hasattr(candidate, "current_status"):
        setattr(candidate, "current_status", "meeting_scheduled")
        return

    if not hasattr(candidate, "status"):
        return

    status_value = getattr(candidate, "status")
    if isinstance(status_value, Enum):
        status_enum = status_value.__class__
        if "MEETING_SCHEDULED" in status_enum.__members__:
            candidate.status = status_enum.MEETING_SCHEDULED
        elif "IN_PROGRESS" in status_enum.__members__:
            candidate.status = status_enum.IN_PROGRESS
        return

    setattr(candidate, "status", "meeting_scheduled")


@router.get("/slots")
async def get_slots(
    candidate_name: str = Query(..., description="Candidate name from UI profile context"),
    meeting_type: str = Query(..., description="Meeting type"),
    interviewer_name: Optional[str] = Query(None, description="Optional interviewer override"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    candidate = _find_candidate(db, candidate_name)
    canonical_meeting_type = _canonical_meeting_type(meeting_type)
    assigned_to = _assigned_person_for_meeting(candidate, canonical_meeting_type)

    if not assigned_to:
        raise HTTPException(
            status_code=404,
            detail=f"No assignee configured for '{meeting_type}' on candidate '{candidate.name}'.",
        )

    effective_interviewer = (
        interviewer_name.strip()
        if isinstance(interviewer_name, str) and interviewer_name.strip()
        else assigned_to
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
        "all_interviewers": get_all_interviewers(
            role_filter=_role_filter_for_meeting_type(canonical_meeting_type)
        ),
    }


@router.post("/book")
async def book_meeting(payload: BookMeetingRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    candidate = _find_candidate(db, payload.candidate_name)
    canonical_meeting_type = _canonical_meeting_type(payload.meeting_type)

    booking_result = book_slot(
        candidate_name=candidate.name,
        meeting_type=canonical_meeting_type,
        interviewer_name=payload.interviewer_name,
        date=payload.date,
        time=payload.time,
        booked_by=payload.booked_by or "HR",
    )

    if not booking_result.get("success"):
        error = booking_result.get("error")
        if error in {"slot_not_found", "slot_unavailable"}:
            raise HTTPException(status_code=409, detail=booking_result.get("message"))
        raise HTTPException(status_code=500, detail=booking_result.get("message", "Booking failed."))

    _set_candidate_meeting_status(candidate)
    db.commit()

    return {"message": "Meeting booked successfully.", "booking": booking_result["booking"]}


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
            "reason": "No assigned_hr configured for this candidate.",
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

    manager_result: Dict[str, Any]
    if not manager_assignee:
        manager_result = {
            "status": "PENDING",
            "reason": "No assigned_manager configured for this candidate.",
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
