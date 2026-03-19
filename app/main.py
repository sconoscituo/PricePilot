import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db, AsyncSessionLocal
from app.routers import products, users, alerts

logger = logging.getLogger(__name__)
settings = get_settings()

# APScheduler 인스턴스
scheduler = AsyncIOScheduler(timezone="Asia/Seoul")


async def scheduled_price_update() -> None:
    """모든 추적 상품 가격 주기적 갱신 (스케줄러 호출)"""
    from sqlalchemy import select
    from app.models.product import Product
    from app.services.price_tracker import PriceTrackerService

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Product))
        products_list = result.scalars().all()
        logger.info(f"가격 갱신 시작: 총 {len(products_list)}개 상품")
        for product in products_list:
            await PriceTrackerService.fetch_and_update_price(product.id, db)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 라이프사이클 핸들러"""
    # 시작: DB 테이블 생성 + 스케줄러 시작
    await init_db()
    logger.info("데이터베이스 초기화 완료")

    # 1시간마다 가격 갱신
    scheduler.add_job(scheduled_price_update, "interval", hours=1, id="price_update")
    scheduler.start()
    logger.info("가격 추적 스케줄러 시작 (1시간 간격)")

    yield

    # 종료: 스케줄러 정지
    scheduler.shutdown(wait=False)
    logger.info("스케줄러 종료")


# FastAPI 앱 생성
app = FastAPI(
    title="PricePilot",
    description="쿠팡/네이버쇼핑 최저가 추적 + 가격 알림 서비스. Gemini API로 상품 분석.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 설정 (개발 환경: 전체 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(users.router)
app.include_router(products.router)
app.include_router(alerts.router, prefix="/api/v1")


@app.get("/", tags=["health"])
async def root():
    """헬스체크 엔드포인트"""
    return {
        "service": "PricePilot",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health():
    """서버 상태 확인"""
    return {"status": "ok"}
