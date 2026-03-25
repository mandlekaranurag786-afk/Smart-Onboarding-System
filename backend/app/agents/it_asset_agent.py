"""
Agent 2 - IT Asset Agent
Monitors IT asset assignment with SLA tracking and escalation
"""
from typing import Dict, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ITAssetAgent:
    """
    Agent 2: IT Asset Agent
    - Monitor SLA every hour
    - Escalate if overdue
    - Dispatch credentials on completion
    - Unlock portal
    - Notify orchestrator
    """
    
    def __init__(self):
        self.name = "ITAssetAgent"
        self.sla_hours = 24  # 24 hour SLA for IT asset assignment
        logger.info("IT Asset Agent initialized")
    
    async def start_monitoring(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start monitoring IT asset assignment for candidate.
        
        This agent runs continuously and checks:
        1. Has IT responded?
        2. Is SLA breached?
        3. Should we escalate?
        
        Args:
            candidate_data: Candidate information
            
        Returns:
            Monitoring status
        """
        logger.info(f"Starting IT monitoring for: {candidate_data.get('name')}")
        
        result = {
            "agent": self.name,
            "candidate": candidate_data.get('name'),
            "monitoring_started": datetime.now().isoformat(),
            "sla_deadline": (datetime.now() + timedelta(hours=self.sla_hours)).isoformat(),
            "status": "monitoring"
        }
        
        # TODO: This should be a background task that runs every hour
        # For now, we'll return the monitoring setup
        
        return result
    
    async def check_it_status(self, candidate_id: int) -> Dict[str, Any]:
        """
        Check IT asset assignment status.
        
        Returns:
            Status: pending, assigned, overdue, escalated
        """
        # TODO: Query database for IT task status
        logger.info(f"Checking IT status for candidate: {candidate_id}")
        
        # Mock response
        return {
            "candidate_id": candidate_id,
            "it_status": "pending",
            "assigned_at": None,
            "sla_breached": False
        }
    
    async def handle_it_decision(self, candidate_id: int, decision: str, reason: str = None) -> Dict[str, Any]:
        """
        Handle IT decision (Yes/No).
        
        Args:
            candidate_id: Candidate ID
            decision: "yes" or "no"
            reason: Reason if "no"
            
        Returns:
            Action result
        """
        logger.info(f"IT decision for candidate {candidate_id}: {decision}")
        
        if decision.lower() == "yes":
            # IT assigned assets
            result = await self._on_it_completed(candidate_id)
            return result
        else:
            # IT declined, capture reason and reschedule
            result = await self._on_it_declined(candidate_id, reason)
            return result
    
    async def _on_it_completed(self, candidate_id: int) -> Dict[str, Any]:
        """
        Handle IT completion.
        
        Actions:
        1. Mark IT task as complete
        2. Dispatch credentials to candidate
        3. Unlock portal access
        4. Notify orchestrator to trigger scheduling agent
        """
        logger.info(f"IT completed for candidate: {candidate_id}")
        
        # 1. Mark task complete
        # TODO: Update database
        
        # 2. Send credentials
        await self._send_credentials(candidate_id)
        
        # 3. Unlock portal
        await self._unlock_portal(candidate_id)
        
        # 4. Notify orchestrator
        # This will trigger Agent 3 (Scheduling)
        
        return {
            "status": "it_completed",
            "candidate_id": candidate_id,
            "actions": ["credentials_sent", "portal_unlocked"],
            "next_agent": "SchedulingAgent"
        }
    
    async def _on_it_declined(self, candidate_id: int, reason: str) -> Dict[str, Any]:
        """
        Handle IT decline.
        
        Actions:
        1. Capture reason
        2. Set reminder
        3. Update SLA
        """
        logger.info(f"IT declined for candidate {candidate_id}: {reason}")
        
        return {
            "status": "it_declined",
            "candidate_id": candidate_id,
            "reason": reason,
            "reminder_scheduled": True
        }
    
    async def _send_credentials(self, candidate_id: int):
        """Send IT credentials to candidate"""
        logger.info(f"Sending credentials to candidate: {candidate_id}")
        # TODO: Implement email with credentials
        return {"status": "sent"}
    
    async def _unlock_portal(self, candidate_id: int):
        """Unlock portal access for candidate"""
        logger.info(f"Unlocking portal for candidate: {candidate_id}")
        # TODO: Update database to enable portal access
        return {"status": "unlocked"}
    
    async def escalate_overdue(self, candidate_id: int) -> Dict[str, Any]:
        """
        Escalate overdue IT tasks.
        
        Called by background scheduler when SLA breached.
        """
        logger.warning(f"Escalating overdue IT task for candidate: {candidate_id}")
        
        from app.config import IT_EMAIL, ADMIN_EMAIL
        
        # Send escalation email
        # TODO: Implement escalation email
        
        return {
            "status": "escalated",
            "candidate_id": candidate_id,
            "escalated_to": [IT_EMAIL, ADMIN_EMAIL],
            "timestamp": datetime.now().isoformat()
        }
