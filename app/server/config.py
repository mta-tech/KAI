from typing import Any

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    load_dotenv()

    APP_NAME: str | None
    APP_VERSION: str | None
    APP_DESCRIPTION: str | None
    APP_ENVIRONMENT: str

    APP_HOST: str
    APP_PORT: int
    APP_ENABLE_HOT_RELOAD: bool

    TYPESENSE_API_KEY: str
    TYPESENSE_HOST: str
    TYPESENSE_PORT: int
    TYPESENSE_PROTOCOL: str
    TYPESENSE_TIMEOUT: int

    OPENAI_API_KEY: str | None
    DEFAULT_AI_MODEL: str | None
    DEFAULT_EMBEDDING_MODEL: str | None

    ENCRYPT_KEY: str

    class Config:
        env_file = ".env"

    def require(self, key: str) -> Any:
        val = self[key]
        if val is None:
            raise ValueError(f"Missing required config value '{key}'")
        return val

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)
