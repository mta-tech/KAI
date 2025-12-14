"""Pydantic AI agents for chart visualization."""

from __future__ import annotations

import logging
from typing import Any

from pydantic_ai import Agent

from app.modules.chartviz.models import ChartType, ChartWidget, ChartRecommendation
from app.modules.chartviz.prompts import (
    get_generation_system_prompt,
    get_recommendation_system_prompt,
    format_data_for_prompt,
    format_recommendation_prompt,
)
from app.utils.model.pydantic_ai_model import get_pydantic_ai_model

logger = logging.getLogger(__name__)


class ChartGenerationAgent:
    """Agent for generating chart configurations using Pydantic AI."""

    def __init__(
        self,
        model_family: str | None = None,
        model_name: str | None = None,
    ):
        """Initialize the chart generation agent.

        Args:
            model_family: LLM provider family (google, openai, ollama, etc.)
            model_name: Model name (e.g., gemini-2.0-flash, gpt-4o)
        """
        self.model_family = model_family
        self.model_name = model_name

    async def generate(
        self,
        data: list[dict[str, Any]],
        chart_type: ChartType,
        user_prompt: str | None = None,
        language: str = "id",
    ) -> ChartWidget:
        """Generate chart configuration for the specified chart type.

        Args:
            data: SQL result data to visualize
            chart_type: Target chart type
            user_prompt: Original user question for context
            language: Language for labels (id/en)

        Returns:
            ChartWidget configuration

        Raises:
            ValueError: If data is empty
            Exception: If generation fails
        """
        if not data:
            raise ValueError("Data cannot be empty")

        # Get model instance
        model = get_pydantic_ai_model(self.model_family, self.model_name)

        # Create agent with structured output
        agent: Agent[None, ChartWidget] = Agent(
            model,
            result_type=ChartWidget,
            system_prompt=get_generation_system_prompt(chart_type, language),
        )

        # Format the prompt
        prompt = format_data_for_prompt(data, user_prompt, language)

        try:
            # Run the agent
            result = await agent.run(prompt)
            widget = result.data

            # Ensure widget_type matches requested type
            widget.widget_type = chart_type

            # Copy data to widget if not populated
            if not widget.widget_data:
                widget.widget_data = data

            return widget

        except Exception as e:
            logger.error(f"Chart generation failed: {e}")
            raise


class ChartRecommendationAgent:
    """Agent for recommending chart types using Pydantic AI."""

    def __init__(
        self,
        model_family: str | None = None,
        model_name: str | None = None,
    ):
        """Initialize the chart recommendation agent.

        Args:
            model_family: LLM provider family (google, openai, ollama, etc.)
            model_name: Model name (e.g., gemini-2.0-flash, gpt-4o)
        """
        self.model_family = model_family
        self.model_name = model_name

    async def recommend(
        self,
        data: list[dict[str, Any]],
        user_prompt: str | None = None,
        language: str = "id",
    ) -> ChartRecommendation:
        """Recommend the best chart type for the data.

        Args:
            data: SQL result data to analyze
            user_prompt: Original user question for context
            language: Language for response (id/en)

        Returns:
            ChartRecommendation with type, confidence, and rationale

        Raises:
            ValueError: If data is empty
            Exception: If recommendation fails
        """
        if not data:
            raise ValueError("Data cannot be empty")

        # Get model instance
        model = get_pydantic_ai_model(self.model_family, self.model_name)

        # Create agent with structured output
        agent: Agent[None, ChartRecommendation] = Agent(
            model,
            result_type=ChartRecommendation,
            system_prompt=get_recommendation_system_prompt(language),
        )

        # Format the prompt
        prompt = format_recommendation_prompt(data, user_prompt, language)

        try:
            # Run the agent
            result = await agent.run(prompt)
            return result.data

        except Exception as e:
            logger.error(f"Chart recommendation failed: {e}")
            raise


# Convenience functions for direct use


async def generate_chart(
    data: list[dict[str, Any]],
    chart_type: ChartType,
    user_prompt: str | None = None,
    language: str = "id",
    model_family: str | None = None,
    model_name: str | None = None,
) -> ChartWidget:
    """Generate chart configuration.

    Convenience function that creates an agent and generates a chart.

    Args:
        data: SQL result data to visualize
        chart_type: Target chart type
        user_prompt: Original user question
        language: Language for labels
        model_family: Optional LLM provider override
        model_name: Optional model name override

    Returns:
        ChartWidget configuration
    """
    agent = ChartGenerationAgent(model_family, model_name)
    return await agent.generate(data, chart_type, user_prompt, language)


async def recommend_chart(
    data: list[dict[str, Any]],
    user_prompt: str | None = None,
    language: str = "id",
    model_family: str | None = None,
    model_name: str | None = None,
) -> ChartRecommendation:
    """Recommend best chart type.

    Convenience function that creates an agent and recommends a chart type.

    Args:
        data: SQL result data to analyze
        user_prompt: Original user question
        language: Language for response
        model_family: Optional LLM provider override
        model_name: Optional model name override

    Returns:
        ChartRecommendation with type and rationale
    """
    agent = ChartRecommendationAgent(model_family, model_name)
    return await agent.recommend(data, user_prompt, language)


async def auto_generate_chart(
    data: list[dict[str, Any]],
    user_prompt: str | None = None,
    language: str = "id",
    model_family: str | None = None,
    model_name: str | None = None,
) -> ChartWidget:
    """Automatically recommend and generate chart.

    Convenience function that recommends the best chart type
    and then generates the configuration.

    Args:
        data: SQL result data to visualize
        user_prompt: Original user question
        language: Language for labels
        model_family: Optional LLM provider override
        model_name: Optional model name override

    Returns:
        ChartWidget configuration with auto-selected type
    """
    # First, get recommendation
    recommendation = await recommend_chart(
        data, user_prompt, language, model_family, model_name
    )

    # Then generate with recommended type
    return await generate_chart(
        data, recommendation.chart_type, user_prompt, language, model_family, model_name
    )


__all__ = [
    "ChartGenerationAgent",
    "ChartRecommendationAgent",
    "generate_chart",
    "recommend_chart",
    "auto_generate_chart",
]
