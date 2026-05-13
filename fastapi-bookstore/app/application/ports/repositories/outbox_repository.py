from abc import ABC, abstractmethod


class OutboxRepository(ABC):

    @abstractmethod
    def add(self, event_type: str, payload: dict) -> None:
        pass

    @abstractmethod
    def get_unprocessed(self) -> list:
        pass

    @abstractmethod
    def mark_processed(self, event_id: int) -> None:
        pass

