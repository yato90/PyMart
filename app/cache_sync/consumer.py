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


async def process_product_created(product_id: int) -> None:
    async with AsyncSessionLocal() as session:
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
                print(
                    f"Skipping empty message: "
                    f"partition={message.partition}, "
                    f"offset={message.offset}"
                )
                await consumer.commit()
                continue

            print(
                f"Received event: "
                f"partition={message.partition}, "
                f"offset={message.offset}, "
                f"value={event}"
            )

            if event["event"] == "product.created":
                await process_product_created(
                    product_id=event["product_id"],
                )

            await consumer.commit()

            print(
                f"Processed successfully: "
                f"partition={message.partition}, "
                f"offset={message.offset}"
            )

    finally:
        await consumer.stop()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(consume())
