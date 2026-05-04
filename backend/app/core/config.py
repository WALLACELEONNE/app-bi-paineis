from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    PROJECT_NAME: str = "BI Agro Platform"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "DEBUG"

    DATABASE_URL: str = (
        "postgresql+asyncpg://bi_admin:bi_secret_dev@localhost:5432/bi_agro"
    )
    DATABASE_URL_SYNC: str = (
        "postgresql+psycopg2://bi_admin:bi_secret_dev@localhost:5432/bi_agro"
    )

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_URL: str = "redis://localhost:6379/1"

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minio_admin"
    MINIO_SECRET_KEY: str = "minio_secret_dev"
    MINIO_BUCKET: str = "bi-uploads"
    MINIO_SECURE: bool = False

    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:5173"]'

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
