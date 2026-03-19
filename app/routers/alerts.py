"""
가격 하락 알림 라우터
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/alerts", tags=["가격 알림"])

try:
    from app.models.alert import PriceAlert
    HAS_ALERT = True
except ImportError:
    HAS_ALERT = False


class AlertCreate(BaseModel):
    product_url: str
    product_name: str
    current_price: float
    target_price: float
    notification_email: Optional[str] = None


@router.post("/")
async def create_price_alert(
    alert: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """가격 하락 알림 등록"""
    if alert.target_price >= alert.current_price:
        raise HTTPException(400, "목표가는 현재가보다 낮아야 합니다")

    discount_rate = (alert.current_price - alert.target_price) / alert.current_price * 100

    if HAS_ALERT:
        new_alert = PriceAlert(
            user_id=current_user.id,
            product_url=alert.product_url,
            product_name=alert.product_name,
            current_price=alert.current_price,
            target_price=alert.target_price,
            notification_email=alert.notification_email or getattr(current_user, "email", ""),
            is_active=True,
        )
        db.add(new_alert)
        await db.commit()
        await db.refresh(new_alert)
        alert_id = new_alert.id
    else:
        alert_id = None

    return {
        "message": "알림이 등록되었습니다",
        "alert_id": alert_id,
        "product_name": alert.product_name,
        "target_price": alert.target_price,
        "discount_rate": round(discount_rate, 1),
        "status": "모니터링 중",
    }


@router.get("/")
async def get_my_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """내 알림 목록 조회"""
    if not HAS_ALERT:
        return {"alerts": [], "total": 0}

    result = await db.execute(
        select(PriceAlert).where(
            PriceAlert.user_id == current_user.id,
            PriceAlert.is_active == True
        )
    )
    alerts = result.scalars().all()
    return {
        "alerts": [
            {
                "id": a.id,
                "product_name": getattr(a, "product_name", ""),
                "current_price": getattr(a, "current_price", 0),
                "target_price": getattr(a, "target_price", 0),
                "status": "모니터링 중",
            }
            for a in alerts
        ],
        "total": len(alerts),
    }
