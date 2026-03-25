"""
Candidates API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import date
import asyncio

from app.database import get_db
from app.models.candidate import Candidate, CandidateStatus
from app.models.checklist import Checklist
from app.models.task import Task
from app.agents.orchestrator import OrchestratorAgent

router = APIRouter()

# Pydantic schemas
class CandidateCreate(BaseModel):
    name: str
    email: str
    department: str
    role: str = "Employee"
    joining_date: str  # Format: "YYYY-MM-DD" or "DD/MM/YYYY"
    reporting_manager: str = None

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
    Create a new candidate and trigger onboarding flow
    
    This endpoint:
    1. Triggers the orchestrator agent
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
        
        # Prepare data for orchestrator
        candidate_dict = {
            "name": candidate_data.name,
            "email": candidate_data.email,
            "department": candidate_data.department,
            "role": candidate_data.role,
            "joining_date": joining_date_str,
            "reporting_manager": candidate_data.reporting_manager
        }
        
        # Trigger orchestrator agent
        orchestrator = OrchestratorAgent()
        result = await orchestrator.start_onboarding(candidate_dict)
        
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
            "owner": task.owner.value,
            "status": task.status.value,
            "assigned_to": task.assigned_to_name,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed_date": task.completed_date.isoformat() if task.completed_date else None
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
