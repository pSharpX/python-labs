from dependency_injector import containers, providers
from sqlalchemy.orm import Session

from app.configs import DatabaseSettings
from app.core.database import DatabaseConfig
from app.infrastructure.database import UnitOfWork
from app.infrastructure.repositories import OutboxRepositoryImpl, UserRepositoryImpl, BookRepositoryImpl, \
    AuthorRepositoryImpl, CategoryRepositoryImpl

def get_db(config: DatabaseConfig) -> Session:
    yield from config.get_db()


class SqlContainer(containers.DeclarativeContainer):

    database_settings = providers.ThreadSafeSingleton(DatabaseSettings)

    database_config = providers.Factory(
        DatabaseConfig,
        settings=database_settings,
    )
    get_db = providers.Resource(get_db, config=database_config)
    uow = providers.Factory(UnitOfWork, db=get_db)

    outbox_repo = providers.Factory(OutboxRepositoryImpl, db=get_db)
    user_repo = providers.Factory(UserRepositoryImpl, db=get_db)
    book_repo = providers.Factory(BookRepositoryImpl, db=get_db)
    author_repo = providers.Factory(AuthorRepositoryImpl, db=get_db)
    category_repo = providers.Factory(CategoryRepositoryImpl, db=get_db)
