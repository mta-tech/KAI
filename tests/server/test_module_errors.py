"""Tests for module exceptions and ERROR_MAPPING.

This module tests all module-specific exception classes and their integration
with the ERROR_MAPPING dictionary in app/server/errors.py.
"""

import pytest
from fastapi.responses import JSONResponse

from app.server.errors import (
    CustomError,
    ERROR_MAPPING,
    error_response,
    module_exceptions,
)

# Analytics module exceptions
from app.modules.analytics.exceptions import (
    AnalyticsError,
    AnomalyDetectionError,
    CorrelationAnalysisError,
    ForecastingError,
    InsufficientDataError,
    InvalidMethodError,
    StatisticalCalculationError,
)

# Visualization module exceptions
from app.modules.visualization.exceptions import (
    ChartExportError,
    ChartGenerationError,
    ChartRecommendationError,
    InvalidChartTypeError,
    MissingColumnError,
    ThemeNotFoundError,
    VisualizationError,
)

# Dashboard module exceptions
from app.modules.dashboard.exceptions import (
    DashboardCreationError,
    DashboardError,
    DashboardExecutionError,
    DashboardNotFoundError,
    DashboardRenderError,
    ShareTokenError,
    WidgetExecutionError,
    WidgetNotFoundError,
    WidgetQueryGenerationError,
)

# ChartViz module exceptions
from app.modules.chartviz.exceptions import (
    AnalysisDataExtractionError,
    AutoChartGenerationError,
    ChartVizError,
    ChartVizGenerationError,
    ChartVizRecommendationError,
    InvalidChartTypeError as ChartVizInvalidChartTypeError,
)


class TestCustomError:
    """Tests for CustomError base class."""

    def test_custom_error_with_message_only(self) -> None:
        """Should create error with message only."""
        error = CustomError("Test error message")

        assert str(error) == "Test error message"
        assert error.description is None

    def test_custom_error_with_description(self) -> None:
        """Should create error with message and description."""
        error = CustomError("Test error message", description="Detailed description")

        assert str(error) == "Test error message"
        assert error.description == "Detailed description"

    def test_custom_error_is_exception(self) -> None:
        """CustomError should be an Exception."""
        error = CustomError("Test error")
        assert isinstance(error, Exception)


class TestAnalyticsExceptions:
    """Tests for analytics module exception classes."""

    def test_analytics_error_inherits_from_custom_error(self) -> None:
        """AnalyticsError should inherit from CustomError."""
        error = AnalyticsError("Analytics error")
        assert isinstance(error, CustomError)
        assert isinstance(error, Exception)

    def test_insufficient_data_error(self) -> None:
        """InsufficientDataError should inherit from AnalyticsError."""
        error = InsufficientDataError("Not enough data")
        assert isinstance(error, AnalyticsError)
        assert isinstance(error, CustomError)

    def test_statistical_calculation_error(self) -> None:
        """StatisticalCalculationError should inherit from AnalyticsError."""
        error = StatisticalCalculationError("Calculation failed")
        assert isinstance(error, AnalyticsError)

    def test_correlation_analysis_error(self) -> None:
        """CorrelationAnalysisError should inherit from AnalyticsError."""
        error = CorrelationAnalysisError("Correlation failed")
        assert isinstance(error, AnalyticsError)

    def test_anomaly_detection_error(self) -> None:
        """AnomalyDetectionError should inherit from AnalyticsError."""
        error = AnomalyDetectionError("Detection failed")
        assert isinstance(error, AnalyticsError)

    def test_forecasting_error(self) -> None:
        """ForecastingError should inherit from AnalyticsError."""
        error = ForecastingError("Forecasting failed")
        assert isinstance(error, AnalyticsError)

    def test_invalid_method_error(self) -> None:
        """InvalidMethodError should inherit from AnalyticsError."""
        error = InvalidMethodError("Invalid method")
        assert isinstance(error, AnalyticsError)

    def test_analytics_errors_with_description(self) -> None:
        """Analytics errors should support description parameter."""
        error = InsufficientDataError(
            "Need at least 10 data points",
            description="Provide more data for analysis",
        )
        assert str(error) == "Need at least 10 data points"
        assert error.description == "Provide more data for analysis"


