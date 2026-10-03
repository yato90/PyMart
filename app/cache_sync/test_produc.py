import asyncio
import json

from aiokafka import AIOKafkaProducer


async def main():
    producer = AIOKafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )

    await producer.start()

    try:
        await producer.send_and_wait(
            "product-events",
            value={
                "event_id": "1ad11fa5-f55f-4a7a-8cb2-40bc95092bde",
                "event": "product.created",
                "product_id": 100010,
            },
        )
    finally:
        await producer.stop()


asyncio.run(main())