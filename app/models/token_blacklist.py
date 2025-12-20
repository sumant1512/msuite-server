"""
Token Blacklist Model
For tracking invalidated JWT tokens (logout, forced logout)
"""
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class TokenBlacklist(Base):
    """Model for storing blacklisted tokens"""
    __tablename__ = "token_blacklist"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(Text, nullable=False, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    reason = Column(String(50), default="logout")  # logout, forced_logout, security
    blacklisted_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)  # Token's original expiry

    def __repr__(self):
        return f"<TokenBlacklist(user_id={self.user_id}, reason={self.reason})>"
