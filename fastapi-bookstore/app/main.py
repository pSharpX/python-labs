
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.api.middleware import RequestContextMiddleware
from app.api.v1.router import api_router
from app.core.starter import ContainerStarter


@asynccontextmanager
async def lifespan(app: FastAPI):
    container: ContainerStarter = app.container

    # Resolve dependencies from container
    container.initialize()
    await container.start()
    yield
    await container.stop()
    container.destroy()

container_starter = ContainerStarter()

logging_config = container_starter.container.logging_config()
logging_config.setup_logging()

app = FastAPI(lifespan=lifespan)
app.container = container_starter

app.add_middleware(RequestContextMiddleware)

app.include_router(api_router, prefix="/api/v1")

register_exception_handlers(app)

@app.get("/")
async def health_check():
    return {"status": "up"}
