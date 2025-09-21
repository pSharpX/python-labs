from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from configs.DatabaseSettings import settings

engine = create_engine(settings.connection_url())

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)