from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session, Session
from app.configs import DatabaseSettings

Base = declarative_base()

class DatabaseConfig:
    def __init__(self, settings: DatabaseSettings):
        self._settings = settings
        self._engine = create_engine(self._settings.connection_url())
        self._session_factory = scoped_session(sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False
        ))
        self.create_database()

    def create_database(self) -> None:
        Base.metadata.create_all(self._engine)

    def get_db(self):
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
