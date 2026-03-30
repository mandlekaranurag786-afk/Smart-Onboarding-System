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
    
    return {
        "id": task.id,
        "name": task.name,
        "status": task.status.value,
        "skipped": True,
        "reason": task.fallback_reason,
        "message": "Task skipped successfully"
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
            completed_date=task.completed_date.isoformat() if task.completed_date else None
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
        completed_date=task.completed_date.isoformat() if task.completed_date else None
    )
