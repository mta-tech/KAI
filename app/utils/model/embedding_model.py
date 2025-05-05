from typing import Any

# from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_core.embeddings import Embeddings
from overrides import override

from app.modules.database_connection.models import DatabaseConnection
from app.utils.model import LLMModel


class EmbeddingModel(LLMModel):
    @override
    def get_model(
        self,
        database_connection: DatabaseConnection | None = None,
        model_family: str | None = None,
        model_name: str | None = None,
        api_base: str | None = None,
        **kwargs: Any,
    ) -> Embeddings:
        model_family = model_family or self.settings.require("EMBEDDING_FAMILY")
        model_name = model_name or self.settings.require("EMBEDDING_MODEL")
        dimensions = self.settings.require("EMBEDDING_DIMENSIONS")
        if model_family == "openai":
            return OpenAIEmbeddings(
                model=model_name,
                api_key=self.settings.require("OPENAI_API_KEY"),
                dimensions=dimensions,
                **kwargs,
            )
        if model_family == "google":
            return GoogleGenerativeAIEmbeddings(
                model=model_name,
                api_key=self.settings.require("GOOGLE_API_KEY"),
                dimensions=dimensions,
                task_type='RETRIEVAL_QUERY',
                **kwargs,
            )
        if model_family == "ollama":
            return OllamaEmbeddings(
                model=model_name,
                base_url=self.settings.require("OLLAMA_API_BASE"),
                **kwargs,
            )

        # if model_family == "huggingface":
        #     return HuggingFaceEndpointEmbeddings(
        #         model=model_name,
        #         task="feature-extraction",
        #         huggingfacehub_api_token=self.settings.require(
        #             "HUGGINGFACEHUB_API_TOKEN"
        #         ),
        #           dimensions=dimensions,
        #         **kwargs,
        #     )
        raise ValueError("No model family found upon embedding model")
