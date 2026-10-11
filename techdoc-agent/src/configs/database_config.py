from __future__ import annotations


from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from settings import DatabaseSettings

# Default to PostgreSQL async URL format; can be overridden via environment variable
db_settings = DatabaseSettings()

# Create the asynchronous SQLAlchemy engine
async_engine = create_async_engine(
    db_settings.url,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Session factory for generating async sessions
async_session_maker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncSession:
    """Dependency provider for FastAPI or service layer to obtain an async session."""
    async with async_session_maker() as session:
        yield session