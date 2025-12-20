"""
Discount and coupon models
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Float, DateTime, Boolean, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from typing import List, Optional
import uuid
from datetime import datetime
import enum

from app.core.database import Base


class DiscountType(str, enum.Enum):
    """Discount type enumeration"""
    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"
    FREE_SHIPPING = "FREE_SHIPPING"


class Coupon(Base):
    """Discount coupons"""
    __tablename__ = "coupons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ecommerce_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ecommerce.id"), nullable=False)
    
    # Coupon details
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # Discount configuration
    discount_type: Mapped[DiscountType] = mapped_column(SQLEnum(DiscountType), nullable=False)
    discount_value: Mapped[float] = mapped_column(Float, nullable=False)  # Percentage or fixed amount
    
    # Usage limits
    usage_limit: Mapped[int] = mapped_column(Integer, nullable=True)  # Total uses allowed
    usage_count: Mapped[int] = mapped_column(Integer, default=0)  # Current usage
    usage_limit_per_customer: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Minimum requirements
    minimum_purchase_amount: Mapped[float] = mapped_column(Float, nullable=True)
    
    # Validity period
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    ecommerce: Mapped["Ecommerce"] = relationship("Ecommerce", back_populates="coupons")

    def __repr__(self):
        return f"<Coupon {self.code}>"
