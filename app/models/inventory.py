from sqlalchemy import Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from datetime import datetime
from typing import Optional
import uuid


class Inventory(Base):
    """Inventory model for product stock tracking"""
    __tablename__ = "inventory"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), primary_key=True
    )
    
    # Stock levels
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reserved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Computed available quantity (quantity - reserved)
    # This is calculated in the application layer
    
    # Alert settings
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=10)
    
    # Audit
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    product: Mapped["Product"] = relationship(
        "Product", back_populates="inventory"
    )

    @property
    def available(self) -> int:
        """Calculate available inventory"""
        return max(0, self.quantity - self.reserved)
    
    @property
    def is_low_stock(self) -> bool:
        """Check if inventory is below threshold"""
        return self.available <= self.low_stock_threshold

    def __repr__(self) -> str:
        return f"<Inventory(product_id={self.product_id}, quantity={self.quantity}, available={self.available})>"
