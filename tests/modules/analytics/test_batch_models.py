"""Tests for batch analytics models."""

from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from app.modules.analytics.batch_models import (
    AnalyticsBatchRequest,
    AnalyticsBatchResult,
    AnalyticsBatchStatus,
    AnalyticsOperationType,
    BatchJobStatus,
    SingleAnalyticsRequest,
)


class TestAnalyticsOperationType:
    """Test cases for AnalyticsOperationType enum."""

    def test_all_operation_types_exist(self) -> None:
        """Should have all expected operation types."""
        expected_types = [
            "descriptive_stats",
            "t_test",
            "correlation",
            "correlation_matrix",
            "anomaly_detection",
            "forecast",
        ]

        for op_type in expected_types:
            assert hasattr(AnalyticsOperationType, op_type.upper())

    def test_operation_type_values(self) -> None:
        """Should have correct string values."""
        assert AnalyticsOperationType.DESCRIPTIVE_STATS.value == "descriptive_stats"
        assert AnalyticsOperationType.T_TEST.value == "t_test"
        assert AnalyticsOperationType.CORRELATION.value == "correlation"
        assert AnalyticsOperationType.CORRELATION_MATRIX.value == "correlation_matrix"
        assert AnalyticsOperationType.ANOMALY_DETECTION.value == "anomaly_detection"
        assert AnalyticsOperationType.FORECAST.value == "forecast"

    def test_operation_type_count(self) -> None:
        """Should have exactly 6 operation types."""
        assert len(AnalyticsOperationType) == 6

    def test_operation_type_is_string_enum(self) -> None:
        """Should be usable as string."""
        op_type = AnalyticsOperationType.DESCRIPTIVE_STATS
        assert op_type.value == "descriptive_stats"
        assert op_type == "descriptive_stats"


class TestBatchJobStatus:
    """Test cases for BatchJobStatus enum."""

    def test_all_statuses_exist(self) -> None:
        """Should have all expected statuses."""
        expected_statuses = [
            "pending",
            "running",
            "completed",
            "partial",
            "failed",
            "cancelled",
        ]

        for status in expected_statuses:
            assert hasattr(BatchJobStatus, status.upper())

    def test_status_values(self) -> None:
        """Should have correct string values."""
        assert BatchJobStatus.PENDING.value == "pending"
        assert BatchJobStatus.RUNNING.value == "running"
        assert BatchJobStatus.COMPLETED.value == "completed"
        assert BatchJobStatus.PARTIAL.value == "partial"
        assert BatchJobStatus.FAILED.value == "failed"
        assert BatchJobStatus.CANCELLED.value == "cancelled"

    def test_status_count(self) -> None:
        """Should have exactly 6 statuses."""
        assert len(BatchJobStatus) == 6


