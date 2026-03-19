"""PricePilot 구독 플랜"""
from enum import Enum

class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"       # 월 4,900원

PLAN_LIMITS = {
    PlanType.FREE: {"tracked_items": 5,  "price_alerts": 3,  "history_days": 7,  "ai_prediction": False},
    PlanType.PRO:  {"tracked_items": 100,"price_alerts": 50, "history_days": 365,"ai_prediction": True},
}

PLAN_PRICES_KRW = {PlanType.FREE: 0, PlanType.PRO: 4900}
