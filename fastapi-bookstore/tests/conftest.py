import pytest
from testcontainers.mysql import MySqlContainer
from app.core.database import DatabaseConfig

seed_data = "db/changelog/"

@pytest.fixture(scope="session")
def mysql_container():
    with MySqlContainer("mysql:8.0", dialect="pymysql", dbname="bookstore_database", seed=seed_data) as mysql:
        # Yield the connection URL to tests
        yield  mysql.get_connection_url()

@pytest.fixture(scope="session")
def database_config(session_mocker, mysql_container):
    mock_settings = session_mocker.MagicMock()
    mock_settings.connection_url.return_value = mysql_container

    config = DatabaseConfig(mock_settings)
    return config

@pytest.fixture()
def get_db(database_config):
    yield from database_config.get_db()
