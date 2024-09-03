from typing import Any

from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_openai import ChatOpenAI
from overrides import override

from app.modules.database_connection.models import DatabaseConnection
from app.utils.model import LLMModel


class EmbeddingModel(LLMModel):
    @override
    def get_model(
        self,
        database_connection: DatabaseConnection,
        model_family="openai",
        model_name="text-embedding-3-large",
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
        if model_family == "huggingface":
            return HuggingFaceEndpointEmbeddings(
                model=model_name,
                task="feature-extraction",
                huggingfacehub_api_token=self.settings.require(
                    "HUGGINGFACEHUB_API_TOKEN"
                ),
                **kwargs,
            )
        raise ValueError("No valid API key environment variable found")
