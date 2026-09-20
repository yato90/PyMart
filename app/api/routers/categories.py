from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_db
from app.schemas.category import (
    CategoryResponse,
    CreateCategoryRequest,
)
from app.services.category_service import CategoryService


router = APIRouter(prefix="/categories", tags=["categories"])


def get_category_service(
    session: AsyncSession = Depends(get_db),
) -> CategoryService:
    return CategoryService(session)


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
    service: CategoryService = Depends(get_category_service),
):
    return await service.create_category(category)