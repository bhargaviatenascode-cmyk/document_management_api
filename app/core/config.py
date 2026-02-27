from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Document Management API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./document_management.db"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7
    upload_dir: str = "uploads"
    max_file_size_bytes: int = 5 * 1024 * 1024
    allowed_content_types: list[str] = ["application/pdf", "image/png", "image/jpeg"]
    rate_limit_login_per_minute: int = 5
    redis_url: str = "redis://localhost:6379/0"
    log_file: str = "app.log"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @field_validator("allowed_content_types", mode="before")
    @classmethod
    def parse_allowed_content_types(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
