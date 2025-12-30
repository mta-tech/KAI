"""Dashboard module exception classes.

These exceptions provide structured error handling for dashboard operations
and integrate with the ERROR_MAPPING in app/server/errors.py for consistent
error codes in API responses.
"""

from app.server.errors import CustomError


class DashboardError(CustomError):
    """Base exception for all dashboard-related errors."""

    pass


class DashboardNotFoundError(DashboardError):
    """Raised when a dashboard cannot be found."""

    pass


class WidgetNotFoundError(DashboardError):
    """Raised when a widget cannot be found."""

    pass


class DashboardCreationError(DashboardError):
    """Raised when dashboard creation fails."""

    pass


class DashboardExecutionError(DashboardError):
    """Raised when dashboard execution fails."""

    pass


class WidgetQueryGenerationError(DashboardError):
    """Raised when widget query generation fails."""

    pass


class WidgetExecutionError(DashboardError):
    """Raised when widget execution fails."""

    pass


class DashboardRenderError(DashboardError):
    """Raised when dashboard rendering fails."""

    pass


class ShareTokenError(DashboardError):
    """Raised when share token operations fail."""

    pass
