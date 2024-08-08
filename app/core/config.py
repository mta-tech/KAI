from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str | None
    APP_VERSION: str | None
    APP_ENVIRONMENT: str

    APP_HOST:str 
    APP_PORT:int
    APP_ENABLE_HOT_RELOAD:int = 1

    class Config:
        env_file = ".env"
