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
        model_family: str,
        model_name: str,
        api_base: str | None = None,
        **kwargs: Any,
    ) -> Any:
        pass
