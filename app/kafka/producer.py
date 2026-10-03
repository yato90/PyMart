import json

from aiokafka import AIOKafkaProducer

from app.core.config import settings


producer: AIOKafkaProducer | None = None


async def start_producer() -> None:
    global producer

    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )

    await producer.start()


async def stop_producer() -> None:
    global producer

    if producer is not None:
        await producer.stop()
        producer = None


async def publish_event(event: dict) -> None:
    if producer is None:
        raise RuntimeError("Kafka producer is not started")

    await producer.send_and_wait(
        "product-events",
        value=event,
    )