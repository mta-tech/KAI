"""Batch analytics models for batch processing of analytics operations."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class BatchJobStatus(str, Enum):
    """Status of a batch analytics job.

    Statuses:
    - pending: Job created but not yet started
    - running: Job is currently processing operations
    - completed: All operations finished successfully
    - partial: Job finished but some operations failed
    - failed: Job failed completely (e.g., all operations failed)
    - cancelled: Job was cancelled before completion
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


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


class AnalyticsBatchRequest(BaseModel):
    """Request model for submitting a batch of analytics operations.

    Allows submitting multiple analytics operations to be processed concurrently
    with configurable concurrency limits.
    """

    operations: list[SingleAnalyticsRequest] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of analytics operations to process. "
        "Must contain at least 1 and at most 100 operations.",
    )
    max_concurrency: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of operations to process concurrently. "
        "Higher values may improve throughput but use more resources.",
    )

    @field_validator("operations")
    @classmethod
    def validate_operations_not_empty(
        cls, v: list[SingleAnalyticsRequest]
    ) -> list[SingleAnalyticsRequest]:
        """Ensure at least one operation is provided."""
        if not v:
            raise ValueError("At least one operation must be provided")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "operations": [
                        {
                            "operation_id": "stats_1",
                            "operation_type": "descriptive_stats",
                            "params": {"data": [1.0, 2.0, 3.0, 4.0, 5.0]},
                        },
                        {
                            "operation_id": "corr_1",
                            "operation_type": "correlation",
                            "params": {
                                "x": [1.0, 2.0, 3.0],
                                "y": [2.0, 4.0, 6.0],
                            },
                        },
                    ],
                    "max_concurrency": 5,
                }
            ]
        }
    }


class AnalyticsBatchResult(BaseModel):
    """Result of a single analytics operation within a batch.

    Tracks the outcome of each operation including success/failure status,
    the actual result data or error message, and timing information.
    """

    operation_id: str = Field(
        ...,
        description="Unique identifier for this operation within the batch.",
    )
    operation_type: AnalyticsOperationType = Field(
        ...,
        description="The type of analytics operation that was executed.",
    )
    status: str = Field(
        ...,
        description="Status of this operation: 'completed' or 'failed'.",
    )
    result: dict[str, Any] | None = Field(
        default=None,
        description="The result data if the operation completed successfully.",
    )
    error: str | None = Field(
        default=None,
        description="Error message if the operation failed.",
    )
    started_at: datetime | None = Field(
        default=None,
        description="When this operation started processing.",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When this operation finished (success or failure).",
    )

    @property
    def is_successful(self) -> bool:
        """Return True if the operation completed successfully."""
        return self.status == "completed"

    @property
    def duration_ms(self) -> float | None:
        """Return the operation duration in milliseconds, if available."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds() * 1000
        return None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "operation_id": "stats_1",
                    "operation_type": "descriptive_stats",
                    "status": "completed",
                    "result": {
                        "count": 5,
                        "mean": 3.0,
                        "std": 1.58,
                        "min": 1.0,
                        "max": 5.0,
                    },
                    "error": None,
                    "started_at": "2024-01-01T12:00:00",
                    "completed_at": "2024-01-01T12:00:01",
                },
                {
                    "operation_id": "corr_1",
                    "operation_type": "correlation",
                    "status": "failed",
                    "result": None,
                    "error": "Insufficient data points for correlation analysis",
                    "started_at": "2024-01-01T12:00:01",
                    "completed_at": "2024-01-01T12:00:01",
                },
            ]
        }
    }


class AnalyticsBatchStatus(BaseModel):
    """Status model for tracking batch analytics job progress.

    Provides comprehensive information about a batch job including:
    - Current processing status
    - Progress counters (total, completed, failed)
    - Individual operation results
    - Timing information
    """

    batch_id: str = Field(
        ...,
        description="Unique identifier for this batch job.",
    )
    status: BatchJobStatus = Field(
        ...,
        description="Current status of the batch job.",
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of operations in this batch.",
    )
    completed: int = Field(
        default=0,
        ge=0,
        description="Number of operations that completed successfully.",
    )
    failed: int = Field(
        default=0,
        ge=0,
        description="Number of operations that failed.",
    )
    results: dict[str, AnalyticsBatchResult] = Field(
        default_factory=dict,
        description="Results of individual operations, keyed by operation_id.",
    )
    created_at: datetime = Field(
        ...,
        description="When the batch job was created.",
    )
    started_at: datetime | None = Field(
        default=None,
        description="When the batch job started processing.",
    )
    updated_at: datetime = Field(
        ...,
        description="When the batch job status was last updated.",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the batch job finished (all operations done).",
    )

    @property
    def pending(self) -> int:
        """Return the number of operations still pending."""
        return self.total - self.completed - self.failed

    @property
    def progress_percent(self) -> float:
        """Return the completion percentage (0-100)."""
        if self.total == 0:
            return 100.0
        return ((self.completed + self.failed) / self.total) * 100

    @property
    def is_finished(self) -> bool:
        """Return True if the batch job has finished processing."""
        return self.status in (
            BatchJobStatus.COMPLETED,
            BatchJobStatus.PARTIAL,
            BatchJobStatus.FAILED,
            BatchJobStatus.CANCELLED,
        )

    @property
    def duration_ms(self) -> float | None:
        """Return the total batch job duration in milliseconds, if available."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds() * 1000
        return None

    def get_successful_results(self) -> list[AnalyticsBatchResult]:
        """Return all successful operation results."""
        return [r for r in self.results.values() if r.is_successful]

    def get_failed_results(self) -> list[AnalyticsBatchResult]:
        """Return all failed operation results."""
        return [r for r in self.results.values() if not r.is_successful]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "batch_id": "550e8400-e29b-41d4-a716-446655440000",
                    "status": "running",
                    "total": 5,
                    "completed": 2,
                    "failed": 0,
                    "results": {},
                    "created_at": "2024-01-01T12:00:00",
                    "started_at": "2024-01-01T12:00:00",
                    "updated_at": "2024-01-01T12:00:05",
                    "completed_at": None,
                },
                {
                    "batch_id": "550e8400-e29b-41d4-a716-446655440001",
                    "status": "completed",
                    "total": 3,
                    "completed": 3,
                    "failed": 0,
                    "results": {
                        "stats_1": {
                            "operation_id": "stats_1",
                            "operation_type": "descriptive_stats",
                            "status": "completed",
                            "result": {"mean": 3.0, "std": 1.58},
                            "error": None,
                            "started_at": "2024-01-01T12:00:00",
                            "completed_at": "2024-01-01T12:00:01",
                        }
                    },
                    "created_at": "2024-01-01T12:00:00",
                    "started_at": "2024-01-01T12:00:00",
                    "updated_at": "2024-01-01T12:00:10",
                    "completed_at": "2024-01-01T12:00:10",
                },
            ]
        }
    }
