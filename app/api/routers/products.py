from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_db
from app.schemas.product import CreateProductRequest, ProductResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])

def get_product_service(session: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(session)


@router.get("", response_model= list[ProductResponse])
async def get_products(
    service: ProductService = Depends(get_product_service)
):
    return await service.get_products()

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
