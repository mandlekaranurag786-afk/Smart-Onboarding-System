"""
Email module for OnboardIQ
Handles all email communications using Azure Communication Services
"""
from .azure_email_service import AzureEmailService
from .email_factory import email_service
from .email_schemas import (
    WelcomeEmailData,
    ITNotificationData,
    ManagerNotificationData,
    LaptopConfirmationData,
    HRAlertData,
    EmailResponse
)

__all__ = [
    "AzureEmailService",
    "email_service",
    "WelcomeEmailData",
    "ITNotificationData",
    "ManagerNotificationData",
    "LaptopConfirmationData",
    "HRAlertData",
    "EmailResponse"
]
