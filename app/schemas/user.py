"""
User schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid
from app.enums.user_role import UserRole


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole
    agency_id: Optional[uuid.UUID] = None
    ecommerce_id: Optional[uuid.UUID] = None


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: Optional[bool] = None
    agency_id: Optional[uuid.UUID] = None
    ecommerce_id: Optional[uuid.UUID] = None


class UserInDB(UserBase):
    """User schema with database fields"""
    id: uuid.UUID
    role: UserRole
    agency_id: Optional[uuid.UUID] = None
    ecommerce_id: Optional[uuid.UUID] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserInDB):
    """User response schema (public data only)"""
    pass
