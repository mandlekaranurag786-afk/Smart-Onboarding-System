"""
Notifications API endpoints
Handles user notifications and alerts
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.base import BaseModel as SQLBaseModel

router = APIRouter()

# Database Model
class Notification(SQLBaseModel):
    """Notification model"""
    __tablename__ = "notifications"
    
    user_id = Column(Integer, nullable=False, index=True)
    user_type = Column(String(50), nullable=False)  # "candidate", "stakeholder"
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(100), nullable=False)  # "task", "meeting", "system", "alert"
    is_read = Column(Boolean, default=False, nullable=False)
    action_url = Column(String(500), nullable=True)
    related_id = Column(Integer, nullable=True)  # Related task/meeting/candidate ID

# Pydantic Schemas
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    user_type: str
    title: str
    message: str
    notification_type: str
    is_read: bool
    action_url: Optional[str]
    related_id: Optional[int]
    created_at: str

class NotificationCreate(BaseModel):
    user_id: int
    user_type: str
    title: str
    message: str
    notification_type: str
    action_url: Optional[str] = None
    related_id: Optional[int] = None

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    user_id: int,
    user_type: str,
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get notifications for a user
    """
    # Ensure table exists
    from app.models.base import Base
    Base.metadata.create_all(bind=db.get_bind())
    
    query = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.user_type == user_type
    )
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    notifications = query.order_by(
        Notification.created_at.desc()
    ).limit(limit).all()
    
    return [
        NotificationResponse(
            id=notif.id,
            user_id=notif.user_id,
            user_type=notif.user_type,
            title=notif.title,
            message=notif.message,
            notification_type=notif.notification_type,
            is_read=notif.is_read,
            action_url=notif.action_url,
            related_id=notif.related_id,
            created_at=notif.created_at.isoformat()
        )
        for notif in notifications
    ]

@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """
    Mark a notification as read
    """
    notification = db.query(Notification).filter_by(id=notification_id).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    db.commit()
    
    return {
        "id": notification.id,
        "is_read": notification.is_read,
        "message": "Notification marked as read"
    }

@router.post("/mark-all-read")
async def mark_all_read(
    user_id: int,
    user_type: str,
    db: Session = Depends(get_db)
):
    """
    Mark all notifications as read for a user
    """
    updated = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.user_type == user_type,
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return {
        "updated_count": updated,
        "message": f"Marked {updated} notifications as read"
    }

@router.post("/", response_model=NotificationResponse)
async def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new notification (internal use)
    """
    notification = Notification(
        user_id=notification_data.user_id,
        user_type=notification_data.user_type,
        title=notification_data.title,
        message=notification_data.message,
        notification_type=notification_data.notification_type,
        action_url=notification_data.action_url,
        related_id=notification_data.related_id,
        is_read=False
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return NotificationResponse(
        id=notification.id,
        user_id=notification.user_id,
        user_type=notification.user_type,
        title=notification.title,
        message=notification.message,
        notification_type=notification.notification_type,
        is_read=notification.is_read,
        action_url=notification.action_url,
        related_id=notification.related_id,
        created_at=notification.created_at.isoformat()
    )

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a notification
    """
    notification = db.query(Notification).filter_by(id=notification_id).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    db.delete(notification)
    db.commit()
    
    return {
        "message": "Notification deleted successfully"
    }

@router.get("/count")
async def get_unread_count(
    user_id: int,
    user_type: str,
    db: Session = Depends(get_db)
):
    """
    Get count of unread notifications
    """
    count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.user_type == user_type,
        Notification.is_read == False
    ).count()
    
    return {
        "user_id": user_id,
        "user_type": user_type,
        "unread_count": count
    }
