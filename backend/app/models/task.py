"""
Task model - represents individual onboarding tasks
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date, DateTime, Enum as SQLEnum
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
    
    # IT Equipment Allocation specific fields
    it_response_token = Column(String(255), nullable=True, unique=True, index=True)
    it_response_received_at = Column(DateTime, nullable=True)
    it_response_type = Column(String(50), nullable=True)  # "button_click", "email_reply"
    it_responder_email = Column(String(255), nullable=True)
    it_responder_name = Column(String(255), nullable=True)
    it_response_message = Column(Text, nullable=True)
    it_reminder_sent_count = Column(Integer, default=0)
    it_last_reminder_sent_at = Column(DateTime, nullable=True)
    
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
            "it_response_token": self.it_response_token,
            "it_response_received_at": self.it_response_received_at.isoformat() if self.it_response_received_at else None,
            "it_response_type": self.it_response_type,
            "it_responder_email": self.it_responder_email,
            "it_responder_name": self.it_responder_name,
            "it_response_message": self.it_response_message,
            "it_reminder_sent_count": self.it_reminder_sent_count,
            "it_last_reminder_sent_at": self.it_last_reminder_sent_at.isoformat() if self.it_last_reminder_sent_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
