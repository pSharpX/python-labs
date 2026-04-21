from app.core.metrics import track_execution_time
from app.domain.entities import Book, Author, Category
from app.domain.repositories import BookRepository, AuthorRepository, CategoryRepository
from app.schemas import BookRequest

class UpdateBookUseCase:
    def __init__(self, book_repo: BookRepository, author_repo: AuthorRepository, category_repo: CategoryRepository):
        self.book_repo = book_repo
        self.author_repo = author_repo
        self.category_repo = category_repo

    @track_execution_time
    def execute(self, id: int, request: BookRequest):
        author_existing = self.author_repo.get_by_id(request.author)
        if not author_existing:
            raise ValueError("Author is invalid")

        category_existing = self.category_repo.get_by_id(request.category)
        if not category_existing:
            raise ValueError("Category is invalid")

        new_book = Book(
            id=id,
            title=request.title,
            description=request.description,
            author=Author(id=author_existing.id, name=author_existing.name, fullname=author_existing.fullname),
            category=Category(id=category_existing.id, name=category_existing.name,
                              description=category_existing.description),
            rating=request.rating,
            published_date=request.published_date)
        self.book_repo.update(id, new_book)