from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.configs import DatabaseSettings

class DatabaseConfig:
    settings: DatabaseSettings
    engine: Engine
    SessionLocal = None
    Base = None

    def __init__(self, settings: DatabaseSettings):
        self.settings = settings
        self.engine = create_engine(self.settings.connection_url())
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        self.Base = declarative_base()

        self.Base.metadata.create_all(bind=self.engine)

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
