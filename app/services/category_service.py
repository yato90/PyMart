from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.category_repository import CategoryRepository
from app.schemas.category import (
    CategoryResponse,
    CreateCategoryRequest,
)


class CategoryService:

    def __init__(self, session: AsyncSession):
        self.repository = CategoryRepository(session)

    async def get_category(self, category_id: int) -> CategoryResponse:
        category = await self.repository.get_by_id(category_id)

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        return CategoryResponse(
            id=category.id,
            name=category.name,
        )

    async def get_categories(self) -> list[CategoryResponse]:
        categories = await self.repository.get_all()

        return [
            CategoryResponse(
                id=category.id,
                name=category.name,
            )
            for category in categories
        ]

    async def create_category(
        self,
        category_data: CreateCategoryRequest,
    ) -> CategoryResponse:
        category = await self.repository.create(
            name=category_data.name,
        )

        await self.repository.session.commit()

        return CategoryResponse(
            id=category.id,
            name=category.name,
        )