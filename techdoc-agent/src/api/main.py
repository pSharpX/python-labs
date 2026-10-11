"""FastAPI application factory.

Run locally:  uvicorn src.api.main:app --reload --port 8000   (from the backend/ folder)
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from settings import ApplicationSettings, get_settings
from src.api.dependencies import AppContainer, build_container
from src.api.routes.proposals import router as proposals_router
from src.api.schemas import HealthResponse
from src.services.proposal_service import ServiceError
from src.utils.logging import configure_logging, get_logger, new_trace_id, trace_id_var


log = get_logger(__name__)
API_VERSION = "1.0.0"

ContainerFactory = Callable[[ApplicationSettings], Awaitable[AppContainer]]


def _error(status_code: int, code: str, message: str, details: Any = None) -> JSONResponse:
    body = {"error": {"code": code, "message": message, "trace_id": trace_id_var.get(), "details": details}}
    return JSONResponse(body, status_code=status_code, headers={"X-Trace-Id": trace_id_var.get()})


def create_app(settings: ApplicationSettings | None = None, container_factory: ContainerFactory | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level, settings.log_json)
    factory = container_factory or build_container

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.container = await factory(settings)
        log.info("API started", extra={"event": {"mcp_available": True}})
        try:
            yield
        finally:
            await app.state.container.aclose()

    app = FastAPI(
        title=settings.app_name,
        version=API_VERSION,
        lifespan=lifespan,
        description="Workflow technical-functional proposal generation (LangGraph). "
        "Long-running steps run in the background: POST endpoints return 202 and clients poll "
        "GET /proposals/{id} until run_state is no longer 'running'.",
    )
    app.add_middleware(
        CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"],
        expose_headers=["X-Trace-Id", "X-Content-SHA256", "Content-Disposition"],
    )

    @app.middleware("http")
    async def trace_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
        incoming = request.headers.get("x-trace-id", "")
        trace_id = incoming if incoming.isalnum() and len(incoming) <= 64 else new_trace_id()
        token = trace_id_var.set(trace_id)
        try:
            response = await call_next(request)
        finally:
            trace_id_var.reset(token)
        response.headers["X-Trace-Id"] = trace_id
        return response

    @app.exception_handler(ServiceError)
    async def service_error(_: Request, exc: ServiceError) -> JSONResponse:
        return _error(exc.status_code, exc.code, exc.message)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = {401: "unauthorized", 403: "forbidden", 404: "not_found", 405: "method_not_allowed"}.get(exc.status_code, "http_error")
        resp = _error(exc.status_code, code, str(exc.detail))
        for k, v in (exc.headers or {}).items():
            resp.headers[k] = v
        return resp

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = [{"loc": list(e.get("loc", [])), "msg": e.get("msg")} for e in exc.errors()]
        return _error(422, "validation_error", "Request validation failed", details)

    @app.exception_handler(Exception)
    async def unhandled(_: Request, exc: Exception) -> JSONResponse:
        log.exception("Unhandled error")
        return _error(500, "internal_error", "An unexpected error occurred")

    @app.get("/health", response_model=HealthResponse, tags=["health"])
    async def health(request: Request) -> HealthResponse:
        container: AppContainer = request.app.state.container
        return HealthResponse(status="ok", version=API_VERSION, mcp_available=True, mcp_detail="Techdoc-MCP")

    app.include_router(proposals_router, prefix=settings.api_prefix)
    return app


app = create_app()  # module-level ASGI app for uvicorn
