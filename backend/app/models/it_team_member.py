"""
ITTeamMember model - represents authorized IT team members
"""
from sqlalchemy import Column, Integer, String
from app.models.base import BaseModel


class ITTeamMember(BaseModel):
    """
    ITTeamMember model - authorized IT team members who can respond to equipment allocation requests
    
    Fields:
    - name: Full name of the IT team member
    - email: Email address (unique, used for authorization)
    - is_active: Whether the member is currently active (0 = inactive, 1 = active)
    - notification_enabled: Whether to send notifications to this member (0 = disabled, 1 = enabled)
    """
    __tablename__ = "it_team_members"
    
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    is_active = Column(Integer, default=1, nullable=False)  # 0 = inactive, 1 = active (SQLite compatible)
    notification_enabled = Column(Integer, default=1, nullable=False)  # 0 = disabled, 1 = enabled
    
    def __repr__(self):
        return f"<ITTeamMember(id={self.id}, name='{self.name}', email='{self.email}', is_active={bool(self.is_active)})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_active": bool(self.is_active),
            "notification_enabled": bool(self.notification_enabled),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