class TestVisualizationExceptions:
    """Tests for visualization module exception classes."""

    def test_visualization_error_inherits_from_custom_error(self) -> None:
        """VisualizationError should inherit from CustomError."""
        error = VisualizationError("Visualization error")
        assert isinstance(error, CustomError)
        assert isinstance(error, Exception)

    def test_chart_generation_error(self) -> None:
        """ChartGenerationError should inherit from VisualizationError."""
        error = ChartGenerationError("Generation failed")
        assert isinstance(error, VisualizationError)
        assert isinstance(error, CustomError)

    def test_invalid_chart_type_error(self) -> None:
        """InvalidChartTypeError should inherit from VisualizationError."""
        error = InvalidChartTypeError("Invalid chart type")
        assert isinstance(error, VisualizationError)

    def test_chart_recommendation_error(self) -> None:
        """ChartRecommendationError should inherit from VisualizationError."""
        error = ChartRecommendationError("Recommendation failed")
        assert isinstance(error, VisualizationError)

    def test_theme_not_found_error(self) -> None:
        """ThemeNotFoundError should inherit from VisualizationError."""
        error = ThemeNotFoundError("Theme not found")
        assert isinstance(error, VisualizationError)

    def test_missing_column_error(self) -> None:
        """MissingColumnError should inherit from VisualizationError."""
        error = MissingColumnError("Column missing")
        assert isinstance(error, VisualizationError)

    def test_chart_export_error(self) -> None:
        """ChartExportError should inherit from VisualizationError."""
        error = ChartExportError("Export failed")
        assert isinstance(error, VisualizationError)


class TestDashboardExceptions:
    """Tests for dashboard module exception classes."""

    def test_dashboard_error_inherits_from_custom_error(self) -> None:
        """DashboardError should inherit from CustomError."""
        error = DashboardError("Dashboard error")
        assert isinstance(error, CustomError)
        assert isinstance(error, Exception)

    def test_dashboard_not_found_error(self) -> None:
        """DashboardNotFoundError should inherit from DashboardError."""
        error = DashboardNotFoundError("Dashboard not found")
        assert isinstance(error, DashboardError)
        assert isinstance(error, CustomError)

    def test_widget_not_found_error(self) -> None:
        """WidgetNotFoundError should inherit from DashboardError."""
        error = WidgetNotFoundError("Widget not found")
        assert isinstance(error, DashboardError)

    def test_dashboard_creation_error(self) -> None:
        """DashboardCreationError should inherit from DashboardError."""
        error = DashboardCreationError("Creation failed")
        assert isinstance(error, DashboardError)

    def test_dashboard_execution_error(self) -> None:
        """DashboardExecutionError should inherit from DashboardError."""
        error = DashboardExecutionError("Execution failed")
        assert isinstance(error, DashboardError)

    def test_widget_query_generation_error(self) -> None:
        """WidgetQueryGenerationError should inherit from DashboardError."""
        error = WidgetQueryGenerationError("Query generation failed")
        assert isinstance(error, DashboardError)

    def test_widget_execution_error(self) -> None:
        """WidgetExecutionError should inherit from DashboardError."""
        error = WidgetExecutionError("Widget execution failed")
        assert isinstance(error, DashboardError)

    def test_dashboard_render_error(self) -> None:
        """DashboardRenderError should inherit from DashboardError."""
        error = DashboardRenderError("Render failed")
        assert isinstance(error, DashboardError)

    def test_share_token_error(self) -> None:
        """ShareTokenError should inherit from DashboardError."""
        error = ShareTokenError("Token error")
        assert isinstance(error, DashboardError)


class TestChartVizExceptions:
    """Tests for chartviz module exception classes."""

    def test_chartviz_error_inherits_from_custom_error(self) -> None:
        """ChartVizError should inherit from CustomError."""
        error = ChartVizError("ChartViz error")
        assert isinstance(error, CustomError)
        assert isinstance(error, Exception)

    def test_chartviz_generation_error(self) -> None:
        """ChartVizGenerationError should inherit from ChartVizError."""
        error = ChartVizGenerationError("Generation failed")
        assert isinstance(error, ChartVizError)
        assert isinstance(error, CustomError)

    def test_chartviz_recommendation_error(self) -> None:
        """ChartVizRecommendationError should inherit from ChartVizError."""
        error = ChartVizRecommendationError("Recommendation failed")
        assert isinstance(error, ChartVizError)

    def test_auto_chart_generation_error(self) -> None:
        """AutoChartGenerationError should inherit from ChartVizError."""
        error = AutoChartGenerationError("Auto generation failed")
        assert isinstance(error, ChartVizError)

    def test_analysis_data_extraction_error(self) -> None:
        """AnalysisDataExtractionError should inherit from ChartVizError."""
        error = AnalysisDataExtractionError("Extraction failed")
        assert isinstance(error, ChartVizError)

    def test_chartviz_invalid_chart_type_error(self) -> None:
        """InvalidChartTypeError should inherit from ChartVizError."""
        error = ChartVizInvalidChartTypeError("Invalid chart type")
        assert isinstance(error, ChartVizError)


