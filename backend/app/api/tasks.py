"""
Tasks API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

from app.database import get_db
from app.models.task import Task, TaskStatus
from app.models.candidate import Candidate
from app.api.activities import log_activity

router = APIRouter()

class TaskUpdate(BaseModel):
    status: str  # "pending", "in_progress", "completed", "overdue", "blocked"

class TaskResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    task_type: str
    owner: str
    assigned_to_name: Optional[str]
    status: str
    due_date: Optional[str]
    completed_date: Optional[str]
    is_fallback: Optional[bool] = False
    fallback_reason: Optional[str] = None

@router.patch("/{task_id}")
async def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """Update task status"""
    task = db.query(Task).filter_by(id=task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update status
    try:
        task.status = TaskStatus[task_update.status.upper()]
        
        # Set completed date if status is completed
        if task.status == TaskStatus.COMPLETED:
            task.completed_date = date.today()
        
        db.commit()
        
        # Recalculate checklist completion
        checklist = task.checklist
        if checklist:
            checklist.calculate_completion()
            db.commit()
            
            # Log activity
            log_activity(
                db,
                user_name=task.checklist.candidate.name if task.checklist and task.checklist.candidate else "System",
                user_role="Candidate",
                action_text=f"completed the {task.name} task.",
                target_object=task.name,
                activity_type="candidate",
                icon_type="check"
            )
        
        return {
            "id": task.id,
            "name": task.name,
            "status": task.status.value,
            "message": "Task updated successfully"
        }
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {task_update.status}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{task_id}/status")
async def update_task_status(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """Alias endpoint for task status updates."""
    return await update_task(task_id, task_update, db)

@router.post("/{task_id}/skip")
async def skip_task(task_id: int, reason: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Skip a task (mark as completed with skip flag)
    """
    task = db.query(Task).filter_by(id=task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Mark as completed but flag as skipped
    task.status = TaskStatus.COMPLETED
    task.completed_date = date.today()
    task.fallback_reason = reason or "Task skipped by user"
    task.is_fallback = 1
    
    db.commit()
    
    # Recalculate checklist completion
    checklist = task.checklist
    if checklist:
        checklist.calculate_completion()
        db.commit()
    
    # Log activity
    log_activity(
        db,
        user_name=task.checklist.candidate.name if task.checklist and task.checklist.candidate else "System",
        user_role="Candidate",
        action_text=f"skipped the {task.name} task.",
        target_object=task.name,
        activity_type="candidate",
        icon_type="alert"
    )
    
    return {
        "id": task.id,
        "name": task.name,
        "status": task.status.value,
        "skipped": True,
        "reason": task.fallback_reason,
        "message": "Task skipped successfully"
    }

@router.post("/{task_id}/recover")
async def recover_task(task_id: int, db: Session = Depends(get_db)):
    """
    Recover a skipped task (mark as pending and clear skip flag)
    """
    task = db.query(Task).filter_by(id=task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Mark as pending and clear skip flag
    task.status = TaskStatus.PENDING
    task.completed_date = None
    task.is_fallback = 0
    task.fallback_reason = None
    
    db.commit()
    
    # Recalculate checklist completion
    checklist = task.checklist
    if checklist:
        checklist.calculate_completion()
        db.commit()
    
    # Log activity
    log_activity(
        db,
        user_name=task.checklist.candidate.name if task.checklist and task.checklist.candidate else "System",
        user_role="Candidate",
        action_text=f"recovered the {task.name} task.",
        target_object=task.name,
        activity_type="candidate",
        icon_type="rotate-cw"
    )
    
    return {
        "id": task.id,
        "name": task.name,
        "status": task.status.value,
        "skipped": False,
        "message": "Task recovered successfully"
    }

@router.post("/{task_id}/complete")
async def complete_task(task_id: int, notes: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Mark a task as complete
    """
    task = db.query(Task).filter_by(id=task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task.status = TaskStatus.COMPLETED
    task.completed_date = date.today()
    
    if notes:
        task.description = f"{task.description}\n\nCompletion Notes: {notes}" if task.description else f"Completion Notes: {notes}"
    
    db.commit()
    
    # Recalculate checklist completion
    checklist = task.checklist
    if checklist:
        checklist.calculate_completion()
        db.commit()
    
    # Log activity
    log_activity(
        db,
        user_name=task.checklist.candidate.name if task.checklist and task.checklist.candidate else "System",
        user_role="Candidate",
        action_text=f"completed the {task.name} task.",
        target_object=task.name,
        activity_type="candidate",
        icon_type="check"
    )
    
    return {
        "id": task.id,
        "name": task.name,
        "status": task.status.value,
        "completed_date": task.completed_date.isoformat(),
        "message": "Task completed successfully"
    }

@router.get("/candidate/{candidate_id}", response_model=List[TaskResponse])
async def get_candidate_tasks(candidate_id: int, db: Session = Depends(get_db)):
    """
    Get all tasks for a specific candidate
    """
    candidate = db.query(Candidate).filter_by(id=candidate_id).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    if not candidate.checklist:
        return []
    
    tasks = candidate.checklist.tasks
    
    return [
        TaskResponse(
            id=task.id,
            name=task.name,
            description=task.description,
            task_type=task.task_type,
            owner=task.owner.value,
            assigned_to_name=task.assigned_to_name,
            status=task.status.value,
            due_date=task.due_date.isoformat() if task.due_date else None,
            completed_date=task.completed_date.isoformat() if task.completed_date else None,
            is_fallback=bool(task.is_fallback),
            fallback_reason=task.fallback_reason
        )
        for task in tasks
    ]

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Get a specific task by ID
    """
    task = db.query(Task).filter_by(id=task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return TaskResponse(
        id=task.id,
        name=task.name,
        description=task.description,
        task_type=task.task_type,
        owner=task.owner.value,
        assigned_to_name=task.assigned_to_name,
        status=task.status.value,
        due_date=task.due_date.isoformat() if task.due_date else None,
        completed_date=task.completed_date.isoformat() if task.completed_date else None,
        is_fallback=bool(task.is_fallback),
        fallback_reason=task.fallback_reason
    )


# ============================================
# CANDIDATE PORTAL TASK ENDPOINTS (JWT Protected)
# ============================================

from app.api.auth import get_current_user
from app.models.task import TaskOwner

@router.post("/me/{task_id}/complete")
async def candidate_complete_task(
    task_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Allow candidate to mark their own task as complete
    Protected endpoint - requires JWT authentication
    Only allows candidates to complete tasks assigned to them
    """
    # Verify user is a candidate
    if current_user["user_type"] != "candidate":
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only accessible to candidates"
        )
    
    candidate = current_user["user"]
    
    # Get the task
    task = db.query(Task).filter_by(id=task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    
    # Verify task belongs to this candidate
    if task.checklist.candidate_id != candidate.id:
        raise HTTPException(
            status_code=403,
            detail="You can only complete your own tasks"
        )
    
    # Verify task is assigned to candidate
    if task.owner != TaskOwner.CANDIDATE:
        raise HTTPException(
            status_code=403,
            detail="This task is not assigned to you. Only HR/IT/Manager can complete this task."
        )
    
    # Check if already completed
    if task.status == TaskStatus.COMPLETED:
        return {
            "id": task.id,
            "name": task.name,
            "status": task.status.value,
            "message": "Task was already completed",
            "completed_date": task.completed_date.isoformat() if task.completed_date else None
        }
    
    # Mark as completed
    task.status = TaskStatus.COMPLETED
    task.completed_date = date.today()
    
    db.commit()
    
    # Recalculate checklist completion
    checklist = task.checklist
    if checklist:
        checklist.calculate_completion()
        db.commit()
    
    # Log activity
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
        "id": task.id,
        "name": task.name,
        "status": task.status.value,
        "completed_date": task.completed_date.isoformat(),
        "completion_percentage": checklist.completion_percentage if checklist else 0,
        "message": "Task completed successfully"
    }


@router.post("/me/{task_id}/start")
async def candidate_start_task(
    task_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Allow candidate to mark their task as in progress
    Protected endpoint - requires JWT authentication
    """
    # Verify user is a candidate
    if current_user["user_type"] != "candidate":
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only accessible to candidates"
        )
    
    candidate = current_user["user"]
    
    # Get the task
    task = db.query(Task).filter_by(id=task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    
    # Verify task belongs to this candidate
    if task.checklist.candidate_id != candidate.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own tasks"
        )
    
    # Verify task is assigned to candidate
    if task.owner != TaskOwner.CANDIDATE:
        raise HTTPException(
            status_code=403,
            detail="This task is not assigned to you"
        )
    
    # Update status to in_progress
    task.status = TaskStatus.IN_PROGRESS
    db.commit()
    
    # Log activity
    log_activity(
        db,
        user_name=candidate.name,
        user_role="Candidate",
        action_text=f"started working on {task.name} task.",
        target_object=task.name,
        activity_type="candidate",
        icon_type="play"
    )
    
    return {
        "id": task.id,
        "name": task.name,
        "status": task.status.value,
        "message": "Task marked as in progress"
    }


@router.get("/me/{task_id}")
async def get_my_task_details(
    task_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific task for logged-in candidate
    Protected endpoint - requires JWT authentication
    """
    # Verify user is a candidate
    if current_user["user_type"] != "candidate":
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only accessible to candidates"
        )
    
    candidate = current_user["user"]
    
    # Get the task
    task = db.query(Task).filter_by(id=task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    
    # Verify task belongs to this candidate
    if task.checklist.candidate_id != candidate.id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own tasks"
        )
    
    return {
        "id": task.id,
        "name": task.name,
        "description": task.description,
        "task_type": task.task_type,
        "owner": task.owner.value,
        "status": task.status.value,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "completed_date": task.completed_date.isoformat() if task.completed_date else None,
        "assigned_to_name": task.assigned_to_name,
        "assigned_to_email": task.assigned_to_email,
        "is_candidate_task": task.owner == TaskOwner.CANDIDATE,
        "can_complete": task.owner == TaskOwner.CANDIDATE and task.status != TaskStatus.COMPLETED
    }
