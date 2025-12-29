"""Analytics module for statistical analysis and forecasting."""

from app.modules.analytics.models import (
    AnomalyResult,
    CorrelationMatrixResult,
    CorrelationResult,
    DescriptiveStats,
    ExportFormat,
    ExportRequest,
    ExportResponse,
    ForecastResult,
    StatisticalTestResult,
    StatisticalTestType,
)
from app.modules.analytics.services import (
    AnomalyService,
    ExportService,
    ForecastingService,
    StatisticalService,
)

# Import routers after services to avoid circular imports
from app.modules.analytics.api import router as analytics_router
from app.modules.analytics.batch_api import router as batch_analytics_router

# Import CLI for command-line access
from app.modules.analytics.cli import cli as analytics_cli

__all__ = [
    "AnomalyResult",
    "AnomalyService",
    "CorrelationMatrixResult",
    "CorrelationResult",
    "DescriptiveStats",
    "ExportFormat",
    "ExportRequest",
    "ExportResponse",
    "ExportService",
    "ForecastResult",
    "ForecastingService",
    "StatisticalService",
    "StatisticalTestResult",
    "StatisticalTestType",
    "analytics_cli",
    "analytics_router",
    "batch_analytics_router",
]
