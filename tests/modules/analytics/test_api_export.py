"""Integration tests for Analytics Export API endpoints."""

from __future__ import annotations

import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.analytics.api import router


@pytest.fixture
def app() -> FastAPI:
    """Create FastAPI app with analytics router."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_data() -> list[float]:
    """Sample numeric data for tests."""
    return [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]


@pytest.fixture
def correlation_data() -> dict:
    """Sample data for correlation tests."""
    return {
        "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        "y": [2.0, 4.0, 5.0, 4.0, 5.0, 6.0, 8.0, 9.0, 10.0, 12.0],
    }


@pytest.fixture
def matrix_data() -> list[dict]:
    """Sample data for correlation matrix tests."""
    return [
        {"a": 1.0, "b": 2.0, "c": 3.0},
        {"a": 2.0, "b": 4.0, "c": 5.0},
        {"a": 3.0, "b": 5.0, "c": 7.0},
        {"a": 4.0, "b": 6.0, "c": 8.0},
        {"a": 5.0, "b": 8.0, "c": 10.0},
    ]


@pytest.fixture
def anomaly_data() -> list[float]:
    """Sample data with anomalies for tests."""
    # Normal data with two clear outliers
    return [10.0, 12.0, 11.0, 13.0, 12.0, 100.0, 11.0, 12.0, 10.0, -50.0]


class TestDescriptiveStatsExport:
    """Tests for POST /api/v2/analytics/descriptive/export endpoint."""

    def test_export_json(self, client: TestClient, sample_data: list[float]) -> None:
        """Should export descriptive statistics as JSON."""
        response = client.post(
            "/api/v2/analytics/descriptive/export",
            json={
                "data": sample_data,
                "column_name": "test_values",
                "format": "json",
                "include_metadata": True,
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert "content-disposition" in response.headers
        assert "descriptive_stats" in response.headers["content-disposition"]
        assert ".json" in response.headers["content-disposition"]

        # Verify JSON content
        content = json.loads(response.content)
        assert "metadata" in content
        assert "result" in content
        assert content["result"]["column"] == "test_values"
        assert content["result"]["count"] == 10
        assert content["result"]["mean"] == 55.0

    def test_export_csv(self, client: TestClient, sample_data: list[float]) -> None:
        """Should export descriptive statistics as CSV."""
        response = client.post(
            "/api/v2/analytics/descriptive/export",
            json={
                "data": sample_data,
                "column_name": "test_values",
                "format": "csv",
                "include_metadata": True,
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/csv")
        assert ".csv" in response.headers["content-disposition"]

        # Verify CSV content
        content = response.content.decode("utf-8")
        assert "column" in content
        assert "mean" in content
        assert "test_values" in content

    def test_export_pdf(self, client: TestClient, sample_data: list[float]) -> None:
        """Should export descriptive statistics as PDF."""
        response = client.post(
            "/api/v2/analytics/descriptive/export",
            json={
                "data": sample_data,
                "column_name": "test_values",
                "format": "pdf",
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert ".pdf" in response.headers["content-disposition"]

        # Verify PDF content (starts with %PDF)
        assert response.content[:4] == b"%PDF"

    def test_export_with_custom_filename(
        self,
        client: TestClient,
        sample_data: list[float],
    ) -> None:
        """Should use custom filename when provided."""
        response = client.post(
            "/api/v2/analytics/descriptive/export",
            json={
                "data": sample_data,
                "format": "json",
                "filename": "my_custom_report",
            },
        )

        assert response.status_code == 200
        assert "my_custom_report" in response.headers["content-disposition"]

    def test_export_without_metadata(
        self,
        client: TestClient,
        sample_data: list[float],
    ) -> None:
        """Should export without metadata wrapper."""
        response = client.post(
            "/api/v2/analytics/descriptive/export",
            json={
                "data": sample_data,
                "format": "json",
                "include_metadata": False,
            },
        )

        assert response.status_code == 200
        content = json.loads(response.content)
        assert "metadata" not in content


class TestCorrelationExport:
    """Tests for POST /api/v2/analytics/correlation/export endpoint."""

    def test_export_json(
        self,
        client: TestClient,
        correlation_data: dict,
    ) -> None:
        """Should export correlation analysis as JSON."""
        response = client.post(
            "/api/v2/analytics/correlation/export",
            json={
                "x": correlation_data["x"],
                "y": correlation_data["y"],
                "method": "pearson",
                "format": "json",
                "include_metadata": True,
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert ".json" in response.headers["content-disposition"]

        # Verify JSON content
        content = json.loads(response.content)
        assert "result" in content
        assert content["result"]["method"] == "pearson"
        assert "coefficient" in content["result"]
        assert "p_value" in content["result"]

    def test_export_csv(
        self,
        client: TestClient,
        correlation_data: dict,
    ) -> None:
        """Should export correlation analysis as CSV."""
        response = client.post(
            "/api/v2/analytics/correlation/export",
            json={
                "x": correlation_data["x"],
                "y": correlation_data["y"],
                "method": "spearman",
                "format": "csv",
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/csv")

        content = response.content.decode("utf-8")
        assert "method" in content
        assert "coefficient" in content

    def test_export_pdf(
        self,
        client: TestClient,
        correlation_data: dict,
    ) -> None:
        """Should export correlation analysis as PDF."""
        response = client.post(
            "/api/v2/analytics/correlation/export",
            json={
                "x": correlation_data["x"],
                "y": correlation_data["y"],
                "format": "pdf",
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.content[:4] == b"%PDF"


class TestCorrelationMatrixExport:
    """Tests for POST /api/v2/analytics/correlation-matrix/export endpoint."""

    def test_export_json(
        self,
        client: TestClient,
        matrix_data: list[dict],
    ) -> None:
        """Should export correlation matrix as JSON."""
        response = client.post(
            "/api/v2/analytics/correlation-matrix/export",
            json={
                "data": matrix_data,
                "method": "pearson",
                "format": "json",
                "include_metadata": True,
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        content = json.loads(response.content)
        assert "result" in content
        assert content["result"]["method"] == "pearson"
        assert "matrix" in content["result"]
        assert "columns" in content["result"]
        assert set(content["result"]["columns"]) == {"a", "b", "c"}

    def test_export_csv(
        self,
        client: TestClient,
        matrix_data: list[dict],
    ) -> None:
        """Should export correlation matrix as CSV."""
        response = client.post(
            "/api/v2/analytics/correlation-matrix/export",
            json={
                "data": matrix_data,
                "format": "csv",
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/csv")

        content = response.content.decode("utf-8")
        # Matrix should contain column names
        assert "a" in content
        assert "b" in content
        assert "c" in content

    def test_export_pdf(
        self,
        client: TestClient,
        matrix_data: list[dict],
    ) -> None:
        """Should export correlation matrix as PDF with heatmap."""
        response = client.post(
            "/api/v2/analytics/correlation-matrix/export",
            json={
                "data": matrix_data,
                "format": "pdf",
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.content[:4] == b"%PDF"


class TestForecastExport:
    """Tests for POST /api/v2/analytics/forecast/export endpoint."""

    def test_export_json(self, client: TestClient, sample_data: list[float]) -> None:
        """Should export forecast results as JSON."""
        response = client.post(
            "/api/v2/analytics/forecast/export",
            json={
                "values": sample_data,
                "periods": 5,
                "format": "json",
                "include_metadata": True,
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        content = json.loads(response.content)
        assert "result" in content
        assert "model_name" in content["result"]
        assert "forecast_values" in content["result"]
        assert "lower_bound" in content["result"]
        assert "upper_bound" in content["result"]
        assert len(content["result"]["forecast_values"]) == 5

    def test_export_csv(self, client: TestClient, sample_data: list[float]) -> None:
        """Should export forecast results as CSV with structured columns."""
        response = client.post(
            "/api/v2/analytics/forecast/export",
            json={
                "values": sample_data,
                "periods": 3,
                "format": "csv",
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/csv")

        content = response.content.decode("utf-8")
        assert "date" in content
        assert "forecast" in content
        assert "lower_bound" in content
        assert "upper_bound" in content

    def test_export_pdf(self, client: TestClient, sample_data: list[float]) -> None:
        """Should export forecast results as PDF with chart."""
        response = client.post(
            "/api/v2/analytics/forecast/export",
            json={
                "values": sample_data,
                "periods": 5,
                "format": "pdf",
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.content[:4] == b"%PDF"


class TestAnomalyExport:
    """Tests for POST /api/v2/analytics/anomalies/export endpoint."""

    def test_export_json_zscore(
        self,
        client: TestClient,
        anomaly_data: list[float],
    ) -> None:
        """Should export anomaly detection results (z-score) as JSON."""
        response = client.post(
            "/api/v2/analytics/anomalies/export",
            json={
                "data": anomaly_data,
                "method": "zscore",
                "threshold": 2.0,
                "format": "json",
                "include_metadata": True,
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        content = json.loads(response.content)
        assert "result" in content
        assert content["result"]["method"] == "z-score"
        assert "anomaly_count" in content["result"]
        assert "anomalies" in content["result"]
        assert content["result"]["anomaly_count"] > 0

    def test_export_json_iqr(
        self,
        client: TestClient,
        anomaly_data: list[float],
    ) -> None:
        """Should export anomaly detection results (IQR) as JSON."""
        response = client.post(
            "/api/v2/analytics/anomalies/export",
            json={
                "data": anomaly_data,
                "method": "iqr",
                "threshold": 1.5,
                "format": "json",
            },
        )

        assert response.status_code == 200
        content = json.loads(response.content)
        assert content["result"]["method"] == "iqr"

    def test_export_csv(
        self,
        client: TestClient,
        anomaly_data: list[float],
    ) -> None:
        """Should export anomaly detection results as CSV."""
        response = client.post(
            "/api/v2/analytics/anomalies/export",
            json={
                "data": anomaly_data,
                "method": "zscore",
                "format": "csv",
                "include_metadata": True,
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/csv")

        content = response.content.decode("utf-8")
        # CSV should contain anomaly data
        assert "index" in content or "value" in content or "Method" in content

    def test_export_pdf(
        self,
        client: TestClient,
        anomaly_data: list[float],
    ) -> None:
        """Should export anomaly detection results as PDF."""
        response = client.post(
            "/api/v2/analytics/anomalies/export",
            json={
                "data": anomaly_data,
                "method": "zscore",
                "format": "pdf",
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.content[:4] == b"%PDF"

    def test_export_invalid_method(
        self,
        client: TestClient,
        anomaly_data: list[float],
    ) -> None:
        """Should return 400 for invalid method."""
        response = client.post(
            "/api/v2/analytics/anomalies/export",
            json={
                "data": anomaly_data,
                "method": "invalid_method",
                "format": "json",
            },
        )

        assert response.status_code == 400


class TestTTestExport:
    """Tests for POST /api/v2/analytics/t-test/export endpoint."""

    def test_export_json(self, client: TestClient) -> None:
        """Should export t-test results as JSON."""
        group1 = [10.0, 12.0, 11.0, 13.0, 12.0, 14.0, 11.0, 12.0]
        group2 = [20.0, 22.0, 21.0, 23.0, 22.0, 24.0, 21.0, 22.0]

        response = client.post(
            "/api/v2/analytics/t-test/export",
            json={
                "group1": group1,
                "group2": group2,
                "alpha": 0.05,
                "format": "json",
                "include_metadata": True,
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        content = json.loads(response.content)
        assert "result" in content
        assert "test_name" in content["result"]
        assert "statistic" in content["result"]
        assert "p_value" in content["result"]
        assert "is_significant" in content["result"]
        # Groups are significantly different
        assert content["result"]["is_significant"] is True

    def test_export_csv(self, client: TestClient) -> None:
        """Should export t-test results as CSV."""
        group1 = [10.0, 12.0, 11.0, 13.0, 12.0]
        group2 = [20.0, 22.0, 21.0, 23.0, 22.0]

        response = client.post(
            "/api/v2/analytics/t-test/export",
            json={
                "group1": group1,
                "group2": group2,
                "format": "csv",
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/csv")

        content = response.content.decode("utf-8")
        assert "test_name" in content
        assert "p_value" in content

    def test_export_pdf(self, client: TestClient) -> None:
        """Should export t-test results as PDF."""
        group1 = [10.0, 12.0, 11.0, 13.0, 12.0]
        group2 = [10.5, 11.5, 10.8, 12.5, 11.2]

        response = client.post(
            "/api/v2/analytics/t-test/export",
            json={
                "group1": group1,
                "group2": group2,
                "format": "pdf",
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.content[:4] == b"%PDF"


class TestResponseHeaders:
    """Tests for response headers across all export endpoints."""

    def test_content_length_header(
        self,
        client: TestClient,
        sample_data: list[float],
    ) -> None:
        """Should include Content-Length header."""
        response = client.post(
            "/api/v2/analytics/descriptive/export",
            json={
                "data": sample_data,
                "format": "json",
            },
        )

        assert response.status_code == 200
        assert "content-length" in response.headers
        assert int(response.headers["content-length"]) > 0
        assert int(response.headers["content-length"]) == len(response.content)

    def test_content_disposition_attachment(
        self,
        client: TestClient,
        sample_data: list[float],
    ) -> None:
        """Should include attachment content-disposition."""
        response = client.post(
            "/api/v2/analytics/forecast/export",
            json={
                "values": sample_data,
                "periods": 3,
                "format": "csv",
            },
        )

        assert response.status_code == 200
        assert "attachment" in response.headers["content-disposition"]


class TestDefaultFormats:
    """Tests for default format behavior."""

    def test_default_format_is_json(
        self,
        client: TestClient,
        sample_data: list[float],
    ) -> None:
        """Should default to JSON format when not specified."""
        response = client.post(
            "/api/v2/analytics/descriptive/export",
            json={
                "data": sample_data,
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_default_include_metadata(
        self,
        client: TestClient,
        sample_data: list[float],
    ) -> None:
        """Should include metadata by default."""
        response = client.post(
            "/api/v2/analytics/descriptive/export",
            json={
                "data": sample_data,
                "format": "json",
            },
        )

        assert response.status_code == 200
        content = json.loads(response.content)
        assert "metadata" in content


class TestErrorHandling:
    """Tests for error handling in export endpoints."""

    def test_empty_data_descriptive(self, client: TestClient) -> None:
        """Should handle empty data gracefully."""
        response = client.post(
            "/api/v2/analytics/descriptive/export",
            json={
                "data": [],
                "format": "json",
            },
        )

        # Should return error status for empty data
        assert response.status_code == 500

    def test_mismatched_correlation_lengths(self, client: TestClient) -> None:
        """Should handle mismatched array lengths for correlation.

        Note: The correlation service truncates arrays to matching lengths,
        so mismatched lengths don't cause errors but process partial data.
        """
        response = client.post(
            "/api/v2/analytics/correlation/export",
            json={
                "x": [1.0, 2.0, 3.0],
                "y": [1.0, 2.0],  # Different length - will be truncated
                "format": "json",
            },
        )

        # Service handles mismatched lengths by using minimum length
        assert response.status_code == 200

    def test_insufficient_forecast_data(self, client: TestClient) -> None:
        """Should handle insufficient data for forecasting.

        Note: The forecast service attempts to process even small datasets,
        providing best-effort results rather than failing.
        """
        response = client.post(
            "/api/v2/analytics/forecast/export",
            json={
                "values": [1.0],  # Only one value
                "periods": 5,
                "format": "json",
            },
        )

        # Service handles small datasets gracefully
        assert response.status_code == 200
