import logging

from app.application.ports.messaging import EventConsumer


logger = logging.getLogger(__name__)

class ConsumerRegistry:

    def __init__(self, consumers: list[EventConsumer]):
        self.consumers = consumers

    def register(self, consumer: EventConsumer):
        self.consumers.append(consumer)

    async def start_all(self):
        logger.info(f"Starting consumers: {len(self.consumers)}")
        for consumer in self.consumers:
            await consumer.start()