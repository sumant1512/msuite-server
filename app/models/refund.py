from sqlalchemy import String, DateTime, ForeignKey, Numeric, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from datetime import datetime
from typing import Optional
import uuid
import enum


class RefundStatus(enum.Enum):
    """Refund status enumeration"""
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class RefundReason(enum.Enum):
    """Refund reason enumeration"""
    CUSTOMER_REQUEST = "CUSTOMER_REQUEST"
    DEFECTIVE_PRODUCT = "DEFECTIVE_PRODUCT"
    WRONG_ITEM = "WRONG_ITEM"
    NOT_AS_DESCRIBED = "NOT_AS_DESCRIBED"
    DAMAGED_IN_TRANSIT = "DAMAGED_IN_TRANSIT"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    OTHER = "OTHER"


class OrderRefund(Base):
    """Order refund model for return and refund management"""
    __tablename__ = "order_refunds"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    # Relationships
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True
    )
    ecommerce_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ecommerce.id"), nullable=False, index=True
    )
    
    # Refund details
    refund_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    reason: Mapped[RefundReason] = mapped_column(Enum(RefundReason), nullable=False)
    status: Mapped[RefundStatus] = mapped_column(
        Enum(RefundStatus), default=RefundStatus.REQUESTED
    )
    
    # Additional information
    customer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    admin_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Processing details
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    processed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    
    # Transaction details
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    refund_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Inventory return
    inventory_returned: Mapped[bool] = mapped_column(default=False)
    
    # Timestamps
    requested_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="refunds")
    ecommerce: Mapped["Ecommerce"] = relationship("Ecommerce")
    approved_by: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[approved_by_id]
    )
    processed_by: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[processed_by_id]
    )

    def __repr__(self) -> str:
        return f"<OrderRefund(id={self.id}, number={self.refund_number}, status={self.status.value})>"
