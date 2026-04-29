import logging
import sys
from enum import Enum
from pythonjsonlogger import json

from app.configs import LoggingSettings
from app.core.request_context import request_id_ctx


class LogFormat(str, Enum):
    JSON = "json"
    TEXT = "text"

class RequestIdFilter(logging.Filter):
    """Filter that adds request_id to all log records."""
    def filter(self, record):
        record.request_id = request_id_ctx.get() or "no-request-id"
        return True

def get_text_formatter():
    return logging.Formatter(
        fmt=(
            "%(asctime)s | %(levelname)-8s | "
            "%(name)s | %(module)s.%(funcName)s:%(lineno)d | "
            "req=%(request_id)s | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

def get_json_formatter():
    return json.JsonFormatter(
        fmt=(
            "%(asctime)s "
            "%(levelname)s "
            "%(request_id)s"
            "%(name)s "
            "%(module)s.%(funcName)s "
            "%(lineno)d "
            "%(message)s "
        )
    )

class LoggingConfig:
    settings: LoggingSettings

    def __init__(self, settings: LoggingSettings):
        self.settings = settings

    def setup_logging(self):
        """Configure logging with automatic request ID injection."""
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(get_text_formatter())

        if self.settings.format == LogFormat.JSON:
            handler.setFormatter(get_json_formatter())

        handler.addFilter(RequestIdFilter())

        root_logger = logging.getLogger()
        root_logger.setLevel(self.settings.level)
        root_logger.handlers.clear()
        root_logger.addHandler(handler)

        # Reduce noise from uvicorn & fastapi
        logging.getLogger("uvicorn.access").disabled = True
        logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
        logging.getLogger("fastapi").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)
