"""Batch analytics models for batch processing of analytics operations."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class AnalyticsOperationType(str, Enum):
    """Types of analytics operations supported in batch processing.

    Each operation type corresponds to an analytics endpoint:
    - descriptive_stats: Calculate descriptive statistics for numeric data
    - t_test: Independent samples t-test between two groups
    - correlation: Correlation analysis between two variables
    - correlation_matrix: Full correlation matrix for a dataset
    - anomaly_detection: Z-score or IQR based anomaly detection
    - forecast: Simple moving average forecast for time series
    """

    DESCRIPTIVE_STATS = "descriptive_stats"
    T_TEST = "t_test"
    CORRELATION = "correlation"
    CORRELATION_MATRIX = "correlation_matrix"
    ANOMALY_DETECTION = "anomaly_detection"
    FORECAST = "forecast"


class SingleAnalyticsRequest(BaseModel):
    """A single analytics operation request within a batch.

    Each request specifies the operation type and parameters needed for that operation.
    Parameters vary by operation type:

    - descriptive_stats: data (list[float|int]), column_name (str, optional)
    - t_test: group1 (list[float|int]), group2 (list[float|int]), alpha (float, optional)
    - correlation: x (list[float|int]), y (list[float|int]), method (str, optional), alpha (float, optional)
    - correlation_matrix: data (list[dict]), method (str, optional)
    - anomaly_detection: data (list[float|int]), method (str, optional), threshold (float, optional)
    - forecast: values (list[float|int]), periods (int, optional)
    """

    operation_id: str | None = Field(
        default=None,
        description="Optional unique identifier for this operation. "
        "If not provided, a sequential ID will be assigned.",
    )
    operation_type: AnalyticsOperationType = Field(
        ...,
        description="The type of analytics operation to perform.",
    )
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters for the analytics operation. "
        "Required parameters depend on the operation_type.",
    )

    @field_validator("params")
    @classmethod
    def validate_params_not_empty(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Ensure params dict is provided for operations that require data."""
        # Basic validation - detailed param validation happens during execution
        return v

    def get_required_params(self) -> list[str]:
        """Return the required parameters for this operation type."""
        required_params: dict[AnalyticsOperationType, list[str]] = {
            AnalyticsOperationType.DESCRIPTIVE_STATS: ["data"],
            AnalyticsOperationType.T_TEST: ["group1", "group2"],
            AnalyticsOperationType.CORRELATION: ["x", "y"],
            AnalyticsOperationType.CORRELATION_MATRIX: ["data"],
            AnalyticsOperationType.ANOMALY_DETECTION: ["data"],
            AnalyticsOperationType.FORECAST: ["values"],
        }
        return required_params.get(self.operation_type, [])

    def validate_required_params(self) -> list[str]:
        """Validate that all required parameters are present.

        Returns:
            List of missing parameter names, empty if all required params are present.
        """
        required = self.get_required_params()
        missing = [param for param in required if param not in self.params]
        return missing

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "operation_id": "stats_1",
                    "operation_type": "descriptive_stats",
                    "params": {"data": [1.0, 2.0, 3.0, 4.0, 5.0], "column_name": "values"},
                },
                {
                    "operation_id": "ttest_1",
                    "operation_type": "t_test",
                    "params": {
                        "group1": [1.0, 2.0, 3.0],
                        "group2": [4.0, 5.0, 6.0],
                        "alpha": 0.05,
                    },
                },
                {
                    "operation_id": "corr_1",
                    "operation_type": "correlation",
                    "params": {
                        "x": [1.0, 2.0, 3.0, 4.0],
                        "y": [2.0, 4.0, 6.0, 8.0],
                        "method": "pearson",
                    },
                },
                {
                    "operation_id": "anomaly_1",
                    "operation_type": "anomaly_detection",
                    "params": {
                        "data": [1.0, 2.0, 100.0, 3.0, 4.0],
                        "method": "zscore",
                        "threshold": 2.0,
                    },
                },
                {
                    "operation_id": "forecast_1",
                    "operation_type": "forecast",
                    "params": {"values": [10, 20, 30, 40, 50], "periods": 5},
                },
            ]
        }
    }
