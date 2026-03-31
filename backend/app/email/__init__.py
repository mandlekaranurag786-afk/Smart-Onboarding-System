"""
Email module for OnboardIQ
Handles all email communications using SendGrid
"""
from .email_service import EmailService
from .email_schemas import (
    WelcomeEmailData,
    ITNotificationData,
    ManagerNotificationData,
    LaptopConfirmationData,
    HRAlertData
)

__all__ = [
    "EmailService",
    "WelcomeEmailData",
    "ITNotificationData",
    "ManagerNotificationData",
    "LaptopConfirmationData",
    "HRAlertData"
]
