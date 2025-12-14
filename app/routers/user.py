from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID

class UserRole(enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    AGENCY_ADMIN = "AGENCY_ADMIN"
    ECOMMERCE = "ECOMMERCE"

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    password_hash: Mapped[str]
    role: Mapped[UserRole] = mapped_column(Enum(UserRole))
