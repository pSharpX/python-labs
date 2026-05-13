from app.infrastructure.messaging.rabbitmq import RabbitMQConnection


class RabbitMQChannelFactory:

    def __init__(self, connection: RabbitMQConnection):
        self.connection = connection

    async def create_channel(self):
        conn = await self.connection.connect()
        return await conn.channel()