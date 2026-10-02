from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_db
from app.schemas.product import CreateProductRequest, ProductResponse, ProductListResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])

def get_product_service(
    session: AsyncSession = Depends(get_db)
) -> ProductService:
    return ProductService(session)


@router.get("", response_model= ProductListResponse)
async def get_products(
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = None,
    service: ProductService = Depends(get_product_service),
):
    return await service.get_products(
        limit=limit,
        cursor=cursor,
    )

@router.get("/{product_id}", response_model= ProductResponse)
async def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    return await service.get_product(product_id)

@router.post("", response_model= ProductResponse)
async def create_product(
    product: CreateProductRequest,
    service: ProductService = Depends(get_product_service)
):
    return await service.create_product(product)

@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    await service.delete_product(product_id)
