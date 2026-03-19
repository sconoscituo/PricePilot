import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.alert import PriceAlert

logger = logging.getLogger(__name__)


class AlertService:
    """목표가 도달 시 알림 생성 서비스"""

    @classmethod
    async def check_and_trigger(cls, product: Product, db: AsyncSession) -> None:
        """현재 가격이 목표가 이하이면 알림 레코드 생성"""
        if product.target_price is None or product.current_price is None:
            return

        if product.current_price <= product.target_price:
            message = (
                f"[PricePilot] '{product.name}' 가격 알림!\n"
                f"목표가 {int(product.target_price):,}원 달성!\n"
                f"현재가: {int(product.current_price):,}원\n"
                f"구매 링크: {product.affiliate_url or product.url}"
            )

            alert = PriceAlert(
                message=message,
                triggered_price=product.current_price,
                product_id=product.id,
                user_id=product.user_id,
            )
            db.add(alert)
            await db.commit()

            logger.info(
                f"알림 생성: 상품 {product.id} ({product.name}) "
                f"현재가 {product.current_price:,}원 <= 목표가 {product.target_price:,}원"
            )

            # 향후 이메일/푸시 알림 연동 지점
            await cls._send_notification(product, message)

    @classmethod
    async def _send_notification(cls, product: Product, message: str) -> None:
        """알림 발송 (현재는 로그만 기록, 이메일/슬랙 연동 확장 가능)"""
        logger.info(f"[알림 발송 대기] 사용자 {product.user_id}: {message}")
        # TODO: 이메일(SMTP) 또는 슬랙 웹훅 연동
