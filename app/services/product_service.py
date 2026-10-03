from decimal import Decimal
from fastapi import HTTPException, status
import json
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.core.cursor import decode_cursor, encode_cursor
from app.schemas.product import (
    CreateProductRequest, 
    ProductResponse,
    ProductListResponse
)
from app.cache.redis import redis_client
from app.database.models.outbox_event import OutboxEvent

class ProductService:

    def __init__(self, session: AsyncSession):
        self.repository = ProductRepository(session)
        self.category_repository = CategoryRepository(session)

    async def get_products(
            self,
            limit: int,
            cursor: str | None,
    ) -> ProductListResponse:
        cursor_created_at = None
        cursor_id = None

        if cursor is not None:
            cursor_created_at, cursor_id = decode_cursor(cursor)

        products = await self.repository.get_all(
            limit=limit + 1,
            cursor_created_at=cursor_created_at,
            cursor_id=cursor_id,
        )

        has_next = len(products) > limit

        if has_next:
            products = products[:limit]

        items = [
            ProductResponse(
                id=product.id,
                name=product.name,
                price=product.price,
                category_id=product.category_id
            )
            for product in products
        ]

        next_cursor = None

        if has_next:
            last_product = products[-1]

            next_cursor = encode_cursor(
                created_at=last_product.created_at,
                product_id=last_product.id,
            )

        return ProductListResponse(
            items=items,
            next_cursor=next_cursor,
        )

    async def get_product(self, product_id: int) -> ProductResponse | None:
        cache_key = f"product:{product_id}"

        cached_product = await redis_client.get(cache_key)

        if cached_product is not None:
            data = json.loads(cached_product)

            return ProductResponse(**data)

        product = await self.repository.get_by_id(product_id)

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        response = ProductResponse(
            id=product.id,
            name=product.name,
            price=product.price,
            category_id= product.category_id
        )

        await redis_client.set(
            cache_key,
            json.dumps(response.model_dump(mode="json")),
            ex=60,
        )
        
        return response

    async def get_products_by_category(
            self,
            category_id: int,
            limit: int,
            cursor: str | None,
    ) -> ProductListResponse:
        category = await self.category_repository.get_by_id(category_id)

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        cursor_created_at = None
        cursor_id = None

        if cursor is not None:
            cursor_created_at, cursor_id = decode_cursor(cursor)

        products = await self.repository.get_by_category_id(
            category_id=category_id,
            limit=limit + 1,
            cursor_created_at=cursor_created_at,
            cursor_id=cursor_id,
        )

        has_next = len(products) > limit

        if has_next:
            products = products[:limit]

        items = [
            ProductResponse(
                id=product.id,
                name=product.name,
                price=product.price,
                category_id=product.category_id
            )
            for product in products
        ]

        next_cursor = None

        if has_next:
            last_product = products[-1]

            next_cursor = encode_cursor(
                created_at=last_product.created_at,
                product_id=last_product.id,
            )

        return ProductListResponse(
            items=items,
            next_cursor=next_cursor,
        )
    
    async def create_product(
        self, 
        product_data:CreateProductRequest
    ) -> ProductResponse:

        category = await self.category_repository.get_by_id(
            product_data.category_id
        )

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        product = await self.repository.create(
            name=product_data.name,
            price=product_data.price,
            category_id=product_data.category_id
        )

        event = {
            "event_id": str(uuid.uuid4()),
            "event": "product.created",
            "product_id": product.id,
        }

        outbox_event = OutboxEvent(
            event_type="product.created",
            payload=json.dumps(event),
        )

        self.repository.session.add(outbox_event)

        await self.repository.session.commit()
        
        return ProductResponse(
            id= product.id,
            name= product.name,
            price= product.price,
            category_id=product.category_id
        )

    async def delete_product(self, product_id: int) -> None:
        product = await self.repository.get_by_id(product_id)

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        await self.repository.delete(product)
        await self.repository.session.commit()

        await redis_client.delete(f"product:{product_id}")