from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, status

from app.core.dependencies import get_create_book_use_case, get_find_book_use_case, get_search_book_use_case, \
    get_update_book_use_case
from app.domain.entities import BookSearchCriteria
from app.schemas import BookRequest, CreateBookRequest
from app.user_cases import CreateBookUseCase, FindBookUseCase, SearchBookUseCase, UpdateBookUseCase

router = APIRouter()

'''
BOOKS = [
    Book(1, "Python Programming", "Code With Me", "Programming", 4, 2010),
    Book(2, "Terraform from scratch", "Code With Me", "Programming", 2, 2010),
    Book(3, "Python for Scientist", "Code With Me", "Programming", 5, 2022),
    Book(4, "Python for Beginners", "Code With Me", "Programming", 2, 2022),
    Book(5, "DevOps - An AI Approach", "Code With Me", "Programming", 2, 2025),
    Book(6, "Python and Pytorch", "Code With Me", "Programming", 4, 2019),
    Book(7, "C#", "Code With Me", "Programming", 2, 2018),
    Book(8, "Math for Machine Learning", "Lee", "Math", 4, 2025),
    Book(9, "Calculus for NN", "Lee", "Math", 1, 2009),
    Book(10, "C++", "Code With Me", "Programming", 4, 2009)
]
'''

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
async def read_books_by_author(author: str, search_book_service: SearchBookUseCase = Depends(get_search_book_use_case)):
    return search_book_service.execute(BookSearchCriteria(author=author))

@router.put("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book_id: int, request: BookRequest, update_book_service: UpdateBookUseCase = Depends(get_update_book_use_case)):
    update_book_service.execute(book_id, request)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0), update_book_service: UpdateBookUseCase = Depends(get_update_book_use_case)):
    pass

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: CreateBookRequest, create_book_service: CreateBookUseCase = Depends(get_create_book_use_case)):
    create_book_service.execute(book_request)
