
from app.domain.entities import User
from app.domain.events import UserCreated

from app.application.commands.register_user import RegisterUserCommand
from app.application.ports.repositories import UserRepository, OutboxRepository
from app.infrastructure.database import UnitOfWork
from app.core.metrics import track_execution_time


class RegisterUserHandler:

    def __init__(
        self,
        user_repo: UserRepository,
        outbox_repo: OutboxRepository,
        uow: UnitOfWork,
    ):
        self.user_repo = user_repo
        self.outbox_repo = outbox_repo
        self.uow = uow

    @track_execution_time
    def handle(
        self,
        command: RegisterUserCommand,
    ) -> str:

        user = User.create(
            email=command.email,
            first_name=command.first_name,
            last_name=command.last_name,
            phone=command.phone,
        )

        event = UserCreated(
            user_id=user.user_id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
        )

        with self.uow:
            self.user_repo.create(user)

            self.outbox_repo.add(
                event_type="user.created",
                payload=event.__dict__,
            )

            self.uow.commit()

        return user.user_id