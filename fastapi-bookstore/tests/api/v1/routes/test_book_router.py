import pytest

from fastapi.testclient import TestClient
from app.main import app
from app.core.dependencies import get_database_settings


@pytest.fixture
def override_database_settings(session_mocker, mysql_container):
    def  _override():
        mock_settings = session_mocker.MagicMock()
        mock_settings.connection_url.return_value = mysql_container
        return mock_settings

    return _override

create_books_requests = [
    ({ "id": None, "title": "Test Book 1", "description": "Test Book 1", "rating": 4, "published_date": 2009, "author": "1", "category": "1"}, 201),
    ({ "id": None, "title": "Test Book 2", "rating": 4, "published_date": 2009, "author": "1", "category": "1"}, 201),
    ({ "id": None, "title": "Test Book 3", "description": "Test Book 1", "rating": 4, "published_date": 2009, "author": "1"}, 400),
    ({ "id": None, "title": "Test Book 4", "description": "Test Book 1", "rating": 4, "published_date": 2009, "category": "1"}, 400),
    ({ "id": None, "title": "Te", "description": "Test Book 1", "rating": 4, "published_date": 2009, "author": "1", "category": "1"}, 400),
    ({ "id": None, "description": "Test Book 6", "rating": 4, "published_date": 2009, "author": "1", "category": "1"}, 400),
    ({ "id": None, "title": "Test Book 7", "description": "Test Book 1", "rating": 100, "published_date": 2009, "author": "1", "category": "1"}, 400),
    ({ "id": None, "title": "Test Book 8", "description": "Test Book 1", "rating": 5, "published_date": 1, "author": "1", "category": "1"}, 400)
]

class TestBookRouter:
    BOOKS_RESOURCE_PATH = "/api/v1/books"

    @pytest.fixture
    def client(self, override_database_settings):
        app.dependency_overrides[get_database_settings] = override_database_settings
        yield TestClient(app)
        app.dependency_overrides.clear()

    @pytest.mark.parametrize("payload,status_code", create_books_requests)
    def test_create_books(self, client, payload, status_code):
        response = client.post(self.BOOKS_RESOURCE_PATH, json=payload)
        assert response.status_code == status_code

        if response.status_code == 400:
            assert response.json() is not None