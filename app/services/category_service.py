from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

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
        try:
            category = await self.repository.create(
                name=category_data.name,
            )

            await self.repository.session.commit()

        except IntegrityError:
            await self.repository.session.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category with this name already exists",
            )

        return CategoryResponse(
            id=category.id,
            name=category.name,
        )

    async def delete_category(self, category_id: int) -> None:
        category = await self.repository.get_by_id(category_id)

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        if await self.repository.has_products(category_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category contains products",
            )

        await self.repository.delete(category)

        await self.repository.session.commit()