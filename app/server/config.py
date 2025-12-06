from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra='ignore', env_file='.env')
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

    GCS_API_KEY: str | None
    GCS_SERVICE_URL: str | None

    AGENT_MAX_ITERATIONS: int
    DH_ENGINE_TIMEOUT: int
    SQL_EXECUTION_TIMEOUT: int
    UPPER_LIMIT_QUERY_RETURN_ROWS: int

    # Agent language setting ("id" for Indonesian, "en" for English)
    AGENT_LANGUAGE: str = "id"

    ENCRYPT_KEY: str

    # Long-term memory configuration
    MEMORY_BACKEND: str = "typesense"  # "typesense" or "letta"
    LETTA_API_KEY: str | None = None
    LETTA_BASE_URL: str | None = None  # For self-hosted Letta

    # Automatic learning via agentic-learning SDK
    ENABLE_AUTO_LEARNING: bool = False  # Toggle automatic memory learning
    AUTO_LEARNING_CAPTURE_ONLY: bool = False  # True = capture only, no injection

    # Memory blocks for session agent (session-specific)
    AUTO_LEARNING_MEMORY_BLOCKS: str = "human,context,user_preferences,corrections"
    # Shared memory block stored in shared agent (visible to all sessions)
    # Note: "shared_knowledge" combines legacy "business_facts" and "data_insights"
    AUTO_LEARNING_SHARED_MEMORY_BLOCK: str = "shared_knowledge"

    # MCP (Model Context Protocol) integration
    MCP_ENABLED: bool = False
    MCP_SERVERS_CONFIG: str | None = None  # Path to mcp-servers.json

    def require(self, key: str) -> Any:
        val = getattr(self, key)
        if val is None:
            raise ValueError(f"Missing required config value '{key}'")
        return val


@lru_cache()
def get_settings() -> Settings:
    """Get cached Settings instance.

    This function returns a cached singleton Settings instance,
    avoiding repeated environment variable parsing and validation.
    Use this instead of Settings() for better performance.

    Returns:
        Cached Settings instance.
    """
    return Settings()
