from app.application.ports.messaging import EventConsumer


class ConsumerRegistry:

    def __init__(self, consumers: list[EventConsumer]):
        self.consumers = consumers

    def register(self, consumer: EventConsumer):
        self.consumers.append(consumer)

    async def start_all(self):
        for consumer in self.consumers:
            await consumer.start()