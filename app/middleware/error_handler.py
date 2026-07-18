from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.errors import AppError


def _request_id(request: Request) -> str | None:
    state_request_id = getattr(request.state, "request_id", None)
    if isinstance(state_request_id, str):
        return state_request_id
    return request.headers.get("X-Request-ID")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> ORJSONResponse:
        logger.bind(category="request").warning("Application error", error_code=exc.error_code, status_code=exc.status_code, path=request.url.path)
        return ORJSONResponse(status_code=exc.status_code, content={"success": False, "error_code": exc.error_code, "message": exc.message, "details": exc.details, "request_id": _request_id(request)})

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException) -> ORJSONResponse:
        logger.bind(category="request").warning("HTTP error", status_code=exc.status_code, path=request.url.path)
        return ORJSONResponse(status_code=exc.status_code, content={"success": False, "error_code": "HTTP_ERROR", "message": str(exc.detail), "details": None, "request_id": _request_id(request)})

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> ORJSONResponse:
        logger.bind(category="request").warning("Request validation failed", path=request.url.path, errors=exc.errors())
        return ORJSONResponse(status_code=422, content={"success": False, "error_code": "VALIDATION_ERROR", "message": "Request validation failed", "details": exc.errors(), "request_id": _request_id(request)})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
        logger.bind(category="request").exception("Unhandled exception", path=request.url.path, error=str(exc))
        return ORJSONResponse(status_code=500, content={"success": False, "error_code": "INTERNAL_SERVER_ERROR", "message": "Internal server error", "details": None, "request_id": _request_id(request)})
