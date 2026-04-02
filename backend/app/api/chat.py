"""
Chat/Messaging API endpoints
Handles chat conversations and AI assistant interactions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.base import BaseModel as SQLBaseModel

router = APIRouter()

# Database Models (inline for chat)
class Conversation(SQLBaseModel):
    """Chat conversation model"""
    __tablename__ = "conversations"
    
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    stakeholder_id = Column(Integer, ForeignKey("stakeholders.id"), nullable=True)
    title = Column(String(255), nullable=True)
    last_message_at = Column(DateTime, default=datetime.utcnow)

class Message(SQLBaseModel):
    """Chat message model"""
    __tablename__ = "messages"
    
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_type = Column(String(50), nullable=False)  # "candidate", "stakeholder", "ai"
    sender_id = Column(Integer, nullable=True)
    sender_name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Integer, default=0)  # 0 = unread, 1 = read

# Pydantic Schemas
class MessageCreate(BaseModel):
    content: str
    sender_type: str  # "candidate", "stakeholder", "ai"
    sender_id: Optional[int] = None
    sender_name: str

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_type: str
    sender_id: Optional[int]
    sender_name: str
    content: str
    is_read: bool
    created_at: str

class ConversationResponse(BaseModel):
    id: int
    candidate_id: int
    stakeholder_id: Optional[int]
    title: Optional[str]
    last_message_at: str
    unread_count: int

class AIMessageRequest(BaseModel):
    question: str
    candidate_id: Optional[int] = None
    context: Optional[dict] = None

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    user_id: int,
    user_type: str,  # "candidate" or "stakeholder"
    db: Session = Depends(get_db)
):
    """
    Get all chat conversations for a user
    """
    # Ensure tables exist
    from app.models.base import Base
    Base.metadata.create_all(bind=db.get_bind())
    
    if user_type == "candidate":
        conversations = db.query(Conversation).filter_by(candidate_id=user_id).all()
    elif user_type == "stakeholder":
        conversations = db.query(Conversation).filter_by(stakeholder_id=user_id).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_type"
        )
    
    result = []
    for conv in conversations:
        # Count unread messages
        unread_count = db.query(Message).filter(
            Message.conversation_id == conv.id,
            Message.is_read == 0,
            Message.sender_type != user_type
        ).count()
        
        result.append(ConversationResponse(
            id=conv.id,
            candidate_id=conv.candidate_id,
            stakeholder_id=conv.stakeholder_id,
            title=conv.title,
            last_message_at=conv.last_message_at.isoformat(),
            unread_count=unread_count
        ))
    
    return result

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get messages from a conversation
    """
    conversation = db.query(Conversation).filter_by(id=conversation_id).first()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = db.query(Message).filter_by(
        conversation_id=conversation_id
    ).order_by(Message.created_at.desc()).limit(limit).offset(offset).all()
    
    return [
        MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            sender_type=msg.sender_type,
            sender_id=msg.sender_id,
            sender_name=msg.sender_name,
            content=msg.content,
            is_read=bool(msg.is_read),
            created_at=msg.created_at.isoformat()
        )
        for msg in reversed(messages)
    ]

@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db)
):
    """
    Send a message in a conversation
    """
    conversation = db.query(Conversation).filter_by(id=conversation_id).first()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Create message
    message = Message(
        conversation_id=conversation_id,
        sender_type=message_data.sender_type,
        sender_id=message_data.sender_id,
        sender_name=message_data.sender_name,
        content=message_data.content,
        is_read=0
    )
    
    db.add(message)
    
    # Update conversation last message time
    conversation.last_message_at = datetime.utcnow()
    
    db.commit()
    db.refresh(message)
    
    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_type=message.sender_type,
        sender_id=message.sender_id,
        sender_name=message.sender_name,
        content=message.content,
        is_read=bool(message.is_read),
        created_at=message.created_at.isoformat()
    )

@router.post("/ai")
async def ai_chat(
    ai_request: AIMessageRequest,
    db: Session = Depends(get_db)
):
    """
    AI assistant chat endpoint (RAG-powered)
    Answers questions using the RAG system
    """
    try:
        from app.rag.rag_system import RAGSystem
        
        # Initialize RAG system
        rag = RAGSystem()
        
        # Get answer from RAG
        answer = rag.query(ai_request.question)
        
        # If candidate_id provided, log the interaction
        if ai_request.candidate_id:
            # Find or create AI conversation
            conversation = db.query(Conversation).filter_by(
                candidate_id=ai_request.candidate_id,
                stakeholder_id=None
            ).first()
            
            if not conversation:
                conversation = Conversation(
                    candidate_id=ai_request.candidate_id,
                    title="AI Assistant Chat"
                )
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
            
            # Save user question
            user_msg = Message(
                conversation_id=conversation.id,
                sender_type="candidate",
                sender_id=ai_request.candidate_id,
                sender_name="User",
                content=ai_request.question,
                is_read=1
            )
            db.add(user_msg)
            
            # Save AI response
            ai_msg = Message(
                conversation_id=conversation.id,
                sender_type="ai",
                sender_id=None,
                sender_name="AI Assistant",
                content=answer,
                is_read=0
            )
            db.add(ai_msg)
            
            conversation.last_message_at = datetime.utcnow()
            db.commit()
        
        return {
            "question": ai_request.question,
            "answer": answer,
            "source": "rag_system",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        # Fallback to simple response if RAG fails
        return {
            "question": ai_request.question,
            "answer": "I'm here to help with your onboarding questions. However, I'm currently unable to access the knowledge base. Please contact HR for assistance.",
            "source": "fallback",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.post("/conversations")
async def create_conversation(
    candidate_id: int,
    stakeholder_id: Optional[int] = None,
    title: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Create a new conversation
    """
    from app.models.candidate import Candidate
    
    # Validate candidate exists
    candidate = db.query(Candidate).filter_by(id=candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Create conversation
    conversation = Conversation(
        candidate_id=candidate_id,
        stakeholder_id=stakeholder_id,
        title=title or f"Chat with {candidate.name}"
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return {
        "id": conversation.id,
        "candidate_id": conversation.candidate_id,
        "stakeholder_id": conversation.stakeholder_id,
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat()
    }
