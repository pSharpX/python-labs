class AppException(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: str = "APP_ERROR",
        status_code: int = 500,
        details: dict | None = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class ResourceNotFound(AppException):
    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "RESOURCE_NOT_FOUND",
        details: dict | None = None,
    ):
        super().__init__(message=message, code=code, status_code=404, details=details or {})


class BookNotFound(ResourceNotFound):
    def __init__(self, book_id: str):
        super().__init__(
            message=f"Book {book_id} not found",
            code="BOOK_NOT_FOUND",
        )


class AuthorNotFound(ResourceNotFound):
    def __init__(self, author_id: str):
        super().__init__(
            message=f"author {author_id} not found",
            code="AUTHOR_NOT_FOUND",
        )


class InsufficientBalance(AppException):
    def __init__(self, balance: float):
        super().__init__(
            message="Insufficient balance",
            code="INSUFFICIENT_BALANCE",
            status_code=409,
            details={"balance": balance},
        )


class BadRequest(AppException):
    def __init__(self, field_name: str, field_value: str):
        super().__init__(
            message=f"Invalid value for {field_name} = {field_value}",
            code="INVALID_REQUEST",
            status_code=400,
            details={"field": field_name},
        )


class BookAlreadyExists(AppException):
    def __init__(self, book_title: str):
        super().__init__(
            message=f"Book with title '{book_title}' already exists",
            code="BOOK_ALREADY_EXISTS",
            status_code=400,
            details={"book_title": book_title},
        )
