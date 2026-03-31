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
from app.email.email_service import email_service
from app.email.email_schemas import (
    WelcomeEmailData,
    ITNotificationData,
    ManagerNotificationData
)
from app.services.excel_service import ask_llm_for_slot, book_slot
from app import config

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
                reporting_manager_email=state.get('reporting_manager_email'),
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


def email_notification_node(state: OnboardingState) -> Dict[str, Any]:
    """
    Email Notification Node
    
    Sends automated emails after candidate creation:
    1. Welcome email to candidate
    2. IT notification to IT team
    3. Manager notification to reporting manager
    """
    logger.info(f"[Email Node] Sending onboarding emails for: {state['candidate_name']}")
    
    email_results = []
    
    try:
        with get_db_context() as db:
            candidate = db.query(Candidate).filter_by(id=state['candidate_id']).first()
            
            if not candidate:
                logger.error(f"Candidate {state['candidate_id']} not found")
                return {
                    "email_status": "failed",
                    "errors": ["Candidate not found"]
                }
            
            # Default onboarding tasks for welcome email
            default_tasks = [
                "Complete personal information form",
                "Upload required documents (ID, certificates)",
                "Review and sign company policies",
                "Complete IT security training",
                "Setup email and communication tools",
                "Meet with reporting manager",
                "Complete department orientation",
                "Setup workstation and tools",
                "Complete compliance training"
            ]
            
            # 1. Send Welcome Email to Candidate
            try:
                first_name = candidate.name.split()[0].lower()
                welcome_data = WelcomeEmailData(
                    candidate_name=candidate.name,
                    candidate_email=candidate.email,
                    role=candidate.role or "Team Member",
                    department=candidate.department,
                    joining_date=candidate.joining_date,
                    reporting_manager=candidate.reporting_manager or "TBD",
                    login_email=candidate.email,
                    login_password=f"{first_name}@123",
                    tasks=default_tasks
                )
                
                response = email_service.send_welcome_email(welcome_data)
                email_results.append({
                    "type": "welcome_email",
                    "recipient": candidate.email,
                    "status": "success" if response.success else "failed",
                    "message": response.message
                })
                logger.info(f"Welcome email sent to {candidate.email}: {response.success}")
                
            except Exception as e:
                logger.error(f"Failed to send welcome email: {e}")
                email_results.append({
                    "type": "welcome_email",
                    "status": "failed",
                    "error": str(e)
                })
            
            # 2. Send IT Notification
            try:
                it_data = ITNotificationData(
                    candidate_name=candidate.name,
                    candidate_email=candidate.email,
                    role=candidate.role or "Team Member",
                    department=candidate.department,
                    joining_date=candidate.joining_date,
                    reporting_manager=candidate.reporting_manager or "TBD"
                )
                
                response = email_service.send_it_notification(it_data)
                email_results.append({
                    "type": "it_notification",
                    "recipient": config.IT_EMAIL,
                    "status": "success" if response.success else "failed",
                    "message": response.message
                })
                logger.info(f"IT notification sent: {response.success}")
                
            except Exception as e:
                logger.error(f"Failed to send IT notification: {e}")
                email_results.append({
                    "type": "it_notification",
                    "status": "failed",
                    "error": str(e)
                })
            
            # 3. Send Manager Notification (if manager email exists)
            if candidate.reporting_manager_email:
                try:
                    manager_data = ManagerNotificationData(
                        manager_name=candidate.reporting_manager or "Manager",
                        manager_email=candidate.reporting_manager_email,
                        candidate_name=candidate.name,
                        candidate_email=candidate.email,
                        role=candidate.role or "Team Member",
                        department=candidate.department,
                        joining_date=candidate.joining_date
                    )
                    
                    response = email_service.send_manager_notification(manager_data)
                    email_results.append({
                        "type": "manager_notification",
                        "recipient": candidate.reporting_manager_email,
                        "status": "success" if response.success else "failed",
                        "message": response.message
                    })
                    logger.info(f"Manager notification sent to {candidate.reporting_manager_email}: {response.success}")
                    
                except Exception as e:
                    logger.error(f"Failed to send manager notification: {e}")
                    email_results.append({
                        "type": "manager_notification",
                        "status": "failed",
                        "error": str(e)
                    })
            else:
                logger.warning(f"No manager email configured for {candidate.name}")
                email_results.append({
                    "type": "manager_notification",
                    "status": "skipped",
                    "reason": "No manager email configured"
                })
        
        # Count successes
        success_count = sum(1 for r in email_results if r.get("status") == "success")
        total_count = len([r for r in email_results if r.get("status") != "skipped"])
        
        logger.info(f"Email notifications complete: {success_count}/{total_count} successful")
        
        return {
            "email_status": "success" if success_count > 0 else "failed",
            "emails_sent": email_results,
            "agent_results": [{
                "agent": "EmailNotification",
                "status": "success",
                "emails_sent": success_count,
                "total_emails": total_count,
                "timestamp": datetime.now().isoformat()
            }]
        }
        
    except Exception as e:
        logger.error(f"Email notification node failed: {e}")
        return {
            "email_status": "failed",
            "errors": [f"EmailNotification: {str(e)}"],
            "agent_results": [{
                "agent": "EmailNotification",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }]
        }


