"""
Subscription plan schemas for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid
from app.models.subscription import SubscriptionInterval


class SubscriptionPlanBase(BaseModel):
    """Base subscription plan schema"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    interval: SubscriptionInterval = SubscriptionInterval.MONTHLY
    features: dict = Field(default_factory=dict)


class SubscriptionPlanCreate(SubscriptionPlanBase):
    """Subscription plan creation schema"""
    pass


class SubscriptionPlanUpdate(BaseModel):
    """Subscription plan update schema"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    interval: Optional[SubscriptionInterval] = None
    features: Optional[dict] = None
    is_active: Optional[bool] = None


class SubscriptionPlanResponse(SubscriptionPlanBase):
    """Subscription plan response schema"""
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
