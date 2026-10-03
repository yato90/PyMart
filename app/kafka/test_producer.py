import asyncio

from app.kafka.producer import (
    publish_product_event,
    start_producer,
    stop_producer,
)


async def main():
    await start_producer()

    try:
        await publish_product_event(
            event_type="product.created",
            product_id=123,
        )
    finally:
        await stop_producer()


if __name__ == "__main__":
    asyncio.run(main())