import re
import logging
from typing import Optional

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.product import Product

logger = logging.getLogger(__name__)
settings = get_settings()


class PriceTrackerService:
    """쿠팡/네이버쇼핑 가격 스크래핑 + Gemini 상품 분석 서비스"""

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ko-KR,ko;q=0.9",
    }

    @classmethod
    async def fetch_price(cls, url: str, platform: str) -> Optional[float]:
        """플랫폼에 따라 가격 스크래핑"""
        try:
            async with httpx.AsyncClient(headers=cls.HEADERS, follow_redirects=True, timeout=15) as client:
                response = await client.get(url)
                response.raise_for_status()
                html = response.text

            if platform == "coupang":
                return cls._parse_coupang_price(html)
            elif platform == "naver":
                return cls._parse_naver_price(html)
            else:
                logger.warning(f"지원하지 않는 플랫폼: {platform}")
                return None
        except Exception as e:
            logger.error(f"가격 조회 실패 [{url}]: {e}")
            return None

    @classmethod
    def _parse_coupang_price(cls, html: str) -> Optional[float]:
        """쿠팡 상품 페이지에서 가격 파싱"""
        soup = BeautifulSoup(html, "html.parser")

        # 쿠팡 가격 셀렉터 (구조 변경 대응용 복수 셀렉터)
        selectors = [
            "span.total-price strong",
            "span.prod-coupon-price strong",
            "span.price-value",
        ]
        for selector in selectors:
            el = soup.select_one(selector)
            if el:
                price_text = re.sub(r"[^\d]", "", el.get_text())
                if price_text:
                    return float(price_text)

        # 정규식 폴백: "원" 앞에 오는 숫자 패턴
        match = re.search(r'"price"\s*:\s*(\d+)', html)
        if match:
            return float(match.group(1))

        return None

    @classmethod
    def _parse_naver_price(cls, html: str) -> Optional[float]:
        """네이버쇼핑 상품 페이지에서 가격 파싱"""
        soup = BeautifulSoup(html, "html.parser")

        selectors = [
            "span.price_num",
            "strong.price_real",
            "em.num",
        ]
        for selector in selectors:
            el = soup.select_one(selector)
            if el:
                price_text = re.sub(r"[^\d]", "", el.get_text())
                if price_text:
                    return float(price_text)

        # JSON-LD 폴백
        match = re.search(r'"price"\s*:\s*"?(\d+)"?', html)
        if match:
            return float(match.group(1))

        return None

    @classmethod
    async def analyze_with_gemini(cls, product_name: str, current_price: float) -> Optional[str]:
        """Gemini API로 상품 구매 적합성 분석"""
        if not settings.gemini_api_key:
            return None

        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel("gemini-pro")

            prompt = (
                f"다음 상품에 대해 한국어로 간단한 구매 조언을 2~3문장으로 작성해주세요.\n"
                f"상품명: {product_name}\n"
                f"현재 가격: {int(current_price):,}원\n"
                f"가격이 적정한지, 어떤 소비자에게 적합한지 분석해주세요."
            )

            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini 분석 실패: {e}")
            return None

    @classmethod
    async def fetch_and_update_price(cls, product_id: int, db: AsyncSession) -> None:
        """상품 가격 조회 후 DB 업데이트 (스케줄러/백그라운드 태스크용)"""
        try:
            result = await db.execute(select(Product).where(Product.id == product_id))
            product = result.scalar_one_or_none()
            if not product:
                return

            new_price = await cls.fetch_price(product.url, product.platform)
            if new_price is None:
                logger.warning(f"상품 {product_id} 가격 조회 실패")
                return

            # 가격 업데이트
            product.current_price = new_price

            # 최저/최고가 갱신
            if product.lowest_price is None or new_price < product.lowest_price:
                product.lowest_price = new_price
            if product.highest_price is None or new_price > product.highest_price:
                product.highest_price = new_price

            # Gemini 분석 (최초 1회 또는 가격 변동 시)
            if product.gemini_summary is None:
                product.gemini_summary = await cls.analyze_with_gemini(product.name, new_price)

            await db.commit()
            logger.info(f"상품 {product_id} 가격 업데이트 완료: {new_price:,}원")

            # 목표가 도달 알림 확인
            from app.services.alert import AlertService
            await AlertService.check_and_trigger(product, db)

        except Exception as e:
            logger.error(f"상품 {product_id} 업데이트 오류: {e}")
            await db.rollback()
