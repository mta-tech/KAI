"""Analytics module for statistical analysis and forecasting."""

from app.modules.analytics.models import (
    AnomalyResult,
    CorrelationMatrixResult,
    CorrelationResult,
    DescriptiveStats,
    ForecastResult,
    StatisticalTestResult,
    StatisticalTestType,
)
from app.modules.analytics.services import (
    AnomalyService,
    ForecastingService,
    StatisticalService,
)

# Import router after services to avoid circular imports
from app.modules.analytics.api import router as analytics_router

__all__ = [
    "AnomalyResult",
    "AnomalyService",
    "CorrelationMatrixResult",
    "CorrelationResult",
    "DescriptiveStats",
    "ForecastResult",
    "ForecastingService",
    "StatisticalService",
    "StatisticalTestResult",
    "StatisticalTestType",
    "analytics_router",
]
