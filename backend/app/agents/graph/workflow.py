"""
LangGraph Workflow - The main orchestration graph

This defines the flow of agents as a state machine.
"""
from typing import Dict, Any
import logging

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents.graph.state import OnboardingState, create_initial_state
from app.agents.graph.nodes import (
    onboarding_trigger_node,
    email_notification_node,
    it_monitoring_node,
    scheduling_agent_node,
    progress_monitor_node
)

logger = logging.getLogger(__name__)


def should_continue(state: OnboardingState) -> str:
    """
    Routing function - decides which node to go to next.
    
    This is the "brain" of the workflow that determines the path.
    """
    current_step = state.get("current_step", "trigger")
    status = state.get("status", "in_progress")
    
    logger.info(f"Routing decision: current_step={current_step}, status={status}")
    
    # If failed, end
    if status == "failed":
        return "end"
    
    # Route based on current step
    if current_step == "trigger":
        return "it_monitoring"
    elif current_step == "it_monitoring":
        return "scheduling"
    elif current_step == "scheduling":
        return "progress"
    elif current_step == "progress":
        return "end"
    elif current_step == "complete":
        return "end"
    else:
        return "end"


def create_onboarding_graph():
    """
    Create the LangGraph workflow for onboarding.
    
    Returns:
        Compiled graph ready for execution
    """
    # Create graph
    workflow = StateGraph(OnboardingState)
    
    # Add nodes (agents)
    workflow.add_node("onboarding_trigger", onboarding_trigger_node)
    workflow.add_node("email_notification", email_notification_node)
    workflow.add_node("it_monitoring", it_monitoring_node)
    workflow.add_node("scheduling", scheduling_agent_node)
    workflow.add_node("progress", progress_monitor_node)
    
    # Set entry point
    workflow.set_entry_point("onboarding_trigger")
    
    # Add workflow edges
    workflow.add_edge("onboarding_trigger", "email_notification")
    workflow.add_edge("email_notification", "it_monitoring")
    workflow.add_edge("it_monitoring", "scheduling")
    workflow.add_edge("scheduling", "progress")
    workflow.add_edge("progress", END)
    
    # Add memory checkpointer (for state persistence)
    memory = MemorySaver()
    
    # Compile graph
    app = workflow.compile(checkpointer=memory)
    
    logger.info("LangGraph workflow compiled successfully with email notifications")
    
    return app


# Create singleton instance
onboarding_graph = create_onboarding_graph()


async def run_onboarding_workflow(candidate_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the complete onboarding workflow.
    
    Args:
        candidate_data: Dict with candidate information
        
    Returns:
        Final state after workflow completion
    """
    logger.info(f"Starting LangGraph workflow for: {candidate_data.get('name')}")
    
    # Create initial state
    initial_state = create_initial_state(candidate_data)
    
    # Run graph
    config = {"configurable": {"thread_id": f"onboarding_{candidate_data.get('email')}"}}
    
    try:
        # Execute workflow and collect all states
        all_states = []
        for state_update in onboarding_graph.stream(initial_state, config):
            all_states.append(state_update)
            logger.info(f"Graph step: {list(state_update.keys())}")
        
        # Get final state from last update
        if all_states:
            # The last state contains the complete accumulated state
            final_state_dict = all_states[-1]
            
            # Extract the state from the last node
            last_node_key = list(final_state_dict.keys())[0]
            final_state = final_state_dict[last_node_key]
            
            logger.info(f"Workflow completed: {final_state.get('status')}")
            
            return {
                "status": final_state.get("status", "success"),
                "candidate_id": final_state.get("candidate_id"),
                "checklist_id": final_state.get("checklist_id"),
                "total_tasks": final_state.get("total_tasks", 0),
                "agent_results": final_state.get("agent_results", []),
                "meetings_scheduled": final_state.get("meetings_scheduled", []),
                "reasoning_traces": final_state.get("reasoning_traces", []),
                "errors": final_state.get("errors", []),
                "started_at": final_state.get("started_at"),
                "completed_at": final_state.get("completed_at")
            }
        
        return {"status": "failed", "error": "No final state"}
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "failed",
            "error": str(e)
        }
