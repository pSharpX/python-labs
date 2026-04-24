import pytest

from app.core.exceptions import BookNotFound
from app.domain.entities import Author, Category, Book
from app.domain.repositories import BookRepository
from app.infrastructure.models import BookModel
from app.infrastructure.repositories import BookRepositoryImpl, AuthorRepositoryImpl, CategoryRepositoryImpl

default_author = Author(id=None, name="Test author", fullname="Test author")
default_category = Category(id=None, name="Test category", description="Test category")

books = [
    Book(id=None, title="Test Book 1", description="Test Book 1", rating=5, published_date=2009, author=None, category=None),
    Book(id=None, title="Test Book 2", description="Test Book 2", rating=10, published_date=1000, author=None, category=None),
    Book(id=None, title="Test Book 3", description="Test Book 3", rating=100, published_date=200000, author=None, category=None),
    Book(id=None, title="Test Book 4", description=None, rating=0, published_date=0, author=None, category=None),
]

invalid_books = [
    Book(id=None, title="Test Book 2", description=None, rating=5, published_date=None, author=None, category=None),
    Book(id=None, title=None, description="Test Book 3", rating=5, published_date=2009, author=None, category=None),
    Book(id=None, title="Test Book 4", description="Test Book 4", rating=None, published_date=2009, author=None, category=None),
]

class TestBookRepositoryImpl:
    book_id: int
    repository: BookRepository

    @pytest.fixture
    def default_book(self):
        return Book(id=None, title="Test Book 1", description="Test Book", rating=5, published_date=2009, author=None, category=None)

    @pytest.fixture
    def default_author_and_category(self, get_db):
        author_repository = AuthorRepositoryImpl(get_db)
        category_repository = CategoryRepositoryImpl(get_db)
        new_author = author_repository.create(default_author)
        new_category = category_repository.create(default_category)
        return new_author, new_category

    @pytest.mark.parametrize("new_book", books)
    def test_create_book(self, mocker, get_db, new_book, default_author_and_category):
        add_spy = mocker.spy(get_db, 'add')
        commit_spy = mocker.spy(get_db, 'commit')
        refresh_spy = mocker.spy(get_db, 'refresh')
        self.repository = BookRepositoryImpl(get_db)

        new_author, new_category = default_author_and_category
        new_book.author = new_author
        new_book.category = new_category

        author = self.repository.create(new_book)

        assert author is not None
        assert isinstance(author, Book)
        assert author.id is not None
        assert author.title == new_book.title
        assert author.description == new_book.description
        assert author.rating == new_book.rating
        assert author.published_date == new_book.published_date

        args, kwargs = refresh_spy.call_args
        book_model = args[0]
        assert book_model is not None
        assert isinstance(book_model, BookModel)

        add_spy.assert_called_once()
        commit_spy.assert_called_once()
        refresh_spy.assert_called_once()

    @pytest.mark.parametrize("invalid_book", invalid_books)
    def test_create_book_with_invalid_data(self, mocker, get_db, invalid_book, default_author_and_category):
        add_spy = mocker.spy(get_db, 'add')
        commit_spy = mocker.spy(get_db, 'commit')
        refresh_spy = mocker.spy(get_db, 'refresh')
        self.repository = BookRepositoryImpl(get_db)

        new_author, new_category = default_author_and_category
        invalid_book.author = new_author
        invalid_book.category = new_category

        with pytest.raises(Exception):
            self.repository.create(invalid_book)

        args, kwargs = add_spy.call_args
        book_model = args[0]
        assert book_model is not None
        assert isinstance(book_model, BookModel)

        add_spy.assert_called_once()
        commit_spy.assert_called_once()
        refresh_spy.assert_not_called()

    def test_create_book_with_absent_data(self, mocker, get_db, default_book):
        add_spy = mocker.spy(get_db, 'add')
        commit_spy = mocker.spy(get_db, 'commit')
        refresh_spy = mocker.spy(get_db, 'refresh')
        self.repository = BookRepositoryImpl(get_db)

        with pytest.raises(ValueError):
            self.repository.create(default_book)

        add_spy.assert_not_called()
        commit_spy.assert_not_called()
        refresh_spy.assert_not_called()

    def test_get_by_id_book(self, mocker, get_db, default_book, default_author_and_category):
        query_spy = mocker.spy(get_db, 'query')
        self.repository = BookRepositoryImpl(get_db)

        new_author, new_category = default_author_and_category
        default_book.author = new_author
        default_book.category = new_category

        book = self.repository.create(default_book)
        existent_book = self.repository.get_by_id(book.id)

        assert existent_book is not None
        assert isinstance(existent_book, Book)
        assert existent_book.id is not None
        assert existent_book.title == book.title
        assert existent_book.description == book.description
        assert existent_book.rating == book.rating
        assert existent_book.published_date == book.published_date

        query_spy.assert_called_once_with(BookModel)

    def test_get_by_id_book_unexistent(self, mocker, get_db):
        query_spy = mocker.spy(get_db, 'query')
        self.repository = BookRepositoryImpl(get_db)

        with pytest.raises(BookNotFound):
            self.repository.get_by_id(10000)

        query_spy.assert_called_once_with(BookModel)
