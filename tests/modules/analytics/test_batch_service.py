"""Tests for AnalyticsBatchService."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

import pytest

from app.modules.analytics.batch_models import (
    AnalyticsBatchResult,
    AnalyticsBatchStatus,
    AnalyticsOperationType,
    BatchJobStatus,
    SingleAnalyticsRequest,
)
from app.modules.analytics.services.batch_service import AnalyticsBatchService


@pytest.fixture
def batch_service() -> AnalyticsBatchService:
    """Create a fresh batch service instance for each test."""
    return AnalyticsBatchService()


@pytest.fixture
def descriptive_stats_operation() -> SingleAnalyticsRequest:
    """Sample descriptive stats operation."""
    return SingleAnalyticsRequest(
        operation_id="stats_1",
        operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
        params={"data": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]},
    )


@pytest.fixture
def t_test_operation() -> SingleAnalyticsRequest:
    """Sample t-test operation."""
    return SingleAnalyticsRequest(
        operation_id="ttest_1",
        operation_type=AnalyticsOperationType.T_TEST,
        params={
            "group1": [10.0, 12.0, 14.0, 16.0, 18.0],
            "group2": [20.0, 22.0, 24.0, 26.0, 28.0],
            "alpha": 0.05,
        },
    )


@pytest.fixture
def correlation_operation() -> SingleAnalyticsRequest:
    """Sample correlation operation."""
    return SingleAnalyticsRequest(
        operation_id="corr_1",
        operation_type=AnalyticsOperationType.CORRELATION,
        params={
            "x": [1.0, 2.0, 3.0, 4.0, 5.0],
            "y": [2.0, 4.0, 6.0, 8.0, 10.0],
            "method": "pearson",
        },
    )


@pytest.fixture
def correlation_matrix_operation() -> SingleAnalyticsRequest:
    """Sample correlation matrix operation."""
    return SingleAnalyticsRequest(
        operation_id="corr_matrix_1",
        operation_type=AnalyticsOperationType.CORRELATION_MATRIX,
        params={
            "data": [
                {"a": 1, "b": 2, "c": 3},
                {"a": 2, "b": 4, "c": 6},
                {"a": 3, "b": 6, "c": 9},
                {"a": 4, "b": 8, "c": 12},
                {"a": 5, "b": 10, "c": 15},
            ],
            "method": "pearson",
        },
    )


@pytest.fixture
def anomaly_detection_operation() -> SingleAnalyticsRequest:
    """Sample anomaly detection operation."""
    return SingleAnalyticsRequest(
        operation_id="anomaly_1",
        operation_type=AnalyticsOperationType.ANOMALY_DETECTION,
        params={
            "data": [1.0, 2.0, 3.0, 100.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0],
            "method": "zscore",
            "threshold": 2.0,
        },
    )


@pytest.fixture
def forecast_operation() -> SingleAnalyticsRequest:
    """Sample forecast operation."""
    return SingleAnalyticsRequest(
        operation_id="forecast_1",
        operation_type=AnalyticsOperationType.FORECAST,
        params={
            "values": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0],
            "periods": 5,
        },
    )


class TestBatchJobCreation:
    """Test cases for batch job creation."""

    def test_create_batch_job_single_operation(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should create a batch job with a single operation."""
        job = batch_service.create_batch_job([descriptive_stats_operation])

        assert job.batch_id is not None
        assert len(job.batch_id) == 36  # UUID format
        assert job.status == BatchJobStatus.PENDING
        assert job.total == 1
        assert job.completed == 0
        assert job.failed == 0
        assert job.results == {}
        assert job.created_at is not None
        assert job.started_at is None
        assert job.completed_at is None

    def test_create_batch_job_multiple_operations(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
        t_test_operation: SingleAnalyticsRequest,
        correlation_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should create a batch job with multiple operations."""
        operations = [
            descriptive_stats_operation,
            t_test_operation,
            correlation_operation,
        ]
        job = batch_service.create_batch_job(operations)

        assert job.total == 3
        assert job.status == BatchJobStatus.PENDING

    def test_create_batch_job_assigns_operation_ids(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should assign sequential operation IDs when not provided."""
        operations = [
            SingleAnalyticsRequest(
                operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
                params={"data": [1.0, 2.0, 3.0]},
            ),
            SingleAnalyticsRequest(
                operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
                params={"data": [4.0, 5.0, 6.0]},
            ),
        ]

        batch_service.create_batch_job(operations)

        # Check that operation IDs were assigned
        assert operations[0].operation_id == "op_0"
        assert operations[1].operation_id == "op_1"

    def test_create_batch_job_preserves_existing_ids(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should preserve existing operation IDs."""
        job = batch_service.create_batch_job([descriptive_stats_operation])

        # The operation should still have its original ID
        assert descriptive_stats_operation.operation_id == "stats_1"
        assert job is not None

    def test_create_batch_job_empty_operations_raises(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should raise ValueError for empty operations list."""
        with pytest.raises(ValueError, match="At least one operation must be provided"):
            batch_service.create_batch_job([])

    def test_create_batch_job_stores_in_memory(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should store job in internal storage."""
        job = batch_service.create_batch_job([descriptive_stats_operation])

        stored_job = batch_service.get_batch_job(job.batch_id)
        assert stored_job is not None
        assert stored_job.batch_id == job.batch_id


class TestBatchJobRetrieval:
    """Test cases for batch job retrieval."""

    def test_get_existing_batch_job(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should retrieve an existing batch job."""
        created_job = batch_service.create_batch_job([descriptive_stats_operation])

        retrieved_job = batch_service.get_batch_job(created_job.batch_id)

        assert retrieved_job is not None
        assert retrieved_job.batch_id == created_job.batch_id
        assert retrieved_job.total == created_job.total

    def test_get_nonexistent_batch_job(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should return None for nonexistent batch job."""
        result = batch_service.get_batch_job("nonexistent-id")

        assert result is None


class TestBatchJobDeletion:
    """Test cases for batch job deletion."""

    def test_delete_existing_batch_job(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should delete an existing batch job."""
        job = batch_service.create_batch_job([descriptive_stats_operation])
        batch_id = job.batch_id

        result = batch_service.delete_batch_job(batch_id)

        assert result is True
        assert batch_service.get_batch_job(batch_id) is None

    def test_delete_nonexistent_batch_job(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should return False for nonexistent batch job."""
        result = batch_service.delete_batch_job("nonexistent-id")

        assert result is False


class TestBatchJobCancellation:
    """Test cases for batch job cancellation."""

    def test_cancel_pending_job(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should cancel a pending batch job."""
        job = batch_service.create_batch_job([descriptive_stats_operation])

        cancelled_job = batch_service.cancel_batch_job(job.batch_id)

        assert cancelled_job is not None
        assert cancelled_job.status == BatchJobStatus.CANCELLED
        assert cancelled_job.completed_at is not None

    def test_cancel_nonexistent_job(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should return None for nonexistent batch job."""
        result = batch_service.cancel_batch_job("nonexistent-id")

        assert result is None

    def test_cancel_completed_job_no_change(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should not cancel an already completed job."""
        job = batch_service.create_batch_job([descriptive_stats_operation])
        # Manually set to completed status
        job.status = BatchJobStatus.COMPLETED

        cancelled_job = batch_service.cancel_batch_job(job.batch_id)

        assert cancelled_job is not None
        assert cancelled_job.status == BatchJobStatus.COMPLETED  # Unchanged

    def test_cancel_failed_job_no_change(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should not cancel an already failed job."""
        job = batch_service.create_batch_job([descriptive_stats_operation])
        job.status = BatchJobStatus.FAILED

        cancelled_job = batch_service.cancel_batch_job(job.batch_id)

        assert cancelled_job is not None
        assert cancelled_job.status == BatchJobStatus.FAILED  # Unchanged


class TestExecuteSingleOperation:
    """Test cases for execute_single_operation routing."""

    def test_execute_descriptive_stats(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should execute descriptive stats operation."""
        result = batch_service.execute_single_operation(descriptive_stats_operation)

        assert result.operation_id == "stats_1"
        assert result.operation_type == AnalyticsOperationType.DESCRIPTIVE_STATS
        assert result.status == "completed"
        assert result.error is None
        assert result.result is not None
        assert "mean" in result.result
        assert "std" in result.result
        assert "count" in result.result
        assert result.result["mean"] == 5.5
        assert result.result["count"] == 10

    def test_execute_t_test(
        self,
        batch_service: AnalyticsBatchService,
        t_test_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should execute t-test operation."""
        result = batch_service.execute_single_operation(t_test_operation)

        assert result.operation_id == "ttest_1"
        assert result.operation_type == AnalyticsOperationType.T_TEST
        assert result.status == "completed"
        assert result.error is None
        assert result.result is not None
        assert "test_name" in result.result
        assert "p_value" in result.result
        assert "is_significant" in result.result

    def test_execute_correlation(
        self,
        batch_service: AnalyticsBatchService,
        correlation_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should execute correlation operation."""
        result = batch_service.execute_single_operation(correlation_operation)

        assert result.operation_id == "corr_1"
        assert result.operation_type == AnalyticsOperationType.CORRELATION
        assert result.status == "completed"
        assert result.error is None
        assert result.result is not None
        assert "coefficient" in result.result
        assert "p_value" in result.result
        assert result.result["coefficient"] > 0.99  # Perfect correlation

    def test_execute_correlation_matrix(
        self,
        batch_service: AnalyticsBatchService,
        correlation_matrix_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should execute correlation matrix operation."""
        result = batch_service.execute_single_operation(correlation_matrix_operation)

        assert result.operation_id == "corr_matrix_1"
        assert result.operation_type == AnalyticsOperationType.CORRELATION_MATRIX
        assert result.status == "completed"
        assert result.error is None
        assert result.result is not None
        assert "matrix" in result.result
        assert "columns" in result.result
        assert len(result.result["columns"]) == 3

    def test_execute_anomaly_detection(
        self,
        batch_service: AnalyticsBatchService,
        anomaly_detection_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should execute anomaly detection operation."""
        result = batch_service.execute_single_operation(anomaly_detection_operation)

        assert result.operation_id == "anomaly_1"
        assert result.operation_type == AnalyticsOperationType.ANOMALY_DETECTION
        assert result.status == "completed"
        assert result.error is None
        assert result.result is not None
        assert "anomaly_count" in result.result
        assert "total_points" in result.result
        assert result.result["total_points"] == 10

    def test_execute_forecast(
        self,
        batch_service: AnalyticsBatchService,
        forecast_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should execute forecast operation."""
        result = batch_service.execute_single_operation(forecast_operation)

        assert result.operation_id == "forecast_1"
        assert result.operation_type == AnalyticsOperationType.FORECAST
        assert result.status == "completed"
        assert result.error is None
        assert result.result is not None
        assert "forecast_values" in result.result
        assert len(result.result["forecast_values"]) == 5

    def test_execute_operation_with_iqr_anomaly_detection(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should execute anomaly detection with IQR method."""
        operation = SingleAnalyticsRequest(
            operation_id="anomaly_iqr_1",
            operation_type=AnalyticsOperationType.ANOMALY_DETECTION,
            params={
                "data": [1.0, 2.0, 3.0, 100.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0],
                "method": "iqr",
                "threshold": 1.5,
            },
        )

        result = batch_service.execute_single_operation(operation)

        assert result.status == "completed"
        assert result.result is not None
        assert result.result["method"] == "iqr"

    def test_execute_operation_with_spearman_correlation(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should execute correlation with Spearman method."""
        operation = SingleAnalyticsRequest(
            operation_id="corr_spearman_1",
            operation_type=AnalyticsOperationType.CORRELATION,
            params={
                "x": [1.0, 2.0, 3.0, 4.0, 5.0],
                "y": [2.0, 4.0, 6.0, 8.0, 10.0],
                "method": "spearman",
            },
        )

        result = batch_service.execute_single_operation(operation)

        assert result.status == "completed"
        assert result.result is not None
        assert result.result["method"] == "spearman"


class TestExecuteOperationErrorHandling:
    """Test cases for error handling in single operation execution."""

    def test_missing_required_params_descriptive_stats(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should fail with missing data parameter."""
        operation = SingleAnalyticsRequest(
            operation_id="stats_fail",
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            params={},
        )

        result = batch_service.execute_single_operation(operation)

        assert result.status == "failed"
        assert result.error is not None
        assert "Missing required parameters" in result.error
        assert "data" in result.error

    def test_missing_required_params_t_test(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should fail with missing group1 and group2 parameters."""
        operation = SingleAnalyticsRequest(
            operation_id="ttest_fail",
            operation_type=AnalyticsOperationType.T_TEST,
            params={"alpha": 0.05},
        )

        result = batch_service.execute_single_operation(operation)

        assert result.status == "failed"
        assert result.error is not None
        assert "Missing required parameters" in result.error
        assert "group1" in result.error
        assert "group2" in result.error

    def test_missing_required_params_correlation(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should fail with missing x and y parameters."""
        operation = SingleAnalyticsRequest(
            operation_id="corr_fail",
            operation_type=AnalyticsOperationType.CORRELATION,
            params={"x": [1.0, 2.0, 3.0]},  # Missing y
        )

        result = batch_service.execute_single_operation(operation)

        assert result.status == "failed"
        assert result.error is not None
        assert "Missing required parameters" in result.error
        assert "y" in result.error

    def test_missing_required_params_forecast(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should fail with missing values parameter."""
        operation = SingleAnalyticsRequest(
            operation_id="forecast_fail",
            operation_type=AnalyticsOperationType.FORECAST,
            params={"periods": 5},  # Missing values
        )

        result = batch_service.execute_single_operation(operation)

        assert result.status == "failed"
        assert result.error is not None
        assert "Missing required parameters" in result.error
        assert "values" in result.error

    def test_invalid_anomaly_detection_method(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should fail with invalid anomaly detection method."""
        operation = SingleAnalyticsRequest(
            operation_id="anomaly_fail",
            operation_type=AnalyticsOperationType.ANOMALY_DETECTION,
            params={
                "data": [1.0, 2.0, 3.0, 4.0, 5.0],
                "method": "invalid_method",
            },
        )

        result = batch_service.execute_single_operation(operation)

        assert result.status == "failed"
        assert result.error is not None
        assert "invalid_method" in result.error.lower() or "unknown" in result.error.lower()

    def test_operation_timing_recorded(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should record start and completion times."""
        result = batch_service.execute_single_operation(descriptive_stats_operation)

        assert result.started_at is not None
        assert result.completed_at is not None
        assert result.completed_at >= result.started_at

    def test_failed_operation_timing_recorded(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should record timing even for failed operations."""
        operation = SingleAnalyticsRequest(
            operation_id="fail_timing",
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            params={},  # Missing required data
        )

        result = batch_service.execute_single_operation(operation)

        assert result.status == "failed"
        assert result.started_at is not None
        assert result.completed_at is not None

    def test_unknown_operation_id_handled(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should handle operations without explicit ID."""
        operation = SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            params={"data": [1.0, 2.0, 3.0, 4.0, 5.0]},
        )

        result = batch_service.execute_single_operation(operation)

        assert result.operation_id == "unknown"
        assert result.status == "completed"


class TestBatchProcessing:
    """Test cases for async batch processing."""

    @pytest.mark.asyncio
    async def test_process_single_operation_batch(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should process batch with single operation."""
        job = batch_service.create_batch_job([descriptive_stats_operation])

        result = await batch_service.process_batch(
            job.batch_id, [descriptive_stats_operation]
        )

        assert result.status == BatchJobStatus.COMPLETED
        assert result.completed == 1
        assert result.failed == 0
        assert result.started_at is not None
        assert result.completed_at is not None
        assert "stats_1" in result.results

    @pytest.mark.asyncio
    async def test_process_multiple_operations_batch(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
        t_test_operation: SingleAnalyticsRequest,
        correlation_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should process batch with multiple operations."""
        operations = [
            descriptive_stats_operation,
            t_test_operation,
            correlation_operation,
        ]
        job = batch_service.create_batch_job(operations)

        result = await batch_service.process_batch(job.batch_id, operations)

        assert result.status == BatchJobStatus.COMPLETED
        assert result.completed == 3
        assert result.failed == 0
        assert len(result.results) == 3

    @pytest.mark.asyncio
    async def test_process_batch_with_failures(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should handle batch with some failing operations."""
        failing_operation = SingleAnalyticsRequest(
            operation_id="fail_1",
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            params={},  # Missing required params
        )
        operations = [descriptive_stats_operation, failing_operation]
        job = batch_service.create_batch_job(operations)

        result = await batch_service.process_batch(job.batch_id, operations)

        assert result.status == BatchJobStatus.PARTIAL
        assert result.completed == 1
        assert result.failed == 1
        assert len(result.results) == 2

    @pytest.mark.asyncio
    async def test_process_batch_all_failures(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should set FAILED status when all operations fail."""
        operations = [
            SingleAnalyticsRequest(
                operation_id="fail_1",
                operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
                params={},
            ),
            SingleAnalyticsRequest(
                operation_id="fail_2",
                operation_type=AnalyticsOperationType.T_TEST,
                params={},
            ),
        ]
        job = batch_service.create_batch_job(operations)

        result = await batch_service.process_batch(job.batch_id, operations)

        assert result.status == BatchJobStatus.FAILED
        assert result.completed == 0
        assert result.failed == 2

    @pytest.mark.asyncio
    async def test_process_batch_nonexistent_raises(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should raise ValueError for nonexistent batch job."""
        with pytest.raises(ValueError, match="Batch job not found"):
            await batch_service.process_batch(
                "nonexistent-id", [descriptive_stats_operation]
            )

    @pytest.mark.asyncio
    async def test_process_batch_respects_max_concurrency(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should respect max_concurrency parameter."""
        # Create many operations
        operations = [
            SingleAnalyticsRequest(
                operation_id=f"stats_{i}",
                operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
                params={"data": [float(i), float(i + 1), float(i + 2)]},
            )
            for i in range(10)
        ]
        job = batch_service.create_batch_job(operations)

        result = await batch_service.process_batch(
            job.batch_id, operations, max_concurrency=2
        )

        assert result.status == BatchJobStatus.COMPLETED
        assert result.completed == 10

    @pytest.mark.asyncio
    async def test_process_batch_cancelled_before_start(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should not process already cancelled batch."""
        job = batch_service.create_batch_job([descriptive_stats_operation])
        batch_service.cancel_batch_job(job.batch_id)

        result = await batch_service.process_batch(
            job.batch_id, [descriptive_stats_operation]
        )

        assert result.status == BatchJobStatus.CANCELLED
        assert result.completed == 0

    @pytest.mark.asyncio
    async def test_process_batch_marks_running_status(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should mark job as RUNNING when processing starts."""
        job = batch_service.create_batch_job([descriptive_stats_operation])

        # Process and verify final state shows it ran
        result = await batch_service.process_batch(
            job.batch_id, [descriptive_stats_operation]
        )

        # Job should have started_at set
        assert result.started_at is not None

    @pytest.mark.asyncio
    async def test_process_batch_all_operation_types(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
        t_test_operation: SingleAnalyticsRequest,
        correlation_operation: SingleAnalyticsRequest,
        correlation_matrix_operation: SingleAnalyticsRequest,
        anomaly_detection_operation: SingleAnalyticsRequest,
        forecast_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should process batch with all operation types."""
        operations = [
            descriptive_stats_operation,
            t_test_operation,
            correlation_operation,
            correlation_matrix_operation,
            anomaly_detection_operation,
            forecast_operation,
        ]
        job = batch_service.create_batch_job(operations)

        result = await batch_service.process_batch(job.batch_id, operations)

        assert result.status == BatchJobStatus.COMPLETED
        assert result.completed == 6
        assert result.failed == 0

        # Verify each operation type was processed
        assert "stats_1" in result.results
        assert "ttest_1" in result.results
        assert "corr_1" in result.results
        assert "corr_matrix_1" in result.results
        assert "anomaly_1" in result.results
        assert "forecast_1" in result.results


class TestProgressTracking:
    """Test cases for progress tracking accuracy."""

    @pytest.mark.asyncio
    async def test_progress_updates_during_processing(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should update progress as operations complete."""
        operations = [
            SingleAnalyticsRequest(
                operation_id=f"stats_{i}",
                operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
                params={"data": [1.0, 2.0, 3.0, 4.0, 5.0]},
            )
            for i in range(5)
        ]
        job = batch_service.create_batch_job(operations)

        result = await batch_service.process_batch(job.batch_id, operations)

        # Final progress should be 100%
        assert result.progress_percent == 100.0
        assert result.pending == 0
        assert result.completed + result.failed == result.total

    @pytest.mark.asyncio
    async def test_progress_with_mixed_results(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should track progress correctly with mixed success/failure."""
        operations = [
            SingleAnalyticsRequest(
                operation_id="success_1",
                operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
                params={"data": [1.0, 2.0, 3.0]},
            ),
            SingleAnalyticsRequest(
                operation_id="fail_1",
                operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
                params={},  # Will fail
            ),
            SingleAnalyticsRequest(
                operation_id="success_2",
                operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
                params={"data": [4.0, 5.0, 6.0]},
            ),
        ]
        job = batch_service.create_batch_job(operations)

        result = await batch_service.process_batch(job.batch_id, operations)

        assert result.total == 3
        assert result.completed == 2
        assert result.failed == 1
        assert result.pending == 0
        assert result.progress_percent == 100.0

    @pytest.mark.asyncio
    async def test_results_stored_by_operation_id(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should store results keyed by operation ID."""
        operations = [
            SingleAnalyticsRequest(
                operation_id="custom_id_1",
                operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
                params={"data": [1.0, 2.0, 3.0]},
            ),
            SingleAnalyticsRequest(
                operation_id="custom_id_2",
                operation_type=AnalyticsOperationType.CORRELATION,
                params={"x": [1.0, 2.0, 3.0], "y": [2.0, 4.0, 6.0]},
            ),
        ]
        job = batch_service.create_batch_job(operations)

        result = await batch_service.process_batch(job.batch_id, operations)

        assert "custom_id_1" in result.results
        assert "custom_id_2" in result.results
        assert result.results["custom_id_1"].operation_id == "custom_id_1"
        assert result.results["custom_id_2"].operation_id == "custom_id_2"

    @pytest.mark.asyncio
    async def test_timestamp_updates(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should update timestamps during processing."""
        job = batch_service.create_batch_job([descriptive_stats_operation])
        initial_updated_at = job.updated_at

        result = await batch_service.process_batch(
            job.batch_id, [descriptive_stats_operation]
        )

        assert result.started_at is not None
        assert result.completed_at is not None
        assert result.updated_at is not None
        assert result.started_at <= result.completed_at


class TestServiceInitialization:
    """Test cases for service initialization."""

    def test_service_creates_empty_job_storage(self) -> None:
        """Should initialize with empty job storage."""
        service = AnalyticsBatchService()

        assert service._batch_jobs == {}

    def test_service_initializes_analytics_services(self) -> None:
        """Should initialize all analytics services."""
        service = AnalyticsBatchService()

        assert service._stat_service is not None
        assert service._anomaly_service is not None
        assert service._forecast_service is not None

    def test_multiple_services_independent(self) -> None:
        """Each service instance should have independent storage."""
        service1 = AnalyticsBatchService()
        service2 = AnalyticsBatchService()

        operation = SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            params={"data": [1.0, 2.0, 3.0]},
        )
        job = service1.create_batch_job([operation])

        # Job should exist in service1 but not service2
        assert service1.get_batch_job(job.batch_id) is not None
        assert service2.get_batch_job(job.batch_id) is None


class TestOperationResultValidation:
    """Test cases for validating operation results content."""

    def test_descriptive_stats_result_fields(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should return all expected descriptive stats fields."""
        result = batch_service.execute_single_operation(descriptive_stats_operation)

        expected_fields = [
            "column",
            "count",
            "mean",
            "std",
            "min",
            "q25",
            "median",
            "q75",
            "max",
            "skewness",
            "kurtosis",
        ]
        for field in expected_fields:
            assert field in result.result

    def test_t_test_result_fields(
        self,
        batch_service: AnalyticsBatchService,
        t_test_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should return all expected t-test fields."""
        result = batch_service.execute_single_operation(t_test_operation)

        expected_fields = [
            "test_name",
            "test_type",
            "statistic",
            "p_value",
            "degrees_of_freedom",
            "is_significant",
            "interpretation",
            "effect_size",
            "effect_size_name",
            "details",
        ]
        for field in expected_fields:
            assert field in result.result

    def test_correlation_result_fields(
        self,
        batch_service: AnalyticsBatchService,
        correlation_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should return all expected correlation fields."""
        result = batch_service.execute_single_operation(correlation_operation)

        expected_fields = [
            "method",
            "coefficient",
            "p_value",
            "is_significant",
            "interpretation",
            "sample_size",
        ]
        for field in expected_fields:
            assert field in result.result

    def test_correlation_matrix_result_fields(
        self,
        batch_service: AnalyticsBatchService,
        correlation_matrix_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should return all expected correlation matrix fields."""
        result = batch_service.execute_single_operation(correlation_matrix_operation)

        expected_fields = ["method", "matrix", "columns"]
        for field in expected_fields:
            assert field in result.result

    def test_anomaly_detection_result_fields(
        self,
        batch_service: AnalyticsBatchService,
        anomaly_detection_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should return all expected anomaly detection fields."""
        result = batch_service.execute_single_operation(anomaly_detection_operation)

        expected_fields = [
            "method",
            "total_points",
            "anomaly_count",
            "anomaly_percentage",
            "anomalies",
            "threshold",
            "interpretation",
        ]
        for field in expected_fields:
            assert field in result.result

    def test_forecast_result_fields(
        self,
        batch_service: AnalyticsBatchService,
        forecast_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should return all expected forecast fields."""
        result = batch_service.execute_single_operation(forecast_operation)

        expected_fields = [
            "model_name",
            "forecast_dates",
            "forecast_values",
            "lower_bound",
            "upper_bound",
            "confidence_level",
            "trend",
            "interpretation",
            "metrics",
        ]
        for field in expected_fields:
            assert field in result.result


class TestEdgeCases:
    """Test cases for edge cases and boundary conditions."""

    def test_descriptive_stats_with_column_name(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should use custom column name in descriptive stats."""
        operation = SingleAnalyticsRequest(
            operation_id="stats_custom_col",
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            params={"data": [1.0, 2.0, 3.0, 4.0, 5.0], "column_name": "custom_column"},
        )

        result = batch_service.execute_single_operation(operation)

        assert result.status == "completed"
        assert result.result["column"] == "custom_column"

    def test_t_test_with_custom_alpha(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should respect custom alpha value in t-test."""
        operation = SingleAnalyticsRequest(
            operation_id="ttest_alpha",
            operation_type=AnalyticsOperationType.T_TEST,
            params={
                "group1": [10.0, 12.0, 14.0, 16.0, 18.0],
                "group2": [11.0, 13.0, 15.0, 17.0, 19.0],
                "alpha": 0.01,
            },
        )

        result = batch_service.execute_single_operation(operation)

        assert result.status == "completed"

    def test_correlation_with_kendall_method(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should support Kendall correlation method."""
        operation = SingleAnalyticsRequest(
            operation_id="corr_kendall",
            operation_type=AnalyticsOperationType.CORRELATION,
            params={
                "x": [1.0, 2.0, 3.0, 4.0, 5.0],
                "y": [2.0, 4.0, 6.0, 8.0, 10.0],
                "method": "kendall",
            },
        )

        result = batch_service.execute_single_operation(operation)

        assert result.status == "completed"
        assert result.result["method"] == "kendall"

    def test_forecast_with_default_periods(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should use default periods when not specified."""
        operation = SingleAnalyticsRequest(
            operation_id="forecast_default",
            operation_type=AnalyticsOperationType.FORECAST,
            params={
                "values": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
            },
        )

        result = batch_service.execute_single_operation(operation)

        assert result.status == "completed"
        # Default is 30 periods
        assert len(result.result["forecast_values"]) == 30

    @pytest.mark.asyncio
    async def test_large_batch_processing(
        self,
        batch_service: AnalyticsBatchService,
    ) -> None:
        """Should handle large batches correctly."""
        operations = [
            SingleAnalyticsRequest(
                operation_id=f"stats_{i}",
                operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
                params={"data": [float(j) for j in range(10)]},
            )
            for i in range(50)
        ]
        job = batch_service.create_batch_job(operations)

        result = await batch_service.process_batch(
            job.batch_id, operations, max_concurrency=10
        )

        assert result.status == BatchJobStatus.COMPLETED
        assert result.completed == 50
        assert len(result.results) == 50

    def test_is_successful_property_works(
        self,
        batch_service: AnalyticsBatchService,
        descriptive_stats_operation: SingleAnalyticsRequest,
    ) -> None:
        """Should correctly set is_successful property on result."""
        result = batch_service.execute_single_operation(descriptive_stats_operation)

        assert result.is_successful is True

        # Test with failing operation
        fail_op = SingleAnalyticsRequest(
            operation_id="fail",
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            params={},
        )
        fail_result = batch_service.execute_single_operation(fail_op)

        assert fail_result.is_successful is False
