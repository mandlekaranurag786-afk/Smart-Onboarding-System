"""
Task model - represents individual onboarding tasks
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class TaskStatus(enum.Enum):
    """Task status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    BLOCKED = "blocked"

class TaskOwner(enum.Enum):
    """Task owner type"""
    HR = "HR"
    IT = "IT"
    ADMIN = "Admin"
    CANDIDATE = "Candidate"
    MANAGER = "Manager"
    DELIVERY_HEAD = "Delivery Head"
    SYSTEM = "System"

class Task(BaseModel):
    """
    Task model - individual onboarding tasks
    
    Relationships:
    - checklist: Many-to-one with Checklist
    """
    __tablename__ = "tasks"
    
    checklist_id = Column(Integer, ForeignKey("checklists.id"), nullable=False, index=True)
    
    # Task Details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(String(100), nullable=False, index=True)  # e.g., "document_signing", "meeting_scheduling"
    
    # Ownership
    owner = Column(SQLEnum(TaskOwner), nullable=False, index=True)
    assigned_to_id = Column(Integer, nullable=True)  # Stakeholder ID
    assigned_to_name = Column(String(255), nullable=True)
    assigned_to_email = Column(String(255), nullable=True)
    
    # Status
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True)
    
    # Scheduling
    due_date = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)
    
    # IT Decision (for IT tasks)
    it_decision = Column(String(50), nullable=True)  # "yes", "no", null
    it_decision_reason = Column(Text, nullable=True)
    
    # Meeting Details (for meeting tasks)
    meeting_scheduled_time = Column(String(100), nullable=True)
    is_fallback = Column(Integer, default=0)  # 0 = False, 1 = True (SQLite compatible)
    fallback_reason = Column(Text, nullable=True)
    
    # Relationships
    checklist = relationship("Checklist", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task(id={self.id}, name='{self.name}', status='{self.status.value}', owner='{self.owner.value}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "checklist_id": self.checklist_id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type,
            "owner": self.owner.value,
            "assigned_to_id": self.assigned_to_id,
            "assigned_to_name": self.assigned_to_name,
            "assigned_to_email": self.assigned_to_email,
            "status": self.status.value,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "it_decision": self.it_decision,
            "it_decision_reason": self.it_decision_reason,
            "meeting_scheduled_time": self.meeting_scheduled_time,
            "is_fallback": bool(self.is_fallback),
            "fallback_reason": self.fallback_reason,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
