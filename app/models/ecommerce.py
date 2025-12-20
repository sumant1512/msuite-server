from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
from datetime import datetime
from typing import Optional
import uuid
import secrets


class Ecommerce(Base):
    """E-commerce tenant model for isolated store instances"""
    __tablename__ = "ecommerce"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    agency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agencies.id"), nullable=False, index=True
    )
    
    # Basic information
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # API access
    api_key: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, default=lambda: secrets.token_urlsafe(32)
    )
    
    # Settings and configuration
    settings: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # Example settings structure:
    # {
    #     "currency": "USD",
    #     "timezone": "America/New_York",
    #     "language": "en",
    #     "tax_rate": 8.5,
    #     "shipping_zones": [...],
    #     "email_templates": {...}
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
    agency: Mapped["Agency"] = relationship(
        "Agency", back_populates="ecommerce"
    )
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="ecommerce", foreign_keys="User.ecommerce_id"
    )
    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="ecommerce", cascade="all, delete-orphan"
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="ecommerce", cascade="all, delete-orphan"
    )
    customers: Mapped[list["Customer"]] = relationship(
        "Customer", back_populates="ecommerce", cascade="all, delete-orphan"
    )
    carts: Mapped[list["Cart"]] = relationship(
        "Cart", back_populates="ecommerce", cascade="all, delete-orphan"
    )
    coupons: Mapped[list["Coupon"]] = relationship(
        "Coupon", back_populates="ecommerce", cascade="all, delete-orphan"
    )
    webhooks: Mapped[list["Webhook"]] = relationship(
        "Webhook", back_populates="ecommerce", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Ecommerce(id={self.id}, name={self.name}, domain={self.domain})>"
