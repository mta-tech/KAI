from functools import wraps
import logging
from typing import Any, Callable

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
