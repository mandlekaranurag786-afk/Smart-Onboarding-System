"""
Authentication API endpoints
Handles user login, logout, and session management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt
import os

from app.database import get_db
from app.models.candidate import Candidate, CandidateAccountStatus
from app.models.stakeholder import Stakeholder
from app.security import hash_password, verify_password

router = APIRouter()
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Pydantic Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: Optional[str] = None  # For demo, password optional
    user_type: str  # "hr", "candidate", "stakeholder"

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    user_type: str
    role: Optional[str] = None
    department: Optional[str] = None
    account_status: Optional[str] = None
    password_reset_required: Optional[bool] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id = payload.get("user_id")
    user_type = payload.get("user_type")
    
    if not user_id or not user_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Fetch user based on type
    if user_type == "candidate":
        user = db.query(Candidate).filter_by(id=user_id).first()
    else:
        user = db.query(Stakeholder).filter_by(id=user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return {"user": user, "user_type": user_type}

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    User login endpoint
    Supports HR, Candidates, and other Stakeholders
    """
    user = None
    user_type = login_data.user_type.lower()
    
    # Find user based on type
    if user_type == "candidate":
        user = db.query(Candidate).filter_by(email=login_data.email).first()
    elif user_type in ["hr", "stakeholder", "it", "admin"]:
        user = db.query(Stakeholder).filter_by(email=login_data.email).first()
        user_type = "stakeholder"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user type. Must be 'candidate', 'hr', or 'stakeholder'"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user_type == "candidate":
        if user.account_status == CandidateAccountStatus.DISABLED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Candidate account is disabled"
            )

        if not login_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required for candidate login"
            )

        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if user.account_status == CandidateAccountStatus.INVITED:
            user.account_status = CandidateAccountStatus.ACTIVE
            db.commit()
    
    # Create access token
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "user_type": user_type
    }
    access_token = create_access_token(token_data)
    
    # Prepare user response
    user_response = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "user_type": user_type,
        "role": getattr(user, "role", None),
        "department": getattr(user, "department", None),
        "account_status": getattr(getattr(user, "account_status", None), "value", None),
        "password_reset_required": bool(getattr(user, "password_reset_required", 0)) if user_type == "candidate" else None
    }
    
    return LoginResponse(
        access_token=access_token,
        user=user_response
    )

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    User logout endpoint
    Note: JWT tokens are stateless, so logout is handled client-side
    """
    return {
        "message": "Logged out successfully",
        "detail": "Please remove the token from client storage"
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information
    """
    user = current_user["user"]
    user_type = current_user["user_type"]
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        user_type=user_type,
        role=getattr(user, "role", None),
        department=getattr(user, "department", None),
        account_status=getattr(getattr(user, "account_status", None), "value", None),
        password_reset_required=bool(getattr(user, "password_reset_required", 0)) if user_type == "candidate" else None
    )


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Allow a candidate to replace their temporary password.
    """
    user = current_user["user"]
    user_type = current_user["user_type"]

    if user_type != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can change password through this endpoint"
        )

    if not verify_password(password_data.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )

    user.password_hash = hash_password(password_data.new_password)
    user.password_reset_required = 0
    user.account_status = CandidateAccountStatus.ACTIVE
    db.commit()

    return {
        "success": True,
        "message": "Password updated successfully"
    }
