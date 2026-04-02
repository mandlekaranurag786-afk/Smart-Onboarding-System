"""
Email Service using Mailgun
Handles all email sending operations
"""
import asyncio
import logging
import requests
from typing import Callable, Optional, TypeVar
from app import config
from app.email.email_templates import (
    render_email,
    WELCOME_EMAIL_TEMPLATE,
    IT_NOTIFICATION_TEMPLATE,
    MANAGER_NOTIFICATION_TEMPLATE,
    LAPTOP_CONFIRMATION_TEMPLATE,
    HR_ALERT_TEMPLATE
)
from app.email.email_schemas import (
    WelcomeEmailData,
    ITNotificationData,
    ManagerNotificationData,
    LaptopConfirmationData,
    HRAlertData,
    EmailResponse
)

logger = logging.getLogger(__name__)
T = TypeVar("T")


class EmailService:
    """
    Email service for sending transactional emails via Mailgun
    """
    
    def __init__(self):
        """Initialize Mailgun client"""
        self.api_key = config.MAILGUN_API_KEY
        self.domain = config.MAILGUN_DOMAIN
        self.from_email = config.EMAIL_FROM_ADDRESS
        self.from_name = config.EMAIL_FROM_NAME
        self.hr_email = config.HR_EMAIL
        self.it_email = config.IT_EMAIL
        self.frontend_url = config.FRONTEND_URL
        
        # Mailgun API endpoint
        self.api_url = f"https://api.mailgun.net/v3/{self.domain}/messages"
        
        if not self.api_key or not self.domain:
            logger.warning("Mailgun API key or domain not configured!")
        
        self.client = bool(self.api_key and self.domain)
    
    def _send_email(
        self,
        to_email: str | list[str],
        subject: str,
        html_content: str,
        to_name: Optional[str] = None
    ) -> EmailResponse:
        """
        Internal method to send email via Mailgun
        
        Args:
            to_email: Recipient email (single string or list of emails)
            subject: Email subject
            html_content: HTML email content
            to_name: Recipient name (optional, only used for single recipient)
            
        Returns:
            EmailResponse with success status
        """
        if not self.client:
            logger.error("Mailgun client not initialized. Check API key and domain.")
            return EmailResponse(
                success=False,
                message="Email service not configured"
            )
        
        try:
            # Prepare recipient(s)
            if isinstance(to_email, list):
                # Multiple recipients - send as list
                recipients = to_email
                recipient_display = ", ".join(to_email)
            else:
                # Single recipient
                recipients = f"{to_name} <{to_email}>" if to_name else to_email
                recipient_display = to_email
            
            sender = f"{self.from_name} <{self.from_email}>"
            
            # Send email via Mailgun API
            response = requests.post(
                self.api_url,
                auth=("api", self.api_key),
                data={
                    "from": sender,
                    "to": recipients,
                    "subject": subject,
                    "html": html_content
                },
                timeout=10
            )
            
            # Check response
            if response.status_code == 200:
                response_data = response.json()
                email_id = response_data.get("id", "")
                
                logger.info(f"Email sent to {recipient_display}: {subject} (ID: {email_id})")
                
                return EmailResponse(
                    success=True,
                    message=f"Email sent successfully to {recipient_display}",
                    email_id=email_id
                )
            else:
                error_msg = response.text
                logger.error(f"Failed to send email to {recipient_display}: {error_msg}")
                return EmailResponse(
                    success=False,
                    message=f"Failed to send email: {error_msg}"
                )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error sending email to {recipient_display}: {str(e)}")
            return EmailResponse(
                success=False,
                message=f"Network error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_display}: {str(e)}")
            return EmailResponse(
                success=False,
                message=f"Failed to send email: {str(e)}"
            )

    async def _run_concurrent_tasks(self, tasks: list[Callable[[], T]]) -> list[T]:
        """
        Execute synchronous email tasks concurrently without changing the
        requests-based Mailgun integration.
        """
        return await asyncio.gather(*(asyncio.to_thread(task) for task in tasks))
    
    def send_welcome_email(self, data: WelcomeEmailData) -> EmailResponse:
        """
        Send welcome email to new candidate
        
        Args:
            data: Welcome email data
            
        Returns:
            EmailResponse
        """
        logger.info(f"Sending welcome email to {data.candidate_name} ({data.candidate_email})")
        
        template_data = {
            "candidate_name": data.candidate_name,
            "role": data.role,
            "department": data.department,
            "joining_date": data.joining_date.strftime("%B %d, %Y"),
            "reporting_manager": data.reporting_manager,
            "login_email": data.login_email,
            "login_password": data.login_password,
            "tasks": data.tasks,
            "portal_url": self.frontend_url
        }
        
        html_content = render_email(
            WELCOME_EMAIL_TEMPLATE,
            template_data,
            self.hr_email
        )
        
        return self._send_email(
            to_email=data.candidate_email,
            subject=f"Welcome to {data.department} - Your Onboarding Journey Begins! 🎉",
            html_content=html_content,
            to_name=data.candidate_name
        )
    
    def send_it_notification(
        self, 
        data: ITNotificationData, 
        additional_recipients: Optional[list[str]] = None
    ) -> EmailResponse:
        """
        Send notification to IT team for new joiner setup
        
        Args:
            data: IT notification data
            additional_recipients: Optional list of additional email addresses (e.g., manager emails)
            
        Returns:
            EmailResponse
        """
        # Build recipient list
        recipients = [self.it_email]
        
        if additional_recipients:
            recipients.extend(additional_recipients)
            logger.info(f"Sending IT notification for {data.candidate_name} to {len(recipients)} recipients")
        else:
            logger.info(f"Sending IT notification for {data.candidate_name}")
        
        template_data = {
            "candidate_name": data.candidate_name,
            "candidate_email": data.candidate_email,
            "role": data.role,
            "department": data.department,
            "joining_date": data.joining_date.strftime("%B %d, %Y"),
            "reporting_manager": data.reporting_manager
        }
        
        html_content = render_email(
            IT_NOTIFICATION_TEMPLATE,
            template_data,
            self.hr_email
        )
        
        # Send to single recipient or multiple
        to_email = recipients if len(recipients) > 1 else self.it_email
        
        return self._send_email(
            to_email=to_email,
            subject=f"🖥️ New Joiner IT Setup Required - {data.candidate_name}",
            html_content=html_content,
            to_name="IT Team" if len(recipients) == 1 else None
        )
        # Prepare recipients list
        recipients = [self.it_email]
        if additional_recipients:
            recipients.extend(additional_recipients)
        
        # Send to single or multiple recipients
        to_email = recipients if len(recipients) > 1 else self.it_email
        
        return self._send_email(
            to_email=to_email,
            subject=f"🖥️ New Joiner IT Setup Required - {data.candidate_name}",
            html_content=html_content,
            to_name="IT Team" if len(recipients) == 1 else None
        )
    
    def send_manager_notification(
        self, 
        data: ManagerNotificationData,
        additional_recipients: Optional[list[str]] = None
    ) -> EmailResponse:
        """
        Send notification to reporting manager about new team member
        
        Args:
            data: Manager notification data
            additional_recipients: Optional list of additional email addresses (e.g., IT team, HR)
            
        Returns:
            EmailResponse
        """
        # Build recipient list
        recipients = [data.manager_email]
        
        if additional_recipients:
            recipients.extend(additional_recipients)
            logger.info(f"Sending manager notification to {data.manager_name} and {len(additional_recipients)} others")
        else:
            logger.info(f"Sending manager notification to {data.manager_name}")
        
        template_data = {
            "manager_name": data.manager_name,
            "candidate_name": data.candidate_name,
            "candidate_email": data.candidate_email,
            "role": data.role,
            "department": data.department,
            "joining_date": data.joining_date.strftime("%B %d, %Y")
        }
        
        html_content = render_email(
            MANAGER_NOTIFICATION_TEMPLATE,
            template_data,
            self.hr_email
        )
        
        # Send to single recipient or multiple
        to_email = recipients if len(recipients) > 1 else data.manager_email
        
        return self._send_email(
            to_email=to_email,
            subject=f"👋 New Team Member Joining - {data.candidate_name}",
            html_content=html_content,
            to_name=data.manager_name if len(recipients) == 1 else None
        )
    
    def send_laptop_confirmation(self, data: LaptopConfirmationData) -> EmailResponse:
        """
        Send laptop delivery confirmation request to candidate
        
        Args:
            data: Laptop confirmation data
            
        Returns:
            EmailResponse
        """
        logger.info(f"Sending laptop confirmation to {data.candidate_name}")
        
        template_data = {
            "candidate_name": data.candidate_name,
            "confirmation_link_yes": data.confirmation_link_yes,
            "confirmation_link_no": data.confirmation_link_no
        }
        
        html_content = render_email(
            LAPTOP_CONFIRMATION_TEMPLATE,
            template_data,
            self.hr_email
        )
        
        return self._send_email(
            to_email=data.candidate_email,
            subject="💻 Laptop Delivery Confirmation Required",
            html_content=html_content,
            to_name=data.candidate_name
        )
    
    def send_hr_alert(self, data: HRAlertData) -> EmailResponse:
        """
        Send alert email to HR team
        
        Args:
            data: HR alert data
            
        Returns:
            EmailResponse
        """
        logger.info(f"Sending HR alert: {data.alert_type}")
        
        template_data = {
            "alert_type": data.alert_type.replace("_", " ").title(),
            "candidate_name": data.candidate_name,
            "candidate_email": data.candidate_email,
            "message": data.message,
            "additional_info": data.additional_info
        }
        
        html_content = render_email(
            HR_ALERT_TEMPLATE,
            template_data,
            self.hr_email
        )
        
        return self._send_email(
            to_email=self.hr_email,
            subject=f"🔔 OnboardIQ Alert - {data.alert_type.replace('_', ' ').title()}",
            html_content=html_content,
            to_name="HR Team"
        )
    
    def send_bulk_welcome_emails(self, candidates_data: list[WelcomeEmailData]) -> list[EmailResponse]:
        """
        Send welcome emails to multiple candidates
        
        Args:
            candidates_data: List of welcome email data
            
        Returns:
            List of EmailResponse objects
        """
        if not candidates_data:
            return []

        async def _send_all() -> list[EmailResponse]:
            return await self._run_concurrent_tasks(
                [lambda data=data: self.send_welcome_email(data) for data in candidates_data]
            )

        logger.info(f"Sending {len(candidates_data)} welcome emails concurrently")
        return asyncio.run(_send_all())


# Create singleton instance
email_service = EmailService()
