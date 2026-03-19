from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# 비동기 엔진 생성
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # 디버그 모드에서 SQL 로그 출력
    future=True,
)

# 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """모든 모델의 기반 클래스"""
    pass


async def init_db() -> None:
    """테이블 생성 (앱 시작 시 호출)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """의존성 주입용 DB 세션 제공"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
