from sqlalchemy import String, Boolean, DateTime, ForeignKey, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
from datetime import datetime
from typing import Optional
import uuid


class Customer(Base):
    """Customer model for e-commerce user management"""
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    ecommerce_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ecommerce.id"), nullable=False, index=True
    )
    
    # Customer information
    email: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Address information
    addresses: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # Example addresses structure:
    # {
    #     "default": {
    #         "street": "123 Main St",
    #         "city": "New York",
    #         "state": "NY",
    #         "postal_code": "10001",
    #         "country": "USA"
    #     },
    #     "billing": {...},
    #     "shipping": {...}
    # }
    
    # Additional customer data
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, name="metadata")
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    ecommerce: Mapped["Ecommerce"] = relationship(
        "Ecommerce", back_populates="customers"
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="customer", cascade="all, delete-orphan"
    )
    carts: Mapped[list["Cart"]] = relationship(
        "Cart", back_populates="customer", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["ProductReview"]] = relationship(
        "ProductReview", back_populates="customer", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, email={self.email}, full_name={self.full_name})>"
