"""Integration tests for visualization API structured error responses.

These tests verify that API endpoints return structured error responses
with correct error codes when module-specific exceptions are raised.
"""

import pytest
from unittest.mock import MagicMock, patch
import pandas as pd

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.visualization.api import router as visualization_router
from app.modules.visualization.exceptions import (
    ChartGenerationError,
    ChartRecommendationError,
    InvalidChartTypeError,
)


@pytest.fixture
def app():
    """Create FastAPI app with visualization router."""
    app = FastAPI()
    app.include_router(visualization_router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


class TestGenerateChartErrors:
    """Tests for /generate endpoint error responses."""

    def test_invalid_chart_type_returns_structured_response(self, client):
        """Should return structured error when invalid chart type is provided."""
        response = client.post(
            "/api/v2/visualizations/generate",
            json={
                "data": [{"x": 1, "y": 2}],
                "chart_type": "invalid_type",
                "x_column": "x",
                "y_column": "y",
            },
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "invalid_chart_type"
        assert body["detail"]["chart_type"] == "invalid_type"

    def test_invalid_chart_type_error_returns_structured_response(
        self, client, monkeypatch
    ):
        """Should return structured error when InvalidChartTypeError is raised."""
        from app.modules.visualization import api

        mock_service = MagicMock()
        monkeypatch.setattr(api, "_chart_service", mock_service)

        # Force the ValueError to be raised when creating ChartType enum
        response = client.post(
            "/api/v2/visualizations/generate",
            json={
                "data": [{"x": 1, "y": 2}],
                "chart_type": "nonexistent_chart",
                "x_column": "x",
                "y_column": "y",
            },
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "invalid_chart_type"
        assert "nonexistent_chart" in body["detail"]["chart_type"]

    def test_chart_generation_error_returns_structured_response(
        self, client, monkeypatch
    ):
        """Should return structured error when ChartGenerationError is raised."""
        from app.modules.visualization import api
        from app.modules.visualization import ChartType

        mock_service = MagicMock()
        mock_service.generate_chart.side_effect = ChartGenerationError(
            "Failed to generate bar chart"
        )
        monkeypatch.setattr(api, "_chart_service", mock_service)

        response = client.post(
            "/api/v2/visualizations/generate",
            json={
                "data": [{"x": 1, "y": 2}],
                "chart_type": "bar",
                "x_column": "x",
                "y_column": "y",
            },
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "chart_generation_failed"
        assert "Failed to generate bar chart" in body["message"]
        assert body["detail"]["chart_type"] == "bar"

    def test_generic_exception_wrapped_as_chart_generation_error(
        self, client, monkeypatch
    ):
        """Should wrap generic exception as ChartGenerationError."""
        from app.modules.visualization import api

        mock_service = MagicMock()
        mock_service.generate_chart.side_effect = RuntimeError("Unexpected error")
        monkeypatch.setattr(api, "_chart_service", mock_service)

        response = client.post(
            "/api/v2/visualizations/generate",
            json={
                "data": [{"x": 1, "y": 2}],
                "chart_type": "bar",
                "x_column": "x",
                "y_column": "y",
            },
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "chart_generation_failed"
        assert "Chart generation failed" in body["message"]

    def test_chart_generation_error_includes_theme(self, client, monkeypatch):
        """Should include theme in error detail."""
        from app.modules.visualization import api

        mock_service = MagicMock()
        mock_service.generate_chart.side_effect = ChartGenerationError(
            "Theme rendering failed"
        )
        monkeypatch.setattr(api, "_chart_service", mock_service)

        response = client.post(
            "/api/v2/visualizations/generate",
            json={
                "data": [{"x": 1, "y": 2}],
                "chart_type": "line",
                "x_column": "x",
                "y_column": "y",
                "theme": "dark",
            },
        )

        assert response.status_code == 400
        body = response.json()
        assert body["detail"]["theme"] == "dark"


class TestRecommendChartErrors:
    """Tests for /recommend endpoint error responses."""

    def test_chart_recommendation_error_returns_structured_response(
        self, client, monkeypatch
    ):
        """Should return structured error when ChartRecommendationError is raised."""
        from app.modules.visualization import api

        mock_service = MagicMock()
        mock_service.recommend_chart_type.side_effect = ChartRecommendationError(
            "Unable to recommend chart for empty dataset"
        )
        monkeypatch.setattr(api, "_chart_service", mock_service)

        response = client.post(
            "/api/v2/visualizations/recommend",
            json={"data": [{"x": 1, "y": 2}], "x_column": "x", "y_column": "y"},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "chart_recommendation_failed"
        assert "Unable to recommend chart" in body["message"]
        assert body["detail"]["x_column"] == "x"
        assert body["detail"]["y_column"] == "y"

    def test_generic_exception_wrapped_as_recommendation_error(
        self, client, monkeypatch
    ):
        """Should wrap generic exception as ChartRecommendationError."""
        from app.modules.visualization import api

        mock_service = MagicMock()
        mock_service.recommend_chart_type.side_effect = ValueError(
            "Invalid data format"
        )
        monkeypatch.setattr(api, "_chart_service", mock_service)

        response = client.post(
            "/api/v2/visualizations/recommend",
            json={"data": [{"x": 1, "y": 2}]},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "chart_recommendation_failed"
        assert "Recommendation failed" in body["message"]


class TestErrorResponseStructure:
    """Tests verifying the structure of error responses."""

    def test_error_response_has_required_fields(self, client, monkeypatch):
        """Error responses should have error_code, message, and detail fields."""
        from app.modules.visualization import api

        mock_service = MagicMock()
        mock_service.generate_chart.side_effect = ChartGenerationError("Test error")
        monkeypatch.setattr(api, "_chart_service", mock_service)

        response = client.post(
            "/api/v2/visualizations/generate",
            json={
                "data": [{"x": 1, "y": 2}],
                "chart_type": "bar",
            },
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
        from app.modules.visualization import api

        error_with_desc = ChartGenerationError(
            "Chart generation failed",
            description="Ensure data contains numeric values for y-axis",
        )
        mock_service = MagicMock()
        mock_service.generate_chart.side_effect = error_with_desc
        monkeypatch.setattr(api, "_chart_service", mock_service)

        response = client.post(
            "/api/v2/visualizations/generate",
            json={
                "data": [{"x": 1, "y": 2}],
                "chart_type": "bar",
            },
        )

        assert response.status_code == 400
        body = response.json()
        assert (
            body["description"] == "Ensure data contains numeric values for y-axis"
        )


class TestErrorCodeMapping:
    """Tests verifying error codes match ERROR_MAPPING."""

    def test_invalid_chart_type_error_code(self, client, monkeypatch):
        """InvalidChartTypeError should map to 'invalid_chart_type'."""
        from app.modules.visualization import api

        mock_service = MagicMock()
        mock_service.generate_chart.side_effect = InvalidChartTypeError(
            "Unsupported chart type"
        )
        monkeypatch.setattr(api, "_chart_service", mock_service)

        response = client.post(
            "/api/v2/visualizations/generate",
            json={
                "data": [{"x": 1, "y": 2}],
                "chart_type": "bar",
            },
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "invalid_chart_type"

    def test_chart_generation_error_code(self, client, monkeypatch):
        """ChartGenerationError should map to 'chart_generation_failed'."""
        from app.modules.visualization import api

        mock_service = MagicMock()
        mock_service.generate_chart.side_effect = ChartGenerationError(
            "Generation failed"
        )
        monkeypatch.setattr(api, "_chart_service", mock_service)

        response = client.post(
            "/api/v2/visualizations/generate",
            json={
                "data": [{"x": 1, "y": 2}],
                "chart_type": "bar",
            },
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "chart_generation_failed"

    def test_chart_recommendation_error_code(self, client, monkeypatch):
        """ChartRecommendationError should map to 'chart_recommendation_failed'."""
        from app.modules.visualization import api

        mock_service = MagicMock()
        mock_service.recommend_chart_type.side_effect = ChartRecommendationError(
            "Recommendation failed"
        )
        monkeypatch.setattr(api, "_chart_service", mock_service)

        response = client.post(
            "/api/v2/visualizations/recommend",
            json={"data": [{"x": 1}]},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "chart_recommendation_failed"
