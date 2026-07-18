from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from loguru import logger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.api.v1 import api_router
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging import configure_logging
from app.db.database import close_db, init_db
from app.middleware import (
    InputSanitizationMiddleware,
    RequestLoggingMiddleware,
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
    register_exception_handlers,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting Pulse AI API", environment=settings.ENVIRONMENT)

    if settings.should_skip_database_init:
        logger.warning("MongoDB initialization skipped", environment=settings.ENVIRONMENT)
        yield
        logger.info("Pulse AI API stopped")
        return

    await init_db()
    yield
    await close_db()
    logger.info("Pulse AI API stopped")


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Pulse AI backend API",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SlowAPIMiddleware)

    if settings.SECURITY_ALLOWED_HOSTS != ["*"]:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.SECURITY_ALLOWED_HOSTS)

    app.add_middleware(RequestSizeLimitMiddleware)
    app.add_middleware(InputSanitizationMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=settings.BACKEND_CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.BACKEND_CORS_ALLOW_METHODS,
        allow_headers=settings.BACKEND_CORS_ALLOW_HEADERS,
        expose_headers=settings.BACKEND_CORS_EXPOSE_HEADERS,
        max_age=600,
    )
    app.add_middleware(SecurityHeadersMiddleware)

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {"service": settings.APP_NAME, "status": "ok", "version": settings.APP_VERSION}

    return app


app = create_application()
