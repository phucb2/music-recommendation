"""Application settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.env_bootstrap import _BACKEND_ROOT, _REPO_ROOT, load_repo_environment

load_repo_environment()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=(
            _REPO_ROOT / ".env",
            _REPO_ROOT / ".env.local",
            _BACKEND_ROOT / ".env",
        ),
    )

    database_url: str = "postgresql://postgres:postgres@localhost:5432/music"
    cors_origins: str = "http://localhost:3000"


settings = Settings()
