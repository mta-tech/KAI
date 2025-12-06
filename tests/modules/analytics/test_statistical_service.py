"""Tests for StatisticalService."""

import pandas as pd
import pytest

from app.modules.analytics.services.statistical_service import StatisticalService


@pytest.fixture
def stat_service() -> StatisticalService:
    """Statistical service instance."""
    return StatisticalService()


@pytest.fixture
def sample_series() -> pd.Series:
    """Sample series for testing."""
    return pd.Series([10, 12, 14, 16, 18, 20, 22, 24, 26, 28], name="values")


@pytest.fixture
def group1() -> pd.Series:
    """First group for comparison tests."""
    return pd.Series([10, 12, 14, 16, 18])


@pytest.fixture
def group2() -> pd.Series:
    """Second group for comparison tests."""
    return pd.Series([20, 22, 24, 26, 28])


class TestDescriptiveStats:
    """Test cases for descriptive statistics."""

    def test_basic_stats(
        self,
        stat_service: StatisticalService,
        sample_series: pd.Series,
    ) -> None:
        """Should calculate basic descriptive statistics."""
        result = stat_service.descriptive_stats(sample_series)

        assert result.column == "values"
        assert result.count == 10
        assert result.mean == 19.0
        assert result.min == 10
        assert result.max == 28
        assert result.median == 19.0

    def test_skewness_kurtosis(
        self,
        stat_service: StatisticalService,
        sample_series: pd.Series,
    ) -> None:
        """Should calculate skewness and kurtosis."""
        result = stat_service.descriptive_stats(sample_series)

        assert result.skewness is not None
        assert result.kurtosis is not None


class TestTTest:
    """Test cases for t-test."""

    def test_t_test_significant(
        self,
        stat_service: StatisticalService,
        group1: pd.Series,
        group2: pd.Series,
    ) -> None:
        """Should detect significant difference between groups."""
        result = stat_service.t_test_independent(group1, group2)

        assert result.test_name == "Independent Samples T-Test"
        assert result.is_significant is True
        assert result.p_value < 0.05
        assert result.effect_size is not None

    def test_t_test_not_significant(
        self,
        stat_service: StatisticalService,
    ) -> None:
        """Should not detect significance when groups are similar."""
        group1 = pd.Series([10, 11, 12, 13, 14])
        group2 = pd.Series([10, 12, 11, 13, 15])

        result = stat_service.t_test_independent(group1, group2)

        assert result.is_significant is False
        assert result.p_value > 0.05


class TestANOVA:
    """Test cases for ANOVA."""

    def test_anova_significant(
        self,
        stat_service: StatisticalService,
    ) -> None:
        """Should detect significant difference between groups."""
        g1 = pd.Series([1, 2, 3, 4, 5])
        g2 = pd.Series([10, 11, 12, 13, 14])
        g3 = pd.Series([20, 21, 22, 23, 24])

        result = stat_service.anova(g1, g2, g3)

        assert result.test_name == "One-Way ANOVA"
        assert result.is_significant is True
        assert result.details["num_groups"] == 3


class TestCorrelation:
    """Test cases for correlation."""

    def test_pearson_strong_positive(
        self,
        stat_service: StatisticalService,
    ) -> None:
        """Should detect strong positive correlation."""
        x = pd.Series([1, 2, 3, 4, 5])
        y = pd.Series([2, 4, 6, 8, 10])

        result = stat_service.correlation(x, y, method="pearson")

        assert result.method == "pearson"
        assert result.coefficient > 0.9
        assert result.is_significant is True

    def test_correlation_matrix(
        self,
        stat_service: StatisticalService,
    ) -> None:
        """Should calculate correlation matrix."""
        df = pd.DataFrame(
            {
                "a": [1, 2, 3, 4, 5],
                "b": [2, 4, 6, 8, 10],
                "c": [5, 4, 3, 2, 1],
            }
        )

        result = stat_service.correlation_matrix(df)

        assert result.method == "pearson"
        assert "a" in result.columns
        assert "b" in result.columns
        assert "c" in result.columns
        assert len(result.matrix) == 3
