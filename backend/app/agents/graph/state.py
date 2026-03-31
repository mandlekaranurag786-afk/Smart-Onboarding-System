"""
LangGraph State Definition

This defines the state that flows through the agent graph.
Each node can read from and write to this state.
"""
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from datetime import datetime
import operator

class OnboardingState(TypedDict):
    """
    State for the onboarding workflow.
    
    This state is passed between all nodes in the graph.
    Each agent can read from and update this state.
    """
    # Candidate Information
    candidate_id: Optional[int]
    candidate_name: str
    candidate_email: str
    candidate_department: str
    candidate_role: str
    joining_date: str
    reporting_manager: Optional[str]
    reporting_manager_email: Optional[str]
    
    # Workflow Status
    current_step: str  # "trigger", "it_monitoring", "scheduling", "progress", "complete"
    status: str  # "in_progress", "success", "failed"
    
    # Agent Results (accumulated)
    agent_results: Annotated[List[Dict[str, Any]], operator.add]  # Append-only list
    
    # Checklist
    checklist_id: Optional[int]
    total_tasks: int
    completed_tasks: int
    
    # IT Decision (Human-in-Loop)
    it_decision: Optional[str]  # "yes", "no", "pending"
    it_decision_reason: Optional[str]
    
    # Email Status
    email_status: Optional[str]  # "success", "failed", "pending"
    emails_sent: Annotated[List[Dict[str, Any]], operator.add]
    
    # Meetings Scheduled
    meetings_scheduled: Annotated[List[Dict[str, Any]], operator.add]
    
    # Reasoning Traces (for auditability)
    reasoning_traces: Annotated[List[Dict[str, Any]], operator.add]
    
    # Error Handling
    errors: Annotated[List[str], operator.add]
    retry_count: int
    
    # Timestamps
    started_at: str
    completed_at: Optional[str]
    
    # Messages (for LLM context)
    messages: Annotated[List[Dict[str, Any]], operator.add]


def create_initial_state(candidate_data: Dict[str, Any]) -> OnboardingState:
    """
    Create initial state from candidate data.
    
    Args:
        candidate_data: Dict with candidate information
        
    Returns:
        Initial OnboardingState
    """
    return OnboardingState(
        # Candidate info
        candidate_id=None,
        candidate_name=candidate_data.get("name"),
        candidate_email=candidate_data.get("email"),
        candidate_department=candidate_data.get("department"),
        candidate_role=candidate_data.get("role", "Employee"),
        joining_date=candidate_data.get("joining_date"),
        reporting_manager=candidate_data.get("reporting_manager"),
        reporting_manager_email=candidate_data.get("reporting_manager_email"),
        
        # Workflow
        current_step="trigger",
        status="in_progress",
        
        # Collections (empty lists)
        agent_results=[],
        meetings_scheduled=[],
        reasoning_traces=[],
        errors=[],
        messages=[],
        emails_sent=[],
        
        # Checklist
        checklist_id=None,
        total_tasks=0,
        completed_tasks=0,
        
        # IT Decision
        it_decision="pending",
        it_decision_reason=None,
        
        # Email Status
        email_status="pending",
        
        # Metadata
        retry_count=0,
        started_at=datetime.now().isoformat(),
        completed_at=None
    )
