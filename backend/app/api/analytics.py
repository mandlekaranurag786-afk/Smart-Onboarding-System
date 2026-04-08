"""
Analytics API endpoints
"""
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.candidate import Candidate, CandidateStatus
from app.models.checklist import Checklist
from app.models.task import Task, TaskStatus, TaskOwner

router = APIRouter()

class OnboardedMetrics(BaseModel):
    total: int
    this_week: int

class InProgressMetrics(BaseModel):
    total: int

class PendingTasksMetrics(BaseModel):
    total: int
    it: int
    hr: int
    candidate: int

class AvgOnboardingTimeMetrics(BaseModel):
    avg_days: float

class AnalyticsResponse(BaseModel):
    onboarded: OnboardedMetrics
    in_progress: InProgressMetrics
    pending_tasks: PendingTasksMetrics
    avg_onboarding_time: AvgOnboardingTimeMetrics


def _build_candidate_date_filters(date_filter: Optional[str]) -> List:
    if not date_filter:
        return []

    try:
        parsed_date = datetime.strptime(date_filter, "%d/%m/%Y")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use dd/mm/yyyy")

    next_day = parsed_date + timedelta(days=1)
    return [
        Candidate.created_at >= parsed_date,
        Candidate.created_at < next_day,
    ]


def _task_count(db: Session, owner: TaskOwner, statuses: List[TaskStatus], date_filters: List) -> int:
    query = db.query(func.count(Task.id))
    if date_filters:
        query = query.join(Task.checklist).join(Checklist.candidate).filter(*date_filters)
    count = query.filter(Task.owner == owner, Task.status.in_(statuses)).scalar() or 0
    return int(count)


@router.get("/dashboard", response_model=AnalyticsResponse)
async def get_analytics_dashboard(date: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get analytics dashboard data.

    Optional query param `date` accepts dd/mm/yyyy and filters candidates by that date.
    """
    date_filters = _build_candidate_date_filters(date)

    onboarded_total = db.query(func.count(Candidate.id)).filter(
        Candidate.status == CandidateStatus.ONBOARDED,
        *date_filters
    ).scalar() or 0

    week_start = datetime.utcnow() - timedelta(days=7)
    onboarded_this_week = db.query(func.count(Candidate.id)).filter(
        Candidate.status == CandidateStatus.ONBOARDED,
        Candidate.created_at >= week_start,
        *date_filters
    ).scalar() or 0

    in_progress_total = db.query(func.count(Candidate.id)).filter(
        Candidate.status != CandidateStatus.ONBOARDED,
        *date_filters
    ).scalar() or 0

    it_pending = _task_count(
        db,
        TaskOwner.IT,
        [TaskStatus.PENDING],
        date_filters
    )
    hr_pending = _task_count(
        db,
        TaskOwner.HR,
        [TaskStatus.PENDING],
        date_filters
    )
    candidate_pending = _task_count(
        db,
        TaskOwner.CANDIDATE,
        [TaskStatus.PENDING],
        date_filters
    )

    total_pending = it_pending + hr_pending + candidate_pending

    completed_candidates = db.query(Candidate).filter(
        Candidate.status == CandidateStatus.ONBOARDED,
        Candidate.completed_at.isnot(None),
        *date_filters
    ).all()

    if completed_candidates:
        total_days = 0.0
        total_count = 0
        for candidate in completed_candidates:
            if candidate.created_at and candidate.completed_at:
                delta = candidate.completed_at - candidate.created_at
                total_days += delta.total_seconds() / 86400
                total_count += 1
        avg_days = round((total_days / total_count) if total_count else 0.0, 1)
    else:
        avg_days = 0.0

    return {
        "onboarded": {
            "total": int(onboarded_total),
            "this_week": int(onboarded_this_week),
        },
        "in_progress": {
            "total": int(in_progress_total),
        },
        "pending_tasks": {
            "total": int(total_pending),
            "it": int(it_pending),
            "hr": int(hr_pending),
            "candidate": int(candidate_pending),
        },
        "avg_onboarding_time": {
            "avg_days": avg_days,
        },
    }
