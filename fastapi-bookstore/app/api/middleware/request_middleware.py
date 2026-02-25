import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.request_context import generate_request_id, set_request_id

logger = logging.getLogger(__name__)

class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware that assigns and propagates request IDs."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID")
        # Generate new ID if not provided
        if not request_id:
            request_id = generate_request_id()

        # Store in context for access throughout request lifecycle
        set_request_id(request_id)

        method = request.method
        path = request.url.path
        query = str(request.query_params) if request.query_params else ""
        client_ip = request.client.host if request.client else "unknown"
        start_time = time.perf_counter()

        logger.info(
            f"Request started: {method} {path}",
            extra={
                "method": method,
                "path": path,
                "query": query,
                "client_ip": client_ip,
            }
        )

        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            f"Request completed : {method} {path} - {response.status_code} ({duration_ms:.2f}ms)",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": client_ip,
            }
        )

        response.headers["X-Request-ID"] = request_id

        return response
