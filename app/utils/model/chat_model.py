from typing import Any

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from overrides import override

from app.modules.database_connection.models import DatabaseConnection
from app.utils.model import LLMModel


class ChatModel(LLMModel):
    @override
    def get_model(
        self,
        database_connection: DatabaseConnection,
        model_family="openai",
        model_name="gpt-4-turbo-preview",
        api_base: str | None = None,
        **kwargs: Any,
    ) -> Any:
        if model_family == "openai":
            return ChatOpenAI(
                model_name=model_name,
                openai_api_key=self.settings.require("OPENAI_API_KEY"),
                openai_api_base=api_base,
                seed=0,
                **kwargs,
            )
        if model_family == "ollama":
            return ChatOllama(
                model=model_name,
                base_url=self.settings.require("OLLAMA_API_BASE"),
                **kwargs,
            )
        raise ValueError("No model family found upon chat model")
