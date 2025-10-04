from sqlalchemy.orm import Session
from models.BookModel import BookModel

def get_all_books(db: Session):
    return db.query(BookModel).all()

def find_by_id(db: Session, book_id: int):
    return  db.query(BookModel).filter(BookModel.id == book_id).first()

def find_by_title(db: Session, title: str):
    return db.query(BookModel).filter(BookModel.title == title).first()