import asyncio
import json
from datetime import datetime

from sqlalchemy import select

from app.database.connection import AsyncSessionLocal
from app.database.models.outbox_event import OutboxEvent
from app.kafka.producer import (
    publish_event,
    start_producer,
    stop_producer,
)


async def process_outbox() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(OutboxEvent)
            .where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.id)
        )

        events = result.scalars().all()

        for outbox_event in events:
            try:
                event = json.loads(outbox_event.payload)

                await publish_event(event)

                outbox_event.published_at = datetime.utcnow()

                await session.commit()

                print(
                    f"Published outbox event: "
                    f"id={outbox_event.id}, "
                    f"type={outbox_event.event_type}"
                )

            except Exception as exc:
                await session.rollback()

                print(
                    f"Failed to publish outbox event: "
                    f"id={outbox_event.id}, "
                    f"error={exc}"
                )


async def main() -> None:
    while True:
        try:
            await start_producer()

            print("Kafka producer started")

            while True:
                await process_outbox()
                await asyncio.sleep(2)

        except Exception as exc:
            print(f"Outbox publisher error: {exc}")
            print("Retrying in 5 seconds...")

            await asyncio.sleep(5)

        finally:
            await stop_producer()


if __name__ == "__main__":
    asyncio.run(main())