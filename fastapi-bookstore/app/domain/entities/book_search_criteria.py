from dataclasses import dataclass
from typing import Optional

@dataclass
class BookSearchCriteria:
    def __init__(
            self,
            title: Optional[str] = None,
            description: Optional[str] = None,
            author: Optional[str] = None,
            category: Optional[str] = None,
            rating: Optional[int] = None,
            published_date: Optional[int] = None,
    ):
        self.title = title
        self.description = description
        self.author = author
        self.category = category
        self.rating = rating
        self.published_date = published_date