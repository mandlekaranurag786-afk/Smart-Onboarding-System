"""
Email Reply Processor Service
Handles incoming email replies from IT team and updates task status using NLP
"""
import re
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import Task, Candidate
from app.models.task import TaskStatus
from app.services.it_task_service import ITTaskService

logger = logging.getLogger(__name__)


class EmailReplyProcessor:
    """
    Service for processing email replies from IT team
    Uses LLM to detect allocation status from natural language
    """
    
    @staticmethod
    def extract_task_token_from_email(email_body: str, email_subject: str) -> Optional[str]:
        """
        Extract task token from email body or subject
        
        Args:
            email_body: Email body content
            email_subject: Email subject line
            
        Returns:
            Task token if found, None otherwise
        """
        # Pattern: task_id_timestamp_hash (e.g., "123_1704902400_a1b2c3d4")
        token_pattern = r'\b(\d+_\d+_[a-f0-9]{16})\b'
        
        # Search in body first
        match = re.search(token_pattern, email_body, re.IGNORECASE)
        if match:
            logger.info(f"Found task token in email body: {match.group(1)}")
            return match.group(1)
        
        # Search in subject
        match = re.search(token_pattern, email_subject, re.IGNORECASE)
        if match:
            logger.info(f"Found task token in email subject: {match.group(1)}")
            return match.group(1)
        
        logger.warning("No task token found in email")
        return None
    
    @staticmethod
    def find_task_by_candidate_email(candidate_email: str, db: Session) -> Optional[Task]:
        """
        Find pending IT task by candidate email
        
        Args:
            candidate_email: Email of the candidate
            db: Database session
            
        Returns:
            Task object if found, None otherwise
        """
        try:
            # Find candidate
            candidate = db.query(Candidate).filter(
                Candidate.email == candidate_email
            ).first()
            
            if not candidate:
                logger.warning(f"No candidate found with email: {candidate_email}")
                return None
            
            # Find pending IT task for this candidate
            task = db.query(Task).join(
                Task.checklist
            ).filter(
                Task.checklist.has(candidate_id=candidate.id),
                Task.task_type == "it_equipment_allocation",
                Task.status == TaskStatus.PENDING
            ).order_by(Task.created_at.desc()).first()
            
            if task:
                logger.info(f"Found pending IT task {task.id} for candidate {candidate.name}")
                return task
            else:
                logger.warning(f"No pending IT task found for candidate {candidate.name}")
                return None
                
        except Exception as e:
            logger.error(f"Error finding task by candidate email: {e}")
            return None
    
    @staticmethod
    def analyze_email_intent(email_body: str, email_subject: str) -> Tuple[str, float, str]:
        """
        Use LLM to analyze email content and detect IT allocation status
        
        Args:
            email_body: Email body content
            email_subject: Email subject line
            
        Returns:
            Tuple of (intent, confidence, reasoning)
            - intent: "complete", "need_time", or "unclear"
            - confidence: 0.0 to 1.0
            - reasoning: Explanation of the decision
        """
        try:
            from app.llm_client import get_llm_client
            
            llm_client = get_llm_client()
            
            prompt = f"""You are an AI assistant analyzing email replies from IT team members regarding equipment allocation for new employees.

Email Subject: {email_subject}

Email Body:
{email_body}

Analyze this email and determine the IT team's response regarding equipment allocation.

Possible intents:
1. "complete" - IT has completed the allocation (laptop allocated, email setup done, ready)
2. "need_time" - IT needs more time or is delayed (working on it, need a few days, delayed)
3. "unclear" - Cannot determine the intent clearly

Respond in this exact JSON format:
{{
    "intent": "complete" or "need_time" or "unclear",
    "confidence": 0.0 to 1.0,
    "reasoning": "Brief explanation of why you chose this intent"
}}

Keywords to look for:
- Complete: "allocated", "done", "completed", "ready", "set up", "finished", "all set"
- Need Time: "need time", "delayed", "working on", "in progress", "few days", "not ready yet"

Only respond with the JSON, nothing else."""

            response = llm_client.chat.completions.create(
                model=llm_client.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes emails and returns JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            result = json.loads(result_text)
            
            intent = result.get("intent", "unclear")
            confidence = float(result.get("confidence", 0.0))
            reasoning = result.get("reasoning", "No reasoning provided")
            
            logger.info(
                f"Email intent analysis: intent={intent}, "
                f"confidence={confidence:.2f}, reasoning={reasoning}"
            )
            
            return intent, confidence, reasoning
            
        except Exception as e:
            logger.error(f"Error analyzing email intent with LLM: {e}")
            # Fallback to simple keyword matching
            return EmailReplyProcessor._fallback_keyword_analysis(email_body, email_subject)
    
    @staticmethod
    def _fallback_keyword_analysis(email_body: str, email_subject: str) -> Tuple[str, float, str]:
        """
        Fallback keyword-based analysis if LLM fails
        
        Args:
            email_body: Email body content
            email_subject: Email subject line
            
        Returns:
            Tuple of (intent, confidence, reasoning)
        """
        text = f"{email_subject} {email_body}".lower()
        
        # Strong negative indicators (override completion keywords)
        strong_negative = ["not ready", "not done", "not completed", "being set up", "being configured"]
        has_strong_negative = any(neg in text for neg in strong_negative)
        
        # Keywords for completion
        complete_keywords = [
            "allocated", "done", "completed", "ready", "finished",
            "all set", "good to go", "prepared", "active", "everything is done"
        ]
        
        # Keywords for delay
        delay_keywords = [
            "need time", "need more time", "need a few", "need another",
            "delayed", "working on", "in progress", "still working",
            "few days", "more days", "pending", "on order", "being"
        ]
        
        complete_count = sum(1 for keyword in complete_keywords if keyword in text)
        delay_count = sum(1 for keyword in delay_keywords if keyword in text)
        
        # If strong negative, force delay
        if has_strong_negative:
            return "need_time", 0.8, "Strong negative indicator found"
        
        if complete_count > delay_count and complete_count > 0:
            confidence = min(0.8, 0.5 + (complete_count * 0.1))
            return "complete", confidence, f"Found {complete_count} completion keywords"
        elif delay_count > complete_count and delay_count > 0:
            confidence = min(0.8, 0.5 + (delay_count * 0.1))
            return "need_time", confidence, f"Found {delay_count} delay keywords"
        else:
            return "unclear", 0.3, "No clear keywords found"
    
    @staticmethod
    def process_email_reply(
        sender_email: str,
        sender_name: str,
        email_subject: str,
        email_body: str,
        db: Session
    ) -> Dict:
        """
        Process incoming email reply from IT team
        
        Args:
            sender_email: Email address of sender
            sender_name: Name of sender
            email_subject: Email subject line
            email_body: Email body content
            db: Database session
            
        Returns:
            Dictionary with processing result
        """
        try:
            logger.info(f"Processing email reply from {sender_name} ({sender_email})")
            
            # Step 1: Verify sender is IT team member
            if not ITTaskService.verify_it_team_member(sender_email, db):
                logger.warning(f"Unauthorized email from {sender_email}")
                return {
                    "success": False,
                    "error": "Sender is not an authorized IT team member",
                    "error_code": "UNAUTHORIZED"
                }
            
            # Step 2: Extract task token from email
            task_token = EmailReplyProcessor.extract_task_token_from_email(
                email_body, email_subject
            )
            
            task = None
            if task_token:
                # Find task by token
                task = ITTaskService.validate_token(task_token, db)
            
            # Step 3: If no token found, try to find task by candidate email mentioned in email
            if not task:
                # Extract email addresses from email body
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                candidate_emails = re.findall(email_pattern, email_body)
                
                for candidate_email in candidate_emails:
                    if candidate_email.lower() != sender_email.lower():
                        task = EmailReplyProcessor.find_task_by_candidate_email(
                            candidate_email, db
                        )
                        if task:
                            break
            
            if not task:
                logger.warning("Could not find associated task for email reply")
                return {
                    "success": False,
                    "error": "Could not find associated task. Please include task ID or candidate email.",
                    "error_code": "TASK_NOT_FOUND"
                }
            
            # Step 4: Check if task already responded (idempotent)
            if task.it_response_received_at:
                logger.info(f"Task {task.id} already processed (idempotent)")
                return {
                    "success": True,
                    "task_id": task.id,
                    "message": "Task already processed",
                    "idempotent": True
                }
            
            # Step 5: Analyze email intent using LLM
            intent, confidence, reasoning = EmailReplyProcessor.analyze_email_intent(
                email_body, email_subject
            )
            
            logger.info(
                f"Email analysis for task {task.id}: "
                f"intent={intent}, confidence={confidence:.2f}"
            )
            
            # Step 6: Update task based on intent
            if intent == "complete" and confidence >= 0.5:
                task.status = TaskStatus.COMPLETED
                task.completed_date = datetime.now().date()
                new_status = "completed"
            elif intent == "need_time" and confidence >= 0.5:
                task.status = TaskStatus.BLOCKED  # Using BLOCKED for "delayed"
                new_status = "delayed"
            else:
                # If unclear or low confidence, mark as in_progress and notify HR
                task.status = TaskStatus.IN_PROGRESS
                new_status = "in_progress"
                logger.warning(
                    f"Unclear intent for task {task.id} (confidence={confidence:.2f}). "
                    f"Marking as in_progress."
                )
            
            # Step 7: Record response details
            task.it_response_received_at = datetime.now()
            task.it_response_type = "email_reply"
            task.it_responder_email = sender_email
            task.it_responder_name = sender_name
            task.it_response_message = f"{email_subject}\n\n{email_body}"
            
            db.commit()
            
            logger.info(
                f"Task {task.id} updated to {new_status} via email reply from "
                f"{sender_name} ({sender_email})"
            )
            
            # Log activity for IT email response
            try:
                from app.api.activities import log_activity
                candidate = task.checklist.candidate if task.checklist else None
                
                if candidate:
                    if intent == "complete":
                        action_text = f"completed IT equipment allocation for {candidate.name} via email."
                        icon = "check-circle"
                    elif intent == "need_time":
                        action_text = f"requested more time for IT setup for {candidate.name} via email."
                        icon = "clock"
                    else:
                        action_text = f"responded to IT setup request for {candidate.name} via email."
                        icon = "mail"
                    
                    log_activity(
                        db,
                        user_name=sender_name,
                        user_role="IT Team",
                        action_text=action_text,
                        target_object="IT Equipment",
                        activity_type="it_response",
                        icon_type=icon
                    )
                    logger.info(f"Activity logged for IT email response")
                    
                    # Send HR notification email
                    try:
                        from app.email.azure_email_service import AzureEmailService
                        from app.config import HR_EMAIL
                        
                        if HR_EMAIL and intent in ["complete", "need_time"]:
                            email_service = AzureEmailService()
                            
                            status_emoji = "✅" if intent == "complete" else "⏰"
                            status_text = "Completed" if intent == "complete" else "Needs More Time"
                            
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
            <h2>{status_emoji} IT Response Received (Email)</h2>
        </div>
        
        <p>Hi HR Team,</p>
        
        <p>The IT team has responded via email to the equipment allocation request.</p>
        
        <div class="info-box">
            <p><strong>Candidate:</strong> {candidate.name}</p>
            <p><strong>Email:</strong> {candidate.email}</p>
            <p><strong>Department:</strong> {candidate.department}</p>
            <p><strong>IT Status:</strong> {status_text}</p>
            <p><strong>Responded By:</strong> {sender_name}</p>
            <p><strong>Response Method:</strong> Email Reply</p>
            <p><strong>AI Confidence:</strong> {confidence:.0%}</p>
        </div>
        
        <div class="message-box">
            <p><strong>IT Team Message:</strong></p>
            <p>{email_body[:200]}{"..." if len(email_body) > 200 else ""}</p>
        </div>
        
        {"<p>✅ IT equipment has been allocated and is ready for the candidate's joining date.</p>" if intent == "complete" else "<p>⏰ IT team needs more time to complete the allocation.</p>"}
        
        <p>Best regards,<br><strong>OnboardIQ System</strong></p>
    </div>
</body>
</html>
"""
                            
                            hr_result = email_service._send_email(
                                to_email=HR_EMAIL,
                                subject=f"{status_emoji} IT Email Response: {candidate.name} - {status_text}",
                                html_content=hr_notification_html
                            )
                            
                            if hr_result.success:
                                logger.info(f"HR notification sent for IT email response")
                            else:
                                logger.warning(f"Failed to send HR notification: {hr_result.message}")
                    except Exception as e:
                        logger.error(f"Error sending HR notification: {e}")
                        
            except Exception as e:
                logger.error(f"Failed to log activity: {e}")
            
            return {
                "success": True,
                "task_id": task.id,
                "new_status": new_status,
                "intent": intent,
                "confidence": confidence,
                "reasoning": reasoning,
                "message": f"Task status updated to {new_status} based on email analysis"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing email reply: {e}")
            return {
                "success": False,
                "error": f"Internal server error: {str(e)}",
                "error_code": "SERVER_ERROR"
            }


# Singleton instance
email_reply_processor = EmailReplyProcessor()
