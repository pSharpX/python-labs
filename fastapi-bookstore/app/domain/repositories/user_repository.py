from abc import ABC, abstractmethod
from app.domain.entities import User


class UserRepository(ABC):

    @abstractmethod
    def create(self, user: User) -> User:
        pass

    @abstractmethod
    def update(self, id: int, user: User):
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> User:
        pass

    @abstractmethod
    def get_by_ext_user_id(self, ext_user_id: str) -> User | None:
        pass
