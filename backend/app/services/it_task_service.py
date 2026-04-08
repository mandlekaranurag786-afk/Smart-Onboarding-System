"""
IT Task Service - Manages IT equipment allocation workflow
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.models import Task, ITTeamMember, Candidate
from app.config import IT_EMAIL
import logging

logger = logging.getLogger(__name__)


class ITTaskService:
    """Service for managing IT equipment allocation tasks"""
    
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
            
            # Check if already responded (idempotent)
            if task.it_response_received_at:
                logger.info(f"Task {task.id} already processed (idempotent response)")
                return {
                    "success": True,
                    "task_id": task.id,
                    "new_status": task.status.value,
                    "message": "Task already processed",
                    "idempotent": True
                }
            
            # Update task based on response
            from app.models.task import TaskStatus
            
            if response == "complete":
                task.status = TaskStatus.COMPLETED
                task.completed_date = datetime.now().date()
                new_status = "completed"
            elif response == "need_time":
                # Use existing BLOCKED status to represent "delayed"
                task.status = TaskStatus.BLOCKED
                new_status = "delayed"
            else:
                return {
                    "success": False,
                    "error": f"Invalid response type: {response}",
                    "error_code": "INVALID_RESPONSE_TYPE"
                }
            
            # Record response details
            task.it_response_received_at = datetime.now()
            task.it_response_type = "button_click"
            task.it_responder_email = responder_email
            task.it_responder_name = responder_name
            task.it_response_message = message
            
            db.commit()
            
            logger.info(
                f"Task {task.id} updated to {new_status} by {responder_name} ({responder_email})"
            )
            
            return {
                "success": True,
                "task_id": task.id,
                "new_status": new_status,
                "message": "Task status updated successfully"
            }
            
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
                subject=f"🖥️ IT Setup Required: {candidate.name} - Joining {joining_date_str}",
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
