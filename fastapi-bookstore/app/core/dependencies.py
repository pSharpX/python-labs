from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.configs import DatabaseSettings, LoggingSettings, AuthSettings
from app.core.database import DatabaseConfig
from app.core.logging_config import LoggingConfig
from app.application.ports.repositories import BookRepository, AuthorRepository, CategoryRepository, OutboxRepository, UserRepository
from app.application.use_cases import CreateBookUseCase, FindBookUseCase, SearchBookUseCase, UpdateBookUseCase
from app.application.commands.register_user import RegisterUserHandler
from app.application.ports.identity import IdentityProvider
from app.application.ports.messaging import EventPublisher, EventConsumer
from app.application.use_cases.process_outbox.handler import ProcessOutboxHandler
from app.application.use_cases.sync_identity.handler import SyncIdentityHandler
from app.infrastructure.database import UnitOfWork
from app.infrastructure.repositories import BookRepositoryImpl, AuthorRepositoryImpl, CategoryRepositoryImpl, OutboxRepositoryImpl, UserRepositoryImpl
from app.infrastructure.identity.okta import OktaSettings, OktaIdentityProvider
from app.infrastructure.messaging.rabbitmq import RabbitMQPublisher, RabbitMQConsumer, RabbitMQConnection, RabbitMQSettings, \
    RabbitMQChannelFactory


def get_logging_settings() -> LoggingSettings:
    return LoggingSettings()

def get_logging_config(settings: LoggingSettings = Depends(get_logging_settings)) -> LoggingConfig:
    return LoggingConfig(settings=settings)

def get_authentication_settings() -> AuthSettings:
    return AuthSettings()

def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()

def get_database_config(settings: DatabaseSettings = Depends(get_database_settings)) -> DatabaseConfig:
    return DatabaseConfig(settings=settings)

def get_db(config: DatabaseConfig = Depends(get_database_config)) -> Session:
    yield from config.get_db()

def get_uow(db: Session = Depends(get_db)) -> UnitOfWork:
    return UnitOfWork(db)

def get_outbox_repo_impl(db: Session = Depends(get_db)) -> OutboxRepository:
    return OutboxRepositoryImpl(db)

def get_user_repo_impl(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepositoryImpl(db)

def get_book_repo_impl(db: Session = Depends(get_db)) -> BookRepository:
    return BookRepositoryImpl(db)

def get_author_repo_impl(db: Session = Depends(get_db)) -> AuthorRepository:
    return AuthorRepositoryImpl(db)

def get_category_repo_impl(db: Session = Depends(get_db)) -> CategoryRepository:
    return CategoryRepositoryImpl(db)

def get_okta_settings() -> OktaSettings:
    return OktaSettings()

def get_okta_identity_provider_impl(settings: OktaSettings = Depends(get_okta_settings)) -> IdentityProvider:
    return OktaIdentityProvider(settings)

def get_sync_identity_handler(
        identity_provider: IdentityProvider = Depends(get_okta_identity_provider_impl),
        user_repo: UserRepository = Depends(get_user_repo_impl),
        uow: UnitOfWork = Depends(get_uow)
) -> SyncIdentityHandler:
    return SyncIdentityHandler(provider=identity_provider, user_repo=user_repo, uow=uow)

#def get_rabbitmq_settings() -> RabbitMQSettings:
#    return RabbitMQSettings()

def get_rabbitmq_settings(request: Request) -> RabbitMQSettings:
    return request.state.rabbitmq_settings

#def get_rabbitmq_connection(settings: RabbitMQSettings = Depends(get_rabbitmq_settings)) -> RabbitMQConnection:
#    return RabbitMQConnection(settings)

def get_rabbitmq_connection(request: Request) -> RabbitMQConnection:
    return request.state.rabbitmq_connection

def get_rabbitmq_channel_factory(connection: RabbitMQConnection = Depends(get_rabbitmq_connection)) -> RabbitMQChannelFactory:
    return RabbitMQChannelFactory(connection)

def get_event_publisher_impl(
        channel_factory: RabbitMQChannelFactory = Depends(get_rabbitmq_channel_factory),
        settings: RabbitMQSettings = Depends(get_rabbitmq_settings)
) -> EventPublisher:
    return RabbitMQPublisher(channel_factory, exchange_name=settings.exchange_name, queue_name="")

def get_event_consumer_impl(
        channel_factory: RabbitMQChannelFactory = Depends(get_rabbitmq_channel_factory),
        settings: RabbitMQSettings = Depends(get_rabbitmq_settings),
        handler: SyncIdentityHandler = Depends(get_sync_identity_handler),
) -> EventConsumer:
    return RabbitMQConsumer(channel_factory, exchange_name=settings.exchange_name, queue_name="", routing_key="", handler=handler)

def get_create_book_use_case(
        book_repo: BookRepository = Depends(get_book_repo_impl),
        author_repo: AuthorRepository = Depends(get_author_repo_impl),
        category_repo: CategoryRepository = Depends(get_category_repo_impl),
) -> CreateBookUseCase:
    return CreateBookUseCase(book_repo=book_repo, author_repo=author_repo, category_repo=category_repo)

def get_find_book_use_case(repo: BookRepository = Depends(get_book_repo_impl)) -> FindBookUseCase:
    return FindBookUseCase(repo=repo)

def get_search_book_use_case(repo: BookRepository = Depends(get_book_repo_impl)) -> SearchBookUseCase:
    return SearchBookUseCase(repo=repo)

def get_update_book_use_case(
        book_repo: BookRepository = Depends(get_book_repo_impl),
        author_repo: AuthorRepository = Depends(get_author_repo_impl),
        category_repo: CategoryRepository = Depends(get_category_repo_impl),
) -> UpdateBookUseCase:
    return UpdateBookUseCase(book_repo=book_repo, author_repo=author_repo, category_repo=category_repo)

def get_register_user_handler(
        user_repo: UserRepository = Depends(get_user_repo_impl),
        outbox_repo: OutboxRepository = Depends(get_outbox_repo_impl),
        uow: UnitOfWork = Depends(get_uow)
) -> RegisterUserHandler:
    return RegisterUserHandler(user_repo=user_repo, outbox_repo=outbox_repo, uow=uow)

def get_process_outbox_handler(
        outbox_repo: OutboxRepository = Depends(get_outbox_repo_impl),
        publisher: EventPublisher = Depends(get_event_publisher_impl),
        uow: UnitOfWork = Depends(get_uow)
) -> ProcessOutboxHandler:
    return ProcessOutboxHandler(outbox_repo=outbox_repo, publisher=publisher, uow=uow)
