from functools import lru_cache
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    APP_NAME: str = "Pulse AI API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "pulse_ai"
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = 5000
    SKIP_DATABASE_INIT: bool = False

    BACKEND_CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    BACKEND_CORS_ALLOW_CREDENTIALS: bool = True
    BACKEND_CORS_ALLOW_METHODS: list[str] = Field(default_factory=lambda: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    BACKEND_CORS_ALLOW_HEADERS: list[str] = Field(default_factory=lambda: ["Authorization", "Content-Type", "X-Request-ID", "X-CSRF-Token"])
    BACKEND_CORS_EXPOSE_HEADERS: list[str] = Field(default_factory=lambda: ["X-Request-ID", "X-Process-Time-Ms"])

    CLERK_ISSUER: str = ""
    CLERK_JWKS_URL: str = ""
    CLERK_AUDIENCE: str | None = None
    CLERK_AUTHORIZED_PARTIES: list[str] = Field(default_factory=list)
    CLERK_JWKS_CACHE_SECONDS: int = 300
    CLERK_SECRET_KEY: str | None = None
    CLERK_API_BASE_URL: str = "https://api.clerk.com/v1"

    ADMIN_EMAILS: list[str] = Field(default_factory=list)
    ADMIN_CLERK_USER_IDS: list[str] = Field(default_factory=list)

    INTERNAL_JWT_SECRET: str = "change-this-in-production"
    INTERNAL_JWT_ALGORITHM: str = "HS256"
    INTERNAL_JWT_EXPIRES_MINUTES: int = 15

    RATE_LIMIT_DEFAULT: str = "120/minute"
    RATE_LIMIT_HEALTH: str = "60/minute"
    RATE_LIMIT_STORAGE_URI: str = "memory://"

    SECURITY_ALLOWED_HOSTS: list[str] = Field(default_factory=lambda: ["*"])
    SECURITY_HEADERS_ENABLED: bool = True
    SECURITY_ENABLE_HSTS: bool = False
    SECURITY_HSTS_MAX_AGE_SECONDS: int = 31536000
    SECURITY_CONTENT_SECURITY_POLICY: str = "default-src 'self'; frame-ancestors 'none'; base-uri 'self'"
    SECURITY_MAX_REQUEST_SIZE_BYTES: int = 2_097_152
    SECURITY_INPUT_SANITIZATION_ENABLED: bool = True
    SECURITY_BLOCK_SUSPICIOUS_INPUT: bool = True

    DOCUMENT_STORAGE_PROVIDER: str = "metadata"
    DOCUMENT_MAX_UPLOAD_SIZE_MB: int = 25
    DOCUMENT_PREVIEW_MAX_CHARS: int = 5000
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None
    CLOUDINARY_FOLDER: str = "pulse-ai/documents"

    AI_DEFAULT_PROVIDER: str = "mock"
    AI_ENABLED_PROVIDERS: list[str] = Field(default_factory=lambda: ["mock"])
    AI_DEFAULT_MODEL: str = "pulse-ai-default"
    AI_STREAM_PLACEHOLDER_DELAY_MS: int = 35
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    CLAUDE_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    DEEPSEEK_API_KEY: str | None = None

    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False
    LOG_DIR: str = "logs"
    LOG_ROTATION: str = "50 MB"
    LOG_RETENTION: str = "30 days"
    LOG_COMPRESSION: str = "zip"
    LOG_PERFORMANCE_THRESHOLD_MS: int = 1000

    @field_validator(
        "BACKEND_CORS_ORIGINS",
        "BACKEND_CORS_ALLOW_METHODS",
        "BACKEND_CORS_ALLOW_HEADERS",
        "BACKEND_CORS_EXPOSE_HEADERS",
        "CLERK_AUTHORIZED_PARTIES",
        "AI_ENABLED_PROVIDERS",
        "ADMIN_EMAILS",
        "ADMIN_CLERK_USER_IDS",
        "SECURITY_ALLOWED_HOSTS",
        mode="before",
    )
    @classmethod
    def parse_csv_list(cls, value: str | list[str] | None) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator(
        "CLERK_AUDIENCE",
        "CLERK_SECRET_KEY",
        "CLOUDINARY_CLOUD_NAME",
        "CLOUDINARY_API_KEY",
        "CLOUDINARY_API_SECRET",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "CLAUDE_API_KEY",
        "GROQ_API_KEY",
        "DEEPSEEK_API_KEY",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, value: str | None) -> str | None:
        if value == "":
            return None
        return value

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        if self.is_production:
            if self.SKIP_DATABASE_INIT:
                raise ValueError("SKIP_DATABASE_INIT cannot be enabled in production")
            if "*" in self.BACKEND_CORS_ORIGINS and self.BACKEND_CORS_ALLOW_CREDENTIALS:
                raise ValueError("Wildcard CORS origins cannot be used with credentials in production")
            if self.SECURITY_ALLOWED_HOSTS == ["*"]:
                raise ValueError("SECURITY_ALLOWED_HOSTS must be configured in production")
            if not self.CLERK_ISSUER or not self.CLERK_JWKS_URL:
                raise ValueError("Clerk issuer and JWKS URL are required in production")
        return self

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def should_skip_database_init(self) -> bool:
        return self.SKIP_DATABASE_INIT or self.ENVIRONMENT.lower() in {"ci", "test"}

    @property
    def document_max_upload_size_bytes(self) -> int:
        return self.DOCUMENT_MAX_UPLOAD_SIZE_MB * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
