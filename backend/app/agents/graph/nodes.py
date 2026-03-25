"""
LangGraph Nodes - Each agent is a node in the graph

Nodes are functions that take state and return updated state.
"""
from typing import Dict, Any
import logging
from datetime import datetime, date

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

from app.agents.graph.state import OnboardingState
from app.agents.graph.tools import ALL_TOOLS
from app.llm_client import get_llm
from app.database import get_db_context
from app.models.candidate import Candidate, CandidateStatus
from app.models.checklist import Checklist
from app.models.task import Task, TaskStatus, TaskOwner
from app.models.reasoning_trace import ReasoningTrace

logger = logging.getLogger(__name__)


def onboarding_trigger_node(state: OnboardingState) -> Dict[str, Any]:
    """
    Node 1: Onboarding Trigger
    
    Creates candidate record and generates checklist.
    """
    logger.info(f"[Node 1] Onboarding Trigger for: {state['candidate_name']}")
    
    try:
        with get_db_context() as db:
            # Parse joining date
            joining_date_str = state['joining_date']
            if "/" in joining_date_str:
                day, month, year = joining_date_str.split("/")
                joining_date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            joining_date = datetime.strptime(joining_date_str, "%Y-%m-%d").date()
            
            # Create candidate
            candidate = Candidate(
                name=state['candidate_name'],
                email=state['candidate_email'],
                department=state['candidate_department'],
                role=state['candidate_role'],
                joining_date=joining_date,
                reporting_manager=state.get('reporting_manager'),
                status=CandidateStatus.ONBOARDING_STARTED
            )
            db.add(candidate)
            db.flush()
            
            # Create checklist
            checklist = Checklist(candidate_id=candidate.id)
            db.add(checklist)
            db.flush()
            
            # Create 9 tasks
            tasks_data = [
                {"name": "Document Signing", "owner": TaskOwner.HR, "task_type": "document_signing"},
                {"name": "Work Profile Builder", "owner": TaskOwner.CANDIDATE, "task_type": "profile_building"},
                {"name": "Asset Assignment", "owner": TaskOwner.IT, "task_type": "asset_assignment"},
                {"name": "Account Provisioning", "owner": TaskOwner.SYSTEM, "task_type": "account_provisioning"},
                {"name": "Meeting: HR Walkthrough", "owner": TaskOwner.HR, "task_type": "meeting_scheduling"},
                {"name": "Meeting: Reporting Manager", "owner": TaskOwner.MANAGER, "task_type": "meeting_scheduling"},
                {"name": "Meeting: Delivery Head", "owner": TaskOwner.DELIVERY_HEAD, "task_type": "meeting_scheduling"},
                {"name": "Karma Portal Acknowledgment", "owner": TaskOwner.CANDIDATE, "task_type": "portal_acknowledgment"},
                {"name": "Final Review", "owner": TaskOwner.HR, "task_type": "final_review"}
            ]
            
            for task_data in tasks_data:
                task = Task(
                    checklist_id=checklist.id,
                    name=task_data["name"],
                    task_type=task_data["task_type"],
                    owner=task_data["owner"],
                    status=TaskStatus.PENDING
                )
                db.add(task)
            
            db.commit()
            
            logger.info(f"Created candidate ID: {candidate.id} with {len(tasks_data)} tasks")
            
            # Update state
            return {
                "candidate_id": candidate.id,
                "checklist_id": checklist.id,
                "total_tasks": len(tasks_data),
                "completed_tasks": 0,
                "current_step": "it_monitoring",
                "agent_results": [{
                    "agent": "OnboardingTrigger",
                    "status": "success",
                    "candidate_id": candidate.id,
                    "checklist_id": checklist.id,
                    "timestamp": datetime.now().isoformat()
                }]
            }
            
    except Exception as e:
        logger.error(f"Onboarding trigger failed: {e}")
        return {
            "status": "failed",
            "errors": [f"OnboardingTrigger: {str(e)}"]
        }


def it_monitoring_node(state: OnboardingState) -> Dict[str, Any]:
    """
    Node 2: IT Asset Monitoring
    
    Monitors IT asset assignment (simplified for now).
    """
    logger.info(f"[Node 2] IT Monitoring for candidate: {state['candidate_id']}")
    
    # For now, we'll assume IT is pending
    # In production, this would check actual IT status
    
    return {
        "current_step": "scheduling",
        "it_decision": "pending",
        "agent_results": [{
            "agent": "ITAssetAgent",
            "status": "monitoring",
            "sla_deadline": (datetime.now()).isoformat(),
            "timestamp": datetime.now().isoformat()
        }]
    }


