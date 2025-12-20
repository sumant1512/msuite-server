"""
Product review and rating models
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Float, DateTime, Boolean, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from typing import List, Optional
import uuid
from datetime import datetime

from app.core.database import Base


class ProductReview(Base):
    """Product reviews and ratings"""
    __tablename__ = "product_reviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True)
    
    # Review content
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5 stars
    title: Mapped[str] = mapped_column(String(200), nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Review metadata
    is_verified_purchase: Mapped[bool] = mapped_column(Boolean, default=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)  # Moderation
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Images (optional)
    images: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="reviews")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="reviews")
    order: Mapped["Order"] = relationship("Order")

    def __repr__(self):
        return f"<Review {self.id} - Product: {self.product_id} - Rating: {self.rating}>"
