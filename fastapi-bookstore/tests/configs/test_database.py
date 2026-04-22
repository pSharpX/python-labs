import pytest
from testcontainers.mysql import MySqlContainer
import sqlalchemy

from app.core.database import DatabaseConfig

@pytest.fixture(scope="session")
def mysql_container():
    with MySqlContainer("mysql:8.0", dialect="pymysql") as mysql:
        # Yield the connection URL to tests
        yield  mysql.get_connection_url()

@pytest.fixture(scope="session")
def database_config(session_mocker, mysql_container):
    mock_settings = session_mocker.MagicMock()
    mock_settings.connection_url.return_value = mysql_container

    config = DatabaseConfig(mock_settings)
    return config

@pytest.fixture(scope="session")
def get_db(database_config):
    yield from database_config.get_db()

def test_database_connection(mysql_container):
    engine = sqlalchemy.create_engine(mysql_container)
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT 1"))
        assert result.fetchone()[0] == 1

