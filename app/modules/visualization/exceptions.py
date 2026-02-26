"""Visualization module exception classes.

These exceptions provide structured error handling for visualization operations
and integrate with the ERROR_MAPPING in app/server/errors.py for consistent
error codes in API responses.
"""

from app.server.errors import CustomError


class VisualizationError(CustomError):
    """Base exception for all visualization-related errors."""

    pass


class ChartGenerationError(VisualizationError):
    """Raised when chart generation fails."""

    pass


class InvalidChartTypeError(VisualizationError):
    """Raised when an invalid or unsupported chart type is specified."""

    pass


class ChartRecommendationError(VisualizationError):
    """Raised when chart recommendation fails."""

    pass


class ThemeNotFoundError(VisualizationError):
    """Raised when a specified theme cannot be found."""

    pass


class MissingColumnError(VisualizationError):
    """Raised when a required column is missing from the data."""

    pass


class ChartExportError(VisualizationError):
    """Raised when chart export operations fail."""

    pass
