from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, status

from app.core.dependencies import get_create_book_use_case, get_find_book_use_case, get_search_book_use_case, \
    get_update_book_use_case
from app.domain.entities import BookSearchCriteria
from app.schemas import BookRequest, CreateBookRequest
from app.use_cases import CreateBookUseCase, FindBookUseCase, SearchBookUseCase, UpdateBookUseCase

router = APIRouter()

@router.get("/")
async def search_books(
        rating: Optional[int] = Query(None, ge=1, le=5),
        title: Optional[str] = Query(None, max_length=2000),
        published_date: Optional[int] = Query(None, ge=1),
        search_book_service: SearchBookUseCase = Depends(get_search_book_use_case)):
    return search_book_service.execute(BookSearchCriteria(rating=rating, title=title, published_date=published_date))

@router.get("/publish/{published_date}")
async def read_books_by_published_date(published_date: int = Path(gt=0), search_book_service: SearchBookUseCase = Depends(get_search_book_use_case)):
    return search_book_service.execute(BookSearchCriteria(published_date=published_date))

@router.get("/{book_id}")
async def read_by_book_id(book_id: int = Path(gt=0), find_book_service: FindBookUseCase = Depends(get_find_book_use_case)):
    return find_book_service.execute(book_id)

@router.get("/authors/{book_author}/")
async def read_books_by_author(book_author: str, search_book_service: SearchBookUseCase = Depends(get_search_book_use_case)):
    return search_book_service.execute(BookSearchCriteria(author=book_author))

@router.put("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book_id: int, request: BookRequest, update_book_service: UpdateBookUseCase = Depends(get_update_book_use_case)):
    update_book_service.execute(book_id, request)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0), update_book_service: UpdateBookUseCase = Depends(get_update_book_use_case)):
    pass

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: CreateBookRequest, create_book_service: CreateBookUseCase = Depends(get_create_book_use_case)):
    create_book_service.execute(book_request)
