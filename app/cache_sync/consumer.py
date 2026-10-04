import asyncio
import json
from typing import TypedDict

from aiokafka import AIOKafkaConsumer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.cache.redis import redis_client
from app.core.config import settings
from app.database.models.product import Product
from app.database.models.processed_event import ProcessedEvent

from app.cache_sync.handlers.category import (
    process_category_created,
    process_category_deleted,
)
from app.cache_sync.handlers.product import process_product_created

from app.core.logging import logger

class ProductEvent(TypedDict):
    event_id: str
    event: str
    product_id: int


def deserialize_event(value: bytes) -> ProductEvent:
    return json.loads(value.decode("utf-8"))


engine = create_async_engine(
    settings.database_url,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def consume() -> None:
    consumer = AIOKafkaConsumer(
        "product-events",
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id="cache-sync",
        value_deserializer=deserialize_event,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
    )

    await consumer.start()

    try:
        async for message in consumer:
            event = message.value

            if event is None:
                logger.warning(
                    "empty_message_skipped",
                    partition=message.partition,
                    offset=message.offset,
                )
                await consumer.commit()
                continue

            logger.info(
                "event_received",
                partition=message.partition,
                offset=message.offset,
                event_id=event["event_id"],
                event_type=event["event"],
                payload=event,
            )

            processed = False

            if event["event"] == "product.created":
                processed = await process_product_created(
                    event_id=event["event_id"],
                    product_id=event["product_id"],
                )
            elif event["event"] == "category.created":
                processed = await process_category_created(
                    event_id=event["event_id"],
                )
            elif event["event"] == "category.deleted":
                processed = await process_category_deleted(
                    event_id=event["event_id"],
                    category_id=event["category_id"],
                )

            await consumer.commit()

            if processed:
                logger.info(
                    "event_processed",
                    partition=message.partition,
                    offset=message.offset,
                    event_id=event["event_id"],
                )
            else:
                logger.info(
                    "event_skipped_duplicate",
                    partition=message.partition,
                    offset=message.offset,
                    event_id=event["event_id"],
                )

    finally:
        await consumer.stop()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(consume())
