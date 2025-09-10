from fastapi import FastAPI, Path, Query
from Book import *
from BookRequest import *

app = FastAPI()

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

@app.get("/books")
async def read_all_books():
    return BOOKS

@app.get("/books/")
async def read_book_by_rating(book_rating: int = Query(ge=1, le=5)):
    included_books = []
    for book in BOOKS:
        if book.rating == book_rating:
            included_books.append(book)
    return included_books

@app.get("/books/publish/{published_date}")
async def read_books_by_published_date(published_date: int = Path(gt=0)):
    included_books = []
    for book in BOOKS:
        if book.published_date == published_date:
            included_books.append(book)
    return included_books

@app.get("/books/{book_title}")
async def read_book(book_title: str):
    for book in BOOKS:
        if book.title.casefold() == book_title.casefold():
            return book
    return None

@app.get("/books/{book_author}/")
async def read_books_by_author(author: str, category: str):
    included_books = []
    for book in BOOKS:
        if book.author.casefold() == author.casefold() and book.category.casefold() == category.casefold():
            included_books.append(book)
    return included_books

@app.put("/books")
async def update_book(book_request: BookRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_request.id:
            BOOKS[i] = Book(**book_request.model_dump())

@app.delete("/books/{book_id}")
async def delete_book(book_id: int = Path(gt=0)):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)

@app.post("/books")
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))

def find_book_id(book: Book):
    if len(BOOKS) > 0:
        book.id = BOOKS[-1].id + 1
    else:
        book.id = 1
    return book
