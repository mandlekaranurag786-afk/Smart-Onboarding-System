"""
Agent 1 - Onboarding Trigger
Handles initial onboarding setup and notifications
"""
from typing import Dict, Any
import logging
from datetime import datetime, date

from app.database import get_db_context
from app.models.candidate import Candidate, CandidateStatus
from app.models.checklist import Checklist
from app.models.task import Task, TaskStatus, TaskOwner

logger = logging.getLogger(__name__)

class OnboardingTriggerAgent:
    """
    Agent 1: Onboarding Trigger
    - Welcome email to candidate
    - IT request email
    - Create IT ticket
    - Seed checklist
    """
    
    def __init__(self):
        self.name = "OnboardingTrigger"
        logger.info("Onboarding Trigger Agent initialized")
    
    async def trigger_onboarding(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger the onboarding process.
        
        Steps:
        1. Create candidate record in DB
        2. Generate 9-task checklist
        3. Send welcome email to candidate
        4. Send IT request email
        5. Send HR notification
        6. Send Admin notification
        
        Args:
            candidate_data: {name, email, department, joining_date, reporting_manager}
            
        Returns:
            Result with checklist_id, emails_sent, status
        """
        logger.info(f"Triggering onboarding for: {candidate_data.get('name')}")
        
        result = {
            "agent": self.name,
            "candidate": candidate_data.get('name'),
            "timestamp": datetime.now().isoformat(),
            "actions": []
        }
        
        try:
            with get_db_context() as db:
                # 1. Create candidate record
                candidate = self._create_candidate_record(db, candidate_data)
                result["candidate_id"] = candidate.id
                result["actions"].append("candidate_record_created")
                
                # 2. Generate checklist
                checklist = self._generate_checklist(db, candidate)
                result["checklist_id"] = checklist.id
                result["actions"].append("checklist_generated")
            
            # 3. Send welcome email to candidate
            await self._send_welcome_email(candidate_data)
            result["actions"].append("welcome_email_sent")
            
            # 4. Send IT request email
            await self._send_it_request(candidate_data)
            result["actions"].append("it_request_sent")
            
            # 5. Send HR notification
            await self._send_hr_notification(candidate_data)
            result["actions"].append("hr_notification_sent")
            
            # 6. Send Admin notification
            await self._send_admin_notification(candidate_data)
            result["actions"].append("admin_notification_sent")
            
            result["status"] = "success"
            logger.info(f"Onboarding triggered successfully for: {candidate_data.get('name')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Onboarding trigger failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
            return result
    
    def _create_candidate_record(self, db, candidate_data: Dict[str, Any]) -> Candidate:
        """Create candidate record in database"""
        logger.info(f"Creating candidate record for: {candidate_data.get('name')}")
        
        # Parse joining date
        joining_date_str = candidate_data.get('joining_date')
        if isinstance(joining_date_str, str):
            joining_date = datetime.strptime(joining_date_str, "%Y-%m-%d").date()
        else:
            joining_date = joining_date_str or date.today()
        
        candidate = Candidate(
            name=candidate_data.get('name'),
            email=candidate_data.get('email'),
            department=candidate_data.get('department'),
            role=candidate_data.get('role', 'Employee'),
            joining_date=joining_date,
            reporting_manager=candidate_data.get('reporting_manager'),
            status=CandidateStatus.ONBOARDING_STARTED
        )
        
        db.add(candidate)
        db.flush()  # Get the ID without committing
        
        logger.info(f"Created candidate record with ID: {candidate.id}")
        return candidate
    
    def _generate_checklist(self, db, candidate: Candidate) -> Checklist:
        """Generate 9-task onboarding checklist"""
        logger.info(f"Generating checklist for candidate: {candidate.id}")
        
        # Create checklist
        checklist = Checklist(candidate_id=candidate.id)
        db.add(checklist)
        db.flush()
        
        # Define 9 tasks
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
        
        # Create tasks
        for task_data in tasks_data:
            task = Task(
                checklist_id=checklist.id,
                name=task_data["name"],
                task_type=task_data["task_type"],
                owner=task_data["owner"],
                status=TaskStatus.PENDING
            )
            db.add(task)
        
        logger.info(f"Generated checklist with {len(tasks_data)} tasks")
        return checklist
    
    async def _send_welcome_email(self, candidate_data: Dict[str, Any]):
        """Send welcome email to candidate"""
        logger.info(f"Sending welcome email to: {candidate_data.get('email')}")
        # TODO: Implement actual email sending
        return {"status": "sent"}
    
    async def _send_it_request(self, candidate_data: Dict[str, Any]):
        """Send IT asset request email"""
        from app.config import IT_EMAIL
        logger.info(f"Sending IT request to: {IT_EMAIL}")
        # TODO: Implement actual email sending
        return {"status": "sent"}
    
    async def _send_hr_notification(self, candidate_data: Dict[str, Any]):
        """Send HR notification"""
        from app.config import HR_EMAIL
        logger.info(f"Sending HR notification to: {HR_EMAIL}")
        return {"status": "sent"}
    
    async def _send_admin_notification(self, candidate_data: Dict[str, Any]):
        """Send Admin notification"""
        from app.config import ADMIN_EMAIL
        logger.info(f"Sending Admin notification to: {ADMIN_EMAIL}")
        return {"status": "sent"}