def scheduling_agent_node(state: OnboardingState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Node 3: Scheduling Agent (LLM-powered)
    
    Uses LLM with tools to make intelligent routing decisions.
    """
    logger.info(f"[Node 3] Scheduling Agent for: {state['candidate_name']}")
    
    # Get LLM with deterministic temperature for slot decisioning
    llm = get_llm(temperature=0.0)
    reasoning_steps = []
    
    try:
        department = state.get("candidate_department", "")
        candidate_name = state["candidate_name"]
        meeting_type = "Delivery Head Overview"

        # Reuse existing tools to resolve primary + backup stakeholders.
        department_head_tool = next((t for t in ALL_TOOLS if t.name == "get_department_head"), None)
        fallback_tool = next((t for t in ALL_TOOLS if t.name == "get_fallback_approver"), None)

        primary_info: Dict[str, Any] = {}
        backup_info: Dict[str, Any] = {}

        if department_head_tool:
            primary_info = department_head_tool.invoke({"department": department})
            reasoning_steps.append({
                "step": len(reasoning_steps) + 1,
                "action": "get_department_head",
                "input": {"department": department},
                "output": primary_info,
                "timestamp": datetime.now().isoformat(),
            })

        if fallback_tool:
            backup_info = fallback_tool.invoke({"department": department, "role": "Delivery Head"})
            reasoning_steps.append({
                "step": len(reasoning_steps) + 1,
                "action": "get_fallback_approver",
                "input": {"department": department, "role": "Delivery Head"},
                "output": backup_info,
                "timestamp": datetime.now().isoformat(),
            })

        primary_person = (primary_info.get("name") or "").strip()
        backup_person = (backup_info.get("name") or "").strip() or None
        if backup_person and primary_person and backup_person.lower() == primary_person.lower():
            backup_person = None

        decision = ask_llm_for_slot(
            candidate_name=candidate_name,
            meeting_type=meeting_type,
            primary_person=primary_person,
            backup_person=backup_person,
            llm=llm,
        )

        logger.info(
            "[LLM SCHEDULER] candidate=%s meeting=%s reason=%s fallback_note=%s",
            candidate_name,
            meeting_type,
            decision.get("reason", ""),
            decision.get("fallback_note", "N/A"),
        )

        if not decision.get("success"):
            return {
                "current_step": "progress",
                "meetings_scheduled": [],
                "reasoning_traces": [{
                    "decision": "PENDING",
                    "stakeholder_name": primary_person or "Unknown",
                    "stakeholder_email": primary_info.get("email", "unknown@konverge.ai"),
                    "reasoning": decision.get("reason", "No slots available."),
                    "is_fallback": False,
                    "confidence": 1.0,
                    "reasoning_steps": reasoning_steps,
                    "fallback_note": decision.get("fallback_note", "N/A"),
                }],
                "agent_results": [{
                    "agent": "SchedulingAgent",
                    "status": "pending",
                    "reason": decision.get("reason", "No slots available."),
                    "timestamp": datetime.now().isoformat(),
                }],
            }

        booking_result = book_slot(
            candidate_name=candidate_name,
            meeting_type=meeting_type,
            interviewer_name=decision["interviewer"],
            date=decision["date"],
            time=decision["time"],
            booked_by="Scheduling Agent",
        )

        if not booking_result.get("success"):
            return {
                "current_step": "progress",
                "meetings_scheduled": [],
                "reasoning_traces": [{
                    "decision": "PENDING",
                    "stakeholder_name": decision.get("interviewer", "Unknown"),
                    "stakeholder_email": primary_info.get("email", "unknown@konverge.ai"),
                    "reasoning": booking_result.get("message", "Could not book slot."),
                    "is_fallback": False,
                    "confidence": 1.0,
                    "reasoning_steps": reasoning_steps,
                    "fallback_note": decision.get("fallback_note", "N/A"),
                }],
                "agent_results": [{
                    "agent": "SchedulingAgent",
                    "status": "pending",
                    "reason": booking_result.get("message", "Could not book slot."),
                    "timestamp": datetime.now().isoformat(),
                }],
            }

        interviewer_name = decision["interviewer"]
        is_fallback = (
            bool(backup_person)
            and backup_person.lower() == interviewer_name.strip().lower()
        )
        stakeholder_email = (
            backup_info.get("email")
            if is_fallback
            else primary_info.get("email")
        ) or "unknown@konverge.ai"

        decision_data = {
            "decision": f"Assign to {interviewer_name}",
            "stakeholder_name": interviewer_name,
            "stakeholder_email": stakeholder_email,
            "reasoning": decision.get("reason", ""),
            "is_fallback": is_fallback,
            "confidence": 1.0,
            "reasoning_steps": reasoning_steps,
            "fallback_note": decision.get("fallback_note", "N/A"),
        }
        
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
                "meeting_type": meeting_type,
                "stakeholder_name": decision_data.get("stakeholder_name", "Unknown"),
                "stakeholder_email": decision_data.get("stakeholder_email", "unknown@konverge.ai"),
                "is_fallback": decision_data.get("is_fallback", False),
                "reasoning": decision_data.get("reasoning", ""),
                "scheduled_time": f"{decision.get('date', '')} {decision.get('time', '')}",
                "fallback_note": decision_data.get("fallback_note", "N/A"),
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
