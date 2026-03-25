"""
Tasks API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.task import Task, TaskStatus

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
