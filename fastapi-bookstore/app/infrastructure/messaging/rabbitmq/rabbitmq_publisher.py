import json
import aio_pika
from aio_pika import ExchangeType

from app.application.ports.messaging import EventPublisher
from app.infrastructure.messaging.rabbitmq import RabbitMQChannelFactory


class RabbitMQPublisher(EventPublisher):

    def __init__(
            self,
            channel_factory: RabbitMQChannelFactory,
            exchange_name: str,
    ):
        self.channel_factory = channel_factory
        self.exchange_name = exchange_name

    async def publish(self, topic: str, payload: dict):
        channel = await self.channel_factory.create_channel()
        exchange = await channel.declare_exchange(
            self.exchange_name,
            type=ExchangeType.DIRECT,
            durable=True,
            passive=True,
        )

        message = aio_pika.Message(
            body=json.dumps(payload).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await exchange.publish(
            message,
            routing_key=topic,
        )