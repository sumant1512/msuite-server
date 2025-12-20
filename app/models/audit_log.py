"""
Audit logging model for tracking all changes
"""
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime

from app.core.database import Base


class AuditLog(Base):
    """Audit log for tracking all system changes"""
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Who did it
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user_email: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Tenant context
    ecommerce_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    agency_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # Action details
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)  # User, Product, Order, etc.
    resource_id: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Change details
    old_values: Mapped[dict] = mapped_column(JSONB, nullable=True)
    new_values: Mapped[dict] = mapped_column(JSONB, nullable=True)
    
    # Request metadata
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)
    endpoint: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # Additional context
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.resource_type} by {self.user_email}>"
