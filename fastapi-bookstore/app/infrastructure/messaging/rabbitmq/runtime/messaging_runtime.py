from app.infrastructure.messaging.rabbitmq.runtime.background_service_registry import BackgroundServiceRegistry
from app.infrastructure.messaging.rabbitmq.runtime.consumer_registry import ConsumerRegistry


class MessagingRuntime:

    def __init__(
        self,
        connection,
        consumer_registry: ConsumerRegistry,
        background_registry: BackgroundServiceRegistry,
    ):
        self.connection = connection
        self.consumer_registry = (
            consumer_registry
        )
        self.background_registry = (
            background_registry
        )

    async def start(self):
        await self.connection.connect()
        await self.consumer_registry.start_all()
        await self.background_registry.start_all()

    async def stop(self):
        await self.background_registry.stop_all()
        await self.connection.close()