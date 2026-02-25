import logging
import sys
from pythonjsonlogger import jsonlogger
from app.core.request_context import request_id_ctx

class RequestIdFilter(logging.Filter):
    """Filter that adds request_id to all log records."""
    def filter(self, record):
        record.request_id = request_id_ctx.get() or "no-request-id"
        return True

def setup_logging():
    """Configure logging with automatic request ID injection."""
    handler = logging.StreamHandler(sys.stdout)

    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(request_id)s %(name)s  %(module)s.%(funcName)s %(message)s"
    )

    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
