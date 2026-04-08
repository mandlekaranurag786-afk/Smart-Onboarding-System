"""
Activities API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.activity import Activity

router = APIRouter()

class ActivityResponse(BaseModel):
    id: int
    user_name: str
    user_role: Optional[str]
    action_text: str
    target_object: Optional[str]
    activity_type: str
    icon_type: Optional[str]
    created_at: str

@router.get("/", response_model=List[ActivityResponse])
async def get_activities(limit: int = 20, db: Session = Depends(get_db)):
    """
    Get the latest activities for the live stream
    """
    activities = db.query(Activity).order_by(Activity.created_at.desc()).limit(limit).all()
    
    return [
        ActivityResponse(
            id=a.id,
            user_name=a.user_name,
            user_role=a.user_role,
            action_text=a.action_text,
            target_object=a.target_object,
            activity_type=a.activity_type,
            icon_type=a.icon_type,
            created_at=a.created_at.isoformat() + "Z"
        )
        for a in activities
    ]

# Helper function to log activities (to be used internally)
def log_activity(
    db: Session,
    user_name: str,
    action_text: str,
    user_role: Optional[str] = None,
    target_object: Optional[str] = None,
    activity_type: str = "candidate",
    icon_type: str = "user"
):
    """
    Log a new activity to the stream
    """
    new_activity = Activity(
        user_name=user_name,
        user_role=user_role,
        action_text=action_text,
        target_object=target_object,
        activity_type=activity_type,
        icon_type=icon_type
    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity
