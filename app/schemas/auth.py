"""
Authentication schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid
from app.enums.user_role import UserRole


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    """User registration request schema"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    agency_id: Optional[uuid.UUID] = None
    ecommerce_id: Optional[uuid.UUID] = None
    role: Optional[UserRole] = None


class TokenResponse(BaseModel):
    """JWT token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: "UserResponse"


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


class UserResponse(BaseModel):
    """User response schema"""
    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    agency_id: Optional[uuid.UUID] = None
    ecommerce_id: Optional[uuid.UUID] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PasswordChangeRequest(BaseModel):
    """Password change request schema"""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


# Update forward references
TokenResponse.model_rebuild()
