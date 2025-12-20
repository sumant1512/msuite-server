from sqlalchemy import String, Boolean, DateTime, Integer, Numeric, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
from datetime import datetime
from typing import Optional, List
import uuid
import enum


class SubscriptionInterval(enum.Enum):
    """Subscription billing interval"""
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class SubscriptionPlan(Base):
    """Subscription plan model for agency pricing tiers"""
    __tablename__ = "subscription_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    interval: Mapped[SubscriptionInterval] = mapped_column(
        Enum(SubscriptionInterval), default=SubscriptionInterval.MONTHLY
    )
    
    # Features and limits
    features: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # Example features structure:
    # {
    #     "max_ecommerce": 10,
    #     "max_products_per_ecommerce": 1000,
    #     "max_orders_per_month": 10000,
    #     "api_calls_per_month": 100000,
    #     "support_level": "email"
    # }
    
    # Status and audit
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    agencies: Mapped[List["Agency"]] = relationship(
        "Agency", back_populates="subscription_plan"
    )

    def __repr__(self) -> str:
        return f"<SubscriptionPlan(id={self.id}, name={self.name}, price={self.price})>"
