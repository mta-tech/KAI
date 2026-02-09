"""
Official Google GenAI SDK Embeddings Wrapper

This module provides a wrapper around the official google-genai SDK
that implements the LangChain Embeddings interface for backward compatibility.
"""

from typing import List

from google import genai
from google.genai import types
from langchain_core.embeddings import Embeddings


class GoogleGenAIEmbeddingsOfficial(Embeddings):
    """
    Wrapper around official Google GenAI SDK that implements LangChain's Embeddings interface.

    This uses the new google-genai SDK directly instead of the LangChain wrapper,
    ensuring proper support for output_dimensionality and future Google API updates.
    """

    def __init__(
        self,
        model: str = "gemini-embedding-001",
        api_key: str | None = None,
        dimensions: int = 768,
        task_type: str = "RETRIEVAL_QUERY",
    ):
        """
        Initialize the Google GenAI embeddings client.

        Args:
            model: The Google embedding model to use (e.g., "gemini-embedding-001")
            api_key: Google API key. If None, will use GOOGLE_API_KEY env var
            dimensions: Output dimensionality for embeddings (default: 768)
            task_type: Task type for the embedding (RETRIEVAL_QUERY, RETRIEVAL_DOCUMENT, etc.)
        """
        self.model = model
        self.api_key = api_key
        self.dimensions = dimensions
        self.task_type = task_type
        self._client = None

    def _get_client(self) -> genai.Client:
        """Lazy initialization of the Google GenAI client."""
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents using Google GenAI.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors, one for each text
        """
        client = self._get_client()
        embeddings = []

        for text in texts:
            result = client.models.embed_content(
                model=self.model,
                contents=text,
                config=types.EmbedContentConfig(
                    output_dimensionality=self.dimensions,
                    task_type=self.task_type,
                ),
            )
            [embedding_obj] = result.embeddings
            embeddings.append(list(embedding_obj.values))

        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text using Google GenAI.

        Args:
            text: Text string to embed

        Returns:
            Embedding vector as a list of floats
        """
        client = self._get_client()
        result = client.models.embed_content(
            model=self.model,
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=self.dimensions,
                task_type=self.task_type,
            ),
        )
        [embedding_obj] = result.embeddings
        return list(embedding_obj.values)
