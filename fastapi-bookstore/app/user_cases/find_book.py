from app.domain.entities import Book
from app.domain.repositories import BookRepository

class FindBookUseCase:
    def __init__(self, repo: BookRepository):
        self.repo = repo

    def execute(self, id: int) -> Book:
        return self.repo.get_by_id(id)