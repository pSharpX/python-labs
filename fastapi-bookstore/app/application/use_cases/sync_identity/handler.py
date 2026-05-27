import logging

from app.application.ports.identity import IdentityProvider
from app.application.ports.messaging import MessageHandler
from app.application.ports.repositories import UserRepository, OutboxRepository
from app.infrastructure.database import UnitOfWork

logger = logging.getLogger(__name__)

class SyncIdentityHandler(MessageHandler):

    def __init__(
        self,
        provider: IdentityProvider,
        outbox_repo: OutboxRepository,
        user_repo: UserRepository,
        uow: UnitOfWork,
    ):
        self.provider = provider
        self.outbox_repo = outbox_repo
        self.user_repo = user_repo
        self.uow = uow

    async def handle(self, event: dict):
        logger.debug(f"Starting external user registration request: user_id = {event["user_id"]}")
        provider_user_id = await self.provider.create_user(
            email=event["email"],
            first_name=event["first_name"],
            last_name=event["last_name"],
            phone=event["phone"]
        )
        logger.debug(f"External user registration completed successfully: ext_user_id = {provider_user_id}")

        logger.debug("Updating user registration status in database")
        self.user_repo.mark_as_synced(
            user_id=event["user_id"],
            ext_user_id=provider_user_id,
        )
        logger.debug(f"User registration status updated successfully: user_id = {event['user_id']}")

        logger.debug("Adding  user.registration.completed event")
        self.outbox_repo.add(
            event_type="user.registration.completed",
            payload={
                "user_id": event["user_id"],
                "email": event["email"],
                "first_name": event["first_name"],
            },
        )

        self.uow.commit()