from typing import Any

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
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
        if model_family == "openrouter":
            if api_base is None:
                api_base = self.settings.require("OPENROUTER_API_BASE")
            return ChatOpenAI(
                model_name=model_name,
                api_key=self.settings.require("OPENROUTER_API_KEY"),
                base_url=api_base,
                seed=0,
                **kwargs,
            )
        if model_family == "ollama":
            return ChatOllama(
                model=model_name,
                base_url=self.settings.require("OLLAMA_API_BASE"),
                **kwargs,
            )
        if model_family == "model_garden":
            if api_base is None:
                api_base = self.settings.require("MODEL_GARDEN_API_BASE")
            return ChatOpenAI(
                model_name=model_name,
                api_key=self.settings.require("MODEL_GARDEN_API_KEY"),
                base_url=api_base,
                seed=0,
                **kwargs,
            )
        if model_family == "google":
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=self.settings.require("GOOGLE_API_KEY"),
                **kwargs,
            )
        raise ValueError("No model family found upon chat model")
