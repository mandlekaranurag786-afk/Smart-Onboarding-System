"""
Settings & Configuration API endpoints
Manages system settings for email, SLA, RAG, and other configurations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Text, JSON
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import json

from app.database import get_db
from app.models.base import BaseModel as SQLBaseModel

router = APIRouter()

# Database Model
class SystemSetting(SQLBaseModel):
    """System settings model"""
    __tablename__ = "system_settings"
    
    setting_key = Column(String(255), unique=True, nullable=False, index=True)
    setting_value = Column(Text, nullable=False)
    setting_type = Column(String(50), nullable=False)  # "email", "sla", "rag", "general"
    description = Column(Text, nullable=True)

# Pydantic Schemas
class SettingResponse(BaseModel):
    id: int
    setting_key: str
    setting_value: Any
    setting_type: str
    description: Optional[str]

class SettingUpdate(BaseModel):
    setting_value: Any

class EmailSettings(BaseModel):
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None
    mailgun_api_key: Optional[str] = None
    mailgun_domain: Optional[str] = None

class SLASettings(BaseModel):
    task_completion_days: Optional[int] = 7
    meeting_scheduling_hours: Optional[int] = 48
    document_signing_days: Optional[int] = 3
    it_setup_days: Optional[int] = 2

class RAGSettings(BaseModel):
    documents_path: Optional[str] = "./documents"
    persist_dir: Optional[str] = "./chroma_db"
    chunk_size: Optional[int] = 1000
    chunk_overlap: Optional[int] = 200
    top_k: Optional[int] = 5

def get_setting_value(db: Session, key: str, default: Any = None):
    """Helper to get setting value"""
    setting = db.query(SystemSetting).filter_by(setting_key=key).first()
    if not setting:
        return default
    
    try:
        return json.loads(setting.setting_value)
    except:
        return setting.setting_value

def set_setting_value(db: Session, key: str, value: Any, setting_type: str, description: str = None):
    """Helper to set setting value"""
    setting = db.query(SystemSetting).filter_by(setting_key=key).first()
    
    value_str = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
    
    if setting:
        setting.setting_value = value_str
        setting.updated_at = db.func.now()
    else:
        setting = SystemSetting(
            setting_key=key,
            setting_value=value_str,
            setting_type=setting_type,
            description=description
        )
        db.add(setting)
    
    db.commit()
    return setting

@router.get("/")
async def get_all_settings(
    setting_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all system settings or filter by type
    """
    # Ensure table exists
    from app.models.base import Base
    Base.metadata.create_all(bind=db.get_bind())
    
    query = db.query(SystemSetting)
    
    if setting_type:
        query = query.filter(SystemSetting.setting_type == setting_type)
    
    settings = query.all()
    
    result = {}
    for setting in settings:
        try:
            value = json.loads(setting.setting_value)
        except:
            value = setting.setting_value
        
        result[setting.setting_key] = {
            "value": value,
            "type": setting.setting_type,
            "description": setting.description
        }
    
    return result

