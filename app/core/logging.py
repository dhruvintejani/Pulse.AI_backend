import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings


def configure_logging() -> None:
    logger.remove()
    logger.add(sys.stderr, level=settings.LOG_LEVEL, serialize=settings.LOG_JSON, backtrace=not settings.is_production, diagnose=not settings.is_production)

    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        log_dir / "pulse-ai-api.log",
        level=settings.LOG_LEVEL,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression=settings.LOG_COMPRESSION,
        serialize=settings.LOG_JSON,
        enqueue=True,
    )
