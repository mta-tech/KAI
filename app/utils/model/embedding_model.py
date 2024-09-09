from typing import Any

# from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_openai import OpenAIEmbeddings
from overrides import override

from app.modules.database_connection.models import DatabaseConnection
from app.utils.model import LLMModel

DIMENSIONS = 1024


class EmbeddingModel(LLMModel):
    @override
    def get_model(
        self,
        database_connection: DatabaseConnection | None = None,
        model_family: str = "openai",
        model_name: str = "text-embedding-3-small",
        api_base: str | None = None,
        **kwargs: Any,
    ) -> Any:
        if model_family == "openai":
            return OpenAIEmbeddings(
                model=model_name,
                api_key=self.settings.require("OPENAI_API_KEY"),
                model=model_name,
                api_key=self.settings.require("OPENAI_API_KEY"),
                dimensions=DIMENSIONS,
                **kwargs,
            )

          # if model_family == "huggingface":
        #     return HuggingFaceEndpointEmbeddings(
        #         model=model_name,
        #         task="feature-extraction",
        #         huggingfacehub_api_token=self.settings.require(
        #             "HUGGINGFACEHUB_API_TOKEN"
        #         ),
        #         dimensions=DIMENSIONS,
        #         **kwargs,
        #     )
        raise ValueError("No model family found upon embedding model")
