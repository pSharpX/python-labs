from datetime import datetime
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, String, Float, DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from models.BaseModel import BaseModel

class BookModel(BaseModel):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    rating: Mapped[float] = mapped_column(Float)
    published_date: Mapped[datetime] = mapped_column(DateTime)

    author_id: Mapped[int] = mapped_column(ForeignKey('authors.id'))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

    #author: Mapped["AuthorModel"] = relationship(back_populates="AuthorModel")