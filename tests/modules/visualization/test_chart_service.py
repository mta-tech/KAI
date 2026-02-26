"""Tests for ChartService."""

import pandas as pd
import pytest

from app.modules.visualization.models import ChartConfig, ChartType
from app.modules.visualization.services.chart_service import ChartService


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Sample DataFrame for testing."""
    return pd.DataFrame({
        "category": ["A", "B", "C", "D"],
        "value": [10, 20, 15, 25],
        "count": [100, 200, 150, 250],
    })


@pytest.fixture
def time_series_df() -> pd.DataFrame:
    """Time series DataFrame for testing."""
    return pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=10, freq="D"),
        "value": [10, 12, 11, 15, 14, 18, 17, 20, 19, 22],
    })


@pytest.fixture
def chart_service() -> ChartService:
    """Chart service instance."""
    return ChartService()


class TestChartService:
    """Test cases for ChartService."""

    def test_generate_bar_chart(
        self,
        chart_service: ChartService,
        sample_df: pd.DataFrame,
    ) -> None:
        """Should generate bar chart."""
        config = ChartConfig(
            chart_type=ChartType.BAR,
            x_column="category",
            y_column="value",
            title="Test Bar Chart",
        )

        result = chart_service.generate_chart(sample_df, config)

        assert result.chart_type == "bar"
        assert result.html is not None
        assert "plotly" in result.html.lower()
        assert result.json_spec is not None

    def test_generate_line_chart(
        self,
        chart_service: ChartService,
        time_series_df: pd.DataFrame,
    ) -> None:
        """Should generate line chart."""
        config = ChartConfig(
            chart_type=ChartType.LINE,
            x_column="date",
            y_column="value",
            title="Test Line Chart",
        )

        result = chart_service.generate_chart(time_series_df, config)

        assert result.chart_type == "line"
        assert result.html is not None

    def test_generate_pie_chart(
        self,
        chart_service: ChartService,
        sample_df: pd.DataFrame,
    ) -> None:
        """Should generate pie chart."""
        config = ChartConfig(
            chart_type=ChartType.PIE,
            x_column="category",
            y_column="value",
            title="Test Pie Chart",
        )

        result = chart_service.generate_chart(sample_df, config)

        assert result.chart_type == "pie"
        assert result.html is not None

    def test_generate_scatter_chart(
        self,
        chart_service: ChartService,
        sample_df: pd.DataFrame,
    ) -> None:
        """Should generate scatter plot."""
        config = ChartConfig(
            chart_type=ChartType.SCATTER,
            x_column="value",
            y_column="count",
            title="Test Scatter Plot",
        )

        result = chart_service.generate_chart(sample_df, config)

        assert result.chart_type == "scatter"
        assert result.html is not None

    def test_generate_histogram(
        self,
        chart_service: ChartService,
        sample_df: pd.DataFrame,
    ) -> None:
        """Should generate histogram."""
        config = ChartConfig(
            chart_type=ChartType.HISTOGRAM,
            x_column="value",
            title="Test Histogram",
        )

        result = chart_service.generate_chart(sample_df, config)

        assert result.chart_type == "histogram"
        assert result.html is not None

    def test_apply_dark_theme(
        self,
        chart_service: ChartService,
        sample_df: pd.DataFrame,
    ) -> None:
        """Should apply dark theme."""
        config = ChartConfig(
            chart_type=ChartType.BAR,
            x_column="category",
            y_column="value",
            theme="dark",
        )

        result = chart_service.generate_chart(sample_df, config)

        assert result.json_spec is not None
        layout = result.json_spec.get("layout", {})
        assert layout.get("template") is not None

    def test_non_interactive_chart(
        self,
        chart_service: ChartService,
        sample_df: pd.DataFrame,
    ) -> None:
        """Should generate non-interactive chart."""
        config = ChartConfig(
            chart_type=ChartType.BAR,
            x_column="category",
            y_column="value",
            interactive=False,
        )

        result = chart_service.generate_chart(sample_df, config)

        assert result.html is None
        assert result.json_spec is not None


class TestChartRecommendation:
    """Test cases for chart type recommendation."""

    def test_recommend_line_for_time_series(
        self,
        chart_service: ChartService,
        time_series_df: pd.DataFrame,
    ) -> None:
        """Should recommend line chart for time series."""
        rec = chart_service.recommend_chart_type(time_series_df)

        assert rec.chart_type == ChartType.LINE
        assert rec.confidence >= 0.8
        assert rec.x_column == "date"
        assert rec.y_column == "value"

    def test_recommend_bar_for_categorical(
        self,
        chart_service: ChartService,
    ) -> None:
        """Should recommend bar chart for categorical data."""
        df = pd.DataFrame({
            "region": ["North", "South", "East", "West", "Central", "NE", "NW", "SE"],
            "sales": [100, 200, 150, 180, 120, 90, 110, 130],
        })

        rec = chart_service.recommend_chart_type(df)

        assert rec.chart_type == ChartType.BAR
        assert rec.confidence >= 0.7

    def test_recommend_pie_for_few_categories(
        self,
        chart_service: ChartService,
    ) -> None:
        """Should recommend pie chart for few categories."""
        df = pd.DataFrame({
            "status": ["Active", "Inactive", "Pending"],
            "count": [50, 30, 20],
        })

        rec = chart_service.recommend_chart_type(df)

        assert rec.chart_type == ChartType.PIE
        assert rec.confidence >= 0.7