class TestSingleAnalyticsRequest:
    """Test cases for SingleAnalyticsRequest model."""

    def test_create_descriptive_stats_request(self) -> None:
        """Should create valid descriptive stats request."""
        request = SingleAnalyticsRequest(
            operation_id="stats_1",
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            params={"data": [1.0, 2.0, 3.0, 4.0, 5.0]},
        )

        assert request.operation_id == "stats_1"
        assert request.operation_type == AnalyticsOperationType.DESCRIPTIVE_STATS
        assert request.params == {"data": [1.0, 2.0, 3.0, 4.0, 5.0]}

    def test_create_t_test_request(self) -> None:
        """Should create valid t-test request."""
        request = SingleAnalyticsRequest(
            operation_id="ttest_1",
            operation_type=AnalyticsOperationType.T_TEST,
            params={
                "group1": [1.0, 2.0, 3.0],
                "group2": [4.0, 5.0, 6.0],
                "alpha": 0.05,
            },
        )

        assert request.operation_type == AnalyticsOperationType.T_TEST
        assert "group1" in request.params
        assert "group2" in request.params

    def test_create_correlation_request(self) -> None:
        """Should create valid correlation request."""
        request = SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.CORRELATION,
            params={
                "x": [1.0, 2.0, 3.0],
                "y": [2.0, 4.0, 6.0],
                "method": "pearson",
            },
        )

        assert request.operation_type == AnalyticsOperationType.CORRELATION
        assert request.params["method"] == "pearson"

    def test_create_correlation_matrix_request(self) -> None:
        """Should create valid correlation matrix request."""
        request = SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.CORRELATION_MATRIX,
            params={"data": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]},
        )

        assert request.operation_type == AnalyticsOperationType.CORRELATION_MATRIX

    def test_create_anomaly_detection_request(self) -> None:
        """Should create valid anomaly detection request."""
        request = SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.ANOMALY_DETECTION,
            params={
                "data": [1.0, 2.0, 100.0, 3.0, 4.0],
                "method": "zscore",
                "threshold": 2.0,
            },
        )

        assert request.operation_type == AnalyticsOperationType.ANOMALY_DETECTION

    def test_create_forecast_request(self) -> None:
        """Should create valid forecast request."""
        request = SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.FORECAST,
            params={"values": [10, 20, 30, 40, 50], "periods": 5},
        )

        assert request.operation_type == AnalyticsOperationType.FORECAST

    def test_optional_operation_id(self) -> None:
        """Should allow None operation_id."""
        request = SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            params={"data": [1.0, 2.0, 3.0]},
        )

        assert request.operation_id is None

    def test_empty_params_allowed(self) -> None:
        """Should allow empty params dict (validation at execution time)."""
        request = SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            params={},
        )

        assert request.params == {}

    def test_default_params(self) -> None:
        """Should default to empty params dict."""
        request = SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
        )

        assert request.params == {}

    def test_invalid_operation_type(self) -> None:
        """Should reject invalid operation type."""
        with pytest.raises(ValidationError):
            SingleAnalyticsRequest(
                operation_type="invalid_type",
                params={"data": [1.0, 2.0, 3.0]},
            )

    def test_get_required_params_descriptive_stats(self) -> None:
        """Should return correct required params for descriptive_stats."""
        request = SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            params={},
        )

        assert request.get_required_params() == ["data"]

    def test_get_required_params_t_test(self) -> None:
        """Should return correct required params for t_test."""
        request = SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.T_TEST,
            params={},
        )

        assert request.get_required_params() == ["group1", "group2"]

    def test_get_required_params_correlation(self) -> None:
        """Should return correct required params for correlation."""
        request = SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.CORRELATION,
            params={},
        )

        assert request.get_required_params() == ["x", "y"]

    def test_get_required_params_correlation_matrix(self) -> None:
        """Should return correct required params for correlation_matrix."""
        request = SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.CORRELATION_MATRIX,
            params={},
        )

        assert request.get_required_params() == ["data"]

    def test_get_required_params_anomaly_detection(self) -> None:
        """Should return correct required params for anomaly_detection."""
        request = SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.ANOMALY_DETECTION,
            params={},
        )

        assert request.get_required_params() == ["data"]

    def test_get_required_params_forecast(self) -> None:
        """Should return correct required params for forecast."""
        request = SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.FORECAST,
            params={},
        )

        assert request.get_required_params() == ["values"]

    def test_validate_required_params_missing_all(self) -> None:
        """Should detect all missing params."""
        request = SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.T_TEST,
            params={},
        )

        missing = request.validate_required_params()
        assert "group1" in missing
        assert "group2" in missing

    def test_validate_required_params_missing_some(self) -> None:
        """Should detect partially missing params."""
        request = SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.CORRELATION,
            params={"x": [1.0, 2.0, 3.0]},
        )

        missing = request.validate_required_params()
        assert missing == ["y"]

    def test_validate_required_params_all_present(self) -> None:
        """Should return empty list when all params present."""
        request = SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            params={"data": [1.0, 2.0, 3.0]},
        )

        missing = request.validate_required_params()
        assert missing == []