class TestErrorMapping:
    """Tests for ERROR_MAPPING dictionary."""

    def test_error_mapping_contains_analytics_errors(self) -> None:
        """ERROR_MAPPING should contain all analytics error codes."""
        analytics_mappings = {
            "InsufficientDataError": "insufficient_data",
            "StatisticalCalculationError": "statistical_calculation_failed",
            "CorrelationAnalysisError": "correlation_analysis_failed",
            "AnomalyDetectionError": "anomaly_detection_failed",
            "ForecastingError": "forecasting_failed",
            "InvalidMethodError": "invalid_method",
        }

        for error_class, error_code in analytics_mappings.items():
            assert error_class in ERROR_MAPPING, f"{error_class} not in ERROR_MAPPING"
            assert (
                ERROR_MAPPING[error_class] == error_code
            ), f"Expected {error_code}, got {ERROR_MAPPING[error_class]}"

    def test_error_mapping_contains_visualization_errors(self) -> None:
        """ERROR_MAPPING should contain all visualization error codes."""
        visualization_mappings = {
            "ChartGenerationError": "chart_generation_failed",
            "InvalidChartTypeError": "invalid_chart_type",
            "ChartRecommendationError": "chart_recommendation_failed",
            "ThemeNotFoundError": "theme_not_found",
            "MissingColumnError": "missing_column",
            "ChartExportError": "chart_export_failed",
        }

        for error_class, error_code in visualization_mappings.items():
            assert error_class in ERROR_MAPPING, f"{error_class} not in ERROR_MAPPING"
            assert (
                ERROR_MAPPING[error_class] == error_code
            ), f"Expected {error_code}, got {ERROR_MAPPING[error_class]}"

    def test_error_mapping_contains_dashboard_errors(self) -> None:
        """ERROR_MAPPING should contain all dashboard error codes."""
        dashboard_mappings = {
            "DashboardNotFoundError": "dashboard_not_found",
            "WidgetNotFoundError": "widget_not_found",
            "DashboardCreationError": "dashboard_creation_failed",
            "DashboardExecutionError": "dashboard_execution_failed",
            "WidgetQueryGenerationError": "widget_query_generation_failed",
            "WidgetExecutionError": "widget_execution_failed",
            "DashboardRenderError": "dashboard_render_failed",
            "ShareTokenError": "share_token_error",
        }

        for error_class, error_code in dashboard_mappings.items():
            assert error_class in ERROR_MAPPING, f"{error_class} not in ERROR_MAPPING"
            assert (
                ERROR_MAPPING[error_class] == error_code
            ), f"Expected {error_code}, got {ERROR_MAPPING[error_class]}"

    def test_error_mapping_contains_chartviz_errors(self) -> None:
        """ERROR_MAPPING should contain all chartviz error codes."""
        chartviz_mappings = {
            "ChartVizGenerationError": "chartviz_generation_failed",
            "ChartVizRecommendationError": "chartviz_recommendation_failed",
            "AutoChartGenerationError": "auto_chart_generation_failed",
            "AnalysisDataExtractionError": "analysis_data_extraction_failed",
        }

        for error_class, error_code in chartviz_mappings.items():
            assert error_class in ERROR_MAPPING, f"{error_class} not in ERROR_MAPPING"
            assert (
                ERROR_MAPPING[error_class] == error_code
            ), f"Expected {error_code}, got {ERROR_MAPPING[error_class]}"

    def test_error_mapping_contains_database_errors(self) -> None:
        """ERROR_MAPPING should contain database/SQL error codes."""
        database_mappings = {
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
        }

        for error_class, error_code in database_mappings.items():
            assert error_class in ERROR_MAPPING, f"{error_class} not in ERROR_MAPPING"
            assert (
                ERROR_MAPPING[error_class] == error_code
            ), f"Expected {error_code}, got {ERROR_MAPPING[error_class]}"


