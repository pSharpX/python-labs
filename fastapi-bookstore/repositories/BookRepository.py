from sqlalchemy.orm import Session
from models.BookModel import BookModel

def get_all_books(db: Session):
    return db.query(BookModel).all()