class TestAnalyticsBatchRequest:
    """Test cases for AnalyticsBatchRequest model."""

    @pytest.fixture
    def sample_operation(self) -> SingleAnalyticsRequest:
        """Sample operation for testing."""
        return SingleAnalyticsRequest(
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            params={"data": [1.0, 2.0, 3.0]},
        )

    def test_create_valid_batch_request(
        self, sample_operation: SingleAnalyticsRequest
    ) -> None:
        """Should create valid batch request."""
        batch = AnalyticsBatchRequest(
            operations=[sample_operation],
            max_concurrency=5,
        )

        assert len(batch.operations) == 1
        assert batch.max_concurrency == 5

    def test_default_max_concurrency(
        self, sample_operation: SingleAnalyticsRequest
    ) -> None:
        """Should default to concurrency of 5."""
        batch = AnalyticsBatchRequest(operations=[sample_operation])

        assert batch.max_concurrency == 5

    def test_min_operations_validation(self) -> None:
        """Should require at least one operation."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyticsBatchRequest(operations=[])

        errors = exc_info.value.errors()
        assert any("operations" in str(e) for e in errors)

    def test_max_operations_validation(
        self, sample_operation: SingleAnalyticsRequest
    ) -> None:
        """Should reject more than 100 operations."""
        operations = [sample_operation] * 101

        with pytest.raises(ValidationError) as exc_info:
            AnalyticsBatchRequest(operations=operations)

        errors = exc_info.value.errors()
        assert any("operations" in str(e) for e in errors)

    def test_operations_at_max_limit(
        self, sample_operation: SingleAnalyticsRequest
    ) -> None:
        """Should accept exactly 100 operations."""
        operations = [sample_operation] * 100

        batch = AnalyticsBatchRequest(operations=operations)

        assert len(batch.operations) == 100

    def test_min_concurrency_validation(
        self, sample_operation: SingleAnalyticsRequest
    ) -> None:
        """Should reject concurrency less than 1."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyticsBatchRequest(
                operations=[sample_operation],
                max_concurrency=0,
            )

        errors = exc_info.value.errors()
        assert any("max_concurrency" in str(e) for e in errors)

    def test_max_concurrency_validation(
        self, sample_operation: SingleAnalyticsRequest
    ) -> None:
        """Should reject concurrency greater than 20."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyticsBatchRequest(
                operations=[sample_operation],
                max_concurrency=21,
            )

        errors = exc_info.value.errors()
        assert any("max_concurrency" in str(e) for e in errors)

    def test_concurrency_at_max_limit(
        self, sample_operation: SingleAnalyticsRequest
    ) -> None:
        """Should accept concurrency of exactly 20."""
        batch = AnalyticsBatchRequest(
            operations=[sample_operation],
            max_concurrency=20,
        )

        assert batch.max_concurrency == 20

    def test_concurrency_at_min_limit(
        self, sample_operation: SingleAnalyticsRequest
    ) -> None:
        """Should accept concurrency of exactly 1."""
        batch = AnalyticsBatchRequest(
            operations=[sample_operation],
            max_concurrency=1,
        )

        assert batch.max_concurrency == 1

    def test_multiple_operation_types(self) -> None:
        """Should accept different operation types in same batch."""
        operations = [
            SingleAnalyticsRequest(
                operation_id="stats_1",
                operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
                params={"data": [1.0, 2.0, 3.0]},
            ),
            SingleAnalyticsRequest(
                operation_id="corr_1",
                operation_type=AnalyticsOperationType.CORRELATION,
                params={"x": [1.0, 2.0], "y": [2.0, 4.0]},
            ),
            SingleAnalyticsRequest(
                operation_id="forecast_1",
                operation_type=AnalyticsOperationType.FORECAST,
                params={"values": [10, 20, 30]},
            ),
        ]

        batch = AnalyticsBatchRequest(operations=operations)

        assert len(batch.operations) == 3


class TestAnalyticsBatchResult:
    """Test cases for AnalyticsBatchResult model."""

    def test_create_successful_result(self) -> None:
        """Should create successful result."""
        result = AnalyticsBatchResult(
            operation_id="stats_1",
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            status="completed",
            result={"mean": 3.0, "std": 1.58},
        )

        assert result.operation_id == "stats_1"
        assert result.status == "completed"
        assert result.result is not None
        assert result.error is None

    def test_create_failed_result(self) -> None:
        """Should create failed result."""
        result = AnalyticsBatchResult(
            operation_id="stats_1",
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            status="failed",
            error="Insufficient data",
        )

        assert result.status == "failed"
        assert result.result is None
        assert result.error == "Insufficient data"

    def test_is_successful_property_completed(self) -> None:
        """Should return True for completed status."""
        result = AnalyticsBatchResult(
            operation_id="stats_1",
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            status="completed",
            result={"mean": 3.0},
        )

        assert result.is_successful is True

    def test_is_successful_property_failed(self) -> None:
        """Should return False for failed status."""
        result = AnalyticsBatchResult(
            operation_id="stats_1",
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            status="failed",
            error="Error",
        )

        assert result.is_successful is False

    def test_duration_ms_property(self) -> None:
        """Should calculate duration in milliseconds."""
        started = datetime(2024, 1, 1, 12, 0, 0)
        completed = started + timedelta(milliseconds=500)

        result = AnalyticsBatchResult(
            operation_id="stats_1",
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            status="completed",
            result={"mean": 3.0},
            started_at=started,
            completed_at=completed,
        )

        assert result.duration_ms == 500.0

    def test_duration_ms_none_without_times(self) -> None:
        """Should return None when times not set."""
        result = AnalyticsBatchResult(
            operation_id="stats_1",
            operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
            status="completed",
            result={"mean": 3.0},
        )

        assert result.duration_ms is None


class TestAnalyticsBatchStatus:
    """Test cases for AnalyticsBatchStatus model."""

    @pytest.fixture
    def base_status(self) -> AnalyticsBatchStatus:
        """Base status for testing."""
        now = datetime.now()
        return AnalyticsBatchStatus(
            batch_id="test-batch-id",
            status=BatchJobStatus.RUNNING,
            total=10,
            completed=3,
            failed=1,
            created_at=now,
            updated_at=now,
        )

    def test_create_pending_status(self) -> None:
        """Should create pending batch status."""
        now = datetime.now()
        status = AnalyticsBatchStatus(
            batch_id="test-batch-id",
            status=BatchJobStatus.PENDING,
            total=5,
            created_at=now,
            updated_at=now,
        )

        assert status.batch_id == "test-batch-id"
        assert status.status == BatchJobStatus.PENDING
        assert status.total == 5
        assert status.completed == 0
        assert status.failed == 0

    def test_pending_property(self, base_status: AnalyticsBatchStatus) -> None:
        """Should calculate pending operations correctly."""
        # total=10, completed=3, failed=1 => pending=6
        assert base_status.pending == 6

    def test_progress_percent_property(self, base_status: AnalyticsBatchStatus) -> None:
        """Should calculate progress percentage correctly."""
        # (3 + 1) / 10 * 100 = 40%
        assert base_status.progress_percent == 40.0

    def test_progress_percent_zero_total(self) -> None:
        """Should return 100% when total is 0."""
        now = datetime.now()
        status = AnalyticsBatchStatus(
            batch_id="test-batch-id",
            status=BatchJobStatus.COMPLETED,
            total=0,
            created_at=now,
            updated_at=now,
        )

        assert status.progress_percent == 100.0

    def test_is_finished_completed(self) -> None:
        """Should return True for completed status."""
        now = datetime.now()
        status = AnalyticsBatchStatus(
            batch_id="test-batch-id",
            status=BatchJobStatus.COMPLETED,
            total=5,
            completed=5,
            created_at=now,
            updated_at=now,
        )

        assert status.is_finished is True

    def test_is_finished_partial(self) -> None:
        """Should return True for partial status."""
        now = datetime.now()
        status = AnalyticsBatchStatus(
            batch_id="test-batch-id",
            status=BatchJobStatus.PARTIAL,
            total=5,
            completed=3,
            failed=2,
            created_at=now,
            updated_at=now,
        )

        assert status.is_finished is True

    def test_is_finished_failed(self) -> None:
        """Should return True for failed status."""
        now = datetime.now()
        status = AnalyticsBatchStatus(
            batch_id="test-batch-id",
            status=BatchJobStatus.FAILED,
            total=5,
            failed=5,
            created_at=now,
            updated_at=now,
        )

        assert status.is_finished is True

    def test_is_finished_cancelled(self) -> None:
        """Should return True for cancelled status."""
        now = datetime.now()
        status = AnalyticsBatchStatus(
            batch_id="test-batch-id",
            status=BatchJobStatus.CANCELLED,
            total=5,
            created_at=now,
            updated_at=now,
        )

        assert status.is_finished is True

    def test_is_finished_running(self) -> None:
        """Should return False for running status."""
        now = datetime.now()
        status = AnalyticsBatchStatus(
            batch_id="test-batch-id",
            status=BatchJobStatus.RUNNING,
            total=5,
            created_at=now,
            updated_at=now,
        )

        assert status.is_finished is False

    def test_is_finished_pending(self) -> None:
        """Should return False for pending status."""
        now = datetime.now()
        status = AnalyticsBatchStatus(
            batch_id="test-batch-id",
            status=BatchJobStatus.PENDING,
            total=5,
            created_at=now,
            updated_at=now,
        )

        assert status.is_finished is False

    def test_duration_ms_property(self) -> None:
        """Should calculate batch duration in milliseconds."""
        started = datetime(2024, 1, 1, 12, 0, 0)
        completed = started + timedelta(seconds=5)

        status = AnalyticsBatchStatus(
            batch_id="test-batch-id",
            status=BatchJobStatus.COMPLETED,
            total=5,
            completed=5,
            created_at=started,
            started_at=started,
            updated_at=completed,
            completed_at=completed,
        )

        assert status.duration_ms == 5000.0

    def test_duration_ms_none_when_not_finished(self) -> None:
        """Should return None when batch not finished."""
        now = datetime.now()
        status = AnalyticsBatchStatus(
            batch_id="test-batch-id",
            status=BatchJobStatus.RUNNING,
            total=5,
            created_at=now,
            started_at=now,
            updated_at=now,
        )

        assert status.duration_ms is None

    def test_get_successful_results(self) -> None:
        """Should return only successful results."""
        now = datetime.now()
        results = {
            "op1": AnalyticsBatchResult(
                operation_id="op1",
                operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
                status="completed",
                result={"mean": 3.0},
            ),
            "op2": AnalyticsBatchResult(
                operation_id="op2",
                operation_type=AnalyticsOperationType.CORRELATION,
                status="failed",
                error="Error",
            ),
            "op3": AnalyticsBatchResult(
                operation_id="op3",
                operation_type=AnalyticsOperationType.FORECAST,
                status="completed",
                result={"forecast": [1, 2, 3]},
            ),
        }

        status = AnalyticsBatchStatus(
            batch_id="test-batch-id",
            status=BatchJobStatus.PARTIAL,
            total=3,
            completed=2,
            failed=1,
            results=results,
            created_at=now,
            updated_at=now,
        )

        successful = status.get_successful_results()
        assert len(successful) == 2
        assert all(r.is_successful for r in successful)

    def test_get_failed_results(self) -> None:
        """Should return only failed results."""
        now = datetime.now()
        results = {
            "op1": AnalyticsBatchResult(
                operation_id="op1",
                operation_type=AnalyticsOperationType.DESCRIPTIVE_STATS,
                status="completed",
                result={"mean": 3.0},
            ),
            "op2": AnalyticsBatchResult(
                operation_id="op2",
                operation_type=AnalyticsOperationType.CORRELATION,
                status="failed",
                error="Error 1",
            ),
            "op3": AnalyticsBatchResult(
                operation_id="op3",
                operation_type=AnalyticsOperationType.FORECAST,
                status="failed",
                error="Error 2",
            ),
        }

        status = AnalyticsBatchStatus(
            batch_id="test-batch-id",
            status=BatchJobStatus.PARTIAL,
            total=3,
            completed=1,
            failed=2,
            results=results,
            created_at=now,
            updated_at=now,
        )

        failed = status.get_failed_results()
        assert len(failed) == 2
        assert all(not r.is_successful for r in failed)

    def test_empty_results(self) -> None:
        """Should handle empty results dict."""
        now = datetime.now()
        status = AnalyticsBatchStatus(
            batch_id="test-batch-id",
            status=BatchJobStatus.PENDING,
            total=5,
            created_at=now,
            updated_at=now,
        )

        assert status.get_successful_results() == []
        assert status.get_failed_results() == []