class TestErrorResponse:
    """Tests for error_response function."""

    def test_error_response_with_mapped_error(self) -> None:
        """error_response should use ERROR_MAPPING for known errors."""
        error = InsufficientDataError("Not enough data")
        detail = {"column": "sales"}

        response = error_response(error, detail)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert response.body is not None

        # Decode the response body
        import json

        body = json.loads(response.body)
        assert body["error_code"] == "insufficient_data"
        assert body["message"] == "Not enough data"
        assert body["detail"] == {"column": "sales"}

    def test_error_response_with_description(self) -> None:
        """error_response should include description from error."""
        error = ChartGenerationError(
            "Generation failed", description="Invalid data format"
        )
        detail = {}

        response = error_response(error, detail)

        import json

        body = json.loads(response.body)
        assert body["error_code"] == "chart_generation_failed"
        assert body["description"] == "Invalid data format"

    def test_error_response_with_default_error_code(self) -> None:
        """error_response should use default_error_code for unknown errors."""
        error = ValueError("Unknown error")
        detail = {}

        response = error_response(error, detail, default_error_code="generic_error")

        import json

        body = json.loads(response.body)
        assert body["error_code"] == "generic_error"
        assert body["message"] == "Unknown error"

    def test_error_response_removes_metadata(self) -> None:
        """error_response should remove metadata from detail."""
        error = DashboardNotFoundError("Not found")
        detail = {"dashboard_id": "123", "metadata": {"sensitive": "data"}}

        response = error_response(error, detail)

        import json

        body = json.loads(response.body)
        assert body["detail"] == {"dashboard_id": "123"}
        assert "metadata" not in body["detail"]


class TestModuleExceptionsDecorator:
    """Tests for module_exceptions decorator factory."""

    def test_decorator_catches_specified_exception(self) -> None:
        """Decorator should catch specified exception types."""

        @module_exceptions(AnalyticsError)
        def raise_analytics_error():
            raise InsufficientDataError("Not enough data")

        response = raise_analytics_error()

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400

        import json

        body = json.loads(response.body)
        assert body["error_code"] == "insufficient_data"
        assert body["message"] == "Not enough data"

    def test_decorator_catches_tuple_of_exceptions(self) -> None:
        """Decorator should catch multiple exception types."""

        @module_exceptions((VisualizationError, DashboardError))
        def raise_chart_error():
            raise ChartGenerationError("Chart failed")

        response = raise_chart_error()

        import json

        body = json.loads(response.body)
        assert body["error_code"] == "chart_generation_failed"

    def test_decorator_with_default_error_code(self) -> None:
        """Decorator should use default_error_code for unmapped errors."""

        class CustomAnalyticsError(AnalyticsError):
            pass

        @module_exceptions(AnalyticsError, default_error_code="custom_analytics_error")
        def raise_custom_error():
            raise CustomAnalyticsError("Custom error")

        response = raise_custom_error()

        import json

        body = json.loads(response.body)
        assert body["error_code"] == "custom_analytics_error"

    def test_decorator_with_reraise(self) -> None:
        """Decorator should re-raise exception when reraise=True."""

        @module_exceptions(AnalyticsError, reraise=True)
        def raise_analytics_error():
            raise InsufficientDataError("Not enough data")

        with pytest.raises(InsufficientDataError):
            raise_analytics_error()

    def test_decorator_with_custom_status_code(self) -> None:
        """Decorator should use custom status code."""

        @module_exceptions(VisualizationError, status_code=404)
        def raise_theme_error():
            raise ThemeNotFoundError("Theme not found")

        response = raise_theme_error()

        assert response.status_code == 404

    def test_decorator_passes_through_uncaught_exceptions(self) -> None:
        """Decorator should not catch non-specified exceptions."""

        @module_exceptions(AnalyticsError)
        def raise_value_error():
            raise ValueError("Not an analytics error")

        with pytest.raises(ValueError):
            raise_value_error()

    def test_decorator_returns_normal_value(self) -> None:
        """Decorator should return normal value when no exception."""

        @module_exceptions(AnalyticsError)
        def return_value():
            return "success"

        result = return_value()

        assert result == "success"

    def test_decorator_preserves_function_metadata(self) -> None:
        """Decorator should preserve function metadata."""

        @module_exceptions(AnalyticsError)
        def my_function():
            """My function docstring."""
            pass

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My function docstring."

    @pytest.mark.asyncio
    async def test_decorator_works_with_async_function(self) -> None:
        """Decorator should work with async functions."""

        @module_exceptions(DashboardError)
        async def async_raise_error():
            raise DashboardNotFoundError("Dashboard not found")

        response = await async_raise_error()

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400

        import json

        body = json.loads(response.body)
        assert body["error_code"] == "dashboard_not_found"

    @pytest.mark.asyncio
    async def test_async_decorator_returns_normal_value(self) -> None:
        """Async decorator should return normal value when no exception."""

        @module_exceptions(ChartVizError)
        async def async_return_value():
            return {"status": "success"}

        result = await async_return_value()

        assert result == {"status": "success"}

    @pytest.mark.asyncio
    async def test_async_decorator_with_reraise(self) -> None:
        """Async decorator should re-raise when reraise=True."""

        @module_exceptions(ChartVizError, reraise=True)
        async def async_raise_error():
            raise ChartVizGenerationError("Generation failed")

        with pytest.raises(ChartVizGenerationError):
            await async_raise_error()


