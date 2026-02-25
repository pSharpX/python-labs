import logging
import sys
from enum import Enum

from pythonjsonlogger import jsonlogger
from app.core.request_context import request_id_ctx
from app.configs.logging_settings import settings

LOG_FORMAT = settings.format
LOG_LEVEL = settings.level

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
    return jsonlogger.JsonFormatter(
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

def setup_logging():
    """Configure logging with automatic request ID injection."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(get_text_formatter())

    if LOG_FORMAT == LogFormat.JSON:
        handler.setFormatter(get_json_formatter())

    handler.addFilter(RequestIdFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
