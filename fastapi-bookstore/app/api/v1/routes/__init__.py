from app.api.v1.routes.book_router import router as book_router
from app.api.v1.routes.auth_router import router as auth_router

__all__ = [
    "auth_router",
    "book_router",
]