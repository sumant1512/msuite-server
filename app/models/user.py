from sqlalchemy import String, Enum, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.enums.user_role import UserRole
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    
    # Multi-tenancy relationships
    agency_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agencies.id"), nullable=True, index=True
    )
    ecommerce_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ecommerce.id"), nullable=True, index=True
    )
    
    # Status and audit fields
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_activity: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    agency: Mapped[Optional["Agency"]] = relationship(
        "Agency", back_populates="users", foreign_keys=[agency_id]
    )
    ecommerce: Mapped[Optional["Ecommerce"]] = relationship(
        "Ecommerce", back_populates="users", foreign_keys=[ecommerce_id]
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role.value})>"
