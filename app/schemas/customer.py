"""
Customer schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid


class CustomerBase(BaseModel):
    """Base customer schema"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    addresses: Optional[dict] = None
    metadata_: Optional[dict] = Field(None, alias="metadata")


class CustomerCreate(CustomerBase):
    """Customer creation schema"""
    pass


class CustomerUpdate(BaseModel):
    """Customer update schema"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    addresses: Optional[dict] = None
    metadata_: Optional[dict] = Field(None, alias="metadata")


class CustomerStats(BaseModel):
    """Customer statistics schema"""
    total_orders: int
    total_spent: float
    average_order_value: float
    last_order_date: Optional[datetime] = None


class CustomerResponse(CustomerBase):
    """Customer response schema"""
    id: uuid.UUID
    ecommerce_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    total_orders: Optional[int] = None
    total_spent: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
