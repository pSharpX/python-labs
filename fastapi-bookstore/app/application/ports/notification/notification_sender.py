from abc import ABC, abstractmethod


class NotificationSender(ABC):

    @abstractmethod
    async def send_welcome_email(self, email: str, first_name: str) -> None:
        pass