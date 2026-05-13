from abc import ABC, abstractmethod


class IdentityProvider(ABC):

    @abstractmethod
    async def create_user(self, email: str, first_name: str, last_name: str, phone: str) -> str:
        pass

