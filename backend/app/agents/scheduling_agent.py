"""
Agent 3 - Scheduling Agent
Intelligent meeting scheduling with availability checking and fallback routing
"""
from typing import Dict, Any, List
import logging
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage
from app.llm_client import get_llm

logger = logging.getLogger(__name__)

class SchedulingAgent:
    """
    Agent 3: Scheduling Agent
    - Read Excel/Calendar for availability
    - Check availability using LLM reasoning
    - Book primary or fallback to backup
    - Send confirmation emails
    - Mark pending if no slots
    """
    
    def __init__(self):
        self.name = "SchedulingAgent"
        self.llm = get_llm()
        logger.info("Scheduling Agent initialized with LLM")
    
    async def schedule_meetings(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule all required meetings for candidate.
        
        Meetings to schedule:
        1. HR Walkthrough
        2. Reporting Manager Intro
        3. Delivery Head Overview
        
        Args:
            candidate_data: Candidate information with department
            
        Returns:
            Scheduling results for all meetings
        """
        logger.info(f"Scheduling meetings for: {candidate_data.get('name')}")
        
        result = {
            "agent": self.name,
            "candidate": candidate_data.get('name'),
            "meetings": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # 1. Schedule HR meeting
            hr_meeting = await self._schedule_hr_meeting(candidate_data)
            result["meetings"].append(hr_meeting)
            
            # 2. Schedule Reporting Manager meeting
            manager_meeting = await self._schedule_manager_meeting(candidate_data)
            result["meetings"].append(manager_meeting)
            
            # 3. Schedule Delivery Head meeting (uses LLM for intelligent routing)
            delivery_meeting = await self._schedule_delivery_head_meeting(candidate_data)
            result["meetings"].append(delivery_meeting)
            
            result["status"] = "success"
            result["total_scheduled"] = len([m for m in result["meetings"] if m["status"] == "scheduled"])
            
            logger.info(f"Scheduled {result['total_scheduled']} meetings for: {candidate_data.get('name')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Scheduling failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
            return result
    
    async def _schedule_hr_meeting(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule HR walkthrough meeting"""
        logger.info("Scheduling HR meeting")
        
        # Check HR availability (mock)
        from app.config import HR_EMAIL
        
        return {
            "meeting_type": "HR Walkthrough",
            "with": "Mohini (HR)",
            "email": HR_EMAIL,
            "status": "scheduled",
            "scheduled_time": "2026-03-25 10:00 AM",
            "confirmation_sent": True
        }
    
    async def _schedule_manager_meeting(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule Reporting Manager meeting"""
        logger.info("Scheduling Manager meeting")
        
        manager = candidate_data.get('reporting_manager', 'Manager')
        
        return {
            "meeting_type": "Reporting Manager Intro",
            "with": manager,
            "email": f"{manager.lower().replace(' ', '.')}@konverge.ai",
            "status": "scheduled",
            "scheduled_time": "2026-03-25 02:00 PM",
            "confirmation_sent": True
        }
    
    async def _schedule_delivery_head_meeting(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule Delivery Head meeting using LLM for intelligent routing.
        
        This is where the agentic intelligence comes in:
        - Find delivery head for department
        - Check availability
        - Route to fallback if unavailable
        """
        logger.info("Scheduling Delivery Head meeting with LLM routing")
        
        department = candidate_data.get('department', '')
        
        # Use LLM to make intelligent routing decision
        routing_decision = await self._intelligent_routing(candidate_data)
        
        if routing_decision["available"]:
            return {
                "meeting_type": "Delivery Head Overview",
                "with": routing_decision["stakeholder_name"],
                "email": routing_decision["stakeholder_email"],
                "status": "scheduled",
                "scheduled_time": routing_decision["scheduled_time"],
                "is_fallback": routing_decision.get("is_fallback", False),
                "reasoning": routing_decision.get("reasoning", ""),
                "confirmation_sent": True
            }
        else:
            return {
                "meeting_type": "Delivery Head Overview",
                "with": routing_decision["stakeholder_name"],
                "email": routing_decision["stakeholder_email"],
                "status": "pending",
                "reason": routing_decision.get("reason", "No availability"),
                "confirmation_sent": False
            }
    
    async def _intelligent_routing(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to make intelligent routing decision.
        
        This implements the agentic workflow:
        - Candidate from AI dept → Find Sajal
        - Check if Sajal available
        - If on leave → Route to fallback (Jane)
        """
        department = candidate_data.get('department', '')
        name = candidate_data.get('name', '')
        
        # Mock availability data (in production, this comes from calendar/DB)
        availability_data = {
            "Sajal": {"available": False, "on_leave_until": "2026-03-25", "role": "AI Delivery Head"},
            "Jane Smith": {"available": True, "on_leave_until": None, "role": "Senior Delivery Manager"},
            "Prathamesh": {"available": True, "on_leave_until": None, "role": "Cloud Delivery Head"}
        }
        
        # Build LLM prompt
        prompt = f"""You are a meeting scheduling agent for KONVERGE.AI.

CANDIDATE: {name}
DEPARTMENT: {department}

AVAILABILITY DATA:
{self._format_availability(availability_data)}

TASK: Schedule a meeting with the appropriate Delivery Head.

RULES:
1. Find the delivery head for the candidate's department
2. Check if they are available
3. If unavailable, route to the fallback person
4. Provide clear reasoning

OUTPUT FORMAT (JSON):
{{
  "stakeholder_name": "Name",
  "stakeholder_email": "email@konverge.ai",
  "available": true/false,
  "is_fallback": true/false,
  "reasoning": "explanation",
  "scheduled_time": "2026-03-25 03:00 PM"
}}
"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Parse LLM response
            import json
            decision = json.loads(response.content)
            
            logger.info(f"LLM routing decision: {decision}")
            return decision
            
        except Exception as e:
            logger.error(f"LLM routing failed: {e}, using fallback")
            
            # Deterministic fallback
            if "AI" in department or "Artificial Intelligence" in department:
                return {
                    "stakeholder_name": "Jane Smith",
                    "stakeholder_email": "jane@konverge.ai",
                    "available": True,
                    "is_fallback": True,
                    "reasoning": "Sajal on leave, routed to Jane (fallback)",
                    "scheduled_time": "2026-03-25 03:00 PM"
                }
            else:
                return {
                    "stakeholder_name": "Admin",
                    "stakeholder_email": "admin@konverge.ai",
                    "available": True,
                    "is_fallback": False,
                    "reasoning": "Default routing",
                    "scheduled_time": "2026-03-25 03:00 PM"
                }
    
    def _format_availability(self, availability_data: Dict[str, Any]) -> str:
        """Format availability data for LLM"""
        lines = []
        for person, data in availability_data.items():
            status = "AVAILABLE" if data["available"] else f"ON LEAVE until {data['on_leave_until']}"
            lines.append(f"- {person} ({data['role']}): {status}")
        return "\n".join(lines)
