"""Pydantic AI model factory for multi-provider support."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pydantic_ai.models import Model


@lru_cache()
def get_settings() -> Any:
    """Get cached settings instance.

    Uses lazy import to avoid circular dependency with app.server.
    """
    from app.server.config import Settings
    return Settings()


def get_pydantic_ai_model_string(
    model_family: str | None = None,
    model_name: str | None = None,
) -> str:
    """
    Map KAI provider config to Pydantic AI model string.

    Args:
        model_family: LLM provider family (google, openai, ollama, openrouter)
        model_name: Model name (e.g., gemini-2.0-flash, gpt-4o)

    Returns:
        Pydantic AI model string (e.g., 'google-gla:gemini-2.0-flash')
    """
    settings = get_settings()
    family = model_family or settings.CHAT_FAMILY or "google"
    model = model_name or settings.CHAT_MODEL or "gemini-2.0-flash"

    if family == "google":
        return f"google-gla:{model}"
    elif family == "openai":
        return f"openai:{model}"
    elif family == "openrouter":
        # OpenRouter uses OpenAI-compatible API
        return f"openai:{model}"
    elif family == "ollama":
        # Ollama uses OpenAI-compatible API
        return f"openai:{model}"
    elif family == "model_garden":
        # Model Garden uses OpenAI-compatible API
        return f"openai:{model}"
    else:
        # Default to OpenAI format
        return f"openai:{model}"


def setup_pydantic_ai_env() -> None:
    """
    Set up environment variables for Pydantic AI providers.

    Pydantic AI reads API keys from environment variables:
    - OPENAI_API_KEY for OpenAI
    - GOOGLE_API_KEY for Google (Gemini)
    - OPENAI_BASE_URL for custom base URLs

    This function ensures the keys from Settings are available.
    """
    settings = get_settings()

    # Set OpenAI API key if available
    if settings.OPENAI_API_KEY and "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

    # Set Google API key if available
    if settings.GOOGLE_API_KEY and "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY

    # Handle OpenRouter - requires setting base URL
    if settings.OPENROUTER_API_KEY:
        if "OPENAI_API_KEY" not in os.environ:
            os.environ["OPENAI_API_KEY"] = settings.OPENROUTER_API_KEY
        if settings.OPENROUTER_API_BASE and "OPENAI_BASE_URL" not in os.environ:
            os.environ["OPENAI_BASE_URL"] = settings.OPENROUTER_API_BASE

    # Handle Ollama - requires setting base URL
    if settings.OLLAMA_API_BASE and "OPENAI_BASE_URL" not in os.environ:
        os.environ["OPENAI_BASE_URL"] = settings.OLLAMA_API_BASE
        # Ollama doesn't require an API key, but Pydantic AI might expect one
        if "OPENAI_API_KEY" not in os.environ:
            os.environ["OPENAI_API_KEY"] = "ollama"


def get_pydantic_ai_model(
    model_family: str | None = None,
    model_name: str | None = None,
) -> "Model":
    """
    Get a Pydantic AI model instance.

    This is a convenience function that returns a model object
    that can be passed to Agent() constructor.

    Args:
        model_family: LLM provider family
        model_name: Model name

    Returns:
        Pydantic AI Model instance
    """
    # Ensure environment is set up
    setup_pydantic_ai_env()

    settings = get_settings()
    family = model_family or settings.CHAT_FAMILY or "google"

    if family == "google":
        from pydantic_ai.models.gemini import GeminiModel
        model = model_name or settings.CHAT_MODEL or "gemini-2.0-flash"
        return GeminiModel(model)

    elif family == "openai":
        from pydantic_ai.models.openai import OpenAIModel
        model = model_name or settings.CHAT_MODEL or "gpt-4o"
        return OpenAIModel(model)

    elif family == "openrouter":
        from pydantic_ai.models.openai import OpenAIModel
        model = model_name or settings.CHAT_MODEL or "gpt-4o"
        return OpenAIModel(
            model,
            base_url=settings.OPENROUTER_API_BASE,
            api_key=settings.require("OPENROUTER_API_KEY"),
        )

    elif family == "ollama":
        from pydantic_ai.models.openai import OpenAIModel
        model = model_name or settings.CHAT_MODEL or "llama3.2"
        return OpenAIModel(
            model,
            base_url=settings.require("OLLAMA_API_BASE"),
            api_key="ollama",  # Ollama doesn't need real API key
        )

    elif family == "model_garden":
        from pydantic_ai.models.openai import OpenAIModel
        model = model_name or settings.CHAT_MODEL or "gpt-4o"
        return OpenAIModel(
            model,
            base_url=settings.MODEL_GARDEN_API_BASE,
            api_key=settings.require("MODEL_GARDEN_API_KEY"),
        )

    else:
        raise ValueError(f"Unsupported model family: {family}")


__all__ = [
    "get_pydantic_ai_model_string",
    "get_pydantic_ai_model",
    "setup_pydantic_ai_env",
]
