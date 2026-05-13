from abc import ABC, abstractmethod
from app.domain.entities import Author

class AuthorRepository(ABC):

    @abstractmethod
    def create(self, author: Author) -> Author:
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> Author | None:
        pass
