import pytest

from app.core.exceptions import BookNotFound
from app.domain.entities import Book, Category, Author
from app.infrastructure.models import AuthorModel, CategoryModel, BookModel
from app.infrastructure.repositories import BookRepositoryImpl, AuthorRepositoryImpl, CategoryRepositoryImpl
from app.schemas import BookRequest
from app.use_cases import UpdateBookUseCase

class TestUpdateBookUseCase:
    book_id: int = 5
    service: UpdateBookUseCase
    author: Author = Author(id=1, name="Test Author", fullname="Test Author")
    category: Category = Category(id=1, name="Test Category", description="Test Category")
    book: Book = Book(id=book_id, title="Old Test Book", description="Old Test Book", author=author, category=category, rating=3,
                      published_date=2008)

    @pytest.fixture
    def default_request(self):
        return BookRequest(id=self.book_id, title="Updated Test Book", description="Updated Test description", rating=5, published_date=2009, author="Test Author", category="Test Category")

    @pytest.fixture
    def mock_session(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def mock_full_session(self, mocker, mock_session):

        def mock_query(arg1):
            mock = mocker.Mock()
            if arg1 == AuthorModel:
                mock.filter_by.return_value.first.return_value = self.author
            elif arg1 == CategoryModel:
                mock.filter_by.return_value.first.return_value = self.category
            elif arg1 == BookModel:
                mock.filter_by.return_value.first.return_value = self.book
            return mock

        mock_session.query.side_effect = mock_query
        return mock_session

    @pytest.fixture
    def mock_session_with_invalid_book(self, mocker, mock_session):

        def mock_query(arg1):
            mock = mocker.Mock()
            if arg1 == AuthorModel:
                mock.filter_by.return_value.first.return_value = self.author
            elif arg1 == CategoryModel:
                mock.filter_by.return_value.first.return_value = self.category
            elif arg1 == BookModel:
                mock.filter_by.return_value.first.return_value = None
            return mock

        mock_session.query.side_effect = mock_query
        return mock_session

    @pytest.fixture
    def mock_session_with_invalid_author(self, mocker, mock_session):

        def mock_query(arg1):
            mock = mocker.Mock()
            if arg1 == AuthorModel:
                mock.filter_by.return_value.first.return_value = None
            return mock

        mock_session.query.side_effect = mock_query
        return mock_session

    @pytest.fixture
    def mock_session_with_invalid_category(self, mocker, mock_session):

        def mock_query(arg1):
            mock = mocker.Mock()
            if arg1 == AuthorModel:
                mock.filter_by.return_value.first.return_value = self.author
            elif arg1 == CategoryModel:
                mock.filter_by.return_value.first.return_value = None
            return mock

        mock_session.query.side_effect = mock_query
        return mock_session

    @pytest.fixture
    def default_service(self, mocker, request):
        author_repository = AuthorRepositoryImpl(request.param)
        category_repository = CategoryRepositoryImpl(request.param)
        book_repository = BookRepositoryImpl(request.param)
        service = UpdateBookUseCase(book_repository, author_repository, category_repository)
        return service

    def test_update_book(self, mock_full_session, mocker, default_request):
        author_repository = AuthorRepositoryImpl(mock_full_session)
        category_repository = CategoryRepositoryImpl(mock_full_session)
        book_repository = BookRepositoryImpl(mock_full_session)
        self.service = UpdateBookUseCase(book_repository, author_repository, category_repository)

        update_book_spy = mocker.spy(book_repository, 'update')
        get_by_id_author_spy = mocker.spy(author_repository, 'get_by_id')
        get_by_id_category_spy = mocker.spy(category_repository, 'get_by_id')

        self.service.execute(self.book_id, default_request)

        mock_full_session.commit.assert_called_once()
        mock_full_session.refresh.assert_called_once()
        update_book_spy.assert_called_once()
        get_by_id_author_spy.assert_called_once()
        get_by_id_category_spy.assert_called_once()

        args, kwargs = mock_full_session.refresh.call_args
        updated_book = args[0]
        assert updated_book is not None
        assert isinstance(updated_book, Book)
        assert updated_book.title == default_request.title
        assert updated_book.description == default_request.description
        assert updated_book.rating == default_request.rating
        assert updated_book.published_date == default_request.published_date

    def test_update_book_with_invalid_author(self, mock_session_with_invalid_author, mocker, default_request):
        author_repository = AuthorRepositoryImpl(mock_session_with_invalid_author)
        category_repository = CategoryRepositoryImpl(mock_session_with_invalid_author)
        book_repository = BookRepositoryImpl(mock_session_with_invalid_author)
        self.service = UpdateBookUseCase(book_repository, author_repository, category_repository)

        update_book_spy = mocker.spy(book_repository, 'update')
        get_by_id_author_spy = mocker.spy(author_repository, 'get_by_id')
        get_by_id_category_spy = mocker.spy(category_repository, 'get_by_id')

        with pytest.raises(ValueError):
            self.service.execute(self.book_id, default_request)

        mock_session_with_invalid_author.commit.assert_not_called()
        mock_session_with_invalid_author.refresh.assert_not_called()
        update_book_spy.assert_not_called()
        get_by_id_author_spy.assert_called_once()
        get_by_id_category_spy.assert_not_called()

    def test_update_book_with_invalid_category(self, mock_session_with_invalid_category, mocker, default_request):
        author_repository = AuthorRepositoryImpl(mock_session_with_invalid_category)
        category_repository = CategoryRepositoryImpl(mock_session_with_invalid_category)
        book_repository = BookRepositoryImpl(mock_session_with_invalid_category)
        self.service = UpdateBookUseCase(book_repository, author_repository, category_repository)

        update_book_spy = mocker.spy(book_repository, 'update')
        get_by_id_author_spy = mocker.spy(author_repository, 'get_by_id')
        get_by_id_category_spy = mocker.spy(category_repository, 'get_by_id')

        with pytest.raises(ValueError):
            self.service.execute(self.book_id, default_request)

        mock_session_with_invalid_category.commit.assert_not_called()
        mock_session_with_invalid_category.refresh.assert_not_called()
        update_book_spy.assert_not_called()
        get_by_id_author_spy.assert_called_once()
        get_by_id_category_spy.assert_called_once()

    def test_update_book_with_invalid_book(self, mock_session_with_invalid_book, mocker, default_request):
        author_repository = AuthorRepositoryImpl(mock_session_with_invalid_book)
        category_repository = CategoryRepositoryImpl(mock_session_with_invalid_book)
        book_repository = BookRepositoryImpl(mock_session_with_invalid_book)
        self.service = UpdateBookUseCase(book_repository, author_repository, category_repository)

        update_book_spy = mocker.spy(book_repository, 'update')
        get_by_id_author_spy = mocker.spy(author_repository, 'get_by_id')
        get_by_id_category_spy = mocker.spy(category_repository, 'get_by_id')

        with pytest.raises(BookNotFound):
            self.service.execute(self.book_id, default_request)

        mock_session_with_invalid_book.commit.assert_not_called()
        mock_session_with_invalid_book.refresh.assert_not_called()
        update_book_spy.assert_called_once()
        get_by_id_author_spy.assert_called_once()
        get_by_id_category_spy.assert_called_once()
