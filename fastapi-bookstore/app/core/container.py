from dependency_injector import containers, providers
from sqlalchemy.orm import Session

from app.application.commands.register_user import RegisterUserHandler
from app.application.use_cases import CreateBookUseCase, FindBookUseCase, SearchBookUseCase, UpdateBookUseCase
from app.application.use_cases.process_outbox.handler import ProcessOutboxHandler
from app.application.use_cases.sync_identity.handler import SyncIdentityHandler
from app.configs import LoggingSettings, AuthSettings, DatabaseSettings
from app.core.database import DatabaseConfig
from app.core.logging_config import LoggingConfig
from app.infrastructure.database import UnitOfWork
from app.infrastructure.identity.okta import OktaSettings, OktaIdentityProvider
from app.infrastructure.messaging.rabbitmq import RabbitMQSettings, RabbitMQConnection, RabbitMQChannelFactory, \
    RabbitMQPublisher, RabbitMQConsumer
from app.infrastructure.repositories import OutboxRepositoryImpl, UserRepositoryImpl, BookRepositoryImpl, \
    AuthorRepositoryImpl, CategoryRepositoryImpl
from app.workers.outbox_worker import OutboxWorker


def get_db(config: DatabaseConfig) -> Session:
    yield from config.get_db()

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.v1.routes.user_router",
            "app.api.v1.routes.book_router",
            "app.api.v1.routes.auth_router"
        ]
    )
    config = providers.Configuration()

    logging_settings = providers.ThreadSafeSingleton(LoggingSettings)
    database_settings = providers.ThreadSafeSingleton(DatabaseSettings)
    authentication_settings = providers.ThreadSafeSingleton(AuthSettings)
    okta_settings = providers.ThreadSafeSingleton(OktaSettings)
    rabbitmq_settings = providers.ThreadSafeSingleton(RabbitMQSettings)

    logging_config = providers.Factory(
        LoggingConfig,
        settings=logging_settings,
    )

    database_config = providers.Factory(
        DatabaseConfig,
        settings=database_settings,
    )
    get_db = providers.Resource(get_db, config=database_config)
    uow = providers.Factory(UnitOfWork, db=get_db)

    outbox_repo = providers.Factory(OutboxRepositoryImpl, db=get_db)
    user_repo = providers.Factory(UserRepositoryImpl, db=get_db)
    book_repo = providers.Factory(BookRepositoryImpl, db=get_db)
    author_repo = providers.Factory(AuthorRepositoryImpl, db=get_db)
    category_repo = providers.Factory(CategoryRepositoryImpl, db=get_db)

    identity_provider = providers.Factory(OktaIdentityProvider, settings=okta_settings)
    sync_identity_handler = providers.Factory(SyncIdentityHandler, provider=identity_provider, user_repo=user_repo, uow=uow)

    rabbitmq_connection = providers.Factory(RabbitMQConnection, settings=rabbitmq_settings)
    rabbitmq_channel_factory = providers.Factory(RabbitMQChannelFactory, connection=rabbitmq_connection)

    event_publisher = providers.Factory(
        RabbitMQPublisher,
        channel_factory=rabbitmq_channel_factory,
        exchange_name=rabbitmq_settings.provided.exchange_name,
        queue_name=rabbitmq_settings.provided.queue_name,
    )
    event_consumer = providers.Factory(
        RabbitMQConsumer,
        channel_factory=rabbitmq_channel_factory,
        exchange_name=rabbitmq_settings.provided.exchange_name,
        queue_name=rabbitmq_settings.provided.queue_name,
        routing_key=rabbitmq_settings.provided.queue_name,
        handler=sync_identity_handler
    )

    create_book_use_case = providers.Factory(CreateBookUseCase, book_repo=book_repo, author_repo=author_repo, category_repo=category_repo)
    find_book_use_case = providers.Factory(FindBookUseCase, repo=book_repo)
    search_book_use_case = providers.Factory(SearchBookUseCase, repo=book_repo)
    update_book_use_case = providers.Factory(UpdateBookUseCase, book_repo=book_repo, author_repo=author_repo, category_repo=category_repo)

    register_user_handler = providers.Factory(
        RegisterUserHandler,
        user_repo=user_repo,
        outbox_repo=outbox_repo,
        uow=uow
    )
    process_outbox_handler = providers.Factory(
        ProcessOutboxHandler,
        outbox_repo=outbox_repo,
        publisher=event_publisher,
        uow=uow
    )

    outbox_worker = providers.Factory(OutboxWorker, handler=process_outbox_handler)


