"""
Stakeholders API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.stakeholder import Stakeholder

router = APIRouter()

@router.get("/")
async def get_stakeholders(db: Session = Depends(get_db)):
    """Get all stakeholders"""
    stakeholders = db.query(Stakeholder).all()
    
    return [
        {
            "id": s.id,
            "name": s.name,
            "email": s.email,
            "role": s.role,
            "department": s.department,
            "is_available": s.is_available,
            "on_leave_until": s.on_leave_until
        }
        for s in stakeholders
    ]
