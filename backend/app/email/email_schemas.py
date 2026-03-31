"""
Pydantic schemas for email data
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date


class WelcomeEmailData(BaseModel):
    """Data for welcome email to new candidate"""
    candidate_name: str
    candidate_email: EmailStr
    role: str
    department: str
    joining_date: date
    reporting_manager: str
    login_email: EmailStr
    login_password: str
    tasks: List[str]


class ITNotificationData(BaseModel):
    """Data for IT team notification"""
    candidate_name: str
    candidate_email: EmailStr
    role: str
    department: str
    joining_date: date
    reporting_manager: str


class ManagerNotificationData(BaseModel):
    """Data for reporting manager notification"""
    manager_name: str
    manager_email: EmailStr
    candidate_name: str
    candidate_email: EmailStr
    role: str
    department: str
    joining_date: date


class LaptopConfirmationData(BaseModel):
    """Data for laptop confirmation request"""
    candidate_name: str
    candidate_email: EmailStr
    candidate_id: int
    confirmation_link_yes: str
    confirmation_link_no: str


class HRAlertData(BaseModel):
    """Data for HR alert emails"""
    candidate_name: str
    candidate_email: EmailStr
    alert_type: str  # "laptop_received", "laptop_not_received", "sla_breach"
    message: str
    additional_info: Optional[dict] = None


class EmailResponse(BaseModel):
    """Response model for email operations"""
    success: bool
    message: str
    email_id: Optional[str] = None