@router.get("/{setting_key}")
async def get_setting(
    setting_key: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific setting by key
    """
    setting = db.query(SystemSetting).filter_by(setting_key=setting_key).first()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{setting_key}' not found"
        )
    
    try:
        value = json.loads(setting.setting_value)
    except:
        value = setting.setting_value
    
    return {
        "setting_key": setting.setting_key,
        "value": value,
        "type": setting.setting_type,
        "description": setting.description
    }

@router.patch("/")
async def update_settings(
    settings: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Update multiple settings at once
    """
    updated = []
    
    for key, value in settings.items():
        # Determine setting type from key prefix
        if key.startswith("email_"):
            setting_type = "email"
        elif key.startswith("sla_"):
            setting_type = "sla"
        elif key.startswith("rag_"):
            setting_type = "rag"
        else:
            setting_type = "general"
        
        setting = set_setting_value(db, key, value, setting_type)
        updated.append(key)
    
    return {
        "message": "Settings updated successfully",
        "updated_keys": updated
    }

@router.patch("/{setting_key}")
async def update_setting(
    setting_key: str,
    update_data: SettingUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a specific setting
    """
    setting = db.query(SystemSetting).filter_by(setting_key=setting_key).first()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{setting_key}' not found"
        )
    
    value_str = json.dumps(update_data.setting_value) if isinstance(update_data.setting_value, (dict, list)) else str(update_data.setting_value)
    setting.setting_value = value_str
    
    db.commit()
    db.refresh(setting)
    
    return {
        "setting_key": setting.setting_key,
        "value": update_data.setting_value,
        "message": "Setting updated successfully"
    }

@router.get("/email/config")
async def get_email_settings(db: Session = Depends(get_db)):
    """
    Get email configuration settings
    """
    return {
        "smtp_host": get_setting_value(db, "email_smtp_host", "smtp.mailgun.org"),
        "smtp_port": get_setting_value(db, "email_smtp_port", 587),
        "from_email": get_setting_value(db, "email_from_email", "noreply@onboardiq.com"),
        "from_name": get_setting_value(db, "email_from_name", "OnboardIQ"),
        "mailgun_domain": get_setting_value(db, "email_mailgun_domain", "")
    }

@router.patch("/email/config")
async def update_email_settings(
    email_settings: EmailSettings,
    db: Session = Depends(get_db)
):
    """
    Update email configuration
    """
    if email_settings.smtp_host:
        set_setting_value(db, "email_smtp_host", email_settings.smtp_host, "email", "SMTP host")
    if email_settings.smtp_port:
        set_setting_value(db, "email_smtp_port", email_settings.smtp_port, "email", "SMTP port")
    if email_settings.from_email:
        set_setting_value(db, "email_from_email", email_settings.from_email, "email", "From email address")
    if email_settings.from_name:
        set_setting_value(db, "email_from_name", email_settings.from_name, "email", "From name")
    if email_settings.mailgun_api_key:
        set_setting_value(db, "email_mailgun_api_key", email_settings.mailgun_api_key, "email", "Mailgun API key")
    if email_settings.mailgun_domain:
        set_setting_value(db, "email_mailgun_domain", email_settings.mailgun_domain, "email", "Mailgun domain")
    
    return {"message": "Email settings updated successfully"}

@router.get("/sla/config")
async def get_sla_settings(db: Session = Depends(get_db)):
    """
    Get SLA configuration
    """
    return {
        "task_completion_days": get_setting_value(db, "sla_task_completion_days", 7),
        "meeting_scheduling_hours": get_setting_value(db, "sla_meeting_scheduling_hours", 48),
        "document_signing_days": get_setting_value(db, "sla_document_signing_days", 3),
        "it_setup_days": get_setting_value(db, "sla_it_setup_days", 2)
    }

@router.patch("/sla/config")
async def update_sla_settings(
    sla_settings: SLASettings,
    db: Session = Depends(get_db)
):
    """
    Update SLA configuration
    """
    if sla_settings.task_completion_days:
        set_setting_value(db, "sla_task_completion_days", sla_settings.task_completion_days, "sla")
    if sla_settings.meeting_scheduling_hours:
        set_setting_value(db, "sla_meeting_scheduling_hours", sla_settings.meeting_scheduling_hours, "sla")
    if sla_settings.document_signing_days:
        set_setting_value(db, "sla_document_signing_days", sla_settings.document_signing_days, "sla")
    if sla_settings.it_setup_days:
        set_setting_value(db, "sla_it_setup_days", sla_settings.it_setup_days, "sla")
    
    return {"message": "SLA settings updated successfully"}

@router.get("/rag/config")
async def get_rag_settings(db: Session = Depends(get_db)):
    """
    Get RAG system configuration
    """
    return {
        "documents_path": get_setting_value(db, "rag_documents_path", "./documents"),
        "persist_dir": get_setting_value(db, "rag_persist_dir", "./chroma_db"),
        "chunk_size": get_setting_value(db, "rag_chunk_size", 1000),
        "chunk_overlap": get_setting_value(db, "rag_chunk_overlap", 200),
        "top_k": get_setting_value(db, "rag_top_k", 5)
    }

@router.patch("/rag/config")
async def update_rag_settings(
    rag_settings: RAGSettings,
    db: Session = Depends(get_db)
):
    """
    Update RAG system configuration
    """
    if rag_settings.documents_path:
        set_setting_value(db, "rag_documents_path", rag_settings.documents_path, "rag")
    if rag_settings.persist_dir:
        set_setting_value(db, "rag_persist_dir", rag_settings.persist_dir, "rag")
    if rag_settings.chunk_size:
        set_setting_value(db, "rag_chunk_size", rag_settings.chunk_size, "rag")
    if rag_settings.chunk_overlap:
        set_setting_value(db, "rag_chunk_overlap", rag_settings.chunk_overlap, "rag")
    if rag_settings.top_k:
        set_setting_value(db, "rag_top_k", rag_settings.top_k, "rag")
    
    return {"message": "RAG settings updated successfully"}
