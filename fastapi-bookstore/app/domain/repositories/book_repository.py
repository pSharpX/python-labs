from abc import ABC, abstractmethod
from app.domain.entities import Book, BookSearchCriteria
from typing import List


class BookRepository(ABC):

    @abstractmethod
    def create(self, book: Book) -> Book:
        pass

    @abstractmethod
    def update(self, id: int, book: Book):
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Book | None:
        pass

    @abstractmethod
    def get_by_title(self, title: str) -> Book | None:
        pass

    @abstractmethod
    def search(self, criteria: BookSearchCriteria) -> List[Book] | None:
        pass

    @abstractmethod
    def get_all(self) -> List[Book] | None:
        pass