def scheduling_agent_node(state: OnboardingState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Node 3: Scheduling Agent (LLM-powered)
    
    Uses LLM with tools to make intelligent routing decisions.
    """
    logger.info(f"[Node 3] Scheduling Agent for: {state['candidate_name']}")
    
    # Get LLM with tools
    llm = get_llm()
    llm_with_tools = llm.bind_tools(ALL_TOOLS)
    
    # Build prompt
    system_prompt = """You are an intelligent meeting scheduling agent for KONVERGE.AI.

Your job: Schedule a meeting with the appropriate Delivery Head for the candidate.

Available tools:
- get_department_head(department): Find delivery head for department
- check_availability(stakeholder_id): Check if available or on leave
- get_fallback_approver(department, role): Find backup person
- get_workload(stakeholder_id): Check current workload

Process:
1. Find delivery head for candidate's department
2. Check their availability
3. If unavailable, find fallback
4. Make final decision

Output your final decision in this format:
DECISION: Assign to [Name] (ID: [id], Email: [email])
REASON: [explanation]
IS_FALLBACK: [yes/no]
CONFIDENCE: [0.0-1.0]
"""
    
    user_prompt = f"""
CANDIDATE: {state['candidate_name']}
DEPARTMENT: {state['candidate_department']}
TASK: Schedule Delivery Head meeting

Please use the tools to find the right person and schedule the meeting.
"""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    # Invoke LLM with tool calling loop
    reasoning_steps = []
    max_iterations = 5
    iteration = 0
    
    try:
        while iteration < max_iterations:
            response = llm_with_tools.invoke(messages)
            messages.append(response)
            
            # Check if there are tool calls
            if not response.tool_calls:
                # No more tool calls, we have final answer
                break
            
            # Execute tool calls
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                logger.info(f"Calling tool: {tool_name} with args: {tool_args}")
                
                # Find and execute tool
                tool = next((t for t in ALL_TOOLS if t.name == tool_name), None)
                if tool:
                    tool_result = tool.invoke(tool_args)
                    
                    # Add to reasoning steps
                    reasoning_steps.append({
                        "step": len(reasoning_steps) + 1,
                        "action": tool_name,
                        "input": tool_args,
                        "output": tool_result,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Add tool result to messages
                    messages.append(ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call["id"]
                    ))
            
            iteration += 1
        
        # Parse final decision
        final_response = messages[-1].content if isinstance(messages[-1], AIMessage) else str(messages[-1])
        
        # Extract decision details
        decision_data = _parse_llm_decision(final_response, reasoning_steps)
        
        # Store reasoning trace in database
        if state.get('candidate_id'):
            with get_db_context() as db:
                trace = ReasoningTrace(
                    candidate_id=state['candidate_id'],
                    agent_name="SchedulingAgent",
                    task_type="meeting_scheduling",
                    decision=decision_data.get("decision", "Unknown"),
                    reasoning=decision_data.get("reasoning", ""),
                    confidence_score=int(decision_data.get("confidence", 0.8) * 100),
                    assigned_stakeholder_name=decision_data.get("stakeholder_name"),
                    assigned_stakeholder_email=decision_data.get("stakeholder_email"),
                    is_fallback=1 if decision_data.get("is_fallback") else 0,
                    trace_steps=reasoning_steps,
                    llm_model="llama-3.3-70b-versatile",
                    llm_provider="groq"
                )
                db.add(trace)
                db.commit()
        
        logger.info(f"Scheduling decision: {decision_data.get('stakeholder_name')}")
        
        return {
            "current_step": "progress",
            "meetings_scheduled": [{
                "meeting_type": "Delivery Head Overview",
                "stakeholder_name": decision_data.get("stakeholder_name", "Unknown"),
                "stakeholder_email": decision_data.get("stakeholder_email", "unknown@konverge.ai"),
                "is_fallback": decision_data.get("is_fallback", False),
                "reasoning": decision_data.get("reasoning", ""),
                "scheduled_time": "2026-03-25 03:00 PM"
            }],
            "reasoning_traces": [decision_data],
            "agent_results": [{
                "agent": "SchedulingAgent",
                "status": "success",
                "meetings_scheduled": 1,
                "timestamp": datetime.now().isoformat()
            }]
        }
        
    except Exception as e:
        logger.error(f"Scheduling failed: {e}")
        return {
            "current_step": "progress",
            "errors": [f"SchedulingAgent: {str(e)}"],
            "agent_results": [{
                "agent": "SchedulingAgent",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }]
        }


def progress_monitor_node(state: OnboardingState) -> Dict[str, Any]:
    """
    Node 4: Progress Monitor
    
    Tracks completion and marks workflow as complete.
    """
    logger.info(f"[Node 4] Progress Monitor for candidate: {state['candidate_id']}")
    
    return {
        "current_step": "complete",
        "status": "success",
        "completed_at": datetime.now().isoformat(),
        "agent_results": [{
            "agent": "ProgressMonitor",
            "status": "monitoring",
            "timestamp": datetime.now().isoformat()
        }]
    }


def _parse_llm_decision(text: str, reasoning_steps: list) -> Dict[str, Any]:
    """Parse LLM decision text into structured format"""
    lines = text.split('\n')
    
    decision = "Unknown"
    stakeholder_name = "Unknown"
    stakeholder_email = "unknown@konverge.ai"
    reasoning = text
    is_fallback = False
    confidence = 0.8
    
    for line in lines:
        line = line.strip()
        
        if "DECISION:" in line:
            decision = line.replace("DECISION:", "").strip()
            if "(" in decision:
                stakeholder_name = decision.split("(")[0].replace("Assign to", "").strip()
                if "Email:" in decision:
                    stakeholder_email = decision.split("Email:")[1].split(")")[0].strip()
        
        elif "REASON:" in line:
            reasoning = line.replace("REASON:", "").strip()
        
        elif "IS_FALLBACK:" in line:
            is_fallback = "yes" in line.lower()
        
        elif "CONFIDENCE:" in line:
            try:
                confidence = float(line.replace("CONFIDENCE:", "").strip())
            except:
                pass
    
    # Fallback: extract from reasoning steps
    if stakeholder_name == "Unknown" and reasoning_steps:
        for step in reversed(reasoning_steps):
            if step["action"] in ["get_department_head", "get_fallback_approver"]:
                output = step["output"]
                if isinstance(output, dict):
                    stakeholder_name = output.get("name", "Unknown")
                    stakeholder_email = output.get("email", "unknown@konverge.ai")
                    if step["action"] == "get_fallback_approver":
                        is_fallback = True
                    break
    
    return {
        "decision": decision,
        "stakeholder_name": stakeholder_name,
        "stakeholder_email": stakeholder_email,
        "reasoning": reasoning,
        "is_fallback": is_fallback,
        "confidence": confidence,
        "reasoning_steps": reasoning_steps
    }
