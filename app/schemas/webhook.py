"""
Webhook schemas for request/response validation
"""
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.models.webhook import WebhookEventType


class WebhookBase(BaseModel):
    """Base webhook schema"""
    url: str = Field(..., max_length=500)
    events: List[WebhookEventType]
    is_active: bool = True
    retry_count: int = Field(default=3, ge=0, le=10)


class WebhookCreate(WebhookBase):
    """Schema for creating a webhook"""
    pass


class WebhookUpdate(BaseModel):
    """Schema for updating a webhook"""
    url: Optional[str] = Field(None, max_length=500)
    events: Optional[List[WebhookEventType]] = None
    is_active: Optional[bool] = None
    retry_count: Optional[int] = Field(None, ge=0, le=10)


class WebhookResponse(WebhookBase):
    """Schema for webhook response"""
    id: UUID
    ecommerce_id: UUID
    secret: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WebhookDeliveryResponse(BaseModel):
    """Schema for webhook delivery response"""
    id: UUID
    webhook_id: UUID
    event_type: WebhookEventType
    payload: dict
    status: str
    http_status: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    attempt_count: int
    next_retry_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WebhookTest(BaseModel):
    """Schema for testing webhook"""
    event_type: WebhookEventType
    test_payload: dict = Field(default_factory=dict)
