from dependency_injector import containers, providers

from app.application.commands.register_user import RegisterUserHandler
from app.application.use_cases import CreateBookUseCase, FindBookUseCase, SearchBookUseCase, UpdateBookUseCase
from app.application.use_cases.sync_identity.handler import SyncIdentityHandler
from app.application.use_cases.send_notification.handler import SendWelcomeNotificationHandler
from app.configs import LoggingSettings, AuthSettings, MainSettings
from app.core.logging_config import LoggingConfig
from app.infrastructure.identity import IdentityContainer
from app.infrastructure.notification.mailchimp import MailchimpContainer
from app.infrastructure.messaging.rabbitmq import RabbitMQContainer
from app.infrastructure.repositories.sql_dependencies import SqlContainer


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.v1.routes.user_router",
            "app.api.v1.routes.book_router",
            "app.api.v1.routes.auth_router"
        ]
    )
    config = providers.Configuration()

    main_settings = providers.ThreadSafeSingleton(MainSettings)
    logging_settings = providers.ThreadSafeSingleton(LoggingSettings)
    authentication_settings = providers.ThreadSafeSingleton(AuthSettings)

    logging_config = providers.Factory(
        LoggingConfig,
        settings=logging_settings,
    )

    database_dependencies = providers.Container(SqlContainer)
    identity_dependencies = providers.Container(
        IdentityContainer,
        settings=main_settings
    )
    notification_dependencies = providers.Container(MailchimpContainer)

    sync_identity_handler = providers.Factory(
        SyncIdentityHandler,
        provider=identity_dependencies.identity_provider,
        outbox_repo=database_dependencies.outbox_repo,
        user_repo=database_dependencies.user_repo,
        uow=database_dependencies.uow
    )
    send_notification_handler = providers.Factory(
        SendWelcomeNotificationHandler,
        notification_sender=notification_dependencies.notification_sender
    )

    messaging_dependencies = providers.Container(
        RabbitMQContainer,
        database_dependencies=database_dependencies,
        sync_identity_handler=sync_identity_handler,
        send_notification_handler=send_notification_handler,
    )

    create_book_use_case = providers.Factory(
        CreateBookUseCase,
        book_repo=database_dependencies.book_repo,
        author_repo=database_dependencies.author_repo,
        category_repo=database_dependencies.category_repo
    )
    find_book_use_case = providers.Factory(
        FindBookUseCase,
        repo=database_dependencies.book_repo
    )
    search_book_use_case = providers.Factory(
        SearchBookUseCase,
        repo=database_dependencies.book_repo
    )
    update_book_use_case = providers.Factory(
        UpdateBookUseCase,
        book_repo=database_dependencies.book_repo,
        author_repo=database_dependencies.author_repo,
        category_repo=database_dependencies.category_repo
    )

    register_user_handler = providers.Factory(
        RegisterUserHandler,
        user_repo=database_dependencies.user_repo,
        outbox_repo=database_dependencies.outbox_repo,
        uow=database_dependencies.uow
    )
