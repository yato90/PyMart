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

from app.core.logging import logger
from app.core.metrics import (
    OUTBOX_EVENTS_FAILED_TOTAL,
    OUTBOX_EVENTS_PUBLISHED_TOTAL,
)
from prometheus_client import start_http_server

async def process_outbox() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(OutboxEvent)
            .where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.id)
            .with_for_update(skip_locked=True)
        )

        events = result.scalars().all()

        for outbox_event in events:
            outbox_id = outbox_event.id

            try:
                event = json.loads(outbox_event.payload)

                await publish_event(event)

                outbox_event.published_at = datetime.utcnow()

                await session.commit()

                OUTBOX_EVENTS_PUBLISHED_TOTAL.labels(
                    event_type=outbox_event.event_type,
                ).inc()

                logger.info(
                    "outbox_event_published",
                    outbox_id=outbox_id,
                    event_type=outbox_event.event_type,
                )

            except Exception as exc:
                await session.rollback()

                OUTBOX_EVENTS_FAILED_TOTAL.labels(
                    event_type=outbox_event.event_type,
                ).inc()

                logger.error(
                    "outbox_event_publish_failed",
                    outbox_id=outbox_id,
                    error=str(exc),
                )


async def main() -> None:
    while True:
        try:
            await start_producer()

            logger.info("kafka_producer_started")

            while True:
                await process_outbox()
                await asyncio.sleep(2)

        except Exception as exc:
            logger.error(
                "outbox_publisher_error",
                error=str(exc),
            )
            logger.info(
                "outbox_publisher_retrying",
                retry_in_seconds=5,
            )

            await asyncio.sleep(5)

        finally:
            await stop_producer()


if __name__ == "__main__":
    start_http_server(8001)
    asyncio.run(main())