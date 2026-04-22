from typing import Optional, Any
from pydantic import BaseModel, Field

class CreateBookRequest(BaseModel):
    id: Optional[int] = Field(description="ID is not needed on Create", default=None)
    title: str = Field(min_length=3)
    description: Optional[str] = Field(default=None)
    author: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, le=5)
    published_date: int = Field(gt=1999, le=2031)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Software Development",
                "author": "coding_with_john",
                "category": "Programming",
                "rating": 4,
                "published_date": 1999,
            }
        }

class BookRequest(BaseModel):
    id: int = Field(description="ID is not needed on Create", default=None)
    title: str = Field(min_length=3)
    description: Optional[str] = Field(default=None)
    author: str = Field(min_length=2, max_length=100)
    category: str = Field(min_length=2, max_length=100)
    rating: int = Field(gt=0, le=5)
    published_date: int = Field(gt=1999, le=2031)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Software Development",
                "author": "coding_with_john",
                "category": "Programming",
                "rating": 4,
                "published_date": 1999,
            }
        }

class BookResponse(BaseModel):
    id: int
    title: str
    description: str
    author: str
    category: str
    rating: int
    published_date: int

    class Config:
        schema_extra = {
            "example": {
                "title": "Software Development",
                "author": "coding_with_john",
                "category": "Programming",
                "rating": 4,
                "published_date": 1999,
            }
        }

class BookSearchRequest(BaseModel):
    def __init__(self, /, title: Optional[str] = None, description: Optional[str] = None, author: Optional[str] = None,
                 category: Optional[str] = None, rating: Optional[int] = None, published_date: Optional[int] = None,
                 **data: Any):
        super().__init__(**data)
        self.title = title
        self.description = description
        self.author = author
        self.category = category
        self.rating = rating
        self.published_date = published_date