import logging

from app.application.ports.messaging import EventPublisher
from app.application.ports.repositories import OutboxRepository
from app.infrastructure.database import UnitOfWork

logger = logging.getLogger(__name__)

class ProcessOutboxHandler:

    def __init__(
        self,
        outbox_repo: OutboxRepository,
        publisher: EventPublisher,
        uow: UnitOfWork,
    ):
        self.outbox_repo = outbox_repo
        self.publisher = publisher
        self.uow = uow

    async def handle(self):
        logger.debug(f"Running outbox processor")
        events = self.outbox_repo.get_unprocessed()

        for event in events:
            logger.info(f"Publishing event to queue: ID = {event.id}, EVENT_TYPE = {event.event_type}")
            await self.publisher.publish(
                topic=event.event_type,
                payload=event.payload,
            )

            self.outbox_repo.mark_processed(event.id)

        self.uow.commit()