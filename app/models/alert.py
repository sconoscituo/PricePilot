from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PriceAlert(Base):
    """가격 알림 이력 모델"""
    __tablename__ = "price_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 알림 내용
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    triggered_price: Mapped[float | None] = mapped_column(nullable=True)  # 알림이 발생한 시점의 가격

    # 관계
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    product: Mapped["Product"] = relationship("Product", back_populates="alerts")  # noqa: F821

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="alerts")  # noqa: F821

    # 타임스탬프
    triggered_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
