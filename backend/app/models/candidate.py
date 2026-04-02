"""
Candidate model - represents a new joinee
"""
from sqlalchemy import Column, Integer, String, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class CandidateStatus(enum.Enum):
    """Candidate onboarding status"""
    ONBOARDING_STARTED = "onboarding_started"
    IN_PROGRESS = "in_progress"
    ONBOARDED = "onboarded"
    ON_HOLD = "on_hold"


class CandidateAccountStatus(enum.Enum):
    """Candidate portal account status."""
    INVITED = "invited"
    ACTIVE = "active"
    DISABLED = "disabled"

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

    # Candidate Portal Access
    password_hash = Column(String(255), nullable=True)
    account_status = Column(
        SQLEnum(CandidateAccountStatus),
        default=CandidateAccountStatus.INVITED,
        nullable=False,
        index=True
    )
    password_reset_required = Column(Integer, default=1, nullable=False)
    
    # Status
    status = Column(
        SQLEnum(CandidateStatus),
        default=CandidateStatus.ONBOARDING_STARTED,
        nullable=False,
        index=True
    )
    
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
            "account_status": self.account_status.value,
            "password_reset_required": bool(self.password_reset_required),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
