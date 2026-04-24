import pytest

from pydantic import ValidationError
from app.configs import DatabaseSettings

configs = [
    { "host": "localhost", "port": "3306", "user": "root", "password": "admin", "database": "test_db" },
    { "host": "127.0.0.1", "port": "3306", "user": "admin", "password": "admin", "database": "test_db" },
    { "user": "admin", "password": "admin" },
]

invalid_configs = [
    { "host": "localhost", "port": "3306", "user": "root", "password": "", "database": "test_db" },
    { "host": "127.0.0.1", "port": "3306", "user": "admin", "database": "test_db" },
    { "host": "127.0.0.1", "port": "3306", "password": "admin", "database": "test_db" },
]

env_file_content = '''
DATABASE_HOST=test_localhost
DATABASE_USER=test_admin
DATABASE_PASSWORD=test_admin
DATABASE_PORT=3306
DATABASE_NAME=test_database
'''

invalid_env_file_content = '''
DATABASE_HOST=test_localhost
DATABASE_PASSWORD=adm
DATABASE_PORT=3306
DATABASE_NAME=test_database
'''

def initialize_settings(monkeypatch, config):
    if "host" in config:
        monkeypatch.setenv("DATABASE_HOST", config["host"])
    if "port" in config:
        monkeypatch.setenv("DATABASE_PORT", config["port"])
    if "user" in config:
        monkeypatch.setenv("DATABASE_USER", config["user"])
    if "password" in config:
        monkeypatch.setenv("DATABASE_PASSWORD", config["password"])
    if "database" in config:
        monkeypatch.setenv("DATABASE_NAME", config["database"])

class TestDatabaseSettings:

    @pytest.mark.parametrize("config", configs )
    def test_environ_database_settings(self, mocker, monkeypatch, config):
        # Initialize environment variables
        initialize_settings(monkeypatch, config)

        # Disable environment files
        mocker.patch("builtins.open", mocker.mock_open(read_data=""))

        settings = DatabaseSettings()

        assert settings.host is not None
        assert settings.port is not None
        assert settings.user is not None
        assert settings.password is not None
        assert settings.db_name is not None

        assert settings.host == config["host"] if "host" in config else "localhost"
        assert settings.port == int(config["port"]) if "port" in config else 3306
        assert settings.user == config["user"]
        assert settings.password == config["password"]
        assert settings.db_name == config["database"] if "database" in config else "bookstore-db"
        assert settings.connection_url() == f"mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"] if "host" in config else "localhost"}:{int(config["port"]) if "port" in config else 3306}/{config["database"] if "database" in config else "bookstore-db"}"

    def test_envfile_database_settings(self, mocker):
        mocker.patch("builtins.open", mocker.mock_open(read_data=env_file_content))

        settings = DatabaseSettings()

        assert settings.host is not None
        assert settings.port is not None
        assert settings.user is not None
        assert settings.password is not None
        assert settings.db_name is not None

        assert settings.host == "test_localhost"
        assert settings.port == 3306
        assert settings.user == "test_admin"
        assert settings.password == "test_admin"
        assert settings.db_name == "test_database"
        assert settings.connection_url() == f"mysql+pymysql://test_admin:test_admin@test_localhost:3306/test_database"

    @pytest.mark.parametrize("config", invalid_configs)
    def test_environ_database_settings_with_invalid_config(self, mocker, monkeypatch, config):
        initialize_settings(monkeypatch, config)

        mocker.patch("builtins.open", mocker.mock_open(read_data=""))

        with pytest.raises(ValidationError):
            DatabaseSettings()

    def test_envfile_database_settings_with_invalid_config(self, mocker, monkeypatch):
        mocker.patch("builtins.open", mocker.mock_open(read_data=invalid_env_file_content))

        with pytest.raises(ValidationError):
            DatabaseSettings()