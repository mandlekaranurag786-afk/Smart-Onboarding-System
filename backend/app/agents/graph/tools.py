"""
LangChain Tools for Agent Graph

These tools can be called by LLM agents to perform actions.
"""
from langchain_core.tools import tool
from typing import Dict, Any
from datetime import datetime

from app.database import get_db_context
from app.models.stakeholder import Stakeholder


@tool
def get_department_head(department: str) -> Dict[str, Any]:
    """
    Find the delivery head for a given department.
    
    Args:
        department: Department name (e.g., "Artificial Intelligence", "Cloud")
        
    Returns:
        Dict with stakeholder information
    """
    with get_db_context() as db:
        # Query database for delivery head
        stakeholder = db.query(Stakeholder).filter(
            Stakeholder.department.ilike(f"%{department}%"),
            Stakeholder.role == "Delivery Head"
        ).first()
        
        if stakeholder:
            return {
                "stakeholder_id": stakeholder.id,
                "name": stakeholder.name,
                "email": stakeholder.email,
                "department": stakeholder.department,
                "role": stakeholder.role,
                "is_available": stakeholder.is_available
            }
        
        # Fallback to admin
        return {
            "stakeholder_id": 0,
            "name": "Admin",
            "email": "admin@konverge.ai",
            "department": "General",
            "role": "Admin",
            "is_available": True
        }


@tool
def check_availability(stakeholder_id: int) -> Dict[str, Any]:
    """
    Check if a stakeholder is available or on leave.
    
    Args:
        stakeholder_id: ID of the stakeholder
        
    Returns:
        Dict with availability information
    """
    with get_db_context() as db:
        stakeholder = db.query(Stakeholder).filter_by(id=stakeholder_id).first()
        
        if stakeholder:
            return {
                "stakeholder_id": stakeholder.id,
                "name": stakeholder.name,
                "available": stakeholder.is_available,
                "on_leave": not stakeholder.is_available,
                "return_date": stakeholder.on_leave_until,
                "reason": f"On leave until {stakeholder.on_leave_until}" if not stakeholder.is_available else "Available"
            }
        
        return {
            "stakeholder_id": stakeholder_id,
            "available": False,
            "on_leave": False,
            "return_date": None,
            "reason": "Stakeholder not found"
        }


@tool
def get_fallback_approver(department: str, role: str = "Delivery Head") -> Dict[str, Any]:
    """
    Find a fallback approver when primary person is unavailable.
    
    Args:
        department: Department name
        role: Role to find fallback for
        
    Returns:
        Dict with fallback stakeholder information
    """
    with get_db_context() as db:
        # Find fallback (Senior Delivery Manager in same department)
        fallback = db.query(Stakeholder).filter(
            Stakeholder.department.ilike(f"%{department}%"),
            Stakeholder.role == "Senior Delivery Manager",
            Stakeholder.is_available == True
        ).first()
        
        if fallback:
            return {
                "stakeholder_id": fallback.id,
                "name": fallback.name,
                "email": fallback.email,
                "department": fallback.department,
                "role": fallback.role,
                "is_fallback": True
            }
        
        # Ultimate fallback to admin
        return {
            "stakeholder_id": 0,
            "name": "Admin",
            "email": "admin@konverge.ai",
            "department": "General",
            "role": "Administrator",
            "is_fallback": True
        }


@tool
def get_workload(stakeholder_id: int) -> Dict[str, Any]:
    """
    Get current workload for a stakeholder.
    
    Args:
        stakeholder_id: ID of the stakeholder
        
    Returns:
        Dict with workload information
    """
    # TODO: Query actual task counts from database
    # For now, return mock data
    
    workload_map = {
        1: {"pending_tasks": 5, "capacity_status": "moderate"},
        2: {"pending_tasks": 3, "capacity_status": "light"},
        3: {"pending_tasks": 8, "capacity_status": "heavy"},
        5: {"pending_tasks": 2, "capacity_status": "light"}
    }
    
    workload = workload_map.get(stakeholder_id, {"pending_tasks": 0, "capacity_status": "unknown"})
    
    return {
        "stakeholder_id": stakeholder_id,
        **workload
    }


@tool
def send_email(to: str, subject: str, body: str) -> Dict[str, Any]:
    """
    Send an email notification.
    
    Args:
        to: Recipient email
        subject: Email subject
        body: Email body
        
    Returns:
        Dict with send status
    """
    # TODO: Implement actual email sending
    # For now, just log
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Email sent to {to}: {subject}")
    
    return {
        "status": "sent",
        "to": to,
        "subject": subject,
        "sent_at": datetime.now().isoformat()
    }


# Export all tools
ALL_TOOLS = [
    get_department_head,
    check_availability,
    get_fallback_approver,
    get_workload,
    send_email
]
