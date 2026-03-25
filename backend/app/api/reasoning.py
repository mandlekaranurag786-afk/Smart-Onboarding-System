"""
Reasoning traces API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.reasoning_trace import ReasoningTrace

router = APIRouter()

@router.get("/{candidate_id}")
async def get_reasoning_traces(candidate_id: int, db: Session = Depends(get_db)):
    """Get all reasoning traces for a candidate"""
    traces = db.query(ReasoningTrace).filter_by(candidate_id=candidate_id).all()
    
    return [
        {
            "id": t.id,
            "agent_name": t.agent_name,
            "task_type": t.task_type,
            "decision": t.decision,
            "reasoning": t.reasoning,
            "confidence_score": t.confidence_score,
            "assigned_stakeholder_name": t.assigned_stakeholder_name,
            "is_fallback": bool(t.is_fallback),
            "fallback_reason": t.fallback_reason,
            "trace_steps": t.trace_steps,
            "created_at": t.created_at.isoformat()
        }
        for t in traces
    ]
