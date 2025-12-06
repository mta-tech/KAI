"""Tests for AnomalyService."""

import pandas as pd
import pytest

from app.modules.analytics.services.anomaly_service import AnomalyService


@pytest.fixture
def anomaly_service() -> AnomalyService:
    """Anomaly service instance."""
    return AnomalyService()


@pytest.fixture
def normal_series() -> pd.Series:
    """Series with normal distribution."""
    return pd.Series([10, 11, 12, 10, 11, 12, 10, 11, 12, 10])


@pytest.fixture
def series_with_outliers() -> pd.Series:
    """Series with clear outliers."""
    return pd.Series([10, 11, 12, 10, 11, 100, 10, 11, 12, -50])


class TestZScoreDetection:
    """Test cases for Z-score anomaly detection."""

    def test_no_anomalies(
        self,
        anomaly_service: AnomalyService,
        normal_series: pd.Series,
    ) -> None:
        """Should find no anomalies in normal data."""
        result = anomaly_service.detect_zscore(normal_series)

        assert result.method == "z-score"
        assert result.anomaly_count == 0
        assert result.anomaly_percentage == 0.0

    def test_with_anomalies(
        self,
        anomaly_service: AnomalyService,
        series_with_outliers: pd.Series,
    ) -> None:
        """Should detect anomalies in data with outliers."""
        result = anomaly_service.detect_zscore(series_with_outliers, threshold=2.0)

        assert result.method == "z-score"
        assert result.anomaly_count > 0
        assert len(result.anomalies) > 0

    def test_zero_variance(
        self,
        anomaly_service: AnomalyService,
    ) -> None:
        """Should handle zero variance data."""
        constant = pd.Series([5, 5, 5, 5, 5])
        result = anomaly_service.detect_zscore(constant)

        assert result.anomaly_count == 0
        assert "No variance" in result.interpretation


class TestIQRDetection:
    """Test cases for IQR anomaly detection."""

    def test_no_anomalies(
        self,
        anomaly_service: AnomalyService,
        normal_series: pd.Series,
    ) -> None:
        """Should find no anomalies in normal data."""
        result = anomaly_service.detect_iqr(normal_series)

        assert result.method == "iqr"
        assert result.anomaly_count == 0

    def test_with_anomalies(
        self,
        anomaly_service: AnomalyService,
        series_with_outliers: pd.Series,
    ) -> None:
        """Should detect anomalies using IQR method."""
        result = anomaly_service.detect_iqr(series_with_outliers)

        assert result.method == "iqr"
        assert result.anomaly_count > 0
        # Check that detected anomalies have direction
        for anomaly in result.anomalies:
            assert "direction" in anomaly


class TestIsolationForest:
    """Test cases for Isolation Forest anomaly detection."""

    def test_isolation_forest(
        self,
        anomaly_service: AnomalyService,
    ) -> None:
        """Should detect anomalies using Isolation Forest."""
        df = pd.DataFrame(
            {
                "x": [1, 2, 3, 4, 5, 100, 2, 3, 4, 5],
                "y": [1, 2, 3, 4, 5, 100, 2, 3, 4, 5],
            }
        )

        result = anomaly_service.detect_isolation_forest(
            df, columns=["x", "y"], contamination=0.1
        )

        assert result.method == "isolation_forest"
        assert result.total_points == 10
        assert result.anomaly_count > 0
