
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.api.middleware import RequestContextMiddleware
from app.api.v1.router import api_router
from app.core.dependencies import get_logging_settings
from app.core.logging_config import LoggingConfig
from app.core.container import Container


@asynccontextmanager
async def lifespan(app: FastAPI):
    container: Container = app.container

    # Resolve dependencies from container
    container.init_resources()
    connection = container.rabbitmq_connection()
    worker = container.outbox_worker()
    consumer = container.event_consumer()
    await connection.connect()
    await consumer.consume()
    await worker.start()
    yield
    await worker.stop()
    await connection.close()
    container.shutdown_resources()

container = Container()
app = FastAPI(lifespan=lifespan)
app.container = container

app.add_middleware(RequestContextMiddleware)

app.include_router(api_router, prefix="/api/v1")

LoggingConfig(get_logging_settings())
register_exception_handlers(app)

@app.get("/")
async def health_check():
    return {"status": "up"}
