import aio_pika

from app.infrastructure.messaging.rabbitmq import RabbitMQSettings


class RabbitMQConnection:

    def __init__(self, settings: RabbitMQSettings):
        self.settings = settings
        self._connection = None

    async def connect(self):
        if not self._connection:
            self._connection = (
                await aio_pika.connect_robust(
                    self.settings.connection_string
                )
            )

        return self._connection

    async def close(self):
        if self._connection:
            await self._connection.close()