class TestExceptionRaisingAndCatching:
    """Integration tests for raising and catching module exceptions."""

    def test_catch_analytics_base_exception(self) -> None:
        """Should catch any AnalyticsError subclass with base class."""
        errors_to_test = [
            InsufficientDataError("Not enough data"),
            StatisticalCalculationError("Calc failed"),
            CorrelationAnalysisError("Correlation failed"),
            AnomalyDetectionError("Detection failed"),
            ForecastingError("Forecasting failed"),
            InvalidMethodError("Invalid method"),
        ]

        for error in errors_to_test:
            try:
                raise error
            except AnalyticsError as e:
                assert str(e) == str(error)
                error_code = ERROR_MAPPING.get(e.__class__.__name__)
                assert error_code is not None

    def test_catch_visualization_base_exception(self) -> None:
        """Should catch any VisualizationError subclass with base class."""
        errors_to_test = [
            ChartGenerationError("Generation failed"),
            InvalidChartTypeError("Invalid type"),
            ChartRecommendationError("Recommendation failed"),
            ThemeNotFoundError("Theme not found"),
            MissingColumnError("Column missing"),
            ChartExportError("Export failed"),
        ]

        for error in errors_to_test:
            try:
                raise error
            except VisualizationError as e:
                assert str(e) == str(error)
                error_code = ERROR_MAPPING.get(e.__class__.__name__)
                assert error_code is not None

    def test_catch_dashboard_base_exception(self) -> None:
        """Should catch any DashboardError subclass with base class."""
        errors_to_test = [
            DashboardNotFoundError("Not found"),
            WidgetNotFoundError("Widget not found"),
            DashboardCreationError("Creation failed"),
            DashboardExecutionError("Execution failed"),
            WidgetQueryGenerationError("Query gen failed"),
            WidgetExecutionError("Widget exec failed"),
            DashboardRenderError("Render failed"),
            ShareTokenError("Token error"),
        ]

        for error in errors_to_test:
            try:
                raise error
            except DashboardError as e:
                assert str(e) == str(error)
                error_code = ERROR_MAPPING.get(e.__class__.__name__)
                assert error_code is not None

    def test_catch_chartviz_base_exception(self) -> None:
        """Should catch any ChartVizError subclass with base class."""
        errors_to_test = [
            ChartVizGenerationError("Generation failed"),
            ChartVizRecommendationError("Recommendation failed"),
            AutoChartGenerationError("Auto gen failed"),
            AnalysisDataExtractionError("Extraction failed"),
            ChartVizInvalidChartTypeError("Invalid type"),
        ]

        for error in errors_to_test:
            try:
                raise error
            except ChartVizError as e:
                assert str(e) == str(error)
                # Note: InvalidChartTypeError in chartviz module is separate
                # and may not be in ERROR_MAPPING (only viz module's is)
                error_code = ERROR_MAPPING.get(e.__class__.__name__)
                # ChartVizInvalidChartTypeError is not mapped, others should be
                if not isinstance(e, ChartVizInvalidChartTypeError):
                    assert error_code is not None

    def test_catch_custom_error_base(self) -> None:
        """Should catch any module exception with CustomError base."""
        all_errors = [
            InsufficientDataError("Analytics"),
            ChartGenerationError("Visualization"),
            DashboardNotFoundError("Dashboard"),
            ChartVizGenerationError("ChartViz"),
        ]

        for error in all_errors:
            try:
                raise error
            except CustomError as e:
                assert str(e) == str(error)
