"""
SLA event model - stores warnings, breaches, and escalations for task SLAs
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime

from app.models.base import BaseModel


class SLAEvent(BaseModel):
    """Audit trail for SLA-related state changes."""

    __tablename__ = "sla_events"

    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    candidate_id = Column(Integer, nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # warning, breach, escalated, resolved
    severity = Column(String(20), nullable=False, default="info")
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    triggered_at = Column(DateTime, nullable=False, index=True)
    owner = Column(String(100), nullable=True, index=True)

