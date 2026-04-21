from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import and_

from app.core.exceptions import BookNotFound
from app.domain.entities import Book, BookSearchCriteria
from app.domain.repositories import BookRepository
from app.infrastructure.models import BookModel

class BookRepositoryImpl(BookRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, book: Book) -> Book:
        db_book = BookModel(title=book.title, description=book.description, rating=book.rating, published_date=book.published_date, author_id=book.author.id, category_id=book.category.id)
        self.db.add(db_book)
        self.db.commit()
        self.db.refresh(db_book)

        return Book(id=db_book.id, title=db_book.title, description=db_book.description, rating=db_book.rating, published_date=db_book.published_date, author=book.author, category=book.category)

    def update(self, id: int, book: Book):
        db_book = self.db.query(BookModel).filter_by(id=id).first()
        if not db_book:
            return
        db_book.title = book.title
        db_book.description = book.description
        db_book.rating = book.rating
        db_book.published_date = book.published_date

        self.db.commit()
        self.db.refresh(db_book)

    def get_all(self):
        return self.db.query(BookModel).all()

    def get_by_id(self, book_id: int):
        db_book = self.db.query(BookModel).filter_by(id = book_id).first()
        if not db_book:
            raise BookNotFound(f"{book_id}")
        return Book(id=db_book.id, title=db_book.title, description=db_book.description, rating=db_book.rating, published_date=db_book.published_date, author=None, category=None)

    def get_by_title(self, title: str):
        db_book = self.db.query(BookModel).filter(BookModel.title == title).first()
        if not db_book:
            return None
        return Book(id=db_book.id, title=db_book.title, description=db_book.description, rating=db_book.rating, published_date=db_book.published_date)

    def search(self, criteria: BookSearchCriteria) -> List[Book]:
        query = self.db.query(BookModel)
        filters = []

        if criteria.title:
            filters.append(BookModel.title.ilike(f"%{criteria.title}%"))
        if criteria.description:
            filters.append(BookModel.description.ilike(f"%{criteria.description}%"))
        if criteria.rating:
            filters.append(BookModel.rating == criteria.rating)
        if criteria.published_date:
            filters.append(BookModel.published_date == criteria.published_date)

        if filters:
            query = query.filter(and_(*filters))

        results = query.all()
        return [
            Book(id=db_book.id, title=db_book.title, description=db_book.description, rating=db_book.rating, published_date=db_book.published_date, author=None, category=None)
            for db_book in results
        ]
