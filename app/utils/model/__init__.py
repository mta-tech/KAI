from abc import ABC, abstractmethod
from typing import Any

from app.modules.database_connection.models import DatabaseConnection
from app.server.config import Settings


class LLMModel(ABC):
    def __init__(self):
        self.settings = Settings()

    @abstractmethod
    def get_model(
        self,
        database_connection: DatabaseConnection,
        model_family="openai",
        model_name="gpt-3.5-turbo-preview",
        api_base: str | None = None,
        **kwargs: Any,
    ) -> Any:
        pass
