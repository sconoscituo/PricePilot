from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.product import Product
from app.models.alert import PriceAlert
from app.models.user import User
from app.routers.users import get_current_user
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate, AlertResponse
from app.services.price_tracker import PriceTrackerService
from app.services.alert import AlertService

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductResponse, status_code=201)
async def add_product(
    product_in: ProductCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """상품 추가 및 즉시 가격 조회"""
    product = Product(
        name=product_in.name,
        url=product_in.url,
        platform=product_in.platform,
        target_price=product_in.target_price,
        user_id=current_user.id,
    )
    db.add(product)
    await db.flush()
    await db.refresh(product)

    # 백그라운드에서 즉시 가격 조회 + Gemini 분석 실행
    background_tasks.add_task(
        PriceTrackerService.fetch_and_update_price, product.id, db
    )

    return product


@router.get("/", response_model=list[ProductResponse])
async def list_products(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """내 상품 목록 조회"""
    result = await db.execute(
        select(Product).where(Product.user_id == current_user.id)
    )
    return result.scalars().all()


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """상품 상세 조회"""
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.user_id == current_user.id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
    return product


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """상품 정보 수정 (이름, 목표가)"""
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.user_id == current_user.id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")

    if product_in.name is not None:
        product.name = product_in.name
    if product_in.target_price is not None:
        product.target_price = product_in.target_price

    await db.flush()
    await db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """상품 삭제"""
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.user_id == current_user.id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")

    await db.delete(product)


@router.get("/{product_id}/alerts", response_model=list[AlertResponse])
async def get_price_alerts(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """상품별 가격 알림 이력 조회"""
    # 상품 소유권 확인
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")

    alerts_result = await db.execute(
        select(PriceAlert)
        .where(PriceAlert.product_id == product_id)
        .order_by(PriceAlert.triggered_at.desc())
    )
    return alerts_result.scalars().all()


@router.post("/{product_id}/refresh", response_model=ProductResponse)
async def refresh_price(
    product_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """수동으로 가격 즉시 갱신"""
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.user_id == current_user.id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")

    background_tasks.add_task(
        PriceTrackerService.fetch_and_update_price, product.id, db
    )
    return product
