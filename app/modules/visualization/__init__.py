"""Visualization module for KAI."""

from app.modules.visualization.exceptions import (
    ChartExportError,
    ChartGenerationError,
    ChartRecommendationError,
    InvalidChartTypeError,
    MissingColumnError,
    ThemeNotFoundError,
    VisualizationError,
)
from app.modules.visualization.models import (
    ChartConfig,
    ChartRecommendation,
    ChartResult,
    ChartType,
    Theme,
)
from app.modules.visualization.services import ChartService, ThemeService

# Import router after services to avoid circular imports
from app.modules.visualization.api import router as visualization_router

__all__ = [
    # Exceptions
    "ChartExportError",
    "ChartGenerationError",
    "ChartRecommendationError",
    "InvalidChartTypeError",
    "MissingColumnError",
    "ThemeNotFoundError",
    "VisualizationError",
    # Models
    "ChartConfig",
    "ChartRecommendation",
    "ChartResult",
    "ChartType",
    "Theme",
    # Services
    "ChartService",
    "ThemeService",
    # Router
    "visualization_router",
]
