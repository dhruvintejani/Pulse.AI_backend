from typing import Any


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400, error_code: str = "APP_ERROR", details: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details


class AuthenticationError(AppError):
    def __init__(self, message: str = "Authentication required", details: Any = None) -> None:
        super().__init__(message=message, status_code=401, error_code="AUTHENTICATION_REQUIRED", details=details)


class AuthorizationError(AppError):
    def __init__(self, message: str = "You do not have access to this resource", details: Any = None) -> None:
        super().__init__(message=message, status_code=403, error_code="FORBIDDEN", details=details)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", details: Any = None) -> None:
        super().__init__(message=message, status_code=404, error_code="NOT_FOUND", details=details)
