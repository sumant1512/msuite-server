"""
Agency schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid
from app.models.agency import SubscriptionStatus


class AgencyBase(BaseModel):
    """Base agency schema"""
    name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)


class AgencyCreate(AgencyBase):
    """Agency creation schema"""
    subscription_plan_id: uuid.UUID
    admin_email: EmailStr
    admin_name: str = Field(..., min_length=2, max_length=100)
    admin_password: str = Field(..., min_length=8)
    max_ecommerce: int = Field(default=3, gt=0)
    metadata_: Optional[dict] = Field(None, alias="metadata")


class AgencyUpdate(BaseModel):
    """Agency update schema"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    subscription_plan_id: Optional[uuid.UUID] = None
    subscription_status: Optional[SubscriptionStatus] = None
    max_ecommerce: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    metadata_: Optional[dict] = Field(None, alias="metadata")


class AgencyResponse(AgencyBase):
    """Agency response schema"""
    id: uuid.UUID
    subscription_plan_id: uuid.UUID
    subscription_status: SubscriptionStatus
    subscription_expires_at: Optional[datetime]
    max_ecommerce: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    ecommerce_count: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
