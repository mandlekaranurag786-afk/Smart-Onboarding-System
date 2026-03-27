"""
Email Service using SendGrid
Handles all email sending operations
"""
import logging
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
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


class EmailService:
    """
    Email service for sending transactional emails via SendGrid
    """
    
    def __init__(self):
        """Initialize SendGrid client"""
        self.api_key = config.SENDGRID_API_KEY
        self.from_email = config.EMAIL_FROM_ADDRESS
        self.from_name = config.EMAIL_FROM_NAME
        self.hr_email = config.HR_EMAIL
        self.it_email = config.IT_EMAIL
        self.frontend_url = config.FRONTEND_URL
        
        if not self.api_key:
            logger.warning("SendGrid API key not configured!")
        
        self.client = SendGridAPIClient(self.api_key) if self.api_key else None
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        to_name: Optional[str] = None
    ) -> EmailResponse:
        """
        Internal method to send email via SendGrid
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML email content
            to_name: Recipient name (optional)
            
        Returns:
            EmailResponse with success status
        """
        if not self.client:
            logger.error("SendGrid client not initialized. Check API key.")
            return EmailResponse(
                success=False,
                message="Email service not configured"
            )
        
        try:
            # Create email message
            from_email_obj = Email(self.from_email, self.from_name)
            to_email_obj = To(to_email, to_name)
            content = Content("text/html", html_content)
            
            mail = Mail(
                from_email=from_email_obj,
                to_emails=to_email_obj,
                subject=subject,
                html_content=content
            )
            
            # Send email
            response = self.client.send(mail)
            
            logger.info(f"Email sent to {to_email}: {subject} (Status: {response.status_code})")
            
            return EmailResponse(
                success=True,
                message=f"Email sent successfully to {to_email}",
                email_id=response.headers.get('X-Message-Id')
            )
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return EmailResponse(
                success=False,
                message=f"Failed to send email: {str(e)}"
            )
    
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
    
    def send_it_notification(self, data: ITNotificationData) -> EmailResponse:
        """
        Send notification to IT team for new joiner setup
        
        Args:
            data: IT notification data
            
        Returns:
            EmailResponse
        """
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
        
        return self._send_email(
            to_email=self.it_email,
            subject=f"🖥️ New Joiner IT Setup Required - {data.candidate_name}",
            html_content=html_content,
            to_name="IT Team"
        )
    
    def send_manager_notification(self, data: ManagerNotificationData) -> EmailResponse:
        """
        Send notification to reporting manager about new team member
        
        Args:
            data: Manager notification data
            
        Returns:
            EmailResponse
        """
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
        
        return self._send_email(
            to_email=data.manager_email,
            subject=f"👋 New Team Member Joining - {data.candidate_name}",
            html_content=html_content,
            to_name=data.manager_name
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
        responses = []
        for data in candidates_data:
            response = self.send_welcome_email(data)
            responses.append(response)
        return responses


# Create singleton instance
email_service = EmailService()
