"""
Email Reply Processor Service
Handles incoming email replies from IT team and updates task status using NLP
"""
import re
import logging
from typing import Dict, Optional, Tuple
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
    def sanitize_email_content(email_body: str) -> str:
        """Remove quoted thread noise and HTML so the classifier sees the fresh reply."""
        if not email_body:
            return ""

        text = re.sub(r"<[^>]+>", " ", email_body)
        text = re.sub(r"\r\n?", "\n", text)

        split_markers = [
            r"\nOn .+ wrote:",
            r"\nFrom:",
            r"\n-----Original Message-----",
            r"\n________________________________",
        ]

        for marker in split_markers:
            parts = re.split(marker, text, maxsplit=1, flags=re.IGNORECASE)
            if parts:
                text = parts[0]

        cleaned_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                cleaned_lines.append("")
                continue
            if stripped.startswith(">"):
                continue
            cleaned_lines.append(stripped)

        cleaned = "\n".join(cleaned_lines)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

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
            cleaned_email_body = EmailReplyProcessor.sanitize_email_content(email_body)

            task_token = EmailReplyProcessor.extract_task_token_from_email(
                cleaned_email_body or email_body, email_subject
            )
            
            task = None
            if task_token:
                # Find task by token
                task = ITTaskService.validate_token(task_token, db)
            
            # Step 3: If no token found, try to find task by candidate email mentioned in email
            if not task:
                # Extract email addresses from email body
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                candidate_emails = re.findall(email_pattern, f"{cleaned_email_body}\n{email_subject}")
                
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
                cleaned_email_body or email_body, email_subject
            )
            
            logger.info(
                f"Email analysis for task {task.id}: "
                f"intent={intent}, confidence={confidence:.2f}"
            )
            
            normalized_response = intent if confidence >= 0.5 else "unclear"
            if normalized_response == "unclear":
                logger.warning(
                    f"Unclear intent for task {task.id} (confidence={confidence:.2f}). Marking as in_progress."
                )

            result = ITTaskService.apply_it_response(
                task=task,
                response=normalized_response,
                responder_email=sender_email,
                responder_name=sender_name,
                message=f"{email_subject}\n\n{cleaned_email_body or email_body}",
                response_type="email_reply",
                db=db,
                confidence=confidence,
            )

            if result.get("success"):
                result["intent"] = intent
                result["confidence"] = confidence
                result["reasoning"] = reasoning
                result["message"] = (
                    f"Task status updated to {result.get('new_status')} based on email analysis"
                )

            return result
            
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
