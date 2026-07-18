import time
from urllib.parse import parse_qsl, urlencode
from uuid import uuid4
from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from app.core.config import settings

SENSITIVE_QUERY_KEYS = {"access_token", "api_key", "auth", "code", "key", "password", "refresh_token", "secret", "signature", "token"}


def redact_query_string(query: str) -> str:
    if not query:
        return ""
    try:
        pairs = parse_qsl(query, keep_blank_values=True)
    except ValueError:
        return "[unparseable]"
    redacted_pairs = [(key, "[REDACTED]" if key.lower() in SENSITIVE_QUERY_KEYS else value) for key, value in pairs]
    return urlencode(redacted_pairs)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", uuid4().hex)
        request.state.request_id = request_id
        start_time = time.perf_counter()
        client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or (request.client.host if request.client else None)
        query = redact_query_string(str(request.url.query))

        with logger.contextualize(request_id=request_id):
            logger.bind(category="request").info("Request started", method=request.method, path=request.url.path, query=query, client=client_ip)
            try:
                response = await call_next(request)
            except Exception:
                logger.bind(category="request").exception("Unhandled request error", method=request.method, path=request.url.path, client=client_ip)
                raise

            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time-Ms"] = str(duration_ms)
            logger.bind(category="request").info("Request completed", method=request.method, path=request.url.path, status_code=response.status_code, duration_ms=duration_ms)

            if duration_ms >= settings.LOG_PERFORMANCE_THRESHOLD_MS:
                logger.bind(category="performance").warning("Slow request detected", method=request.method, path=request.url.path, duration_ms=duration_ms)

            return response
