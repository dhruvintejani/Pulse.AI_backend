import re
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from app.core.config import settings

SUSPICIOUS_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"<script",
        r"javascript:",
        r"\bonerror\s*=",
        r"\bonload\s*=",
        r"union\s+select",
        r"drop\s+table",
        r"insert\s+into",
        r"delete\s+from",
    ]
]


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.SECURITY_MAX_REQUEST_SIZE_BYTES:
            return Response("Request body too large", status_code=413)
        return await call_next(request)


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not settings.SECURITY_INPUT_SANITIZATION_ENABLED:
            return await call_next(request)

        target = f"{request.url.path}?{request.url.query}"
        if settings.SECURITY_BLOCK_SUSPICIOUS_INPUT and any(pattern.search(target) for pattern in SUSPICIOUS_PATTERNS):
            return Response("Suspicious input blocked", status_code=400)

        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        if not settings.SECURITY_HEADERS_ENABLED:
            return response

        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()")
        response.headers.setdefault("Content-Security-Policy", settings.SECURITY_CONTENT_SECURITY_POLICY)
        if settings.SECURITY_ENABLE_HSTS:
            response.headers.setdefault("Strict-Transport-Security", f"max-age={settings.SECURITY_HSTS_MAX_AGE_SECONDS}; includeSubDomains")
        return response
