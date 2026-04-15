"""
Candidates API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import date, datetime
import asyncio

from app.database import get_db
from app.models.candidate import Candidate, CandidateStatus
from app.models.checklist import Checklist
from app.models.task import Task, TaskStatus
from app.api.activities import log_activity
from app.api.auth import get_current_user

router = APIRouter()

# Pydantic schemas
class CandidateCreate(BaseModel):
    name: str
    email: str
    department: str
    role: str = "Employee"
    joining_date: str  # Format: "YYYY-MM-DD" or "DD/MM/YYYY"
    reporting_manager: str = None
    reporting_manager_email: str = None

class CandidateResponse(BaseModel):
    id: int
    name: str
    email: str
    department: str
    role: str
    joining_date: str
    reporting_manager: str
    status: str
    completion_percentage: float
    total_tasks: int
    completed_tasks: int
    
    class Config:
        from_attributes = True

@router.post("/", response_model=CandidateResponse)
async def create_candidate(candidate_data: CandidateCreate, db: Session = Depends(get_db)):
    """
    Create a new candidate and trigger onboarding flow using LangGraph
    
    This endpoint:
    1. Triggers the LangGraph workflow
    2. Creates candidate record
    3. Generates checklist
    4. Sends notifications
    5. Returns candidate with progress
    """
    try:
        # Parse joining date (handle both formats)
        joining_date_str = candidate_data.joining_date
        if "/" in joining_date_str:
            # DD/MM/YYYY format
            day, month, year = joining_date_str.split("/")
            joining_date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Prepare data for LangGraph workflow
        candidate_dict = {
            "name": candidate_data.name,
            "email": candidate_data.email,
            "department": candidate_data.department,
            "role": candidate_data.role,
            "joining_date": joining_date_str,
            "reporting_manager": candidate_data.reporting_manager,
            "reporting_manager_email": candidate_data.reporting_manager_email
        }
        
        # Run LangGraph workflow
        from app.agents.graph import run_onboarding_workflow
        result = await run_onboarding_workflow(candidate_dict)
        
        if result["status"] != "success":
            raise HTTPException(status_code=500, detail=f"Onboarding failed: {result.get('error')}")
        
        # Get the created candidate from database
        candidate = db.query(Candidate).filter_by(email=candidate_data.email).first()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found after creation")
        
        # Calculate progress
        checklist = candidate.checklist
        total_tasks = len(checklist.tasks) if checklist else 0
        completed_tasks = sum(1 for task in checklist.tasks if task.status.value == "completed") if checklist else 0
        completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Log activity
        log_activity(
            db,
            user_name=candidate.name,
            user_role="Candidate",
            action_text=f"started the onboarding process.",
            target_object=candidate.role or "Position",
            activity_type="candidate",
            icon_type="user"
        )
        
        return CandidateResponse(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            department=candidate.department,
            role=candidate.role,
            joining_date=candidate.joining_date.isoformat(),
            reporting_manager=candidate.reporting_manager or "",
            status=candidate.status.value,
            completion_percentage=completion_percentage,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[CandidateResponse])
async def get_candidates(db: Session = Depends(get_db)):
    """Get all candidates with their progress"""
    candidates = db.query(Candidate).all()
    
    result = []
    for candidate in candidates:
        checklist = candidate.checklist
        total_tasks = len(checklist.tasks) if checklist else 0
        completed_tasks = sum(1 for task in checklist.tasks if task.status.value == "completed") if checklist else 0
        completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        result.append(CandidateResponse(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            department=candidate.department,
            role=candidate.role,
            joining_date=candidate.joining_date.isoformat(),
            reporting_manager=candidate.reporting_manager or "",
            status=candidate.status.value,
            completion_percentage=completion_percentage,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks
        ))
    
    return result

@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get a specific candidate by ID"""
    candidate = db.query(Candidate).filter_by(id=candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    checklist = candidate.checklist
    total_tasks = len(checklist.tasks) if checklist else 0
    completed_tasks = sum(1 for task in checklist.tasks if task.status.value == "completed") if checklist else 0
    completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return CandidateResponse(
        id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        department=candidate.department,
        role=candidate.role,
        joining_date=candidate.joining_date.isoformat(),
        reporting_manager=candidate.reporting_manager or "",
        status=candidate.status.value,
        completion_percentage=completion_percentage,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks
    )

@router.get("/{candidate_id}/progress")
async def get_candidate_progress(candidate_id: int, db: Session = Depends(get_db)):
    """Get detailed progress for a candidate"""
    candidate = db.query(Candidate).filter_by(id=candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    checklist = candidate.checklist
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    
    tasks = []
    for task in checklist.tasks:
        tasks.append({
            "id": task.id,
            "name": task.name,
            "task_type": task.task_type,
            "owner": task.owner.value,
            "status": task.status.value,
            "assigned_to": task.assigned_to_name,
            "assigned_to_name": task.assigned_to_name,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed_date": task.completed_date.isoformat() if task.completed_date else None,
            "meeting_scheduled_time": task.meeting_scheduled_time,
            "is_fallback": bool(task.is_fallback),
            "fallback_reason": task.fallback_reason,
            "it_response_received_at": task.it_response_received_at.isoformat() if task.it_response_received_at else None,
            "it_responder_name": task.it_responder_name,
            "it_responder_email": task.it_responder_email,
            "created_at": task.created_at.isoformat(),
        })
    
    return {
        "candidate_id": candidate.id,
        "candidate_name": candidate.name,
        "status": candidate.status.value,
        "completion_percentage": checklist.completion_percentage,
        "total_tasks": len(tasks),
        "completed_tasks": sum(1 for t in tasks if t["status"] == "completed"),
        "tasks": tasks
    }


# ============================================
# CANDIDATE PORTAL ENDPOINTS (JWT Protected)
# ============================================

@router.patch("/me/tasks/{task_id}/complete")
async def complete_my_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Allow logged-in candidate to acknowledge eligible checklist tasks.
    """
    try:
        if current_user["user_type"] != "candidate":
            raise HTTPException(status_code=403, detail="Not a candidate")

        candidate = current_user["user"]

        task = db.query(Task).join(Checklist).filter(
            Task.id == task_id,
            Checklist.candidate_id == candidate.id
        ).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        owner_value = task.owner.value if hasattr(task.owner, "value") else str(task.owner)
        owner_key = owner_value.strip().upper().replace(" ", "_")
        task_name = (task.name or "").strip().lower()
        is_meeting_task = "meeting" in task_name
        is_final_review_task = "final review" in task_name

        if is_final_review_task:
            raise HTTPException(status_code=403, detail="You cannot complete this task")

        if is_meeting_task:
            if not task.meeting_scheduled_time:
                raise HTTPException(
                    status_code=403,
                    detail="Waiting for HR to schedule this meeting"
                )
        else:
            allowed_owners = {"HR", "CANDIDATE", "SYSTEM"}
            if owner_key not in allowed_owners:
                raise HTTPException(
                    status_code=403,
                    detail="You cannot complete this task"
                )

        task.status = TaskStatus.COMPLETED
        task.completed_date = datetime.utcnow().date()

        checklist = task.checklist
        if checklist:
            checklist.calculate_completion()

        if checklist and checklist.completion_percentage == 100.0:
            candidate.status = CandidateStatus.ONBOARDED

        db.commit()

        log_activity(
            db,
            user_name=candidate.name,
            user_role="Candidate",
            action_text=f"completed the {task.name} task.",
            target_object=task.name,
            activity_type="candidate",
            icon_type="check"
        )

        return {
            "message": "Task completed successfully",
            "task_id": task_id,
            "completion_percentage": checklist.completion_percentage if checklist else 0.0
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me/profile")
async def get_my_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get logged-in candidate's profile
    Protected endpoint - requires JWT authentication
    """
    # Verify user is a candidate
    if current_user["user_type"] != "candidate":
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only accessible to candidates"
        )
    
    candidate = current_user["user"]
    
    return {
        "id": candidate.id,
        "name": candidate.name,
        "email": candidate.email,
        "department": candidate.department,
        "role": candidate.role,
        "joining_date": candidate.joining_date.isoformat(),
        "reporting_manager": candidate.reporting_manager,
        "reporting_manager_email": candidate.reporting_manager_email,
        "status": candidate.status.value,
        "account_status": candidate.account_status.value,
        "password_reset_required": bool(candidate.password_reset_required)
    }


@router.get("/me/tasks")
async def get_my_tasks(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get logged-in candidate's tasks
    Protected endpoint - requires JWT authentication
    Only returns tasks assigned to the authenticated candidate
    """
    # Verify user is a candidate
    if current_user["user_type"] != "candidate":
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only accessible to candidates"
        )
    
    candidate = current_user["user"]
    
    # Get candidate's checklist
    if not candidate.checklist:
        return {
            "candidate_id": candidate.id,
            "candidate_name": candidate.name,
            "tasks": [],
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0
        }
    
    # Get all tasks from the checklist
    tasks = []
    completed_count = 0
    pending_count = 0
    
    for task in candidate.checklist.tasks:
        task_data = {
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "task_type": task.task_type,
            "owner": task.owner.value,
            "status": task.status.value,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed_date": task.completed_date.isoformat() if task.completed_date else None,
            "meeting_scheduled_time": task.meeting_scheduled_time,
            "assigned_to_name": task.assigned_to_name,
            "assigned_to_email": task.assigned_to_email
        }
        tasks.append(task_data)
        
        if task.status.value == "completed":
            completed_count += 1
        else:
            pending_count += 1
    
    return {
        "candidate_id": candidate.id,
        "candidate_name": candidate.name,
        "tasks": tasks,
        "total_tasks": len(tasks),
        "completed_tasks": completed_count,
        "pending_tasks": pending_count
    }


@router.get("/me/checklist")
async def get_my_checklist(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get logged-in candidate's checklist with progress
    Protected endpoint - requires JWT authentication
    """
    # Verify user is a candidate
    if current_user["user_type"] != "candidate":
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only accessible to candidates"
        )
    
    candidate = current_user["user"]
    
    # Get candidate's checklist
    if not candidate.checklist:
        raise HTTPException(
            status_code=404,
            detail="Checklist not found for this candidate"
        )
    
    checklist = candidate.checklist
    
    # Organize tasks by owner/category
    tasks_by_owner = {}
    for task in checklist.tasks:
        owner = task.owner.value
        if owner not in tasks_by_owner:
            tasks_by_owner[owner] = []
        
        tasks_by_owner[owner].append({
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "task_type": task.task_type,
            "status": task.status.value,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed_date": task.completed_date.isoformat() if task.completed_date else None,
            "assigned_to_name": task.assigned_to_name
        })
    
    total_tasks = len(checklist.tasks)
    completed_tasks = sum(1 for task in checklist.tasks if task.status.value == "completed")
    
    return {
        "checklist_id": checklist.id,
        "candidate_id": candidate.id,
        "candidate_name": candidate.name,
        "completion_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": total_tasks - completed_tasks,
        "tasks_by_owner": tasks_by_owner,
        "created_at": checklist.created_at.isoformat(),
        "updated_at": checklist.updated_at.isoformat()
    }
