from typing import List
from app.domain.entities import Book, BookSearchCriteria
from app.domain.repositories import BookRepository

class SearchBookUseCase:
    def __init__(self, repo: BookRepository):
        self.repo = repo

    def execute(self, criteria: BookSearchCriteria) -> List[Book]:
        return self.repo.search(criteria)