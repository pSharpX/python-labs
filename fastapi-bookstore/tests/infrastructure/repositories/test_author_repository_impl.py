import pytest

from app.domain.entities import Author
from app.domain.repositories import AuthorRepository
from app.infrastructure.models import AuthorModel
from app.infrastructure.repositories import AuthorRepositoryImpl
from tests.core.test_database import get_db, database_config, mysql_container

authors = [
    Author(id=None, name="Test Author 1", fullname="Test Author"),
    Author(id=None, name="Test Author 2", fullname="Test Author"),
    Author(id=None, name="Test Author 3", fullname="Test Author"),
    Author(id=None, name="Test Author 4", fullname="Test Author"),
    Author(id=None, name="Test Author 5", fullname="Test Author"),
    Author(id=None, name="Test Author 6", fullname="Test Author"),
    Author(id=None, name="Test Author 7", fullname="Test Author"),
    Author(id=None, name="Test Author 8", fullname="Test Author"),
    Author(id=None, name="Test Author 9", fullname="Test Author"),
    Author(id=None, name="Test Author 10", fullname="Test Author")
]

class TestAuthorRepositoryImpl:
    author_id: int
    repository: AuthorRepository

    @pytest.fixture
    def default_author(self):
        return Author(id=None, name="Test Author", fullname="Test Author")

    @pytest.fixture
    def invalid_author(self):
        return Author(id=None, name=None, fullname="Test Author Test Author Test Author Test Author Test Author Test Author Test Author Test Author Test Author")

    @pytest.mark.parametrize("new_author", authors)
    def test_create_author(self, mocker, get_db, new_author):
        add_spy = mocker.spy(get_db, 'add')
        commit_spy = mocker.spy(get_db, 'commit')
        refresh_spy = mocker.spy(get_db, 'refresh')
        self.repository = AuthorRepositoryImpl(get_db)

        author = self.repository.create(new_author)

        assert author is not None
        assert isinstance(author, Author)
        assert author.id is not None
        assert author.name == new_author.name
        assert author.fullname == new_author.fullname

        args, kwargs = refresh_spy.call_args
        author_model = args[0]
        assert author_model is not None
        assert isinstance(author_model, AuthorModel)

        add_spy.assert_called_once()
        commit_spy.assert_called_once()
        refresh_spy.assert_called_once()

    def test_create_author_invalid(self, mocker, get_db, invalid_author):
        add_spy = mocker.spy(get_db, 'add')
        commit_spy = mocker.spy(get_db, 'commit')
        refresh_spy = mocker.spy(get_db, 'refresh')
        self.repository = AuthorRepositoryImpl(get_db)

        with pytest.raises(Exception):
            self.repository.create(invalid_author)

        args, kwargs = add_spy.call_args
        author_model = args[0]
        assert author_model is not None
        assert isinstance(author_model, AuthorModel)

        add_spy.assert_called_once()
        commit_spy.assert_called_once()
        refresh_spy.assert_not_called()

    def test_get_by_id_author(self, mocker, get_db, default_author):
        query_spy = mocker.spy(get_db, 'query')
        self.repository = AuthorRepositoryImpl(get_db)

        author = self.repository.create(default_author)
        existent_author = self.repository.get_by_id(author.id)

        assert existent_author is not None
        assert isinstance(existent_author, Author)
        assert existent_author.id is not None
        assert existent_author.name == default_author.name
        assert existent_author.fullname == default_author.fullname

        query_spy.assert_called_once_with(AuthorModel)

    def test_get_by_id_author_unexistent(self, mocker, get_db, default_author):
        query_spy = mocker.spy(get_db, 'query')
        self.repository = AuthorRepositoryImpl(get_db)

        unexistent_author = self.repository.get_by_id(10000)

        assert unexistent_author is None

        query_spy.assert_called_once_with(AuthorModel)
