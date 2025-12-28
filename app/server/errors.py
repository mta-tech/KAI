import asyncio
from functools import wraps
import logging
from typing import Any, Callable, Type, Union

import openai
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

ERROR_MAPPING = {
    # Database/SQL errors
    "InvalidId": "invalid_object_id",
    "InvalidDBConnectionError": "invalid_database_connection",
    "InvalidURIFormatError": "invalid_database_uri_format",
    "SSHInvalidDatabaseConnectionError": "ssh_invalid_database_connection",
    "EmptyDBError": "empty_database",
    "DatabaseConnectionNotFoundError": "database_connection_not_found",
    "GoldenSQLNotFoundError": "golden_sql_not_found",
    "LLMNotSupportedError": "llm_model_not_supported",
    "PromptNotFoundError": "prompt_not_found",
    "SQLGenerationError": "sql_generation_not_created",
    "SQLInjectionError": "sql_injection",
    "SQLGenerationNotFoundError": "sql_generation_not_found",
    "NLGenerationError": "nl_generation_not_created",
    "MalformedGoldenSQLError": "invalid_golden_sql",
    "SchemaNotSupportedError": "schema_not_supported",
    # Analytics module errors
    "InsufficientDataError": "insufficient_data",
    "StatisticalCalculationError": "statistical_calculation_failed",
    "CorrelationAnalysisError": "correlation_analysis_failed",
    "AnomalyDetectionError": "anomaly_detection_failed",
    "ForecastingError": "forecasting_failed",
    "InvalidMethodError": "invalid_method",
    # Visualization module errors
    "ChartGenerationError": "chart_generation_failed",
    "InvalidChartTypeError": "invalid_chart_type",
    "ChartRecommendationError": "chart_recommendation_failed",
    "ThemeNotFoundError": "theme_not_found",
    "MissingColumnError": "missing_column",
    "ChartExportError": "chart_export_failed",
    # Dashboard module errors
    "DashboardNotFoundError": "dashboard_not_found",
    "WidgetNotFoundError": "widget_not_found",
    "DashboardCreationError": "dashboard_creation_failed",
    "DashboardExecutionError": "dashboard_execution_failed",
    "WidgetQueryGenerationError": "widget_query_generation_failed",
    "WidgetExecutionError": "widget_execution_failed",
    "DashboardRenderError": "dashboard_render_failed",
    "ShareTokenError": "share_token_error",
    # ChartViz module errors
    "ChartVizGenerationError": "chartviz_generation_failed",
    "ChartVizRecommendationError": "chartviz_recommendation_failed",
    "AutoChartGenerationError": "auto_chart_generation_failed",
    "AnalysisDataExtractionError": "analysis_data_extraction_failed",
}


class CustomError(Exception):
    def __init__(self, message, description=None):
        super().__init__(message)
        self.description = description


def error_response(error, detail: dict, default_error_code=""):
    error_code = ERROR_MAPPING.get(error.__class__.__name__, default_error_code)
    description = getattr(error, "description", None)
    logger.error(
        f"Error code: {error_code}, message: {error}, description: {description}, detail: {detail}"
    )

    detail.pop("metadata", None)

    return JSONResponse(
        status_code=400,
        content={
            "error_code": error_code,
            "message": str(error),
            "description": description,
            "detail": detail,
        },
    )


def module_exceptions(
    exception_types: Union[Type[Exception], tuple[Type[Exception], ...]],
    default_error_code: str = "",
    reraise: bool = False,
    status_code: int = 400,
):
    """A generic decorator factory for module-specific error handling.

    This decorator wraps service functions to catch module-specific exceptions
    and return structured error responses using the ERROR_MAPPING.

    Args:
        exception_types: The exception class(es) to catch. Can be a single
            exception class or a tuple of exception classes.
        default_error_code: The fallback error code to use if the exception
            is not found in ERROR_MAPPING. Defaults to "".
        reraise: If True, re-raises the exception after logging. If False,
            returns an error_response JSONResponse. Defaults to False.
        status_code: The HTTP status code to use in the error response.
            Defaults to 400.

    Returns:
        A decorator that wraps functions with module-specific error handling.

    Example:
        from app.modules.analytics.exceptions import AnalyticsError

        @module_exceptions(AnalyticsError, default_error_code="analytics_error")
        def analyze_data(data):
            # ... analytics logic that may raise AnalyticsError subclasses
            pass

        @module_exceptions(
            (VisualizationError, ChartGenerationError),
            default_error_code="visualization_error",
            reraise=True,
        )
        async def generate_chart(config):
            # ... async chart generation logic
            pass
    """

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return fn(*args, **kwargs)
            except exception_types as e:
                error_code = ERROR_MAPPING.get(
                    e.__class__.__name__, default_error_code
                )
                description = getattr(e, "description", None)
                logger.error(
                    f"Module error - code: {error_code}, "
                    f"message: {e}, description: {description}"
                )

                if reraise:
                    raise

                return JSONResponse(
                    status_code=status_code,
                    content={
                        "error_code": error_code,
                        "message": str(e),
                        "description": description,
                    },
                )

        @wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await fn(*args, **kwargs)
            except exception_types as e:
                error_code = ERROR_MAPPING.get(
                    e.__class__.__name__, default_error_code
                )
                description = getattr(e, "description", None)
                logger.error(
                    f"Module error - code: {error_code}, "
                    f"message: {e}, description: {description}"
                )

                if reraise:
                    raise

                return JSONResponse(
                    status_code=status_code,
                    content={
                        "error_code": error_code,
                        "message": str(e),
                        "description": description,
                    },
                )

        # Return the appropriate wrapper based on whether the function is async
        if asyncio.iscoroutinefunction(fn):
            return async_wrapper
        return sync_wrapper

    return decorator


def sql_agent_exceptions():  # noqa: C901
    def decorator(fn: Callable[[str], str]) -> Callable[[str], str]:  # noqa: C901
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: PLR0911
            try:
                return fn(*args, **kwargs)
            except openai.AuthenticationError as e:
                # Handle authentication error here
                return f"OpenAI API authentication error: {e}"
            except openai.RateLimitError as e:
                # Handle API error here, e.g. retry or log
                return f"OpenAI API request exceeded rate limit: {e}"
            except openai.BadRequestError as e:
                # Handle connection error here
                return f"OpenAI API request timed out: {e}"
            except openai.APIResponseValidationError as e:
                # Handle rate limit error (we recommend using exponential backoff)
                return f"OpenAI API response is invalid: {e}"
            except openai.OpenAIError as e:
                # Handle timeout error (we recommend using exponential backoff)
                return f"OpenAI API returned an error: {e}"
            except SQLAlchemyError as e:
                return f"Error: {e}"
            except Exception as e:
                return f"Error: {e}"

        return wrapper

    return decorator
