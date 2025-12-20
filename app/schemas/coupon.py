"""
Coupon schemas for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.coupon import DiscountType


class CouponBase(BaseModel):
    """Base coupon schema"""
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    discount_type: DiscountType
    discount_value: float = Field(..., gt=0)
    usage_limit: Optional[int] = Field(None, ge=1)
    usage_limit_per_customer: Optional[int] = Field(None, ge=1)
    minimum_purchase_amount: Optional[float] = Field(None, ge=0)
    valid_from: datetime
    valid_until: Optional[datetime] = None
    is_active: bool = True


class CouponCreate(CouponBase):
    """Schema for creating a coupon"""
    pass


class CouponUpdate(BaseModel):
    """Schema for updating a coupon"""
    description: Optional[str] = Field(None, max_length=500)
    discount_value: Optional[float] = Field(None, gt=0)
    usage_limit: Optional[int] = Field(None, ge=1)
    usage_limit_per_customer: Optional[int] = Field(None, ge=1)
    minimum_purchase_amount: Optional[float] = Field(None, ge=0)
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None


class CouponResponse(CouponBase):
    """Schema for coupon response"""
    id: UUID
    ecommerce_id: UUID
    usage_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CouponValidation(BaseModel):
    """Schema for validating a coupon"""
    is_valid: bool
    discount_amount: Optional[float] = None
    message: Optional[str] = None
