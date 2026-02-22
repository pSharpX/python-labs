from abc import ABC, abstractmethod
from app.domain.entities import Category

class CategoryRepository(ABC):

    @abstractmethod
    def create(self, category: Category) -> Category:
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> Category | None:
        pass
