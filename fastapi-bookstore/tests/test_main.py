import pytest

from fastapi.testclient import TestClient
from app.main import app


class TestMain:

    @pytest.fixture
    def default_client(self):
        return TestClient(app)

    def test_health_check(self, default_client):
        response = default_client.get("/")
        assert response.status_code == 200
        assert response.json() == {"status": "up"}