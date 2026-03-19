from datetime import datetime
from sqlalchemy import String, Boolean, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # 관계
    products: Mapped[list["Product"]] = relationship("Product", back_populates="user", cascade="all, delete-orphan")  # noqa: F821
    alerts: Mapped[list["PriceAlert"]] = relationship("PriceAlert", back_populates="user", cascade="all, delete-orphan")  # noqa: F821

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
