from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
from datetime import datetime
from typing import Optional, List
import uuid
import enum


class SubscriptionStatus(enum.Enum):
    """Subscription status enumeration"""
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"
    TRIAL = "TRIAL"


class Agency(Base):
    """Agency model for managing multiple e-commerce tenants"""
    __tablename__ = "agencies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Subscription management
    subscription_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False
    )
    subscription_status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL
    )
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    
    # Limits
    max_ecommerce: Mapped[int] = mapped_column(Integer, default=3)
    
    # Resale pricing - allows agencies to set their own pricing for ecommerce stores
    resale_price_per_ecommerce: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="Custom pricing per ecommerce store for agency resale"
    )
    
    # Status and audit
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, name="metadata")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    subscription_plan: Mapped["SubscriptionPlan"] = relationship(
        "SubscriptionPlan", back_populates="agencies"
    )
    ecommerce: Mapped[List["Ecommerce"]] = relationship(
        "Ecommerce", back_populates="agency", cascade="all, delete-orphan"
    )
    users: Mapped[List["User"]] = relationship(
        "User", back_populates="agency", foreign_keys="User.agency_id"
    )
    invoices: Mapped[List["Invoice"]] = relationship(
        "Invoice", back_populates="agency", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Agency(id={self.id}, name={self.name}, status={self.subscription_status.value})>"
