"""
Checklist model - represents the onboarding checklist
"""
from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Checklist(BaseModel):
    """
    Checklist model - one per candidate
    
    Relationships:
    - candidate: Many-to-one with Candidate
    - tasks: One-to-many with Task
    """
    __tablename__ = "checklists"
    
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, unique=True, index=True)
    completion_percentage = Column(Float, default=0.0, nullable=False)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="checklist")
    tasks = relationship("Task", back_populates="checklist", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Checklist(id={self.id}, candidate_id={self.candidate_id}, completion={self.completion_percentage}%)>"
    
    def calculate_completion(self):
        """Calculate completion percentage based on tasks"""
        if not self.tasks:
            return 0.0
        
        completed_tasks = sum(1 for task in self.tasks if task.status == "completed")
        total_tasks = len(self.tasks)
        
        self.completion_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0.0
        return self.completion_percentage
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "completion_percentage": self.completion_percentage,
            "total_tasks": len(self.tasks) if self.tasks else 0,
            "completed_tasks": sum(1 for task in self.tasks if task.status == "completed") if self.tasks else 0,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
