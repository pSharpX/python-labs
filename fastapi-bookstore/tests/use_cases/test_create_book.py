import pytest
from app.schemas import CreateBookRequest
from app.use_cases import CreateBookUseCase
from app.domain.entities import Book, Author, Category


@pytest.fixture
def default_book_request():
    return CreateBookRequest(title="Test Book", description="Test Book", author="Test Author", category="Test Category", rating=5, published_date=2009)

@pytest.fixture
def default_author():
    return Author(id=1, name="Test Author", fullname="Test Author")

@pytest.fixture
def default_category():
    return Category(id=1, name="Test Category", description="Test Category")

@pytest.fixture
def default_book(default_author, default_category):
    return Book(id=1, title="Test Book", description="Test Book", author=default_author, category=default_category, rating=5, published_date=2009)

@pytest.fixture
def mock_book_repository(mocker):
    return mocker.Mock()

@pytest.fixture
def mock_author_repository(mocker):
    return mocker.Mock()

@pytest.fixture
def mock_category_repository(mocker):
    return mocker.Mock()

def test_create_new_book(default_book_request, default_book, default_author, default_category, mock_book_repository, mock_author_repository, mock_category_repository):
    mock_book_repository.get_by_title.return_value = None
    mock_book_repository.create.return_value = default_book
    mock_author_repository.get_by_id.return_value = default_author
    mock_category_repository.get_by_id.return_value = default_category

    create_book_service = CreateBookUseCase(mock_book_repository, mock_author_repository, mock_category_repository)
    new_book = create_book_service.execute(default_book_request)

    assert new_book is not None
    assert isinstance(new_book, Book)
    assert new_book.id is not None
    assert new_book.title == default_book_request.title
    assert new_book.description == default_book_request.description

    mock_book_repository.get_by_title.assert_called_once_with(default_book_request.title)
    mock_author_repository.get_by_id.assert_called_once_with(default_book_request.author)
    mock_category_repository.get_by_id.assert_called_once_with(default_book_request.category)

def test_create_existent_book(default_book_request, default_book, mock_book_repository, mock_author_repository, mock_category_repository):
    mock_book_repository.get_by_title.return_value = default_book

    create_book_service = CreateBookUseCase(mock_book_repository, mock_author_repository, mock_category_repository)

    with pytest.raises(ValueError):
        create_book_service.execute(default_book_request)

    mock_book_repository.get_by_title.assert_called_once_with(default_book_request.title)
    mock_author_repository.get_by_id.assert_not_called()
    mock_category_repository.get_by_id.assert_not_called()

def test_create_book_with_invalid_author(default_book_request, mock_book_repository, mock_author_repository, mock_category_repository):
    mock_book_repository.get_by_title.return_value = None
    mock_author_repository.get_by_id.return_value = None

    create_book_service = CreateBookUseCase(mock_book_repository, mock_author_repository, mock_category_repository)

    with pytest.raises(ValueError):
        create_book_service.execute(default_book_request)

    mock_book_repository.get_by_title.assert_called_once_with(default_book_request.title)
    mock_author_repository.get_by_id.assert_called_once_with(default_book_request.author)
    mock_category_repository.get_by_id.assert_not_called()
    mock_category_repository.create.assert_not_called()

def test_create_book_with_invalid_category(default_book_request, default_author, mock_book_repository, mock_author_repository, mock_category_repository):
    mock_book_repository.get_by_title.return_value = None
    mock_author_repository.get_by_id.return_value = default_author
    mock_category_repository.get_by_id.return_value = None

    create_book_service = CreateBookUseCase(mock_book_repository, mock_author_repository, mock_category_repository)

    with pytest.raises(ValueError):
        create_book_service.execute(default_book_request)

    mock_book_repository.get_by_title.assert_called_once_with(default_book_request.title)
    mock_author_repository.get_by_id.assert_called_once_with(default_book_request.author)
    mock_category_repository.get_by_id.assert_called_once_with(default_book_request.category)
    mock_category_repository.create.assert_not_called()