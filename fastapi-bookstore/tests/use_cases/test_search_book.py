import pytest
from unittest.mock import Mock
from app.domain.entities import Book, Category, Author, BookSearchCriteria
from app.domain.repositories import BookRepository
from app.infrastructure.models import AuthorModel, CategoryModel, BookModel
from app.infrastructure.repositories import BookRepositoryImpl
from app.use_cases import SearchBookUseCase

class TestSearchBookUseCase:
    mock_session = Mock()
    repository: BookRepository = BookRepositoryImpl(mock_session)
    service: SearchBookUseCase = SearchBookUseCase(repository)
    author: Author = Author(id=1, name="Test Author", fullname="Test Author")
    category: Category = Category(id=1, name="Test Category", description="Test Category")
    book: Book = Book(id=1, title="Test Book", description="Test Book", author=author, category=category, rating=5, published_date=2009)
    author_model: AuthorModel = AuthorModel(id=1, name="Test Author", fullname="Test Author")
    category_model: CategoryModel = CategoryModel(id=1, name="Test Category", description="Test Category")
    book_model: BookModel = BookModel(id=1, title="Test Book", description="Test Book", author=author_model, category=category_model, rating=5,
                      published_date=2009)

    @pytest.fixture
    def mock_book_repository(self, mocker):
        return mocker.Mock()

    def test_search_book(self, mock_book_repository):
        criteria: BookSearchCriteria = BookSearchCriteria(title="Test Book", rating=5, published_date=2009, author="Test Author", category="Test Category")
        mock_book_repository.search.return_value = [self.book]

        self.service = SearchBookUseCase(mock_book_repository)
        results = self.service.execute(criteria)

        assert results is not None
        assert isinstance(results, list)
        assert len(results) == 1
        assert isinstance(results[0], Book)
        assert results[0].title == self.book.title
        assert results[0].description == self.book.description

        mock_book_repository.search.assert_called_once_with(criteria)

    def test_search_book_by_title(self, mocker):
        mock_query = mocker.Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [self.book_model]

        criteria: BookSearchCriteria = BookSearchCriteria(title="Test Book")

        spy = mocker.spy(self.repository, 'search')
        results = self.service.execute(criteria)

        assert results is not None
        assert isinstance(results, list)
        assert len(results) == 1
        assert isinstance(results[0], Book)

        spy.assert_called_once_with(criteria)
        mock_query.filter.assert_called_once()
        mock_query.all.assert_called_once()

    def test_search_all_books(self, mocker):
        mock_query = mocker.Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [self.book_model]

        criteria: BookSearchCriteria = BookSearchCriteria()

        spy = mocker.spy(self.repository, 'search')
        results = self.service.execute(criteria)

        assert results is not None
        assert isinstance(results, list)
        assert len(results) == 1
        assert isinstance(results[0], Book)

        spy.assert_called_once_with(criteria)
        mock_query.filter.assert_not_called()
        mock_query.all.assert_called_once()