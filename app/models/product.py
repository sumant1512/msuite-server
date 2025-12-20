from sqlalchemy import String, Boolean, DateTime, ForeignKey, Numeric, Text, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
from datetime import datetime
from typing import Optional
import uuid


class Product(Base):
    """Product model for e-commerce catalog management"""
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    ecommerce_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ecommerce.id"), nullable=False, index=True
    )
    
    # Basic product information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sku: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Pricing
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    compare_at_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    cost: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Organization
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    tags: Mapped[Optional[list]] = mapped_column(ARRAY(String), nullable=True)
    
    # Media
    images: Mapped[Optional[list]] = mapped_column(ARRAY(String), nullable=True)
    
    # Variants and options
    variants: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # Example variants structure:
    # {
    #     "size": ["Small", "Medium", "Large"],
    #     "color": ["Red", "Blue", "Green"]
    # }
    
    # Additional data
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, name="metadata")
    
    # Status and audit
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    ecommerce: Mapped["Ecommerce"] = relationship(
        "Ecommerce", back_populates="products"
    )
    inventory: Mapped[Optional["Inventory"]] = relationship(
        "Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan"
    )
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="product"
    )
    reviews: Mapped[list["ProductReview"]] = relationship(
        "ProductReview", back_populates="product", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name={self.name}, sku={self.sku})>"
