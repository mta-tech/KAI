from pydantic_settings import BaseSettings


class Settings(BaseSettings):
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

    class Config:
        env_file = ".env"
