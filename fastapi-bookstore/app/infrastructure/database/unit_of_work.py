from sqlalchemy.orm import Session


class UnitOfWork:

    def __init__(self, db: Session):
        self.session = db

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self.rollback()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()