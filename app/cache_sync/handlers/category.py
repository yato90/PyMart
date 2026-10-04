from sqlalchemy import select

from app.cache.redis import redis_client
from app.database.connection import AsyncSessionLocal
from app.database.models.processed_event import ProcessedEvent

from app.core.logging import logger


async def process_category_created(
    event_id: str,
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
                event_type="category.created",
            )
            return False

        await redis_client.delete("categories:all")

        logger.info(
            "category_cache_invalidated",
            event_id=event_id,
            cache_key="categories:all",
        )

        session.add(
            ProcessedEvent(
                event_id=event_id,
            )
        )

        await session.commit()

        return True