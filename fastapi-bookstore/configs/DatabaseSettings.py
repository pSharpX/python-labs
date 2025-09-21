from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(env_prefix="database_", env_file=".env", env_file_encoding="utf-8")

    host: str = Field("localhost")
    port: int = Field("3306", alias="database_port") # when alias set env_prefix will be ignored.
    user: str = Field()
    password: str = Field()
    db_name: str = Field("bookstore-db", alias="name")

    def connection_url(self):
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"#?charset = utf8/charset=utf8mb4


settings = DatabaseSettings()