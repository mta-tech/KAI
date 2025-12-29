"""ChartViz module exception classes.

These exceptions provide structured error handling for chart visualization operations
and integrate with the ERROR_MAPPING in app/server/errors.py for consistent
error codes in API responses.
"""

from app.server.errors import CustomError


class ChartVizError(CustomError):
    """Base exception for all chart visualization-related errors."""

    pass


class ChartVizGenerationError(ChartVizError):
    """Raised when chart visualization generation fails."""

    pass


class ChartVizRecommendationError(ChartVizError):
    """Raised when chart recommendation fails."""

    pass


class AutoChartGenerationError(ChartVizError):
    """Raised when automatic chart generation fails."""

    pass


class AnalysisDataExtractionError(ChartVizError):
    """Raised when analysis data extraction fails."""

    pass


class InvalidChartTypeError(ChartVizError):
    """Raised when an invalid or unsupported chart type is specified."""

    pass
