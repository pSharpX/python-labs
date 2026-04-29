import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_database_settings
from app.main import app


@pytest.fixture
def override_database_settings(session_mocker, mysql_container):
    def  _override():
        mock_settings = session_mocker.MagicMock()
        mock_settings.connection_url.return_value = mysql_container
        return mock_settings

    return _override

default_book = { "id": None, "title": "Test Book 1", "description": "Test Book 1", "rating": 4, "published_date": 2009, "author": "1", "category": "1"}

create_books_requests = [
    (default_book, 201),
    ({ "id": None, "title": "Test Book 2", "rating": 4, "published_date": 2009, "author": "1", "category": "1"}, 201),
    ({ "id": None, "title": "Test Book 3", "description": "Test Book 1", "rating": 4, "published_date": 2009, "author": "1"}, 400),
    ({ "id": None, "title": "Test Book 4", "description": "Test Book 1", "rating": 4, "published_date": 2009, "author": "1000" , "category": "1"}, 400),
    ({ "id": None, "title": "Te", "description": "Test Book 1", "rating": 4, "published_date": 2009, "author": "1", "category": "1"}, 400),
    ({ "id": None, "description": "Test Book 6", "rating": 4, "published_date": 2009, "author": "1", "category": "1"}, 400),
    ({ "id": None, "title": "Test Book 7", "description": "Test Book 1", "rating": 100, "published_date": 2009, "author": "1", "category": "1"}, 400),
    ({ "id": None, "title": "Test Book 8", "description": "Test Book 1", "rating": 5, "published_date": 1, "author": "1", "category": "1"}, 400)
]

update_books_requests = [
    (1, { "id": 1, "title": "Update Test Book 1", "description": "Update Test Book 1", "rating": 3, "published_date": 2021, "author": "1", "category": "1"}, 204),
    (1, { "id": 1, "title": "Update Test Book 2", "rating": 5, "published_date": 2021, "author": "1", "category": "1"}, 204),
    (1, { "id": 1, "title": "Test Book 3", "description": "Test Book 1", "rating": 4, "published_date": 2009, "author": "1"}, 400),
    (1, { "id": 1, "title": "Test Book 4", "description": "Test Book 1", "rating": 4, "published_date": 2009, "author": "1000" , "category": "1"}, 400),
    (1, { "id": 1, "title": "Te", "description": "Test Book 1", "rating": 4, "published_date": 2009, "author": "1", "category": "1"}, 400),
    (1, { "id": 1, "description": "Test Book 6", "rating": 4, "published_date": 2009, "author": "1", "category": "1"}, 400),
    (1, { "id": 1, "title": "Test Book 7", "description": "Test Book 1", "rating": 100, "published_date": 2009, "author": "1", "category": "1"}, 400),
    (1, { "id": 1, "title": "Test Book 8", "description": "Test Book 1", "rating": 5, "published_date": 1, "author": "1", "category": "1"}, 400)
]

search_books_requests = [
    ({ "title": default_book["title"], "rating": default_book["rating"], "published_date": default_book["published_date"]}, 200, 1),
    ({ "title": default_book["title"], "rating": 1, "published_date": default_book["published_date"]}, 200, 0),
    ({ "title": "Unexistent test book" }, 200, 0),
    ({ "title": default_book["title"], "rating": 10, "published_date": default_book["published_date"]}, 400, 0),
    ({ "title": default_book["title"], "rating": default_book["rating"], "published_date": 1}, 400, 0),
]

class TestBookRouter:
    BOOKS_RESOURCE_PATH = "/api/v1/books"

    @pytest.fixture
    def client(self, override_database_settings):
        app.dependency_overrides[get_database_settings] = override_database_settings
        yield TestClient(app)
        app.dependency_overrides.clear()

    @pytest.mark.parametrize("payload, status_code", create_books_requests)
    def test_create_books(self, client, payload, status_code):
        response = client.post(self.BOOKS_RESOURCE_PATH, json=payload)
        assert response.status_code == status_code

        if response.status_code == 400:
            assert response.json() is not None
            assert "error" in response.json()

    @pytest.mark.parametrize("book_id, payload, status_code", update_books_requests)
    def test_update_books(self, client, book_id, payload, status_code):
        response = client.put(f"{self.BOOKS_RESOURCE_PATH}/{book_id}", json=payload)
        assert response.status_code == status_code

        if response.status_code == 400:
            assert response.json() is not None
            assert "error" in response.json()

    @pytest.mark.parametrize("params, status_code, expected_count", search_books_requests)
    def test_search_books(self, client, params, status_code, expected_count):
        response = client.get(self.BOOKS_RESOURCE_PATH, params=params)
        assert response.status_code == status_code

        if response.status_code == 200:
            assert isinstance(response.json(), list)
            assert len(response.json()) == expected_count
        elif response.status_code == 400:
            assert response.json() is not None
            assert "error" in response.json()

    @pytest.mark.parametrize("book_id, status_code", [(1, 200), (0, 400), ("invalid_book_id", 400), (1000, 404)])
    def test_get_books_by_id(self, client, book_id, status_code):
        response = client.get(f"{self.BOOKS_RESOURCE_PATH}/{book_id}")
        assert response.status_code == status_code
        assert response.json() is not None

        if response.status_code == 200:
            assert "title" in response.json()
            assert "description" in response.json()
            assert "rating" in response.json()
            assert "published_date" in response.json()
            assert "author" in response.json()
            assert "category" in response.json()
        elif response.status_code == 400:
            assert "error" in response.json()

    @pytest.mark.parametrize("published_date, status_code", [(2009, 200), (0, 400), ("invalid_published_date", 400)])
    def test_get_books_by_published_date(self, client, published_date, status_code):
        response = client.get(f"{self.BOOKS_RESOURCE_PATH}/publish/{published_date}")
        assert response.status_code == status_code
        assert response.json() is not None

        if response.status_code == 200:
            assert isinstance(response.json(), list)
        elif response.status_code == 400:
            assert "error" in response.json()