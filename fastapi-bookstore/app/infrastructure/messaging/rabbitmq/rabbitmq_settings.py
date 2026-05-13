
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitMQSettings(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(env_prefix="rabbitmq_", env_file=".env", env_file_encoding="utf-8", extra="allow")

    connection_string: str = Field("amqp://guest:guest@127.0.0.1/", max_length=200, min_length=5)
    queue_name: str = Field("test_queue", max_length=200, min_length=5)
    exchange_name: str = Field("test_exchange_name", min_length=5, max_length=100)
