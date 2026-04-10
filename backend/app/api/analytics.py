"""
Analytics & Reporting API endpoints
Provides KPI metrics and onboarding statistics for HR Dashboard
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.candidate import Candidate, CandidateStatus
from app.models.task import Task, TaskStatus
from app.models.checklist import Checklist
from app.models.sla_event import SLAEvent
from app.services.sla_service import SLAService

router = APIRouter()

@router.get("/overview")
async def get_analytics_overview(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get KPI metrics overview
    - Total candidates
    - Onboarding completion rate
    - Average time to onboard
    - Active onboardings
    - Completed onboardings
    """
    # Build query with date filters
    query = db.query(Candidate)
    
    if start_date:
        query = query.filter(Candidate.created_at >= start_date)
    if end_date:
        query = query.filter(Candidate.created_at <= end_date)
    
    candidates = query.all()
    total_candidates = len(candidates)
    
    # Status breakdown
    status_counts = {
        "onboarding_started": 0,
        "in_progress": 0,
        "onboarded": 0,
        "on_hold": 0
    }
    
    total_completion = 0
    onboarding_times = []
    
    for candidate in candidates:
        status_counts[candidate.status.value] += 1
        
        # Calculate completion percentage
        if candidate.checklist:
            total_completion += candidate.checklist.completion_percentage
            
            # Calculate time to onboard for completed candidates
            if candidate.status == CandidateStatus.ONBOARDED:
                days_to_onboard = (candidate.updated_at - candidate.created_at).days
                onboarding_times.append(days_to_onboard)
    
    # Calculate averages
    avg_completion = total_completion / total_candidates if total_candidates > 0 else 0
    avg_time_to_onboard = sum(onboarding_times) / len(onboarding_times) if onboarding_times else 0
    
    # Task statistics
    total_tasks = db.query(Task).count()
    completed_tasks = db.query(Task).filter(Task.status == TaskStatus.COMPLETED).count()
    overdue_tasks = db.query(Task).filter(Task.status == TaskStatus.OVERDUE).count()
    
    return {
        "summary": {
            "total_candidates": total_candidates,
            "active_onboardings": status_counts["in_progress"],
            "completed_onboardings": status_counts["onboarded"],
            "on_hold": status_counts["on_hold"],
            "avg_completion_rate": round(avg_completion, 2),
            "avg_time_to_onboard_days": round(avg_time_to_onboard, 1)
        },
        "status_breakdown": status_counts,
        "tasks": {
            "total": total_tasks,
            "completed": completed_tasks,
            "overdue": overdue_tasks,
            "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
        },
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        **SLAService.get_metrics(db),
    }

