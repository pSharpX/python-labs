from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domain.repositories import BookRepository, AuthorRepository, CategoryRepository
from app.infrastructure.repositories import BookRepositoryImpl, AuthorRepositoryImpl, CategoryRepositoryImpl

from app.use_cases import CreateBookUseCase, FindBookUseCase, SearchBookUseCase, UpdateBookUseCase

def get_book_repo_impl(db: Session = Depends(get_db)) -> BookRepository:
    return BookRepositoryImpl(db)

def get_author_repo_impl(db: Session = Depends(get_db)) -> AuthorRepository:
    return AuthorRepositoryImpl(db)

def get_category_repo_impl(db: Session = Depends(get_db)) -> CategoryRepository:
    return CategoryRepositoryImpl(db)

def get_create_book_use_case(
        book_repo: BookRepository = Depends(get_book_repo_impl),
        author_repo: AuthorRepository = Depends(get_author_repo_impl),
        category_repo: CategoryRepository = Depends(get_category_repo_impl),
) -> CreateBookUseCase:
    return CreateBookUseCase(book_repo=book_repo, author_repo=author_repo, category_repo=category_repo)

def get_find_book_use_case(repo: BookRepository = Depends(get_book_repo_impl)) -> FindBookUseCase:
    return FindBookUseCase(repo=repo)

def get_search_book_use_case(repo: BookRepository = Depends(get_book_repo_impl)) -> SearchBookUseCase:
    return SearchBookUseCase(repo=repo)

def get_update_book_use_case(
        book_repo: BookRepository = Depends(get_book_repo_impl),
        author_repo: AuthorRepository = Depends(get_author_repo_impl),
        category_repo: CategoryRepository = Depends(get_category_repo_impl),
) -> UpdateBookUseCase:
    return UpdateBookUseCase(book_repo=book_repo, author_repo=author_repo, category_repo=category_repo)