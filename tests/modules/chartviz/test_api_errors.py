"""Integration tests for chartviz API structured error responses.

These tests verify that API endpoints return structured error responses
with correct error codes when module-specific exceptions are raised.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.chartviz.api import router as chartviz_router, get_service
from app.modules.chartviz.models import ChartType
from app.modules.chartviz.exceptions import (
    AnalysisDataExtractionError,
    AutoChartGenerationError,
    ChartVizGenerationError,
    ChartVizRecommendationError,
    InvalidChartTypeError,
)


@pytest.fixture
def mock_service():
    """Create mock chartviz service."""
    service = MagicMock()
    service.generate_chart = AsyncMock()
    service.recommend_chart = AsyncMock()
    service.auto_generate = AsyncMock()
    service.generate_from_analysis = AsyncMock()
    return service


@pytest.fixture
def app(mock_service):
    """Create FastAPI app with chartviz router."""
    app = FastAPI()
    app.include_router(chartviz_router)
    # Override the get_service dependency
    app.dependency_overrides[get_service] = lambda: mock_service
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


class TestGenerateChartErrors:
    """Tests for /generate endpoint error responses."""

    def test_chartviz_generation_error_returns_structured_response(
        self, client, mock_service
    ):
        """Should return structured error when ChartVizGenerationError is raised."""
        mock_service.generate_chart.side_effect = ChartVizGenerationError(
            "Failed to generate chart configuration"
        )

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/generate",
                json={
                    "data": [{"x": 1, "y": 2}],
                    "chart_type": "bar",
                    "user_prompt": "Show sales data",
                },
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "chartviz_generation_failed"
        assert "Failed to generate chart" in body["message"]
        assert body["detail"]["chart_type"] == "bar"

    def test_invalid_chart_type_error_returns_structured_response(
        self, client, mock_service
    ):
        """Should return structured error when InvalidChartTypeError is raised."""
        mock_service.generate_chart.side_effect = InvalidChartTypeError(
            "Unsupported chart type: waterfall"
        )

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/generate",
                json={
                    "data": [{"x": 1, "y": 2}],
                    "chart_type": "bar",
                    "user_prompt": "Show sales data",
                },
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "invalid_chart_type"
        assert "Unsupported chart type" in body["message"]

    def test_value_error_wrapped_as_invalid_chart_type(self, client, mock_service):
        """Should wrap ValueError as InvalidChartTypeError."""
        mock_service.generate_chart.side_effect = ValueError(
            "Invalid chart type specified"
        )

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/generate",
                json={
                    "data": [{"x": 1, "y": 2}],
                    "chart_type": "bar",
                    "user_prompt": "Show data",
                },
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "invalid_chart_type"

    def test_generic_exception_wrapped_as_generation_error(self, client, mock_service):
        """Should wrap generic exception as ChartVizGenerationError."""
        mock_service.generate_chart.side_effect = RuntimeError("Unexpected error")

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/generate",
                json={
                    "data": [{"x": 1, "y": 2}],
                    "chart_type": "bar",
                    "user_prompt": "Show data",
                },
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "chartviz_generation_failed"
        assert "Chart generation failed" in body["message"]

    def test_chart_type_none_in_detail(self, client, mock_service):
        """Should handle None chart_type in error detail."""
        mock_service.generate_chart.side_effect = ChartVizGenerationError(
            "Failed to generate chart"
        )

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/generate",
                json={
                    "data": [{"x": 1, "y": 2}],
                    "user_prompt": "Auto-detect chart type",
                },
            )

        assert response.status_code == 400
        body = response.json()
        assert body["detail"]["chart_type"] is None


class TestRecommendChartErrors:
    """Tests for /recommend endpoint error responses."""

    def test_chartviz_recommendation_error_returns_structured_response(
        self, client, mock_service
    ):
        """Should return structured error when ChartVizRecommendationError is raised."""
        mock_service.recommend_chart.side_effect = ChartVizRecommendationError(
            "Unable to recommend chart for provided data"
        )

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/recommend",
                json={
                    "data": [{"x": 1, "y": 2}],
                    "user_prompt": "Recommend best chart",
                },
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "chartviz_recommendation_failed"
        assert "Unable to recommend chart" in body["message"]
        assert body["detail"]["user_prompt"] == "Recommend best chart"

    def test_value_error_wrapped_as_recommendation_error(self, client, mock_service):
        """Should wrap ValueError as ChartVizRecommendationError."""
        mock_service.recommend_chart.side_effect = ValueError("Empty data provided")

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/recommend",
                json={
                    "data": [{"x": 1}],
                    "user_prompt": "Recommend chart",
                },
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "chartviz_recommendation_failed"

    def test_generic_exception_wrapped_as_recommendation_error(
        self, client, mock_service
    ):
        """Should wrap generic exception as ChartVizRecommendationError."""
        mock_service.recommend_chart.side_effect = RuntimeError("Unexpected error")

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/recommend",
                json={
                    "data": [{"x": 1}],
                    "user_prompt": "Recommend chart",
                },
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "chartviz_recommendation_failed"
        assert "Chart recommendation failed" in body["message"]


class TestAutoGenerateChartErrors:
    """Tests for /auto endpoint error responses."""

    def test_auto_chart_generation_error_returns_structured_response(
        self, client, mock_service
    ):
        """Should return structured error when AutoChartGenerationError is raised."""
        mock_service.auto_generate.side_effect = AutoChartGenerationError(
            "Auto chart generation failed: no suitable type"
        )

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/auto",
                json={
                    "data": [{"x": 1, "y": 2}],
                    "user_prompt": "Generate automatic chart",
                },
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "auto_chart_generation_failed"
        assert "Auto chart generation failed" in body["message"]
        assert body["detail"]["user_prompt"] == "Generate automatic chart"

    def test_value_error_wrapped_as_auto_generation_error(self, client, mock_service):
        """Should wrap ValueError as AutoChartGenerationError."""
        mock_service.auto_generate.side_effect = ValueError("Invalid data format")

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/auto",
                json={
                    "data": [{"x": 1}],
                    "user_prompt": "Auto generate",
                },
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "auto_chart_generation_failed"

    def test_generic_exception_wrapped_as_auto_generation_error(
        self, client, mock_service
    ):
        """Should wrap generic exception as AutoChartGenerationError."""
        mock_service.auto_generate.side_effect = RuntimeError("Unexpected error")

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/auto",
                json={
                    "data": [{"x": 1}],
                    "user_prompt": "Auto generate",
                },
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "auto_chart_generation_failed"
        assert "Auto chart generation failed" in body["message"]


class TestGenerateFromAnalysisErrors:
    """Tests for /from-analysis endpoint error responses."""

    def test_analysis_data_extraction_error_returns_structured_response(
        self, client, mock_service
    ):
        """Should return structured error when AnalysisDataExtractionError is raised."""
        mock_service.generate_from_analysis.side_effect = AnalysisDataExtractionError(
            "No data found in analysis result"
        )

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/from-analysis",
                json={"analysis_result": {"type": "statistical", "data": None}},
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "analysis_data_extraction_failed"
        assert "No data found" in body["message"]

    def test_chartviz_generation_error_during_from_analysis(
        self, client, mock_service
    ):
        """Should return structured error when ChartVizGenerationError is raised."""
        mock_service.generate_from_analysis.side_effect = ChartVizGenerationError(
            "Failed to generate chart from analysis"
        )

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/from-analysis",
                json={
                    "analysis_result": {"type": "statistical", "data": [1, 2, 3]},
                    "chart_type": "bar",
                },
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "chartviz_generation_failed"
        assert body["detail"]["chart_type"] == "bar"

    def test_value_error_wrapped_as_extraction_error(self, client, mock_service):
        """Should wrap ValueError as AnalysisDataExtractionError."""
        mock_service.generate_from_analysis.side_effect = ValueError(
            "Invalid analysis result format"
        )

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/from-analysis",
                json={"analysis_result": {}},
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "analysis_data_extraction_failed"

    def test_generic_exception_wrapped_as_extraction_error(self, client, mock_service):
        """Should wrap generic exception as AnalysisDataExtractionError."""
        mock_service.generate_from_analysis.side_effect = RuntimeError(
            "Unexpected error"
        )

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/from-analysis",
                json={"analysis_result": {"data": [1, 2, 3]}},
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "analysis_data_extraction_failed"
        assert "Chart generation from analysis failed" in body["message"]


class TestErrorResponseStructure:
    """Tests verifying the structure of error responses."""

    def test_error_response_has_required_fields(self, client, mock_service):
        """Error responses should have error_code, message, and detail fields."""
        mock_service.generate_chart.side_effect = ChartVizGenerationError("Test error")

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/generate",
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

    def test_error_response_with_description(self, client, mock_service):
        """Error responses should include description when provided."""
        error_with_desc = ChartVizGenerationError(
            "Generation failed",
            description="Ensure data contains at least 2 data points",
        )
        mock_service.generate_chart.side_effect = error_with_desc

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/generate",
                json={
                    "data": [{"x": 1, "y": 2}],
                    "chart_type": "bar",
                },
            )

        assert response.status_code == 400
        body = response.json()
        assert body["description"] == "Ensure data contains at least 2 data points"


class TestErrorCodeMapping:
    """Tests verifying error codes match ERROR_MAPPING."""

    def test_chartviz_generation_error_code(self, client, mock_service):
        """ChartVizGenerationError should map to 'chartviz_generation_failed'."""
        mock_service.generate_chart.side_effect = ChartVizGenerationError(
            "Generation failed"
        )

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/generate",
                json={
                    "data": [{"x": 1}],
                    "chart_type": "bar",
                },
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "chartviz_generation_failed"

    def test_chartviz_recommendation_error_code(self, client, mock_service):
        """ChartVizRecommendationError should map to 'chartviz_recommendation_failed'."""
        mock_service.recommend_chart.side_effect = ChartVizRecommendationError(
            "Recommendation failed"
        )

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/recommend",
                json={"data": [{"x": 1}]},
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "chartviz_recommendation_failed"

    def test_auto_chart_generation_error_code(self, client, mock_service):
        """AutoChartGenerationError should map to 'auto_chart_generation_failed'."""
        mock_service.auto_generate.side_effect = AutoChartGenerationError(
            "Auto generation failed"
        )

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/auto",
                json={"data": [{"x": 1}]},
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "auto_chart_generation_failed"

    def test_analysis_data_extraction_error_code(self, client, mock_service):
        """AnalysisDataExtractionError should map to 'analysis_data_extraction_failed'."""
        mock_service.generate_from_analysis.side_effect = AnalysisDataExtractionError(
            "Extraction failed"
        )

        with patch("app.modules.chartviz.api.get_service", return_value=mock_service):
            response = client.post(
                "/api/v2/chartviz/from-analysis",
                json={"analysis_result": {}},
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "analysis_data_extraction_failed"
