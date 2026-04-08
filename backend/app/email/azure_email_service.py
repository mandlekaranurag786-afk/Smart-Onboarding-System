"""
Azure Communication Services Email Implementation
Handles all email sending operations via Azure with retry logic
"""
import asyncio
import logging
import time
from typing import Callable, Optional, TypeVar
from azure.communication.email import EmailClient
from azure.core.exceptions import AzureError, HttpResponseError
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


class AzureEmailService:
    """
    Email service for sending transactional emails via Azure Communication Services
    """
    
    def __init__(self):
        """Initialize Azure Communication Services Email client"""
        self.connection_string = config.AZURE_COMMUNICATION_CONNECTION_STRING
        self.sender_address = config.AZURE_COMMUNICATION_SENDER_ADDRESS
        self.from_name = config.EMAIL_FROM_NAME
        self.hr_email = config.HR_EMAIL
        self.it_email = config.IT_EMAIL
        self.frontend_url = config.FRONTEND_URL
        
        # Initialize Azure Email Client
        self.client = None
        if self.connection_string and self.sender_address:
            try:
                self.client = EmailClient.from_connection_string(self.connection_string)
                logger.info("Azure Communication Services Email client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Azure Email client: {str(e)}")
                self.client = None
        else:
            logger.warning("Azure Communication Services connection string or sender address not configured!")
    
    def _send_email(
        self,
        to_email: str | list[str],
        subject: str,
        html_content: str,
        to_name: Optional[str] = None,
        max_retries: int = 3
    ) -> EmailResponse:
        """
        Internal method to send email via Azure Communication Services with retry logic
        
        Args:
            to_email: Recipient email (single string or list of emails)
            subject: Email subject
            html_content: HTML email content
            to_name: Recipient name (optional, only used for single recipient)
            max_retries: Maximum number of retry attempts for rate limiting
            
        Returns:
            EmailResponse with success status
        """
        if not self.client:
            logger.error("Azure Email client not initialized. Check connection string and sender address.")
            return EmailResponse(
                success=False,
                message="Email service not configured"
            )
        
        # Prepare recipient(s)
        if isinstance(to_email, list):
            recipients = [{"address": email} for email in to_email]
            recipient_display = ", ".join(to_email)
        else:
            recipients = [{"address": to_email}]
            if to_name:
                recipients[0]["displayName"] = to_name
            recipient_display = to_email
        
        # Prepare email message
        message = {
            "senderAddress": self.sender_address,
            "recipients": {
                "to": recipients
            },
            "content": {
                "subject": subject,
                "html": html_content
            }
        }
        
        # Retry logic for rate limiting
        for attempt in range(max_retries):
            try:
                # Send email via Azure Communication Services
                logger.info(f"Sending email to {recipient_display}: {subject} (attempt {attempt + 1}/{max_retries})")
                
                poller = self.client.begin_send(message)
                result = poller.result()
                
                # Azure SDK returns a dict with 'status' and 'id' keys
                if isinstance(result, dict):
                    status = result.get('status', 'Unknown')
                    message_id = result.get('id', result.get('messageId', None))
                else:
                    # If it's an object, try to get attributes
                    status = getattr(result, 'status', 'Unknown')
                    message_id = getattr(result, 'message_id', getattr(result, 'id', None))
                
                # Check result status
                if status == "Succeeded" or status == "Queued":
                    logger.info(f"Email sent successfully to {recipient_display} (ID: {message_id})")
                    
                    return EmailResponse(
                        success=True,
                        message=f"Email sent successfully to {recipient_display}",
                        email_id=message_id
                    )
                else:
                    error_msg = f"Email status: {status}"
                    logger.error(f"Failed to send email to {recipient_display}: {error_msg}")
                    return EmailResponse(
                        success=False,
                        message=f"Failed to send email: {error_msg}"
                    )
                
            except HttpResponseError as e:
                # Handle rate limiting with exponential backoff
                if e.status_code == 429:  # Too Many Requests
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + 1  # Exponential backoff: 2, 5, 9 seconds
                        logger.warning(f"Rate limit hit for {recipient_display}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Rate limit exceeded for {recipient_display} after {max_retries} attempts")
                        return EmailResponse(
                            success=False,
                            message=f"Rate limit exceeded. Please try again later."
                        )
                else:
                    logger.error(f"Azure HTTP error sending email to {recipient_display}: {str(e)}")
                    return EmailResponse(
                        success=False,
                        message=f"Azure error: {str(e)}"
                    )
                    
            except AzureError as e:
                logger.error(f"Azure error sending email to {recipient_display}: {str(e)}")
                return EmailResponse(
                    success=False,
                    message=f"Azure error: {str(e)}"
                )
            except Exception as e:
                logger.error(f"Failed to send email to {recipient_display}: {str(e)}")
                return EmailResponse(
                    success=False,
                    message=f"Failed to send email: {str(e)}"
                )
        
        # Should not reach here, but just in case
        return EmailResponse(
            success=False,
            message="Failed to send email after multiple attempts"
        )

    async def _run_concurrent_tasks(self, tasks: list[Callable[[], T]]) -> list[T]:
        """
        Execute synchronous email tasks concurrently
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
            additional_recipients: Optional list of additional email addresses
            
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
    
    def send_manager_notification(
        self, 
        data: ManagerNotificationData,
        additional_recipients: Optional[list[str]] = None
    ) -> EmailResponse:
        """
        Send notification to reporting manager about new team member
        
        Args:
            data: Manager notification data
            additional_recipients: Optional list of additional email addresses
            
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
        Send welcome emails to multiple candidates concurrently
        
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

        logger.info(f"Sending {len(candidates_data)} welcome emails concurrently via Azure")
        return asyncio.run(_send_all())


# Create singleton instance
azure_email_service = AzureEmailService()
