from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import json
import uuid

from app.repositories.category_repository import CategoryRepository
from app.schemas.category import (
    CategoryResponse,
    CreateCategoryRequest,
)

from app.cache.redis import redis_client
from app.database.models.outbox_event import OutboxEvent


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
        cache_key = "categories:all"

        cached_categories = await redis_client.get(cache_key)

        if cached_categories is not None:
            data = json.loads(cached_categories)
            return [
                CategoryResponse(**category)
                for category in data
            ]
    
        categories = await self.repository.get_all()

        response = [
            CategoryResponse(
                id=category.id,
                name=category.name,
            )
            for category in categories
        ]

        await redis_client.set(
            cache_key,
            json.dumps(
                [
                    category.model_dump(mode="json")
                    for category in response
                ]
            ),
            ex=60,
        )
        
        return response

    async def create_category(
        self,
        category_data: CreateCategoryRequest,
    ) -> CategoryResponse:
        try:
            category = await self.repository.create(
                name=category_data.name,
            )

            event = {
                "event_id": str(uuid.uuid4()),
                "event": "category.created",
                "category_id": category.id,
            }

            outbox_event = OutboxEvent(
                event_type="category.created",
                payload=json.dumps(event),
            )

            self.repository.session.add(outbox_event)

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