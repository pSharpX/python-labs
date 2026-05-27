from abc import ABC, abstractmethod


class MessageHandler(ABC):

    @abstractmethod
    async def handle(
            self,
            payload: dict,
    ) -> None:
        pass