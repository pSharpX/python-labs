from abc import ABC, abstractmethod


class EventConsumer(ABC):

    @abstractmethod
    async def on_message(self, message) -> None:
        pass