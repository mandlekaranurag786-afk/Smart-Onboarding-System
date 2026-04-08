"""
Email Service Factory
Provides unified interface using Azure Communication Services exclusively
"""
import logging
from typing import Optional
from app import config
from app.email.email_schemas import (
    WelcomeEmailData,
    ITNotificationData,
    ManagerNotificationData,
    LaptopConfirmationData,
    HRAlertData,
    EmailResponse
)

logger = logging.getLogger(__name__)


class UnifiedEmailService:
    """
    Unified email service using Azure Communication Services exclusively
    Designed for enterprise-grade email delivery with built-in retry logic
    """
    
    def __init__(self):
        """Initialize email service with Azure Communication Services"""
        # Import Azure service
        from app.email.azure_email_service import azure_email_service
        
        self.email_service = azure_email_service
        
        logger.info("Email service initialized with Azure Communication Services")
        
        # Expose common attributes
        self.hr_email = self.email_service.hr_email
        self.it_email = self.email_service.it_email
        self.frontend_url = self.email_service.frontend_url
        self.from_name = self.email_service.from_name
        self.sender_address = self.email_service.sender_address
    
    def send_welcome_email(self, data: WelcomeEmailData) -> EmailResponse:
        """Send welcome email to new candidate"""
        return self.email_service.send_welcome_email(data)
    
    def send_it_notification(
        self, 
        data: ITNotificationData, 
        additional_recipients: Optional[list[str]] = None
    ) -> EmailResponse:
        """Send notification to IT team"""
        return self.email_service.send_it_notification(data, additional_recipients)
    
    def send_manager_notification(
        self, 
        data: ManagerNotificationData,
        additional_recipients: Optional[list[str]] = None
    ) -> EmailResponse:
        """Send notification to reporting manager"""
        return self.email_service.send_manager_notification(data, additional_recipients)
    
    def send_laptop_confirmation(self, data: LaptopConfirmationData) -> EmailResponse:
        """Send laptop delivery confirmation request"""
        return self.email_service.send_laptop_confirmation(data)
    
    def send_hr_alert(self, data: HRAlertData) -> EmailResponse:
        """Send alert email to HR team"""
        return self.email_service.send_hr_alert(data)
    
    def send_bulk_welcome_emails(self, candidates_data: list[WelcomeEmailData]) -> list[EmailResponse]:
        """
        Send welcome emails to multiple candidates concurrently
        
        Args:
            candidates_data: List of welcome email data
            
        Returns:
            List of EmailResponse objects
        """
        return self.email_service.send_bulk_welcome_emails(candidates_data)


# Create singleton instance - this is what should be imported
email_service = UnifiedEmailService()
