from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Ecommerce(Base):
    __tablename__ = "ecommerces"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    agency_id: Mapped[int] = mapped_column(ForeignKey("agencies.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)