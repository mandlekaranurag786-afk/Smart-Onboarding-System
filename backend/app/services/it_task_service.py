"""
IT Task Service - Manages IT equipment allocation workflow
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import Task, ITTeamMember, Candidate
from app.models.task import TaskStatus
from app.config import IT_EMAIL
import logging

from app.services.it_task_events import it_task_event_bus

logger = logging.getLogger(__name__)


class ITTaskService:
    """Service for managing IT equipment allocation tasks"""

    @staticmethod
    def _build_task_update_payload(task: Task) -> Dict[str, Any]:
        """Create a consistent payload for API responses and realtime events."""
        candidate = task.checklist.candidate if task.checklist else None

        days_pending = 0
        if task.status.value == "pending" and task.created_at:
            days_pending = max(0, (datetime.now() - task.created_at).days)

        return {
            "task_id": task.id,
            "candidate_id": candidate.id if candidate else None,
            "candidate_name": candidate.name if candidate else "Unknown",
            "status": task.status.value,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "response_received_at": (
                task.it_response_received_at.isoformat()
                if task.it_response_received_at else None
            ),
            "responder_name": task.it_responder_name,
            "responder_email": task.it_responder_email,
            "days_pending": days_pending,
        }

    @staticmethod
    def _publish_task_update(task: Task) -> None:
        payload = ITTaskService._build_task_update_payload(task)
        it_task_event_bus.publish_task_update(task.id, payload)

    @staticmethod
    def _log_it_response_activity(
        db: Session,
        task: Task,
        responder_name: str,
        response: str,
        response_type: str,
    ) -> None:
        try:
            from app.api.activities import log_activity

            candidate = task.checklist.candidate if task.checklist else None
            if not candidate:
                return

            if response == "complete":
                action_text = f"completed IT equipment allocation for {candidate.name}"
                icon = "check-circle"
            elif response == "need_time":
                action_text = f"requested more time for IT setup for {candidate.name}"
                icon = "clock"
            else:
                action_text = f"responded to IT setup request for {candidate.name}"
                icon = "mail"

            if response_type == "email_reply":
                action_text += " via email."
            else:
                action_text += "."

            log_activity(
                db,
                user_name=responder_name,
                user_role="IT Team",
                action_text=action_text,
                target_object="IT Equipment",
                activity_type="it_response",
                icon_type=icon,
            )
            logger.info(f"Activity logged for IT response on task {task.id}")
        except Exception as exc:
            logger.error(f"Failed to log IT response activity for task {task.id}: {exc}")

    @staticmethod
    def _send_hr_notification(
        task: Task,
        response: str,
        responder_name: str,
        response_type: str,
        message: Optional[str] = None,
        confidence: Optional[float] = None,
    ) -> None:
        try:
            from app.config import HR_EMAIL
            from app.email.azure_email_service import AzureEmailService

            if not HR_EMAIL or response not in {"complete", "need_time"}:
                return

            candidate = task.checklist.candidate if task.checklist else None
            if not candidate:
                return

            email_service = AzureEmailService()
            status_emoji = "✅" if response == "complete" else "⏰"
            status_text = "Completed" if response == "complete" else "Needs More Time"
            response_label = "Email Reply" if response_type == "email_reply" else "Action Button"

            message_block = ""
            if message:
                trimmed_message = message[:200]
                if len(message) > 200:
                    trimmed_message += "..."
                message_block = f"""
        <div class="message-box">
            <p><strong>IT Team Message:</strong></p>
            <p>{trimmed_message}</p>
        </div>
