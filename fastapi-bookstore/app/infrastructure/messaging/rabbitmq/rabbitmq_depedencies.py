from dependency_injector import containers, providers

from app.application.use_cases.process_outbox.handler import ProcessOutboxHandler
from app.application.use_cases.send_notification.handler import SendWelcomeNotificationHandler
from app.application.use_cases.sync_identity.handler import SyncIdentityHandler
from app.infrastructure.messaging.rabbitmq import RabbitMQSettings, RabbitMQConnection, RabbitMQChannelFactory, \
    RabbitMQPublisher, RabbitMQConsumer
from app.infrastructure.messaging.rabbitmq.runtime import ConsumerRegistry, BackgroundServiceRegistry
from app.infrastructure.messaging.rabbitmq.runtime.messaging_runtime import MessagingRuntime
from app.workers.outbox_worker import OutboxWorker


class RabbitMQContainer(containers.DeclarativeContainer):

    database_dependencies = providers.DependenciesContainer()
    sync_identity_handler = providers.Dependency(instance_of=SyncIdentityHandler)
    send_notification_handler = providers.Dependency(instance_of=SendWelcomeNotificationHandler)

    rabbitmq_settings = providers.ThreadSafeSingleton(RabbitMQSettings)

    rabbitmq_connection = providers.Factory(RabbitMQConnection, settings=rabbitmq_settings)
    rabbitmq_channel_factory = providers.Factory(RabbitMQChannelFactory, connection=rabbitmq_connection)

    event_publisher = providers.Factory(
        RabbitMQPublisher,
        channel_factory=rabbitmq_channel_factory,
        exchange_name=rabbitmq_settings.provided.exchange_name,
    )

    event_consumers = providers.List(
        providers.Factory(
            RabbitMQConsumer,
            channel_factory=rabbitmq_channel_factory,
            exchange_name=rabbitmq_settings.provided.exchange_name,
            queue_name=rabbitmq_settings.provided.registration_queue_name,
            routing_key="user.created",
            handler=sync_identity_handler
        ),
        providers.Factory(
            RabbitMQConsumer,
            channel_factory=rabbitmq_channel_factory,
            exchange_name=rabbitmq_settings.provided.exchange_name,
            queue_name=rabbitmq_settings.provided.notification_queue_name,
            routing_key="user.registration.completed",
            handler=send_notification_handler
        )
    )

    process_outbox_handler = providers.Factory(
        ProcessOutboxHandler,
        outbox_repo=database_dependencies.outbox_repo,
        publisher=event_publisher,
        uow=database_dependencies.uow
    )

    background_workers = providers.List(
        providers.Factory(
            OutboxWorker,
            handler=process_outbox_handler
        )
    )

    consumer_registry = providers.Factory(
        ConsumerRegistry,
        consumers=event_consumers
    )

    background_registry = providers.Factory(
        BackgroundServiceRegistry,
        services=background_workers
    )

    messaging_runtime = providers.Factory(
        MessagingRuntime,
        connection=rabbitmq_connection,
        consumer_registry=consumer_registry,
        background_registry=background_registry
    )
