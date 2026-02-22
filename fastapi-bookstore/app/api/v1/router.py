from fastapi import APIRouter
from app.api.v1.routes import auth_router, book_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(book_router, prefix="/books", tags=["Books"])
