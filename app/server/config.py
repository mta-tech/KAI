from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str | None = None
    APP_VERSION: str | None = None
    APP_DESCRIPTION: str | None = None
    APP_ENVIRONMENT: str = "development"

    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8015
    APP_ENABLE_HOT_RELOAD: bool = False
    GENERATED_CSV_PATH: str = "app\\data\\dbdata\\generated_csv"

    TYPESENSE_API_KEY: str = "xyz"
    TYPESENSE_HOST: str = "localhost"
    TYPESENSE_PORT: int = 8108
    TYPESENSE_PROTOCOL: str = "http"
    TYPESENSE_TIMEOUT: int = 5

    OPENAI_API_KEY: str | None = None
    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_API_BASE: str | None = None
    GOOGLE_API_KEY: str | None = None

    MODEL_GARDEN_API_KEY: str | None = None
    MODEL_GARDEN_API_BASE: str | None = None

    CHAT_FAMILY: str | None = None
    CHAT_MODEL: str | None = None

    EMBEDDING_FAMILY: str | None = None
    EMBEDDING_MODEL: str | None = None
    EMBEDDING_DIMENSIONS: int = 768

    OLLAMA_API_BASE: str | None = None
    HUGGINGFACEHUB_API_TOKEN: str | None = None

    GCS_API_KEY: str | None = None
    GCS_SERVICE_URL: str | None = None

    AGENT_MAX_ITERATIONS: int = 20
    DH_ENGINE_TIMEOUT: int = 180
    SQL_EXECUTION_TIMEOUT: int = 60
    UPPER_LIMIT_QUERY_RETURN_ROWS: int = 50

    MEMORY_BACKEND: str = "typesense"
    LETTA_API_KEY: str | None = None
    LETTA_BASE_URL: str | None = None

    ENABLE_AUTO_LEARNING: bool = False
    AUTO_LEARNING_MEMORY_BLOCKS: str = "persona,human"
    AUTO_LEARNING_CAPTURE_ONLY: bool = False

    AGENT_LANGUAGE: str = "en"
    MCP_ENABLED: bool = False

    ENCRYPT_KEY: str = ""

    class Config:
        env_file = ".env.local"
        extra = "ignore"  # Ignore extra environment variables

    def require(self, key: str) -> Any:
        val = getattr(self, key)
        if val is None:
            raise ValueError(f"Missing required config value '{key}'")
        return val


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance loaded from environment / .env.local."""
    return Settings()
