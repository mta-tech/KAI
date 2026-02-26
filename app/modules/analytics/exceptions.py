"""Analytics module exception classes.

These exceptions provide structured error handling for analytics operations
and integrate with the ERROR_MAPPING in app/server/errors.py for consistent
error codes in API responses.
"""

from app.server.errors import CustomError


class AnalyticsError(CustomError):
    """Base exception for all analytics-related errors."""

    pass


class InsufficientDataError(AnalyticsError):
    """Raised when there is not enough data for statistical analysis."""

    pass


class StatisticalCalculationError(AnalyticsError):
    """Raised when a statistical calculation fails."""

    pass


class CorrelationAnalysisError(AnalyticsError):
    """Raised when correlation analysis fails."""

    pass


class AnomalyDetectionError(AnalyticsError):
    """Raised when anomaly detection fails."""

    pass


class ForecastingError(AnalyticsError):
    """Raised when forecasting operations fail."""

    pass


class InvalidMethodError(AnalyticsError):
    """Raised when an invalid or unsupported method is specified."""

    pass
