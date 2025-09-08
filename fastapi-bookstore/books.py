from fastapi import FastAPI
from Book import *
from BookRequest import *

app = FastAPI()

BOOKS = [
    Book(1, "Python Programming", "Code With Me", "Programming", 4),
    Book(2, "Terraform from scratch", "Code With Me", "Programming", 2),
    Book(3, "Python for Scientist", "Code With Me", "Programming", 5),
    Book(4, "Python for Beginners", "Code With Me", "Programming", 2),
    Book(5, "DevOps - An AI Approach", "Code With Me", "Programming", 2),
    Book(6, "Python and Pytorch", "Code With Me", "Programming", 4),
    Book(7, "C#", "Code With Me", "Programming", 2),
    Book(8, "Math for Machine Learning", "Lee", "Math", 4),
    Book(9, "Calculus for NN", "Lee", "Math", 1),
    Book(10, "C++", "Code With Me", "Programming", 4)
]

@app.get("/books")
async def read_all_books():
    return BOOKS

@app.get("/books/{book_title}")
async def read_book(book_title: str):
    print(book_title)
    for book in BOOKS:
        if book.get("title").casefold() == book_title.casefold():
            return book
    return None

@app.get("/books/{book_author}/")
async def read_books_by_author(author: str, category: str):
    included_books = []
    for book in BOOKS:
        if book.get("author").casefold() == author.casefold() and book.get("category").casefold() == category.casefold():
            included_books.append(book)
    return included_books

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
