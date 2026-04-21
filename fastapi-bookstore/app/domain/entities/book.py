from dataclasses import dataclass
from app.domain.entities.author import Author
from app.domain.entities.category import Category

@dataclass
class Book:
    id: int
    title: str
    description: str | None
    author: Author | None
    category: Category | None
    rating: int
    published_date: int

    def __init__(self, id, title: str, description: str | None, author: Author | None, category: Category | None, rating: int, published_date: int):
        self.id = id
        self.title = title
        self.description = description
        self.author = author
        self.category = category
        self.rating = rating
        self.published_date = published_date