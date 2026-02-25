from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ):
        print(exc.code, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ):
        # Log the actual exception for debugging
        import traceback

        error_traceback = traceback.format_exc()
        print(f"[ERROR] Unhandled exception: {type(exc).__name__}: {str(exc)}")
        print(f"[ERROR] Traceback:\n{error_traceback}")

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": f"Unexpected error occurred: {type(exc).__name__}: {str(exc)}",
                    "details": {
                        "exception_type": type(exc).__name__,
                        "exception_message": str(exc),
                    },
                }
            },
        )
