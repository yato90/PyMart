from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from app.database.dependencies import get_db
from app.schemas.category import (
    CategoryResponse,
    CreateCategoryRequest,
)
from app.services.category_service import CategoryService

from app.services.product_service import ProductService
from app.schemas.product import ProductResponse, ProductListResponse

from app.auth.dependencies import require_admin
from app.database.models.user import User


router = APIRouter(prefix="/categories", tags=["categories"])


def get_category_service(
    session: AsyncSession = Depends(get_db),
) -> CategoryService:
    return CategoryService(session)

def get_product_service(
    session: AsyncSession = Depends(get_db),
) -> ProductService:
    return ProductService(session)

@router.get("", response_model=list[CategoryResponse])
async def get_categories(
    service: CategoryService = Depends(get_category_service),
):
    return await service.get_categories()


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
):
    return await service.get_category(category_id)


@router.post("", response_model=CategoryResponse,)
async def create_category(
    category: CreateCategoryRequest,
    current_user: Annotated[
        User,
        Depends(require_admin),
    ],
    service: CategoryService = Depends(get_category_service),
):
    return await service.create_category(category)

@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: int,
    current_user: Annotated[
        User,
        Depends(require_admin),
    ],
    service: CategoryService = Depends(get_category_service),
):
    await service.delete_category(category_id)

@router.get(
    "/{category_id}/products", 
    response_model=ProductListResponse,
)
async def get_category_products(
    category_id: int,
    limit: int = Query(
        default=20,
        ge=1,
        le=100
    ),
    cursor: str | None = None,
    service: ProductService = Depends(get_product_service)
):
    return await service.get_products_by_category(
        category_id=category_id,
        limit=limit,
        cursor=cursor,
    )