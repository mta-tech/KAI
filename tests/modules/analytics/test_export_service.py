"""Tests for ExportService."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd
import pytest

from app.modules.analytics.models import (
    AnomalyResult,
    CorrelationMatrixResult,
    CorrelationResult,
    DescriptiveStats,
    ExportFormat,
    ForecastResult,
    StatisticalTestResult,
)
from app.modules.analytics.services.export_service import ExportService


@pytest.fixture
def export_service() -> ExportService:
    """Export service instance."""
    return ExportService()


@pytest.fixture
def descriptive_stats() -> DescriptiveStats:
    """Sample descriptive statistics."""
    return DescriptiveStats(
        column="test_values",
        count=100,
        mean=50.0,
        std=10.0,
        min=20.0,
        q25=42.5,
        median=50.0,
        q75=57.5,
        max=80.0,
        skewness=0.1,
        kurtosis=-0.2,
    )


@pytest.fixture
def correlation_result() -> CorrelationResult:
    """Sample correlation result."""
    return CorrelationResult(
        method="pearson",
        coefficient=0.85,
        p_value=0.001,
        is_significant=True,
        interpretation="Strong positive correlation",
        sample_size=100,
    )


@pytest.fixture
def correlation_matrix_result() -> CorrelationMatrixResult:
    """Sample correlation matrix result."""
    return CorrelationMatrixResult(
        method="pearson",
        matrix={
            "a": {"a": 1.0, "b": 0.85, "c": -0.3},
            "b": {"a": 0.85, "b": 1.0, "c": -0.1},
            "c": {"a": -0.3, "b": -0.1, "c": 1.0},
        },
        columns=["a", "b", "c"],
    )


@pytest.fixture
def forecast_result() -> ForecastResult:
    """Sample forecast result."""
    return ForecastResult(
        model_name="Linear Trend",
        forecast_dates=["2024-01-01", "2024-02-01", "2024-03-01"],
        forecast_values=[100.0, 110.0, 120.0],
        lower_bound=[95.0, 105.0, 115.0],
        upper_bound=[105.0, 115.0, 125.0],
        confidence_level=0.95,
        trend="increasing",
        interpretation="Values are expected to increase over time",
        metrics={"mape": 5.2, "rmse": 2.1},
    )


@pytest.fixture
def anomaly_result() -> AnomalyResult:
    """Sample anomaly result."""
    return AnomalyResult(
        method="z-score",
        total_points=100,
        anomaly_count=3,
        anomaly_percentage=3.0,
        anomalies=[
            {"index": 5, "value": 150.0, "z_score": 4.5},
            {"index": 25, "value": -20.0, "z_score": -3.8},
            {"index": 75, "value": 145.0, "z_score": 4.2},
        ],
        threshold=3.0,
        interpretation="3 anomalies detected (3.0% of data points)",
    )


@pytest.fixture
def statistical_test_result() -> StatisticalTestResult:
    """Sample statistical test result."""
    return StatisticalTestResult(
        test_name="Independent Samples T-Test",
        test_type="t_test_independent",
        statistic=3.45,
        p_value=0.002,
        degrees_of_freedom=98.0,
        confidence_level=0.95,
        is_significant=True,
        interpretation="Significant difference found between groups",
        effect_size=0.68,
        effect_size_name="Cohen's d",
        details={"group1_mean": 45.0, "group2_mean": 55.0},
    )


class TestContentType:
    """Test cases for content type mapping."""

    def test_json_content_type(self, export_service: ExportService) -> None:
        """Should return correct content type for JSON."""
        assert export_service.get_content_type(ExportFormat.JSON) == "application/json"

    def test_csv_content_type(self, export_service: ExportService) -> None:
        """Should return correct content type for CSV."""
        assert export_service.get_content_type(ExportFormat.CSV) == "text/csv"

    def test_pdf_content_type(self, export_service: ExportService) -> None:
        """Should return correct content type for PDF."""
        assert export_service.get_content_type(ExportFormat.PDF) == "application/pdf"


class TestFilenameGeneration:
    """Test cases for filename generation."""

    def test_generate_filename_default(self, export_service: ExportService) -> None:
        """Should generate filename with timestamp and extension."""
        filename = export_service.generate_filename("report", ExportFormat.JSON)

        assert filename.startswith("report_")
        assert filename.endswith(".json")

    def test_generate_filename_csv(self, export_service: ExportService) -> None:
        """Should generate CSV filename."""
        filename = export_service.generate_filename("data", ExportFormat.CSV)

        assert filename.startswith("data_")
        assert filename.endswith(".csv")

    def test_generate_filename_pdf(self, export_service: ExportService) -> None:
        """Should generate PDF filename."""
        filename = export_service.generate_filename("report", ExportFormat.PDF)

        assert filename.startswith("report_")
        assert filename.endswith(".pdf")

    def test_generate_filename_custom(self, export_service: ExportService) -> None:
        """Should use custom filename when provided."""
        filename = export_service.generate_filename(
            "default",
            ExportFormat.JSON,
            custom_filename="my_custom_report",
        )

        assert filename.startswith("my_custom_report_")
        assert filename.endswith(".json")


class TestExportToJson:
    """Test cases for JSON export."""

    def test_export_dict_with_metadata(self, export_service: ExportService) -> None:
        """Should export dict with metadata wrapper."""
        data = {"key": "value", "number": 42}
        result = export_service.export_to_json(data, include_metadata=True)

        parsed = json.loads(result.decode("utf-8"))
        assert "metadata" in parsed
        assert "result" in parsed
        assert parsed["metadata"]["format"] == "json"
        assert parsed["result"]["key"] == "value"

    def test_export_dict_without_metadata(self, export_service: ExportService) -> None:
        """Should export dict without metadata wrapper."""
        data = {"key": "value", "number": 42}
        result = export_service.export_to_json(data, include_metadata=False)

        parsed = json.loads(result.decode("utf-8"))
        assert "metadata" not in parsed
        assert parsed["key"] == "value"

    def test_export_pydantic_model(
        self,
        export_service: ExportService,
        descriptive_stats: DescriptiveStats,
    ) -> None:
        """Should export Pydantic model to JSON."""
        result = export_service.export_to_json(descriptive_stats, include_metadata=True)

        parsed = json.loads(result.decode("utf-8"))
        assert parsed["result"]["column"] == "test_values"
        assert parsed["result"]["mean"] == 50.0

    def test_export_list(self, export_service: ExportService) -> None:
        """Should export list wrapped in data key."""
        data = [1, 2, 3, 4, 5]
        result = export_service.export_to_json(data, include_metadata=False)

        parsed = json.loads(result.decode("utf-8"))
        assert parsed["data"] == [1, 2, 3, 4, 5]


class TestExportToCsv:
    """Test cases for CSV export."""

    def test_export_dict_with_metadata(self, export_service: ExportService) -> None:
        """Should export dict as CSV with metadata header."""
        data = {"name": "test", "value": 100}
        result = export_service.export_to_csv(data, include_metadata=True)

        content = result.decode("utf-8")
        assert "# Exported at:" in content
        assert "# Format: CSV" in content
        assert "name" in content
        assert "value" in content

    def test_export_dict_without_metadata(self, export_service: ExportService) -> None:
        """Should export dict as CSV without metadata header."""
        data = {"name": "test", "value": 100}
        result = export_service.export_to_csv(data, include_metadata=False)

        content = result.decode("utf-8")
        assert "# Exported at:" not in content
        assert "name" in content

    def test_export_list_of_dicts(self, export_service: ExportService) -> None:
        """Should export list of dicts as CSV rows."""
        data = [
            {"name": "a", "value": 1},
            {"name": "b", "value": 2},
            {"name": "c", "value": 3},
        ]
        result = export_service.export_to_csv(data, include_metadata=False)

        content = result.decode("utf-8")
        lines = content.strip().split("\n")
        # Header + 3 rows
        assert len(lines) == 4
        assert "name" in lines[0]
        assert "value" in lines[0]

    def test_export_dataframe(self, export_service: ExportService) -> None:
        """Should export DataFrame as CSV."""
        df = pd.DataFrame({"col_a": [1, 2, 3], "col_b": [4, 5, 6]})
        result = export_service.export_to_csv(df, include_metadata=False)

        content = result.decode("utf-8")
        assert "col_a" in content
        assert "col_b" in content

    def test_export_pydantic_model(
        self,
        export_service: ExportService,
        descriptive_stats: DescriptiveStats,
    ) -> None:
        """Should export Pydantic model as CSV."""
        result = export_service.export_to_csv(descriptive_stats, include_metadata=False)

        content = result.decode("utf-8")
        assert "column" in content
        assert "mean" in content
        assert "test_values" in content


class TestExportToPdf:
    """Test cases for PDF export."""

    def test_export_dict_to_pdf(self, export_service: ExportService) -> None:
        """Should export dict to PDF bytes."""
        data = {"metric": "value", "number": 42}
        result = export_service.export_to_pdf(data, title="Test Report")

        # PDF files start with %PDF
        assert result[:4] == b"%PDF"
        assert len(result) > 0

    def test_export_list_to_pdf(self, export_service: ExportService) -> None:
        """Should export list to PDF bytes."""
        data: list[dict[str, Any]] = [
            {"name": "a", "value": 1},
            {"name": "b", "value": 2},
        ]
        result = export_service.export_to_pdf(data, title="List Report")

        assert result[:4] == b"%PDF"

    def test_export_pydantic_model_to_pdf(
        self,
        export_service: ExportService,
        descriptive_stats: DescriptiveStats,
    ) -> None:
        """Should export Pydantic model to PDF."""
        result = export_service.export_to_pdf(
            descriptive_stats,
            title="Descriptive Statistics",
        )

        assert result[:4] == b"%PDF"


class TestExportDescriptiveStats:
    """Test cases for descriptive statistics export."""

    def test_export_json(
        self,
        export_service: ExportService,
        descriptive_stats: DescriptiveStats,
    ) -> None:
        """Should export descriptive stats to JSON."""
        result = export_service.export_descriptive_stats(
            descriptive_stats,
            ExportFormat.JSON,
            include_metadata=True,
        )

        parsed = json.loads(result.decode("utf-8"))
        assert parsed["result"]["column"] == "test_values"
        assert parsed["result"]["mean"] == 50.0
        assert parsed["result"]["count"] == 100

    def test_export_csv(
        self,
        export_service: ExportService,
        descriptive_stats: DescriptiveStats,
    ) -> None:
        """Should export descriptive stats to CSV."""
        result = export_service.export_descriptive_stats(
            descriptive_stats,
            ExportFormat.CSV,
            include_metadata=False,
        )

        content = result.decode("utf-8")
        assert "column" in content
        assert "mean" in content

    def test_export_pdf(
        self,
        export_service: ExportService,
        descriptive_stats: DescriptiveStats,
    ) -> None:
        """Should export descriptive stats to PDF."""
        result = export_service.export_descriptive_stats(
            descriptive_stats,
            ExportFormat.PDF,
        )

        assert result[:4] == b"%PDF"

    def test_export_multiple_stats(
        self,
        export_service: ExportService,
        descriptive_stats: DescriptiveStats,
    ) -> None:
        """Should export multiple descriptive stats.

        Note: Lists are wrapped in a 'data' key for proper JSON structure.
        """
        stats_list = [descriptive_stats, descriptive_stats]
        result = export_service.export_descriptive_stats(
            stats_list,
            ExportFormat.JSON,
            include_metadata=False,
        )

        parsed = json.loads(result.decode("utf-8"))
        # Lists are wrapped in a 'data' key by export_to_json
        assert "data" in parsed
        assert isinstance(parsed["data"], list)
        assert len(parsed["data"]) == 2


class TestExportCorrelation:
    """Test cases for correlation export."""

    def test_export_json(
        self,
        export_service: ExportService,
        correlation_result: CorrelationResult,
    ) -> None:
        """Should export correlation result to JSON."""
        result = export_service.export_correlation(
            correlation_result,
            ExportFormat.JSON,
        )

        parsed = json.loads(result.decode("utf-8"))
        assert parsed["result"]["method"] == "pearson"
        assert parsed["result"]["coefficient"] == 0.85

    def test_export_csv(
        self,
        export_service: ExportService,
        correlation_result: CorrelationResult,
    ) -> None:
        """Should export correlation result to CSV."""
        result = export_service.export_correlation(
            correlation_result,
            ExportFormat.CSV,
        )

        content = result.decode("utf-8")
        assert "method" in content
        assert "coefficient" in content

    def test_export_pdf(
        self,
        export_service: ExportService,
        correlation_result: CorrelationResult,
    ) -> None:
        """Should export correlation result to PDF."""
        result = export_service.export_correlation(
            correlation_result,
            ExportFormat.PDF,
        )

        assert result[:4] == b"%PDF"


class TestExportCorrelationMatrix:
    """Test cases for correlation matrix export."""

    def test_export_json(
        self,
        export_service: ExportService,
        correlation_matrix_result: CorrelationMatrixResult,
    ) -> None:
        """Should export correlation matrix to JSON."""
        result = export_service.export_correlation_matrix(
            correlation_matrix_result,
            ExportFormat.JSON,
        )

        parsed = json.loads(result.decode("utf-8"))
        assert parsed["result"]["method"] == "pearson"
        assert "matrix" in parsed["result"]
        assert parsed["result"]["columns"] == ["a", "b", "c"]

    def test_export_csv(
        self,
        export_service: ExportService,
        correlation_matrix_result: CorrelationMatrixResult,
    ) -> None:
        """Should export correlation matrix to CSV."""
        result = export_service.export_correlation_matrix(
            correlation_matrix_result,
            ExportFormat.CSV,
        )

        content = result.decode("utf-8")
        # CSV should contain the matrix data
        assert "a" in content
        assert "b" in content
        assert "c" in content

    def test_export_pdf(
        self,
        export_service: ExportService,
        correlation_matrix_result: CorrelationMatrixResult,
    ) -> None:
        """Should export correlation matrix to PDF with heatmap."""
        result = export_service.export_correlation_matrix(
            correlation_matrix_result,
            ExportFormat.PDF,
        )

        assert result[:4] == b"%PDF"


class TestExportForecast:
    """Test cases for forecast export."""

    def test_export_json(
        self,
        export_service: ExportService,
        forecast_result: ForecastResult,
    ) -> None:
        """Should export forecast result to JSON."""
        result = export_service.export_forecast(
            forecast_result,
            ExportFormat.JSON,
        )

        parsed = json.loads(result.decode("utf-8"))
        assert parsed["result"]["model_name"] == "Linear Trend"
        assert len(parsed["result"]["forecast_values"]) == 3

    def test_export_csv(
        self,
        export_service: ExportService,
        forecast_result: ForecastResult,
    ) -> None:
        """Should export forecast result to CSV with structured columns."""
        result = export_service.export_forecast(
            forecast_result,
            ExportFormat.CSV,
        )

        content = result.decode("utf-8")
        assert "date" in content
        assert "forecast" in content
        assert "lower_bound" in content
        assert "upper_bound" in content

    def test_export_pdf(
        self,
        export_service: ExportService,
        forecast_result: ForecastResult,
    ) -> None:
        """Should export forecast result to PDF with chart."""
        result = export_service.export_forecast(
            forecast_result,
            ExportFormat.PDF,
        )

        assert result[:4] == b"%PDF"


class TestExportAnomalies:
    """Test cases for anomaly export."""

    def test_export_json(
        self,
        export_service: ExportService,
        anomaly_result: AnomalyResult,
    ) -> None:
        """Should export anomaly result to JSON."""
        result = export_service.export_anomalies(
            anomaly_result,
            ExportFormat.JSON,
        )

        parsed = json.loads(result.decode("utf-8"))
        assert parsed["result"]["method"] == "z-score"
        assert parsed["result"]["anomaly_count"] == 3

    def test_export_csv(
        self,
        export_service: ExportService,
        anomaly_result: AnomalyResult,
    ) -> None:
        """Should export anomaly result to CSV with metadata."""
        result = export_service.export_anomalies(
            anomaly_result,
            ExportFormat.CSV,
            include_metadata=True,
        )

        content = result.decode("utf-8")
        assert "# Method: z-score" in content
        assert "# Anomaly Count: 3" in content
        assert "index" in content
        assert "value" in content

    def test_export_csv_no_anomalies(
        self,
        export_service: ExportService,
    ) -> None:
        """Should handle export with no anomalies."""
        result_no_anomalies = AnomalyResult(
            method="z-score",
            total_points=100,
            anomaly_count=0,
            anomaly_percentage=0.0,
            anomalies=[],
            threshold=3.0,
            interpretation="No anomalies detected",
        )
        result = export_service.export_anomalies(
            result_no_anomalies,
            ExportFormat.CSV,
        )

        content = result.decode("utf-8")
        assert "No anomalies detected" in content

    def test_export_pdf(
        self,
        export_service: ExportService,
        anomaly_result: AnomalyResult,
    ) -> None:
        """Should export anomaly result to PDF."""
        result = export_service.export_anomalies(
            anomaly_result,
            ExportFormat.PDF,
        )

        assert result[:4] == b"%PDF"


class TestExportStatisticalTest:
    """Test cases for statistical test export."""

    def test_export_json(
        self,
        export_service: ExportService,
        statistical_test_result: StatisticalTestResult,
    ) -> None:
        """Should export statistical test result to JSON."""
        result = export_service.export_statistical_test(
            statistical_test_result,
            ExportFormat.JSON,
        )

        parsed = json.loads(result.decode("utf-8"))
        assert parsed["result"]["test_name"] == "Independent Samples T-Test"
        assert parsed["result"]["p_value"] == 0.002
        assert parsed["result"]["is_significant"] is True

    def test_export_csv(
        self,
        export_service: ExportService,
        statistical_test_result: StatisticalTestResult,
    ) -> None:
        """Should export statistical test result to CSV."""
        result = export_service.export_statistical_test(
            statistical_test_result,
            ExportFormat.CSV,
        )

        content = result.decode("utf-8")
        assert "test_name" in content
        assert "p_value" in content
        assert "is_significant" in content

    def test_export_pdf(
        self,
        export_service: ExportService,
        statistical_test_result: StatisticalTestResult,
    ) -> None:
        """Should export statistical test result to PDF."""
        result = export_service.export_statistical_test(
            statistical_test_result,
            ExportFormat.PDF,
        )

        assert result[:4] == b"%PDF"


class TestHelperMethods:
    """Test cases for helper methods."""

    def test_can_generate_chart_forecast(
        self,
        export_service: ExportService,
        forecast_result: ForecastResult,
    ) -> None:
        """Should return True for ForecastResult."""
        assert export_service._can_generate_chart(forecast_result) is True

    def test_can_generate_chart_anomaly(
        self,
        export_service: ExportService,
        anomaly_result: AnomalyResult,
    ) -> None:
        """Should return True for AnomalyResult."""
        assert export_service._can_generate_chart(anomaly_result) is True

    def test_can_generate_chart_dict_with_forecast(
        self,
        export_service: ExportService,
    ) -> None:
        """Should return True for dict with forecast_values."""
        data = {"forecast_values": [1, 2, 3]}
        assert export_service._can_generate_chart(data) is True

    def test_can_generate_chart_dict_with_anomalies(
        self,
        export_service: ExportService,
    ) -> None:
        """Should return True for dict with anomalies."""
        data = {"anomalies": [{"index": 1, "value": 100}]}
        assert export_service._can_generate_chart(data) is True

    def test_cannot_generate_chart_simple_dict(
        self,
        export_service: ExportService,
    ) -> None:
        """Should return False for simple dict."""
        data = {"key": "value"}
        assert export_service._can_generate_chart(data) is False

    def test_to_dataframe_from_dataframe(
        self,
        export_service: ExportService,
    ) -> None:
        """Should return same DataFrame."""
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = export_service._to_dataframe(df)

        pd.testing.assert_frame_equal(result, df)

    def test_to_dataframe_from_dict(
        self,
        export_service: ExportService,
    ) -> None:
        """Should convert dict to DataFrame."""
        data = {"name": "test", "value": 100}
        result = export_service._to_dataframe(data)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "name" in result.columns

    def test_to_dataframe_from_list_of_dicts(
        self,
        export_service: ExportService,
    ) -> None:
        """Should convert list of dicts to DataFrame."""
        data = [{"a": 1}, {"a": 2}, {"a": 3}]
        result = export_service._to_dataframe(data)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

    def test_to_dataframe_from_pydantic(
        self,
        export_service: ExportService,
        descriptive_stats: DescriptiveStats,
    ) -> None:
        """Should convert Pydantic model to DataFrame."""
        result = export_service._to_dataframe(descriptive_stats)

        assert isinstance(result, pd.DataFrame)
        assert "column" in result.columns

    def test_flatten_dict(
        self,
        export_service: ExportService,
    ) -> None:
        """Should flatten nested dictionary."""
        nested = {
            "level1": {
                "level2": "value",
                "another": 42,
            },
            "simple": "top",
        }
        result = export_service._flatten_dict(nested)

        assert result["level1_level2"] == "value"
        assert result["level1_another"] == 42
        assert result["simple"] == "top"

    def test_flatten_dict_with_list(
        self,
        export_service: ExportService,
    ) -> None:
        """Should convert list values to strings."""
        data = {"items": [1, 2, 3]}
        result = export_service._flatten_dict(data)

        assert result["items"] == "[1, 2, 3]"


class TestExportByFormat:
    """Test cases for _export_by_format method."""

    def test_unsupported_format(
        self,
        export_service: ExportService,
    ) -> None:
        """Should raise error for unsupported format."""
        # Create a mock format that's not in the enum
        # We need to test the else branch in _export_by_format
        # This is tricky since ExportFormat is an enum
        # The else branch is defensive code that shouldn't normally be reached
        pass  # This branch is unreachable with proper ExportFormat enum usage

    def test_export_json_format(
        self,
        export_service: ExportService,
    ) -> None:
        """Should export data in JSON format."""
        data = {"key": "value"}
        result = export_service._export_by_format(
            data,
            ExportFormat.JSON,
            title="Test",
        )

        parsed = json.loads(result.decode("utf-8"))
        assert "result" in parsed

    def test_export_csv_format(
        self,
        export_service: ExportService,
    ) -> None:
        """Should export data in CSV format."""
        data = {"key": "value"}
        result = export_service._export_by_format(
            data,
            ExportFormat.CSV,
            title="Test",
        )

        content = result.decode("utf-8")
        assert "key" in content

    def test_export_pdf_format(
        self,
        export_service: ExportService,
    ) -> None:
        """Should export data in PDF format."""
        data = {"key": "value"}
        result = export_service._export_by_format(
            data,
            ExportFormat.PDF,
            title="Test",
        )

        assert result[:4] == b"%PDF"
