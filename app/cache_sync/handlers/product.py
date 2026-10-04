import json

from sqlalchemy import select

from app.cache.redis import redis_client
from app.database.connection import AsyncSessionLocal
from app.database.models.processed_event import ProcessedEvent
from app.database.models.product import Product

from app.core.logging import logger

async def process_product_created(
    event_id: str,
    product_id: int,
) -> bool:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ProcessedEvent).where(
                ProcessedEvent.event_id == event_id
            )
        )

        processed_event = result.scalar_one_or_none()

        if processed_event is not None:
            logger.info(
                "event_already_processed",
                event_id=event_id,
            )
            return False

        result = await session.execute(
            select(Product).where(Product.id == product_id)
        )

        product = result.scalar_one_or_none()

        if product is None:
            raise ValueError(
                f"Product {product_id} not found"
            )

        data = {
            "id": product.id,
            "name": product.name,
            "price": str(product.price),
            "category_id": product.category_id,
        }

        await redis_client.set(
            f"product:{product.id}",
            json.dumps(data),
            ex=60,
        )

        session.add(
            ProcessedEvent(
                event_id=event_id,
            )
        )

        await session.commit()

        return True