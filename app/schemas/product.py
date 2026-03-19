from datetime import datetime
from pydantic import BaseModel, HttpUrl


class ProductCreate(BaseModel):
    """상품 추가 요청 스키마"""
    name: str
    url: str
    platform: str  # coupang | naver
    target_price: float | None = None  # 목표가 (선택)


class ProductUpdate(BaseModel):
    """상품 수정 요청 스키마"""
    name: str | None = None
    target_price: float | None = None


class ProductResponse(BaseModel):
    """상품 응답 스키마"""
    id: int
    name: str
    url: str
    platform: str
    current_price: float | None
    lowest_price: float | None
    highest_price: float | None
    target_price: float | None
    affiliate_url: str | None
    gemini_summary: str | None
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AlertResponse(BaseModel):
    """알림 이력 응답 스키마"""
    id: int
    message: str
    triggered_price: float | None
    product_id: int
    user_id: int
    triggered_at: datetime

    model_config = {"from_attributes": True}
