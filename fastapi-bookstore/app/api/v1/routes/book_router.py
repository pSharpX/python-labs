from typing import Optional

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Path, Query, status

from app.domain.entities import BookSearchCriteria
from app.schemas import BookRequest, CreateBookRequest
from app.application.use_cases import CreateBookUseCase, FindBookUseCase, SearchBookUseCase, UpdateBookUseCase
from app.core.container import Container

router = APIRouter()

@router.get("")
@inject
async def search_books(
        rating: Optional[int] = Query(None, ge=1, le=5),
        title: Optional[str] = Query(None, max_length=100),
        published_date: Optional[int] = Query(None, gt=1999, le=2031),
        search_book_service: SearchBookUseCase = Depends(Provide[Container.search_book_use_case])
):
    return search_book_service.execute(BookSearchCriteria(rating=rating, title=title, published_date=published_date))

@router.get("/publish/{published_date}")
@inject
async def read_books_by_published_date(
        published_date: int = Path(gt=0),
        search_book_service: SearchBookUseCase = Depends(Provide[Container.search_book_use_case])
):
    return search_book_service.execute(BookSearchCriteria(published_date=published_date))

@router.get("/{book_id}")
@inject
async def read_book_by_id(book_id: int = Path(gt=0), find_book_service: FindBookUseCase = Depends(Provide[Container.find_book_use_case])):
    return find_book_service.execute(book_id)

@router.get("/authors/{book_author}/")
@inject
async def read_books_by_author(book_author: str, search_book_service: SearchBookUseCase = Depends(Provide[Container.search_book_use_case])):
    return search_book_service.execute(BookSearchCriteria(author=book_author))

@router.put("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def update_book(
        book_id: int,
        request: BookRequest,
        update_book_service: UpdateBookUseCase = Depends(Provide[Container.update_book_use_case])
):
    update_book_service.execute(book_id, request)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_book(book_id: int = Path(gt=0), update_book_service: UpdateBookUseCase = Depends(Provide[Container.update_book_use_case])):
    pass

@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_book(book_request: CreateBookRequest, create_book_service: CreateBookUseCase = Depends(Provide[Container.create_book_use_case])):
    create_book_service.execute(book_request)
