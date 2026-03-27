"""
ReasoningTrace model - stores agent decision reasoning
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class ReasoningTrace(BaseModel):
    """
    ReasoningTrace model - stores agent reasoning for auditability
    
    This is critical for the agentic workflow - every decision
    made by the LLM is stored with full reasoning trace.
    
    Relationships:
    - candidate: Many-to-one with Candidate
    """
    __tablename__ = "reasoning_traces"
    
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    
    # Agent Information
    agent_name = Column(String(100), nullable=False, index=True)  # e.g., "SchedulingAgent"
    task_type = Column(String(100), nullable=False, index=True)  # e.g., "meeting_scheduling"
    
    # Decision Details
    decision = Column(Text, nullable=False)  # The final decision made
    reasoning = Column(Text, nullable=False)  # Why this decision was made
    confidence_score = Column(Integer, nullable=True)  # 0-100
    
    # Routing Information
    assigned_stakeholder_id = Column(Integer, nullable=True)
    assigned_stakeholder_name = Column(String(255), nullable=True)
    assigned_stakeholder_email = Column(String(255), nullable=True)
    is_fallback = Column(Integer, default=0)  # 0 = False, 1 = True
    fallback_reason = Column(Text, nullable=True)
    
    # Full Trace (JSON)
    trace_steps = Column(JSON, nullable=True)  # Array of reasoning steps
    
    # LLM Details
    llm_model = Column(String(100), nullable=True)  # e.g., "llama-3.3-70b-versatile"
    llm_provider = Column(String(50), nullable=True)  # e.g., "groq"
    
    # Relationships
    candidate = relationship("Candidate", back_populates="reasoning_traces")
    
    def __repr__(self):
        return f"<ReasoningTrace(id={self.id}, agent='{self.agent_name}', candidate_id={self.candidate_id})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "agent_name": self.agent_name,
            "task_type": self.task_type,
            "decision": self.decision,
            "reasoning": self.reasoning,
            "confidence_score": self.confidence_score,
            "assigned_stakeholder_id": self.assigned_stakeholder_id,
            "assigned_stakeholder_name": self.assigned_stakeholder_name,
            "assigned_stakeholder_email": self.assigned_stakeholder_email,
            "is_fallback": bool(self.is_fallback),
            "fallback_reason": self.fallback_reason,
            "trace_steps": self.trace_steps,
            "llm_model": self.llm_model,
            "llm_provider": self.llm_provider,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
