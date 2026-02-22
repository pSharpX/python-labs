from sqlalchemy.orm import Session
from app.domain.entities import Author
from app.domain.repositories import AuthorRepository
from app.infrastructure.models import AuthorModel

class AuthorRepositoryImpl(AuthorRepository):

    def __init__(self, db: Session):
        self.db = db

    def create(self, author: Author) -> Author:
        db_author = AuthorModel(name=author.name, fullname=author.fullname)
        self.db.add(db_author)
        self.db.commit()
        self.db.refresh(db_author)

        return Author(id=db_author.id, name=db_author.name, fullname=db_author.fullname)

    def get_by_id(self, author_id: int):
        db_author = self.db.query(AuthorModel).filter_by(id = id).first()
        if not db_author:
            return None
        return Author(id=db_author.id, name=db_author.name, fullname=db_author.fullname)
