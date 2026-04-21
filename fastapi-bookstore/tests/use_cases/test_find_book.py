import pytest
from app.domain.entities import Book, Category, Author
from app.use_cases import FindBookUseCase
from app.core.exceptions import BookNotFound

class TestFindBookUseCase:
    book_id: int = 5
    service: FindBookUseCase
    author: Author = Author(id=1, name="Test Author", fullname="Test Author")
    category: Category = Category(id=1, name="Test Category", description="Test Category")
    book: Book = Book(id=1, title="Test Book", description="Test Book", author=author, category=category, rating=5, published_date=2009)

    @pytest.fixture
    def mock_book_repository(self, mocker):
        return mocker.Mock()

    def test_find_book(self, mock_book_repository):
        mock_book_repository.get_by_id.return_value = self.book

        self.service = FindBookUseCase(mock_book_repository)
        existent_book = self.service.execute(self.book_id)

        assert existent_book is not None
        assert isinstance(existent_book, Book)
        assert existent_book.id is not None
        assert existent_book.title == self.book.title
        assert existent_book.description == self.book.description
        assert existent_book.rating == self.book.rating
        assert existent_book.published_date == self.book.published_date

        mock_book_repository.get_by_id.assert_called_once_with(self.book_id)

    def test_find_unexistent_book(self, mock_book_repository):
        mock_book_repository.get_by_id.side_effect = BookNotFound(f"{self.book_id}")

        self.service = FindBookUseCase(mock_book_repository)

        with pytest.raises(BookNotFound):
            self.service.execute(self.book_id)

        mock_book_repository.get_by_id.assert_called_once_with(self.book_id)