"""
Stakeholder model - represents team members (HR, IT, Managers, etc.)
"""
from sqlalchemy import Column, String, Boolean
from app.models.base import BaseModel

class Stakeholder(BaseModel):
    """
    Stakeholder model - team members involved in onboarding
    
    Examples: HR (Mohini), IT (Sagar), Delivery Heads (Sajal, Prathamesh)
    """
    __tablename__ = "stakeholders"
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    role = Column(String(100), nullable=False, index=True)  # "HR", "IT", "Delivery Head", etc.
    department = Column(String(255), nullable=True, index=True)
    
    # Availability
    is_available = Column(Boolean, default=True, nullable=False)
    on_leave_until = Column(String(50), nullable=True)  # Date string
    
    # Fallback
    fallback_stakeholder_id = Column(String(100), nullable=True)  # ID of fallback person
    
    def __repr__(self):
        return f"<Stakeholder(id={self.id}, name='{self.name}', role='{self.role}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "department": self.department,
            "is_available": self.is_available,
            "on_leave_until": self.on_leave_until,
            "fallback_stakeholder_id": self.fallback_stakeholder_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