"""

            confidence_line = ""
            if confidence is not None:
                confidence_line = f"<p><strong>AI Confidence:</strong> {confidence:.0%}</p>"

            hr_notification_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: auto; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; background-color: #ffffff; }}
        .header {{ background-color: #4CAF50; color: white; padding: 15px; border-radius: 6px 6px 0 0; text-align: center; }}
        .info-box {{ background-color: #f9f9f9; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0; border-radius: 4px; }}
        .message-box {{ background-color: #f0f7ff; padding: 15px; border-left: 4px solid #2196F3; margin: 20px 0; border-radius: 4px; font-style: italic; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>{status_emoji} IT Response Received</h2>
        </div>

        <p>Hi HR Team,</p>
        <p>The IT team has responded to the equipment allocation request.</p>

        <div class="info-box">
            <p><strong>Candidate:</strong> {candidate.name}</p>
            <p><strong>Email:</strong> {candidate.email}</p>
            <p><strong>Department:</strong> {candidate.department}</p>
            <p><strong>IT Status:</strong> {status_text}</p>
            <p><strong>Responded By:</strong> {responder_name}</p>
            <p><strong>Response Method:</strong> {response_label}</p>
            {confidence_line}
        </div>
        {message_block}
        {"<p>✅ IT equipment has been allocated and is ready for the candidate's joining date.</p>" if response == "complete" else "<p>⏰ IT team needs more time to complete the allocation.</p>"}

        <p>Best regards,<br><strong>OnboardIQ System</strong></p>
    </div>
</body>
</html>
"""

            subject_prefix = "IT Email Response" if response_type == "email_reply" else "IT Response"
            hr_result = email_service._send_email(
                to_email=HR_EMAIL,
                subject=f"{status_emoji} {subject_prefix}: {candidate.name} - {status_text}",
                html_content=hr_notification_html,
            )

            if hr_result.success:
                logger.info(f"HR notification sent for task {task.id}")
            else:
                logger.warning(f"Failed to send HR notification for task {task.id}: {hr_result.message}")
        except Exception as exc:
            logger.error(f"Error sending HR notification for task {task.id}: {exc}")

    @staticmethod
    def _sync_account_provisioning_task(task: Task, response: str) -> None:
        """
        Keep the legacy Account Provisioning checklist task aligned with IT completion.

        The candidate portal still renders the SYSTEM-owned "Account Provisioning"
        task, while the IT workflow updates the dedicated `it_equipment_allocation`
        task. To keep both HR and candidate views consistent, we mirror completion
        state onto the legacy task in the same checklist.
        """
        checklist = task.checklist
        if not checklist:
            return

        account_task = next(
            (
                checklist_task for checklist_task in checklist.tasks
                if checklist_task.id != task.id
                and (checklist_task.task_type or "").lower() == "account_provisioning"
            ),
            None,
        )

        if not account_task:
            return

        if response == "complete":
            account_task.status = TaskStatus.COMPLETED
            account_task.completed_date = datetime.now().date()
        elif response == "need_time":
            account_task.status = TaskStatus.PENDING
            account_task.completed_date = None
        elif response == "unclear":
            account_task.status = TaskStatus.IN_PROGRESS
            account_task.completed_date = None

    @staticmethod
    def apply_it_response(
        task: Task,
        response: str,
        responder_email: str,
        responder_name: str,
        message: Optional[str],
        response_type: str,
        db: Session,
        confidence: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Apply a validated IT response and fan out the downstream effects."""
        if task.it_response_received_at:
            logger.info(f"Task {task.id} already processed (idempotent response)")
            return {
                "success": True,
                "task_id": task.id,
                "new_status": task.status.value,
                "message": "Task already processed",
                "idempotent": True,
                "task_event": ITTaskService._build_task_update_payload(task),
            }

        if response == "complete":
            task.status = TaskStatus.COMPLETED
            task.completed_date = datetime.now().date()
            new_status = "completed"
        elif response == "need_time":
            task.status = TaskStatus.BLOCKED
            new_status = "delayed"
        elif response == "unclear":
            task.status = TaskStatus.IN_PROGRESS
            new_status = "in_progress"
        else:
            return {
                "success": False,
                "error": f"Invalid response type: {response}",
                "error_code": "INVALID_RESPONSE_TYPE",
            }

        task.it_response_received_at = datetime.now()
        task.it_response_type = response_type
        task.it_responder_email = responder_email
        task.it_responder_name = responder_name
        task.it_response_message = message
        ITTaskService._sync_account_provisioning_task(task, response)

        checklist = task.checklist
        if checklist:
            checklist.calculate_completion()

        db.commit()
        db.refresh(task)

        logger.info(
            f"Task {task.id} updated to {new_status} by {responder_name} ({responder_email}) via {response_type}"
        )

        ITTaskService._log_it_response_activity(
            db=db,
            task=task,
            responder_name=responder_name,
            response=response,
            response_type=response_type,
        )
        ITTaskService._send_hr_notification(
            task=task,
            response=response,
            responder_name=responder_name,
            response_type=response_type,
            message=message,
            confidence=confidence,
        )
        ITTaskService._publish_task_update(task)

        return {
            "success": True,
            "task_id": task.id,
            "new_status": new_status,
            "message": "Task status updated successfully",
            "task_event": ITTaskService._build_task_update_payload(task),
        }
    
    @staticmethod
    def create_it_task(
        checklist_id: int,
        candidate_id: int,
        candidate_name: str,
        joining_date,  # Can be datetime or date
        db: Session
    ) -> Task:
        """
        Create an IT equipment allocation task with response token
        
        Args:
            checklist_id: ID of the checklist this task belongs to
            candidate_id: ID of the candidate
            candidate_name: Name of the candidate
            joining_date: Candidate's joining date (datetime or date object)
            db: Database session
            
        Returns:
            Created Task object with response token
            
        Example:
            >>> task = ITTaskService.create_it_task(
            ...     checklist_id=1,
            ...     candidate_id=123,
            ...     candidate_name="John Doe",
            ...     joining_date=datetime(2024, 1, 15),
            ...     db=db
            ... )
            >>> print(f"Created task {task.id} with token {task.it_response_token}")
        """
        from app.models.task import TaskStatus, TaskOwner
        from datetime import date
        
        try:
            # Calculate due date (1 day before joining date)
            if joining_date:
                # Convert to date if it's a datetime
                if isinstance(joining_date, datetime):
                    joining_date_obj = joining_date.date()
                else:
                    joining_date_obj = joining_date
                due_date = joining_date_obj - timedelta(days=1)
            else:
                due_date = None
            
            # Create IT task
            task = Task(
                checklist_id=checklist_id,
                name=f"IT Equipment Allocation for {candidate_name}",
                description=(
                    f"Allocate laptop, setup email account, assign software licenses, "
                    f"and configure system access for {candidate_name}"
                ),
                task_type="it_equipment_allocation",
                owner=TaskOwner.IT,
                assigned_to_email=IT_EMAIL,
                assigned_to_name="IT Team",
                status=TaskStatus.PENDING,
                due_date=due_date,
                it_reminder_sent_count=0
            )
            
            db.add(task)
            db.flush()  # Flush to get task.id
            
            # Generate and assign response token
            token = ITTaskService.generate_response_token(task.id, candidate_id)
            task.it_response_token = token
            
            db.commit()
            
            logger.info(
                f"Created IT task {task.id} for candidate {candidate_id} "
                f"with token {token[:20]}..."
            )
            
            return task
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating IT task: {e}")
            raise
    
    @staticmethod
    def generate_response_token(task_id: int, candidate_id: int) -> str:
        """
        Generate a secure, unique token for task responses
        
        Format: {task_id}_{timestamp}_{random_hash}
        
        Args:
            task_id: ID of the task
            candidate_id: ID of the candidate
            
        Returns:
            Secure token string
            
        Example:
            >>> token = ITTaskService.generate_response_token(123, 456)
            >>> print(token)
            '123_1704902400_a1b2c3d4e5f6g7h8'
        """
        timestamp = int(datetime.now().timestamp())
        random_bytes = secrets.token_bytes(16)
        hash_input = f"{task_id}_{candidate_id}_{timestamp}_{random_bytes.hex()}"
        token_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        return f"{task_id}_{timestamp}_{token_hash}"
    
    @staticmethod
    def validate_token(token: str, db: Session) -> Optional[Task]:
        """
        Validate a response token and return the associated task
        
        Args:
            token: The response token to validate
            db: Database session
            
        Returns:
            Task object if token is valid, None otherwise
            
        Example:
            >>> task = ITTaskService.validate_token("123_1704902400_a1b2c3d4", db)
            >>> if task:
            ...     print(f"Valid token for task: {task.name}")
        """
        if not token:
            logger.warning("Empty token provided")
            return None
        
        try:
            # Query task by token
            task = db.query(Task).filter(Task.it_response_token == token).first()
            
            if not task:
                logger.warning(f"No task found for token: {token[:20]}...")
                return None
            
            # Check if task already has a response
            if task.it_response_received_at:
                logger.info(f"Task {task.id} already has a response (idempotent check)")
                # Still return the task for idempotent handling
                return task
            
            return task
            
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return None
    
    @staticmethod
    def verify_it_team_member(email: str, db: Session) -> bool:
        """
        Verify if email belongs to authorized IT team member
        
        Args:
            email: Email address to verify
            db: Database session
            
        Returns:
            True if authorized, False otherwise
            
        Example:
            >>> is_authorized = ITTaskService.verify_it_team_member("it@company.com", db)
            >>> if is_authorized:
            ...     print("Authorized IT team member")
        """
        if not email:
            return False
        
        # Normalize email to lowercase for comparison
        email = email.lower().strip()
        
        # Check against IT_EMAIL config
        if IT_EMAIL and email == IT_EMAIL.lower().strip():
            logger.info(f"Email {email} authorized via IT_EMAIL config")
            return True
        
        # Check against ITTeamMember table
        try:
            member = db.query(ITTeamMember).filter(
                ITTeamMember.email == email,
                ITTeamMember.is_active == 1
            ).first()
            
            if member:
                logger.info(f"Email {email} authorized via ITTeamMember table")
                return True
            else:
                logger.warning(f"Email {email} not authorized")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying IT team member: {e}")
            return False
    
    @staticmethod
    def create_it_task_token(task: Task, candidate_id: int, db: Session) -> str:
        """
        Generate and assign a response token to an IT task
        
        Args:
            task: Task object to assign token to
            candidate_id: ID of the candidate
            db: Database session
            
        Returns:
            Generated token string
            
        Example:
            >>> task = db.query(Task).filter(Task.id == 123).first()
            >>> token = ITTaskService.create_it_task_token(task, 456, db)
            >>> db.commit()
        """
        # Generate token
        token = ITTaskService.generate_response_token(task.id, candidate_id)
        
        # Assign to task
        task.it_response_token = token
        
        logger.info(f"Generated token for task {task.id}")
        return token
    
    @staticmethod
    def process_button_response(
        token: str,
        response: str,
        responder_email: str,
        responder_name: str,
        message: Optional[str],
        db: Session
    ) -> Dict:
        """
        Process action button click from IT team
        
        Args:
            token: Task response token
            response: Response type ("complete" or "need_time")
            responder_email: Email of IT team member
            responder_name: Name of IT team member
            message: Optional message from IT team
            db: Database session
            
        Returns:
            Dictionary with success status and details
            
        Example:
            >>> result = ITTaskService.process_button_response(
            ...     token="123_1704902400_a1b2c3d4",
            ...     response="complete",
            ...     responder_email="it@company.com",
            ...     responder_name="John Doe",
            ...     message="Laptop allocated",
            ...     db=db
            ... )
            >>> print(result["success"])
            True
        """
        try:
            # Validate token
            task = ITTaskService.validate_token(token, db)
            if not task:
                return {
                    "success": False,
                    "error": "Invalid or expired token",
                    "error_code": "INVALID_TOKEN"
                }
            
            # Verify IT team member
            if not ITTaskService.verify_it_team_member(responder_email, db):
                # Log unauthorized attempt
                logger.warning(
                    f"Unauthorized response attempt - "
                    f"Email: {responder_email}, Task: {task.id}, Token: {token[:20]}..."
                )
                return {
                    "success": False,
                    "error": "Unauthorized: Email not recognized as IT team member",
                    "error_code": "UNAUTHORIZED"
                }
            
            result = ITTaskService.apply_it_response(
                task=task,
                response=response,
                responder_email=responder_email,
                responder_name=responder_name,
                message=message,
                response_type="button_click",
                db=db,
            )
            return result
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing button response: {e}")
            return {
                "success": False,
                "error": "Internal server error",
                "error_code": "SERVER_ERROR"
            }

    
    @staticmethod
    def send_it_notification_email(
        task: Task,
        candidate: Candidate,
        db: Session
    ) -> Dict:
        """
        Send IT notification email with action buttons
        
        Args:
            task: IT task object
            candidate: Candidate object
            db: Database session
            
        Returns:
            Dictionary with success status and details
            
        Example:
            >>> result = ITTaskService.send_it_notification_email(task, candidate, db)
            >>> if result["success"]:
            ...     print("Email sent successfully")
        """
        try:
            from app.email.email_templates import render_it_equipment_allocation_email
            from app.email.azure_email_service import AzureEmailService
            from app.config import IT_EMAIL, BACKEND_URL
            
            if not IT_EMAIL:
                logger.error("IT_EMAIL not configured")
                return {
                    "success": False,
                    "error": "IT_EMAIL not configured"
                }
            
            if not task.it_response_token:
                logger.error(f"Task {task.id} has no response token")
                return {
                    "success": False,
                    "error": "Task has no response token"
                }
            
            # Prepare email data
            joining_date_str = candidate.joining_date.strftime("%B %d, %Y") if candidate.joining_date else "TBD"
            
            # Render email HTML
            email_html = render_it_equipment_allocation_email(
                candidate_name=candidate.name,
                candidate_email=candidate.email,
                role=candidate.role or "N/A",
                department=candidate.department or "N/A",
                joining_date=joining_date_str,
                reporting_manager=candidate.reporting_manager or "N/A",
                task_token=task.it_response_token,
                backend_url=BACKEND_URL or "http://localhost:8000"
            )
            
            # Send email using Azure service
            email_service = AzureEmailService()
            result = email_service._send_email(
                to_email=IT_EMAIL,
                subject=f"🖥️ IT Setup Required [Task:{task.it_response_token}] {candidate.name} - Joining {joining_date_str}",
                html_content=email_html
            )
            
            if result.success:
                logger.info(
                    f"IT notification email sent for task {task.id} to {IT_EMAIL}"
                )
                return {
                    "success": True,
                    "message": "IT notification email sent successfully",
                    "recipient": IT_EMAIL
                }
            else:
                logger.error(
                    f"Failed to send IT notification email for task {task.id}: "
                    f"{result.message}"
                )
                return {
                    "success": False,
                    "error": result.message
                }
                
        except Exception as e:
            logger.error(f"Error sending IT notification email: {e}")
            return {
                "success": False,
                "error": str(e)
            }
