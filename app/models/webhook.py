"""
Webhook and notification models
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Text, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from typing import List, Optional
import uuid
from datetime import datetime
import enum

from app.core.database import Base


class WebhookEventType(str, enum.Enum):
    """Webhook event types"""
    ORDER_CREATED = "ORDER_CREATED"
    ORDER_UPDATED = "ORDER_UPDATED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    PAYMENT_SUCCESS = "PAYMENT_SUCCESS"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PRODUCT_CREATED = "PRODUCT_CREATED"
    PRODUCT_UPDATED = "PRODUCT_UPDATED"
    INVENTORY_LOW = "INVENTORY_LOW"
    CUSTOMER_CREATED = "CUSTOMER_CREATED"


class Webhook(Base):
    """Webhook endpoints configured by tenants"""
    __tablename__ = "webhooks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ecommerce_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ecommerce.id"), nullable=False)
    
    # Webhook configuration
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    secret: Mapped[str] = mapped_column(String(255), nullable=False)  # For signature verification
    
    # Event subscriptions
    events: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Retry configuration
    retry_count: Mapped[int] = mapped_column(Integer, default=3)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    ecommerce: Mapped["Ecommerce"] = relationship("Ecommerce", back_populates="webhooks")
    deliveries: Mapped[List["WebhookDelivery"]] = relationship("WebhookDelivery", back_populates="webhook", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Webhook {self.url}>"


class WebhookDelivery(Base):
    """Webhook delivery attempts and status"""
    __tablename__ = "webhook_deliveries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    webhook_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("webhooks.id"), nullable=False)
    
    # Event details
    event_type: Mapped[WebhookEventType] = mapped_column(SQLEnum(WebhookEventType), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    # Delivery status
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # PENDING, SUCCESS, FAILED
    http_status: Mapped[int] = mapped_column(Integer, nullable=True)
    response_body: Mapped[str] = mapped_column(Text, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Retry tracking
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    next_retry_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    delivered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    webhook: Mapped["Webhook"] = relationship("Webhook", back_populates="deliveries")

    def __repr__(self):
        return f"<WebhookDelivery {self.event_type} - {self.status}>"
