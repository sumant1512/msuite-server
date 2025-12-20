"""
E-commerce schemas for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid


class EcommerceBase(BaseModel):
    """Base e-commerce schema"""
    name: str = Field(..., min_length=2, max_length=200)
    domain: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None


class EcommerceCreate(EcommerceBase):
    """E-commerce creation schema"""
    admin_email: str = Field(..., min_length=3)
    admin_name: str = Field(..., min_length=2, max_length=100)
    admin_password: str = Field(..., min_length=8)
    settings: Optional[dict] = Field(default_factory=lambda: {
        "currency": "USD",
        "timezone": "UTC",
        "language": "en",
        "tax_rate": 0.0
    })


class EcommerceUpdate(BaseModel):
    """E-commerce update schema"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    domain: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    settings: Optional[dict] = None
    is_active: Optional[bool] = None


class EcommerceResponse(EcommerceBase):
    """E-commerce response schema"""
    id: uuid.UUID
    agency_id: uuid.UUID
    api_key: str
    settings: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class EcommerceStats(BaseModel):
    """E-commerce statistics schema"""
    total_products: int = 0
    total_orders: int = 0
    total_customers: int = 0
    total_revenue: float = 0.0
