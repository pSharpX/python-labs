import json
import aio_pika

from app.application.ports.messaging import EventPublisher
from app.infrastructure.messaging.rabbitmq import RabbitMQChannelFactory


class RabbitMQPublisher(EventPublisher):

    def __init__(
            self,
            channel_factory: RabbitMQChannelFactory,
            exchange_name: str,
            queue_name: str,
    ):
        self.channel_factory = channel_factory
        self.exchange_name = exchange_name
        self.queue_name = queue_name

    async def publish(self, topic: str, payload: dict):
        channel = await self.channel_factory.create_channel()
        await channel.declare_queue(self.queue_name, durable=True)
        exchange = await channel.declare_exchange(
            self.exchange_name,
            durable=True,
        )

        message = aio_pika.Message(
            body=json.dumps(payload).encode(),
        )
        await exchange.publish(
            message,
            routing_key=self.queue_name,
        )