from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "RateSimulator"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ratesimulator"
    redis_url: str = "redis://localhost:6379/0"

    fred_api_key: str = ""
    rbi_data_path: str = "./data/rbi_repo_rates.csv"

    default_n_paths: int = 10000
    max_n_paths: int = 50000
    cache_ttl_seconds: int = 3600

    cors_origins: list[str] = ["http://localhost:5173", "https://ratesimulator.vercel.app"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
