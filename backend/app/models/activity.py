"""
Activity model - represents global activity stream events
"""
from sqlalchemy import Column, String, Text, ForeignKey, Integer
from app.models.base import BaseModel
import enum

class ActivityType(enum.Enum):
    """Type of activity"""
    CANDIDATE = "candidate"
    AI = "ai"
    SYSTEM = "system"
    HR = "hr"

class Activity(BaseModel):
    """
    Activity model - for global live activity stream
    """
    __tablename__ = "activities"
    
    user_name = Column(String(255), nullable=False)
    user_role = Column(String(100), nullable=True)
    action_text = Column(Text, nullable=False)
    target_object = Column(String(255), nullable=True)  # e.g., "offer letter", "IT Setup"
    activity_type = Column(String(50), default="candidate", nullable=False)
    icon_type = Column(String(50), nullable=True)  # "user", "bot", "check", "alert"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_name": self.user_name,
            "user_role": self.user_role,
            "action_text": self.action_text,
            "target_object": self.target_object,
            "activity_type": self.activity_type,
            "icon_type": self.icon_type,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
