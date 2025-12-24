"""Chart visualization service for orchestrating chart generation."""

from __future__ import annotations

import logging
from typing import Any

from app.modules.chartviz.models import (
    ChartType,
    ChartWidget,
    ChartRecommendation,
)
from app.modules.chartviz.agent import (
    ChartGenerationAgent,
    ChartRecommendationAgent,
)

logger = logging.getLogger(__name__)


class ChartVizService:
    """Service for chart visualization operations.

    Orchestrates chart generation and recommendation using Pydantic AI agents.
    Provides additional business logic like delta percentage calculation.
    """

    def __init__(
        self,
        model_family: str | None = None,
        model_name: str | None = None,
    ):
        """Initialize the chart visualization service.

        Args:
            model_family: LLM provider family (google, openai, ollama, etc.)
            model_name: Model name (e.g., gemini-2.0-flash, gpt-4o)
        """
        self.generation_agent = ChartGenerationAgent(model_family, model_name)
        self.recommendation_agent = ChartRecommendationAgent(model_family, model_name)

    async def generate_chart(
        self,
        data: list[dict[str, Any]],
        chart_type: ChartType,
        user_prompt: str | None = None,
        language: str = "id",
    ) -> ChartWidget:
        """Generate chart configuration for specified type.

        Args:
            data: SQL result data to visualize
            chart_type: Target chart type
            user_prompt: Original user question for context
            language: Language for labels (id/en)

        Returns:
            ChartWidget configuration
        """
        widget = await self.generation_agent.generate(
            data, chart_type, user_prompt, language
        )

        # Post-process: calculate delta if applicable
        if chart_type in (ChartType.KPI, ChartType.LINE, ChartType.AREA):
            widget = self._calculate_delta(widget, data)

        return widget

    async def recommend_chart(
        self,
        data: list[dict[str, Any]],
        user_prompt: str | None = None,
        language: str = "id",
    ) -> ChartRecommendation:
        """Recommend best chart type for data.

        Args:
            data: SQL result data to analyze
            user_prompt: Original user question for context
            language: Language for response (id/en)

        Returns:
            ChartRecommendation with type, confidence, and rationale
        """
        return await self.recommendation_agent.recommend(data, user_prompt, language)

    async def auto_generate(
        self,
        data: list[dict[str, Any]],
        user_prompt: str | None = None,
        language: str = "id",
    ) -> ChartWidget:
        """Automatically recommend and generate chart.

        First recommends the best chart type, then generates configuration.

        Args:
            data: SQL result data to visualize
            user_prompt: Original user question for context
            language: Language for labels (id/en)

        Returns:
            ChartWidget with auto-selected type
        """
        # Get recommendation
        recommendation = await self.recommend_chart(data, user_prompt, language)
        logger.info(
            f"Recommended chart: {recommendation.chart_type.value} "
            f"(confidence: {recommendation.confidence:.2f})"
        )

        # Generate with recommended type
        return await self.generate_chart(
            data, recommendation.chart_type, user_prompt, language
        )

    async def generate_from_analysis(
        self,
        analysis_result: dict[str, Any],
        chart_type: ChartType | None = None,
        language: str = "id",
    ) -> ChartWidget:
        """Generate chart from analysis service result.

        Extracts relevant data from analysis result and generates chart.

        Args:
            analysis_result: Result from AnalysisService
            chart_type: Specific chart type (None for auto-recommend)
            language: Language for labels (id/en)

        Returns:
            ChartWidget configuration
        """
        # Extract data from analysis result
        # Analysis result may have 'data', 'results', or nested structure
        data = (
            analysis_result.get("data")
            or analysis_result.get("results")
            or analysis_result.get("rows")
            or []
        )

        if not data:
            raise ValueError("No data found in analysis result")

        # Extract user question for context
        user_prompt = analysis_result.get("prompt") or analysis_result.get("query")

        if chart_type:
            return await self.generate_chart(data, chart_type, user_prompt, language)
        else:
            return await self.auto_generate(data, user_prompt, language)

    def _calculate_delta(
        self,
        widget: ChartWidget,
        data: list[dict[str, Any]],
    ) -> ChartWidget:
        """Calculate delta percentage for trend/KPI charts.

        Compares first and last values in the data series.

        Args:
            widget: Chart widget to update
            data: Original data for calculation

        Returns:
            Updated widget with delta percentage
        """
        if len(data) < 2:
            return widget

        # Try to find numeric value column
        value_key = widget.y_axis_key or widget.value_key

        if not value_key:
            # Try to detect numeric column
            sample = data[0]
            for key, val in sample.items():
                if isinstance(val, (int, float)) and not key.lower().endswith("id"):
                    value_key = key
                    break

        if not value_key:
            return widget

        try:
            # Get first and last values
            first_val = data[0].get(value_key)
            last_val = data[-1].get(value_key)

            if first_val and last_val and isinstance(first_val, (int, float)):
                # Calculate percentage change
                if first_val != 0:
                    delta = ((last_val - first_val) / abs(first_val)) * 100
                    widget.widget_delta_percentages = round(delta, 2)
        except (KeyError, TypeError, ZeroDivisionError) as e:
            logger.debug(f"Could not calculate delta: {e}")

        return widget


# Singleton instance for convenience
_service_instance: ChartVizService | None = None


def get_chartviz_service(
    model_family: str | None = None,
    model_name: str | None = None,
) -> ChartVizService:
    """Get or create ChartVizService instance.

    Args:
        model_family: LLM provider family
        model_name: Model name

    Returns:
        ChartVizService instance
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = ChartVizService(model_family, model_name)
    return _service_instance


__all__ = [
    "ChartVizService",
    "get_chartviz_service",
]
