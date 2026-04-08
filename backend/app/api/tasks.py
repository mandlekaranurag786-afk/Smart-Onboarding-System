"""
Tasks API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.task import Task, TaskStatus
from app.models.candidate import Candidate, CandidateStatus

router = APIRouter()

class TaskUpdate(BaseModel):
    status: str  # "pending", "in_progress", "completed", "overdue", "blocked"

@router.patch("/{task_id}")
async def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """Update task status"""
    task = db.query(Task).filter_by(id=task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update status
    try:
        task.status = TaskStatus[task_update.status.upper()]
        
        # Set completed_date if task is being marked as completed
        if task_update.status.upper() == "COMPLETED" and not task.completed_date:
            task.completed_date = datetime.now()
        
        db.commit()
        
        # Recalculate checklist completion
        checklist = task.checklist
        if checklist:
            checklist.calculate_completion()
            
            # Check if all tasks are completed and update candidate status
            all_tasks_completed = all(t.status == TaskStatus.COMPLETED for t in checklist.tasks)
            if all_tasks_completed and checklist.candidate.status != CandidateStatus.ONBOARDED:
                checklist.candidate.status = CandidateStatus.ONBOARDED
                checklist.candidate.completed_at = datetime.now()
            
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
