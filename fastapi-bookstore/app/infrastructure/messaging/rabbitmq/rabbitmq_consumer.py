import json
import logging

import aio_pika

from app.application.use_cases import SyncIdentityHandler
from app.infrastructure.messaging.rabbitmq import RabbitMQChannelFactory
from app.application.ports.messaging import EventConsumer

logger = logging.getLogger(__name__)

class RabbitMQConsumer(EventConsumer):

    def __init__(
        self,
        channel_factory: RabbitMQChannelFactory,
        exchange_name: str,
        queue_name: str,
        routing_key: str,
        handler: SyncIdentityHandler,
    ):
        self.channel_factory = channel_factory
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.handler = handler

    async def on_message(self, message: aio_pika.IncomingMessage):
        """Callable consumer function."""
        try:
            logger.info(f"Message received for processing: {message.body.decode()}")
            payload = json.loads(message.body)
            await self.handler.handle(payload)
            await message.ack()
            logger.info("Message processing completed")
        except Exception as exc:
            await message.reject(requeue=True)
            logger.error(f"Message processing failed: {type(exc).__name__}: {str(exc)}" )

    async def start(self):
        channel = await self.channel_factory.create_channel()
        queue = await channel.declare_queue(self.queue_name, durable=True)
        exchange = await channel.declare_exchange(
            self.exchange_name,
            durable=True,
        )

        await queue.bind(
            exchange,
            routing_key=self.routing_key,
        )

        await queue.consume(self.on_message)
