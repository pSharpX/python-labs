from typing import Optional
from pydantic import BaseModel, Field

class BookRequest(BaseModel):
    id: Optional[int] = Field(description="ID is not needed on Create", default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=2)
    category: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, le=5)

    class Config:
        schema_extra = {
            "example": {
                "title": "Software Development",
                "author": "codingwithjhon",
                "category": "Programming",
                "rating": 4
            }
        }