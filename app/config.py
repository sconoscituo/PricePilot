from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 앱 기본 설정
    app_name: str = "PricePilot"
    debug: bool = True

    # 데이터베이스
    database_url: str = "sqlite+aiosqlite:///./pricepilot.db"

    # JWT 인증
    secret_key: str = "changeme-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24시간

    # Gemini API
    gemini_api_key: str = ""

    # 쿠팡파트너스 API
    coupang_access_key: str = ""
    coupang_secret_key: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 반환 (캐싱)"""
    return Settings()
