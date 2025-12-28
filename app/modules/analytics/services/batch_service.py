"""Batch analytics service for processing multiple analytics operations."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import Any

import pandas as pd

from app.modules.analytics.batch_models import (
    AnalyticsBatchResult,
    AnalyticsBatchStatus,
    AnalyticsOperationType,
    BatchJobStatus,
    SingleAnalyticsRequest,
)
from app.modules.analytics.services.anomaly_service import AnomalyService
from app.modules.analytics.services.forecasting_service import ForecastingService
from app.modules.analytics.services.statistical_service import StatisticalService


class AnalyticsBatchService:
    """Service for processing batches of analytics operations.

    This service manages batch jobs, routes individual operations to the
    appropriate analytics service (StatisticalService, AnomalyService,
    ForecastingService), and tracks progress.

    Attributes:
        _batch_jobs: In-memory storage for batch job statuses.
        _stat_service: Service for statistical operations.
        _anomaly_service: Service for anomaly detection operations.
        _forecast_service: Service for forecasting operations.
    """

    def __init__(self) -> None:
        """Initialize the batch service with analytics services."""
        self._batch_jobs: dict[str, AnalyticsBatchStatus] = {}
        self._stat_service = StatisticalService()
        self._anomaly_service = AnomalyService()
        self._forecast_service = ForecastingService()

    def create_batch_job(
        self,
        operations: list[SingleAnalyticsRequest],
    ) -> AnalyticsBatchStatus:
        """Create a new batch job for processing analytics operations.

        Args:
            operations: List of analytics operations to process.

        Returns:
            AnalyticsBatchStatus with the newly created job information.

        Raises:
            ValueError: If operations list is empty.
        """
        if not operations:
            raise ValueError("At least one operation must be provided")

        batch_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # Assign sequential IDs to operations that don't have one
        for i, op in enumerate(operations):
            if op.operation_id is None:
                op.operation_id = f"op_{i}"

        job = AnalyticsBatchStatus(
            batch_id=batch_id,
            status=BatchJobStatus.PENDING,
            total=len(operations),
            completed=0,
            failed=0,
            results={},
            created_at=now,
            started_at=None,
            updated_at=now,
            completed_at=None,
        )

        self._batch_jobs[batch_id] = job
        return job

    def get_batch_job(self, batch_id: str) -> AnalyticsBatchStatus | None:
        """Retrieve a batch job by its ID.

        Args:
            batch_id: The unique identifier of the batch job.

        Returns:
            The batch job status if found, None otherwise.
        """
        return self._batch_jobs.get(batch_id)

    def delete_batch_job(self, batch_id: str) -> bool:
        """Delete a batch job from storage.

        Args:
            batch_id: The unique identifier of the batch job.

        Returns:
            True if the job was deleted, False if not found.
        """
        if batch_id in self._batch_jobs:
            del self._batch_jobs[batch_id]
            return True
        return False

    def cancel_batch_job(self, batch_id: str) -> AnalyticsBatchStatus | None:
        """Cancel a running or pending batch job.

        Args:
            batch_id: The unique identifier of the batch job.

        Returns:
            Updated batch job status if found and cancellable, None otherwise.
        """
        job = self._batch_jobs.get(batch_id)
        if job is None:
            return None

        # Can only cancel pending or running jobs
        if job.status not in (BatchJobStatus.PENDING, BatchJobStatus.RUNNING):
            return job

        job.status = BatchJobStatus.CANCELLED
        job.updated_at = datetime.utcnow()
        job.completed_at = datetime.utcnow()
        return job

    async def process_batch(
        self,
        batch_id: str,
        operations: list[SingleAnalyticsRequest],
        max_concurrency: int = 5,
    ) -> AnalyticsBatchStatus:
        """Process a batch of analytics operations with concurrency control.

        Uses asyncio.Semaphore to limit concurrent operations and tracks
        progress by updating completed/failed counts as operations finish.

        Args:
            batch_id: The unique identifier of the batch job.
            operations: List of analytics operations to process.
            max_concurrency: Maximum number of operations to run concurrently.
                Defaults to 5.

        Returns:
            The final AnalyticsBatchStatus with all results.

        Raises:
            ValueError: If the batch_id is not found in the job storage.
        """
        job = self._batch_jobs.get(batch_id)
        if job is None:
            raise ValueError(f"Batch job not found: {batch_id}")

        # Check if job was cancelled before starting
        if job.status == BatchJobStatus.CANCELLED:
            return job

        # Mark job as running
        job.status = BatchJobStatus.RUNNING
        job.started_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrency)

        async def process_operation_with_semaphore(
            operation: SingleAnalyticsRequest,
        ) -> AnalyticsBatchResult:
            """Process a single operation with semaphore-based concurrency control."""
            async with semaphore:
                # Check if job was cancelled during processing
                if job.status == BatchJobStatus.CANCELLED:
                    operation_id = operation.operation_id or "unknown"
                    return AnalyticsBatchResult(
                        operation_id=operation_id,
                        operation_type=operation.operation_type,
                        status="failed",
                        result=None,
                        error="Batch job was cancelled",
                        started_at=datetime.utcnow(),
                        completed_at=datetime.utcnow(),
                    )

                # Run the synchronous operation in a thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, self.execute_single_operation, operation
                )
                return result

        # Create tasks for all operations
        tasks = [
            asyncio.create_task(process_operation_with_semaphore(op))
            for op in operations
        ]

        # Process results as they complete
        for completed_task in asyncio.as_completed(tasks):
            try:
                result = await completed_task

                # Check if job was cancelled
                if job.status == BatchJobStatus.CANCELLED:
                    # Cancel remaining tasks
                    for task in tasks:
                        if not task.done():
                            task.cancel()
                    break

                # Update job progress
                operation_id = result.operation_id
                job.results[operation_id] = result

                if result.is_successful:
                    job.completed += 1
                else:
                    job.failed += 1

                job.updated_at = datetime.utcnow()

            except asyncio.CancelledError:
                # Task was cancelled, don't count as failure
                pass
            except Exception as e:
                # Unexpected error - this shouldn't normally happen since
                # execute_single_operation handles errors internally
                job.failed += 1
                job.updated_at = datetime.utcnow()
                # Log the unexpected error but continue processing other operations
                # In production, you'd want proper logging here

        # Determine final status
        now = datetime.utcnow()
        job.completed_at = now
        job.updated_at = now

        if job.status == BatchJobStatus.CANCELLED:
            # Status already set, keep it
            pass
        elif job.failed == job.total:
            job.status = BatchJobStatus.FAILED
        elif job.failed > 0:
            job.status = BatchJobStatus.PARTIAL
        else:
            job.status = BatchJobStatus.COMPLETED

        return job

    def execute_single_operation(
        self,
        operation: SingleAnalyticsRequest,
    ) -> AnalyticsBatchResult:
        """Execute a single analytics operation.

        Routes the operation to the appropriate service based on operation_type
        and returns the result.

        Args:
            operation: The analytics operation to execute.

        Returns:
            AnalyticsBatchResult with operation outcome.
        """
        operation_id = operation.operation_id or "unknown"
        started_at = datetime.utcnow()

        # Validate required parameters
        missing_params = operation.validate_required_params()
        if missing_params:
            return AnalyticsBatchResult(
                operation_id=operation_id,
                operation_type=operation.operation_type,
                status="failed",
                result=None,
                error=f"Missing required parameters: {', '.join(missing_params)}",
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

        try:
            result = self._route_operation(operation)
            return AnalyticsBatchResult(
                operation_id=operation_id,
                operation_type=operation.operation_type,
                status="completed",
                result=result,
                error=None,
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )
        except Exception as e:
            return AnalyticsBatchResult(
                operation_id=operation_id,
                operation_type=operation.operation_type,
                status="failed",
                result=None,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

    def _route_operation(
        self,
        operation: SingleAnalyticsRequest,
    ) -> dict[str, Any]:
        """Route an operation to the appropriate service and return result.

        Args:
            operation: The analytics operation to execute.

        Returns:
            Dictionary containing the operation result.

        Raises:
            ValueError: If the operation type is not supported.
        """
        params = operation.params
        op_type = operation.operation_type

        if op_type == AnalyticsOperationType.DESCRIPTIVE_STATS:
            return self._execute_descriptive_stats(params)
        elif op_type == AnalyticsOperationType.T_TEST:
            return self._execute_t_test(params)
        elif op_type == AnalyticsOperationType.CORRELATION:
            return self._execute_correlation(params)
        elif op_type == AnalyticsOperationType.CORRELATION_MATRIX:
            return self._execute_correlation_matrix(params)
        elif op_type == AnalyticsOperationType.ANOMALY_DETECTION:
            return self._execute_anomaly_detection(params)
        elif op_type == AnalyticsOperationType.FORECAST:
            return self._execute_forecast(params)
        else:
            raise ValueError(f"Unsupported operation type: {op_type}")

    def _execute_descriptive_stats(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute descriptive statistics operation.

        Args:
            params: Parameters containing 'data' and optional 'column_name'.

        Returns:
            Dictionary with descriptive statistics result.
        """
        data = params["data"]
        column_name = params.get("column_name", "value")
        series = pd.Series(data, name=column_name)

        result = self._stat_service.descriptive_stats(series)

        return {
            "column": result.column,
            "count": result.count,
            "mean": result.mean,
            "std": result.std,
            "min": result.min,
            "q25": result.q25,
            "median": result.median,
            "q75": result.q75,
            "max": result.max,
            "skewness": result.skewness,
            "kurtosis": result.kurtosis,
        }

    def _execute_t_test(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute t-test operation.

        Args:
            params: Parameters containing 'group1', 'group2', and optional 'alpha'.

        Returns:
            Dictionary with t-test result.
        """
        group1 = pd.Series(params["group1"])
        group2 = pd.Series(params["group2"])
        alpha = params.get("alpha", 0.05)

        result = self._stat_service.t_test_independent(group1, group2, alpha=alpha)

        return {
            "test_name": result.test_name,
            "test_type": result.test_type,
            "statistic": result.statistic,
            "p_value": result.p_value,
            "degrees_of_freedom": result.degrees_of_freedom,
            "is_significant": result.is_significant,
            "interpretation": result.interpretation,
            "effect_size": result.effect_size,
            "effect_size_name": result.effect_size_name,
            "details": result.details,
        }

    def _execute_correlation(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute correlation operation.

        Args:
            params: Parameters containing 'x', 'y', and optional 'method', 'alpha'.

        Returns:
            Dictionary with correlation result.
        """
        x = pd.Series(params["x"])
        y = pd.Series(params["y"])
        method = params.get("method", "pearson")
        alpha = params.get("alpha", 0.05)

        result = self._stat_service.correlation(x, y, method=method, alpha=alpha)

        return {
            "method": result.method,
            "coefficient": result.coefficient,
            "p_value": result.p_value,
            "is_significant": result.is_significant,
            "interpretation": result.interpretation,
            "sample_size": result.sample_size,
        }

    def _execute_correlation_matrix(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute correlation matrix operation.

        Args:
            params: Parameters containing 'data' (list of dicts) and optional 'method'.

        Returns:
            Dictionary with correlation matrix result.
        """
        data = params["data"]
        method = params.get("method", "pearson")
        df = pd.DataFrame(data)

        result = self._stat_service.correlation_matrix(df, method=method)

        return {
            "method": result.method,
            "matrix": result.matrix,
            "columns": result.columns,
        }

    def _execute_anomaly_detection(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute anomaly detection operation.

        Args:
            params: Parameters containing 'data', optional 'method' and 'threshold'.

        Returns:
            Dictionary with anomaly detection result.
        """
        data = params["data"]
        method = params.get("method", "zscore")
        threshold = params.get("threshold", 3.0)
        series = pd.Series(data)

        if method == "zscore":
            result = self._anomaly_service.detect_zscore(series, threshold=threshold)
        elif method == "iqr":
            result = self._anomaly_service.detect_iqr(series, multiplier=threshold)
        else:
            raise ValueError(f"Unknown anomaly detection method: {method}")

        return {
            "method": result.method,
            "total_points": result.total_points,
            "anomaly_count": result.anomaly_count,
            "anomaly_percentage": result.anomaly_percentage,
            "anomalies": result.anomalies,
            "threshold": result.threshold,
            "interpretation": result.interpretation,
        }

    def _execute_forecast(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute forecast operation.

        Args:
            params: Parameters containing 'values' and optional 'periods'.

        Returns:
            Dictionary with forecast result.
        """
        values = params["values"]
        periods = params.get("periods", 30)
        series = pd.Series(values)

        result = self._forecast_service.forecast_simple(series, periods=periods)

        return {
            "model_name": result.model_name,
            "forecast_dates": result.forecast_dates,
            "forecast_values": result.forecast_values,
            "lower_bound": result.lower_bound,
            "upper_bound": result.upper_bound,
            "confidence_level": result.confidence_level,
            "trend": result.trend,
            "interpretation": result.interpretation,
            "metrics": result.metrics,
        }


# Singleton instance for use across the application
analytics_batch_service = AnalyticsBatchService()
