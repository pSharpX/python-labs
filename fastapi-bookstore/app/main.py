from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.api.middleware import RequestContextMiddleware
#from app.core.database import Base, engine
from app.api.v1.router import api_router
from app.core.dependencies import get_logging_settings
from app.core.logging_config import LoggingConfig

app = FastAPI()

#Base.metadata.create_all(bind=engine)

app.add_middleware(RequestContextMiddleware)

app.include_router(api_router, prefix="/api/v1")

LoggingConfig(get_logging_settings())
register_exception_handlers(app)

@app.get("/")
async def health_check():
    return {"status": "up"}
