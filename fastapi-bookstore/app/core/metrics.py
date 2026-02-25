import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def track_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = (time.time() - start) * 1000

        logger.info(
            f"{func.__name__} executed",
            extra={"duration_ms": round(duration, 2)}
        )
        return result

    return wrapper
