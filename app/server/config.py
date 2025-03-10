from typing import Any

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str | None
    APP_VERSION: str | None
    APP_DESCRIPTION: str | None
    APP_ENVIRONMENT: str

    APP_HOST: str
    APP_PORT: int
    APP_ENABLE_HOT_RELOAD: bool
    GENERATED_CSV_PATH: str = "app\\data\\dbdata\\generated_csv"

    TYPESENSE_API_KEY: str
    TYPESENSE_HOST: str
    TYPESENSE_PORT: int
    TYPESENSE_PROTOCOL: str
    TYPESENSE_TIMEOUT: int

    OPENAI_API_KEY: str | None
    OPENROUTER_API_KEY: str | None
    OPENROUTER_API_BASE: str | None
    GOOGLE_API_KEY: str | None

    MODEL_GARDEN_API_KEY: str | None
    MODEL_GARDEN_API_BASE: str | None

    CHAT_FAMILY: str | None
    CHAT_MODEL: str | None

    EMBEDDING_FAMILY: str | None
    EMBEDDING_MODEL: str | None
    EMBEDDING_DIMENSIONS: int

    OLLAMA_API_BASE: str | None
    HUGGINGFACEHUB_API_TOKEN: str | None

    AGENT_MAX_ITERATIONS: int
    DH_ENGINE_TIMEOUT: int
    SQL_EXECUTION_TIMEOUT: int
    UPPER_LIMIT_QUERY_RETURN_ROWS: int

    ENCRYPT_KEY: str

    class Config:
        env_file = ".env"

    def require(self, key: str) -> Any:
        val = getattr(self, key)
        if val is None:
            raise ValueError(f"Missing required config value '{key}'")
        return val
