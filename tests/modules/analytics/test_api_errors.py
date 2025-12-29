"""Integration tests for analytics API structured error responses.

These tests verify that API endpoints return structured error responses
with correct error codes when module-specific exceptions are raised.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import pandas as pd

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.analytics.api import router as analytics_router
from app.modules.analytics.exceptions import (
    AnomalyDetectionError,
    CorrelationAnalysisError,
    ForecastingError,
    InvalidMethodError,
    StatisticalCalculationError,
)


@pytest.fixture
def app():
    """Create FastAPI app with analytics router."""
    app = FastAPI()
    app.include_router(analytics_router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


class TestDescriptiveStatsErrors:
    """Tests for /descriptive endpoint error responses."""

    def test_statistical_calculation_error_returns_structured_response(
        self, client, monkeypatch
    ):
        """Should return structured error when StatisticalCalculationError is raised."""
        from app.modules.analytics import api

        mock_service = MagicMock()
        mock_service.descriptive_stats.side_effect = StatisticalCalculationError(
            "Calculation failed due to invalid data"
        )
        monkeypatch.setattr(api, "_stat_service", mock_service)

        response = client.post(
            "/api/v2/analytics/descriptive",
            json={"data": [1, 2, 3], "column_name": "test_column"},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "statistical_calculation_failed"
        assert "Calculation failed" in body["message"]
        assert body["detail"]["column_name"] == "test_column"

    def test_generic_exception_wrapped_as_statistical_error(self, client, monkeypatch):
        """Should wrap generic exception as StatisticalCalculationError."""
        from app.modules.analytics import api

        mock_service = MagicMock()
        mock_service.descriptive_stats.side_effect = Exception("Unexpected error")
        monkeypatch.setattr(api, "_stat_service", mock_service)

        response = client.post(
            "/api/v2/analytics/descriptive",
            json={"data": [1, 2, 3], "column_name": "test_column"},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "statistical_calculation_failed"
        assert "Statistics calculation failed" in body["message"]


class TestTTestErrors:
    """Tests for /t-test endpoint error responses."""

    def test_statistical_calculation_error_in_ttest(self, client, monkeypatch):
        """Should return structured error when StatisticalCalculationError is raised."""
        from app.modules.analytics import api

        mock_service = MagicMock()
        mock_service.t_test_independent.side_effect = StatisticalCalculationError(
            "Insufficient data for t-test"
        )
        monkeypatch.setattr(api, "_stat_service", mock_service)

        response = client.post(
            "/api/v2/analytics/t-test",
            json={"group1": [1, 2], "group2": [3, 4], "alpha": 0.05},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "statistical_calculation_failed"
        assert "Insufficient data" in body["message"]
        assert body["detail"]["alpha"] == 0.05

    def test_generic_exception_wrapped_in_ttest(self, client, monkeypatch):
        """Should wrap generic exception in t-test endpoint."""
        from app.modules.analytics import api

        mock_service = MagicMock()
        mock_service.t_test_independent.side_effect = RuntimeError("Runtime error")
        monkeypatch.setattr(api, "_stat_service", mock_service)

        response = client.post(
            "/api/v2/analytics/t-test",
            json={"group1": [1, 2], "group2": [3, 4], "alpha": 0.05},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "statistical_calculation_failed"
        assert "T-test failed" in body["message"]


class TestCorrelationErrors:
    """Tests for /correlation endpoint error responses."""

    def test_correlation_analysis_error_returns_structured_response(
        self, client, monkeypatch
    ):
        """Should return structured error when CorrelationAnalysisError is raised."""
        from app.modules.analytics import api

        mock_service = MagicMock()
        mock_service.correlation.side_effect = CorrelationAnalysisError(
            "Invalid correlation method specified"
        )
        monkeypatch.setattr(api, "_stat_service", mock_service)

        response = client.post(
            "/api/v2/analytics/correlation",
            json={"x": [1, 2, 3], "y": [4, 5, 6], "method": "invalid", "alpha": 0.05},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "correlation_analysis_failed"
        assert "Invalid correlation method" in body["message"]
        assert body["detail"]["method"] == "invalid"
        assert body["detail"]["alpha"] == 0.05

    def test_generic_exception_wrapped_as_correlation_error(self, client, monkeypatch):
        """Should wrap generic exception as CorrelationAnalysisError."""
        from app.modules.analytics import api

        mock_service = MagicMock()
        mock_service.correlation.side_effect = ValueError("Value error")
        monkeypatch.setattr(api, "_stat_service", mock_service)

        response = client.post(
            "/api/v2/analytics/correlation",
            json={"x": [1, 2, 3], "y": [4, 5, 6], "method": "pearson", "alpha": 0.05},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "correlation_analysis_failed"
        assert "Correlation analysis failed" in body["message"]


class TestCorrelationMatrixErrors:
    """Tests for /correlation-matrix endpoint error responses."""

    def test_correlation_matrix_error_returns_structured_response(
        self, client, monkeypatch
    ):
        """Should return structured error for correlation matrix failures."""
        from app.modules.analytics import api

        mock_service = MagicMock()
        mock_service.correlation_matrix.side_effect = CorrelationAnalysisError(
            "Not enough numeric columns"
        )
        monkeypatch.setattr(api, "_stat_service", mock_service)

        response = client.post(
            "/api/v2/analytics/correlation-matrix",
            json={"data": [{"a": 1, "b": 2}], "method": "pearson"},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "correlation_analysis_failed"
        assert "Not enough numeric columns" in body["message"]
        assert body["detail"]["method"] == "pearson"


class TestAnomalyDetectionErrors:
    """Tests for /anomalies endpoint error responses."""

    def test_invalid_method_error_returns_structured_response(
        self, client, monkeypatch
    ):
        """Should return structured error when InvalidMethodError is raised."""
        response = client.post(
            "/api/v2/analytics/anomalies",
            json={"data": [1, 2, 3], "method": "unknown_method", "threshold": 3.0},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "invalid_method"
        assert "Unknown method" in body["message"]
        assert body["detail"]["method"] == "unknown_method"
        assert body["detail"]["threshold"] == 3.0

    def test_anomaly_detection_error_returns_structured_response(
        self, client, monkeypatch
    ):
        """Should return structured error when AnomalyDetectionError is raised."""
        from app.modules.analytics import api

        mock_service = MagicMock()
        mock_service.detect_zscore.side_effect = AnomalyDetectionError(
            "Insufficient data for anomaly detection"
        )
        monkeypatch.setattr(api, "_anomaly_service", mock_service)

        response = client.post(
            "/api/v2/analytics/anomalies",
            json={"data": [1, 2], "method": "zscore", "threshold": 3.0},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "anomaly_detection_failed"
        assert "Insufficient data" in body["message"]

    def test_iqr_method_error_returns_structured_response(self, client, monkeypatch):
        """Should return structured error for IQR method failures."""
        from app.modules.analytics import api

        mock_service = MagicMock()
        mock_service.detect_iqr.side_effect = AnomalyDetectionError(
            "IQR calculation failed"
        )
        monkeypatch.setattr(api, "_anomaly_service", mock_service)

        response = client.post(
            "/api/v2/analytics/anomalies",
            json={"data": [1, 2, 3, 4], "method": "iqr", "threshold": 1.5},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "anomaly_detection_failed"
        assert "IQR calculation failed" in body["message"]

    def test_generic_exception_wrapped_as_anomaly_detection_error(
        self, client, monkeypatch
    ):
        """Should wrap generic exception as AnomalyDetectionError."""
        from app.modules.analytics import api

        mock_service = MagicMock()
        mock_service.detect_zscore.side_effect = RuntimeError("Unexpected error")
        monkeypatch.setattr(api, "_anomaly_service", mock_service)

        response = client.post(
            "/api/v2/analytics/anomalies",
            json={"data": [1, 2, 3], "method": "zscore", "threshold": 3.0},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "anomaly_detection_failed"
        assert "Anomaly detection failed" in body["message"]


class TestForecastErrors:
    """Tests for /forecast endpoint error responses."""

    def test_forecasting_error_returns_structured_response(self, client, monkeypatch):
        """Should return structured error when ForecastingError is raised."""
        from app.modules.analytics import api

        mock_service = MagicMock()
        mock_service.forecast_simple.side_effect = ForecastingError(
            "Insufficient data points for forecasting"
        )
        monkeypatch.setattr(api, "_forecast_service", mock_service)

        response = client.post(
            "/api/v2/analytics/forecast",
            json={"values": [1, 2], "periods": 30},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "forecasting_failed"
        assert "Insufficient data points" in body["message"]
        assert body["detail"]["periods"] == 30

    def test_generic_exception_wrapped_as_forecasting_error(self, client, monkeypatch):
        """Should wrap generic exception as ForecastingError."""
        from app.modules.analytics import api

        mock_service = MagicMock()
        mock_service.forecast_simple.side_effect = Exception("Unexpected error")
        monkeypatch.setattr(api, "_forecast_service", mock_service)

        response = client.post(
            "/api/v2/analytics/forecast",
            json={"values": [1, 2, 3], "periods": 10},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "forecasting_failed"
        assert "Forecast failed" in body["message"]


class TestErrorResponseStructure:
    """Tests verifying the structure of error responses."""

    def test_error_response_has_required_fields(self, client, monkeypatch):
        """Error responses should have error_code, message, and detail fields."""
        from app.modules.analytics import api

        mock_service = MagicMock()
        mock_service.descriptive_stats.side_effect = StatisticalCalculationError(
            "Test error"
        )
        monkeypatch.setattr(api, "_stat_service", mock_service)

        response = client.post(
            "/api/v2/analytics/descriptive",
            json={"data": [1, 2, 3], "column_name": "test"},
        )

        assert response.status_code == 400
        body = response.json()

        # Verify required fields exist
        assert "error_code" in body
        assert "message" in body
        assert "detail" in body
        assert "description" in body

    def test_error_response_with_description(self, client, monkeypatch):
        """Error responses should include description when provided."""
        from app.modules.analytics import api

        error_with_desc = StatisticalCalculationError(
            "Calculation failed",
            description="Provide at least 3 data points for analysis",
        )
        mock_service = MagicMock()
        mock_service.descriptive_stats.side_effect = error_with_desc
        monkeypatch.setattr(api, "_stat_service", mock_service)

        response = client.post(
            "/api/v2/analytics/descriptive",
            json={"data": [1, 2, 3], "column_name": "test"},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["description"] == "Provide at least 3 data points for analysis"
