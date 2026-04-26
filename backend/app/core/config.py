from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_ENV: str = "development"
    APP_NAME: str = "STEI Accreditation System"
    BACKEND_URL: str = "http://localhost:8000"

    # Database
    DATABASE_URL: str = ""

    @model_validator(mode="after")
    def check_database_url(self) -> "Settings":
        if not self.DATABASE_URL:
            raise ValueError(
                "DATABASE_URL is not set. "
                "Please copy .env.example to .env and fill in your database connection string."
            )
        return self

    # JWT
    SECRET_KEY: str = "change-this-to-a-long-random-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7


@lru_cache()
def get_settings() -> Settings:
    return Settings()
