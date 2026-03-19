from datetime import datetime
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Product(Base):
    """추적 중인 상품 모델"""
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 상품 기본 정보
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(2000), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)  # coupang | naver

    # 가격 정보
    current_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    lowest_price: Mapped[float | None] = mapped_column(Float, nullable=True)   # 역대 최저가
    highest_price: Mapped[float | None] = mapped_column(Float, nullable=True)  # 역대 최고가
    target_price: Mapped[float | None] = mapped_column(Float, nullable=True)   # 사용자 목표가

    # 쿠팡파트너스 제휴 링크 (수익화)
    affiliate_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    # Gemini 분석 결과
    gemini_summary: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    # 관계
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="products")  # noqa: F821
    alerts: Mapped[list["PriceAlert"]] = relationship("PriceAlert", back_populates="product", cascade="all, delete-orphan")  # noqa: F821

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
