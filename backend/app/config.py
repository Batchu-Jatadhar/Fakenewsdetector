from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./fakenews.db"
    redis_url: str = "redis://localhost:6379"
    jwt_secret: str = "change-me-to-a-random-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    google_factcheck_api_key: Optional[str] = None
    newsapi_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "openrouter/auto"
    blockchain_enabled: bool = False
    blockchain_endpoint: Optional[str] = None
    cors_origins: str = "http://localhost:3000"
    model_dir: str = "ml/models"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
