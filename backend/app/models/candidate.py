"""
Candidate model - represents a new joinee
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class CandidateStatus(enum.Enum):
    """Candidate onboarding status"""
    ONBOARDING_STARTED = "onboarding_started"
    IN_PROGRESS = "in_progress"
    ONBOARDED = "onboarded"
    ON_HOLD = "on_hold"

class Candidate(BaseModel):
    """
    Candidate model - stores new joinee information
    
    Relationships:
    - checklist: One-to-one with Checklist
    - reasoning_traces: One-to-many with ReasoningTrace
    """
    __tablename__ = "candidates"
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    department = Column(String(255), nullable=False, index=True)
    role = Column(String(255), nullable=True)
    joining_date = Column(Date, nullable=False)
    
    # Reporting Structure
    reporting_manager = Column(String(255), nullable=True)
    reporting_manager_email = Column(String(255), nullable=True)
    
    # Status
    status = Column(
        SQLEnum(CandidateStatus),
        default=CandidateStatus.ONBOARDING_STARTED,
        nullable=False,
        index=True
    )
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    checklist = relationship("Checklist", back_populates="candidate", uselist=False, cascade="all, delete-orphan")
    reasoning_traces = relationship("ReasoningTrace", back_populates="candidate", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Candidate(id={self.id}, name='{self.name}', status='{self.status.value}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "department": self.department,
            "role": self.role,
            "joining_date": self.joining_date.isoformat() if self.joining_date else None,
            "reporting_manager": self.reporting_manager,
            "reporting_manager_email": self.reporting_manager_email,
            "status": self.status.value,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
