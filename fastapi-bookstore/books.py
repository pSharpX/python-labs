from fastapi import FastAPI

app = FastAPI()

BOOKS = [
    { "title": "Python Programming", "author": "Code With Me", "category": "Programming" },
    { "title": "Terraform from scratch", "author": "Code With Me", "category": "Programming" },
    { "title": "Python for Scientist", "author": "Code With Me", "category": "Programming" },
    { "title": "Python for Beginners", "author": "Code With Me", "category": "Programming" },
    { "title": "DevOps - An AI Approach", "author": "Code With Me", "category": "Programming" },
    { "title": "Python and Pytorch", "author": "Code With Me", "category": "Programming" },
    { "title": "C#", "author": "Code With Me", "category": "Programming" },
    { "title": "Visual Basic 2025", "author": "Code With Me", "category": "Programming" },
    { "title": "Java Eloquent", "author": "Code With Me", "category": "Programming" },
    { "title": "C++", "author": "Code With Me", "category": "Programming" },
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