"""Chart visualization module for JavaScript chart libraries.

This module provides AI-powered chart generation using Pydantic AI,
producing JSON configurations compatible with popular JavaScript
chart libraries like Chart.js, ECharts, Recharts, D3.js, and Plotly.js.

Features:
- Generate chart configurations from SQL result data
- AI-powered chart type recommendation
- Language-aware prompts (Indonesian/English)
- Support for multiple chart types: line, bar, pie, scatter, area, kpi, table

Usage:
    from app.modules.chartviz import ChartVizService, ChartType, ChartWidget

    service = ChartVizService()

    # Generate specific chart type
    widget = await service.generate_chart(
        data=[{"month": "Jan", "value": 100}, ...],
        chart_type=ChartType.LINE,
        language="id"
    )

    # Auto-recommend and generate
    widget = await service.auto_generate(
        data=[...],
        user_prompt="Show monthly revenue trend"
    )
"""

from app.modules.chartviz.models import (
    ChartType,
    ChartWidget,
    ChartRecommendation,
    GenerateChartRequest,
    RecommendChartRequest,
    AutoChartRequest,
    SessionVisualizeRequest,
)
from app.modules.chartviz.service import (
    ChartVizService,
    get_chartviz_service,
)
from app.modules.chartviz.agent import (
    ChartGenerationAgent,
    ChartRecommendationAgent,
    generate_chart,
    recommend_chart,
    auto_generate_chart,
)
from app.modules.chartviz.api import router
from app.modules.chartviz.exceptions import (
    ChartVizError,
    ChartVizGenerationError,
    ChartVizRecommendationError,
    AutoChartGenerationError,
    AnalysisDataExtractionError,
    InvalidChartTypeError,
)


__all__ = [
    # Models
    "ChartType",
    "ChartWidget",
    "ChartRecommendation",
    "GenerateChartRequest",
    "RecommendChartRequest",
    "AutoChartRequest",
    "SessionVisualizeRequest",
    # Service
    "ChartVizService",
    "get_chartviz_service",
    # Agents
    "ChartGenerationAgent",
    "ChartRecommendationAgent",
    # Convenience functions
    "generate_chart",
    "recommend_chart",
    "auto_generate_chart",
    # Router
    "router",
    # Exceptions
    "ChartVizError",
    "ChartVizGenerationError",
    "ChartVizRecommendationError",
    "AutoChartGenerationError",
    "AnalysisDataExtractionError",
    "InvalidChartTypeError",
]