@router.get("/applications")
async def get_application_statistics(
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get application/candidate statistics
    - By department
    - By status
    - By joining date
    """
    query = db.query(Candidate)
    
    if department:
        query = query.filter(Candidate.department == department)
    
    candidates = query.all()
    
    # Department breakdown
    dept_stats = {}
    for candidate in candidates:
        dept = candidate.department
        if dept not in dept_stats:
            dept_stats[dept] = {
                "total": 0,
                "onboarded": 0,
                "in_progress": 0
            }
        dept_stats[dept]["total"] += 1
        if candidate.status == CandidateStatus.ONBOARDED:
            dept_stats[dept]["onboarded"] += 1
        elif candidate.status == CandidateStatus.IN_PROGRESS:
            dept_stats[dept]["in_progress"] += 1
    
    # Monthly trend (last 6 months)
    monthly_stats = {}
    for candidate in candidates:
        month_key = candidate.created_at.strftime("%Y-%m")
        if month_key not in monthly_stats:
            monthly_stats[month_key] = 0
        monthly_stats[month_key] += 1
    
    return {
        "total_applications": len(candidates),
        "by_department": dept_stats,
        "monthly_trend": monthly_stats,
        "filter": {
            "department": department
        }
    }

@router.get("/reports/onboarding")
async def get_onboarding_reports(
    candidate_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get detailed onboarding reports
    """
    query = db.query(Candidate)
    
    if candidate_id:
        query = query.filter(Candidate.id == candidate_id)
    
    if status:
        try:
            status_enum = CandidateStatus[status.upper()]
            query = query.filter(Candidate.status == status_enum)
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    candidates = query.all()
    
    reports = []
    for candidate in candidates:
        checklist = candidate.checklist
        
        if not checklist:
            continue
        
        # Task breakdown
        task_breakdown = {
            "pending": 0,
            "in_progress": 0,
            "completed": 0,
            "overdue": 0,
            "blocked": 0
        }
        
        tasks_detail = []
        for task in checklist.tasks:
            task_breakdown[task.status.value] += 1
            tasks_detail.append({
                "id": task.id,
                "name": task.name,
                "owner": task.owner.value,
                "status": task.status.value,
                "assigned_to": task.assigned_to_name,
                "due_date": task.due_date.isoformat() if task.due_date else None
            })
        
        reports.append({
            "candidate": {
                "id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "department": candidate.department,
                "role": candidate.role,
                "joining_date": candidate.joining_date.isoformat(),
                "status": candidate.status.value
            },
            "progress": {
                "completion_percentage": checklist.completion_percentage,
                "total_tasks": len(checklist.tasks),
                "task_breakdown": task_breakdown
            },
            "tasks": tasks_detail,
            "timeline": {
                "started": candidate.created_at.isoformat(),
                "last_updated": candidate.updated_at.isoformat(),
                "days_in_onboarding": (datetime.utcnow() - candidate.created_at).days
            }
        })
    
    return {
        "total_reports": len(reports),
        "reports": reports
    }


@router.get("/sla")
async def get_sla_details(db: Session = Depends(get_db)):
    """
    Get detailed SLA monitoring information for dashboards and admin tooling.
    """
    metrics = SLAService.get_metrics(db)
    recent_events = (
        db.query(SLAEvent)
        .order_by(SLAEvent.triggered_at.desc())
        .limit(20)
        .all()
    )

    return {
        **metrics,
        "recent_events": [
            {
                "task_id": event.task_id,
                "candidate_id": event.candidate_id,
                "event_type": event.event_type,
                "severity": event.severity,
                "title": event.title,
                "message": event.message,
                "owner": event.owner,
                "triggered_at": event.triggered_at.isoformat(),
            }
            for event in recent_events
        ],
    }

@router.get("/dashboard")
async def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    Get comprehensive dashboard metrics for HR
    """
    # Today's stats
    today = datetime.utcnow().date()
    
    # Candidates joining today
    joining_today = db.query(Candidate).filter(
        Candidate.joining_date == today
    ).count()
    
    # Tasks due today
    tasks_due_today = db.query(Task).filter(
        Task.due_date == today,
        Task.status != TaskStatus.COMPLETED
    ).count()
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_candidates = db.query(Candidate).filter(
        Candidate.created_at >= week_ago
    ).count()
    
    # Completion rate trend
    all_checklists = db.query(Checklist).all()
    avg_completion = sum(c.completion_percentage for c in all_checklists) / len(all_checklists) if all_checklists else 0
    
    # Overdue tasks by owner
    overdue_by_owner = db.query(
        Task.owner,
        func.count(Task.id)
    ).filter(
        Task.status == TaskStatus.OVERDUE
    ).group_by(Task.owner).all()
    
    overdue_breakdown = {owner.value: count for owner, count in overdue_by_owner}
    
    return {
        "today": {
            "candidates_joining": joining_today,
            "tasks_due": tasks_due_today
        },
        "recent_activity": {
            "new_candidates_last_7_days": recent_candidates
        },
        "overall": {
            "avg_completion_rate": round(avg_completion, 2),
            "total_active_candidates": db.query(Candidate).filter(
                Candidate.status.in_([CandidateStatus.IN_PROGRESS, CandidateStatus.ONBOARDING_STARTED])
            ).count()
        },
        "overdue_tasks": {
            "total": sum(overdue_breakdown.values()),
            "by_owner": overdue_breakdown
        }
    }
