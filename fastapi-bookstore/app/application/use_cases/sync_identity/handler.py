import logging

from app.application.ports.identity import IdentityProvider
from app.application.ports.repositories import UserRepository
from app.infrastructure.database import UnitOfWork

logger = logging.getLogger(__name__)

class SyncIdentityHandler:

    def __init__(
        self,
        provider: IdentityProvider,
        user_repo: UserRepository,
        uow: UnitOfWork,
    ):
        self.provider = provider
        self.user_repo = user_repo
        self.uow = uow

    async def handle(self, event: dict):
        logger.debug(f"Receiving event from queue: ID = {event["user_id"]}")
        provider_user_id = await self.provider.create_user(
            email=event["email"],
            first_name=event["first_name"],
            last_name=event["last_name"],
            phone=event["phone"]
        )

        self.user_repo.mark_as_synced(
            user_id=event["user_id"],
            ext_user_id=provider_user_id,
        )

        self.uow.commit()