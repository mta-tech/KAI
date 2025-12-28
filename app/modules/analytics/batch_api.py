"""Batch analytics API endpoints.

Provides endpoints for submitting and managing batch analytics operations.
Allows processing multiple analytics operations (descriptive stats, correlations,
forecasts, anomaly detection, etc.) in a single request with progress tracking.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.modules.analytics.batch_models import (
    AnalyticsBatchRequest,
    AnalyticsBatchStatus,
)
from app.modules.analytics.services import analytics_batch_service


router = APIRouter(prefix="/api/v2/analytics/batch", tags=["Batch Analytics"])


@router.post("", response_model=dict[str, Any])
async def create_batch(
    request: AnalyticsBatchRequest,
    background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    """Submit a batch of analytics operations for processing.

    Creates a new batch job and schedules it for background processing.
    Returns immediately with the batch_id and initial status so the client
    can poll for progress using the GET /batch/{batch_id} endpoint.

    Args:
        request: The batch request containing a list of analytics operations
            and optional max_concurrency setting.
        background_tasks: FastAPI BackgroundTasks for async processing.

    Returns:
        Dictionary containing:
        - batch_id: Unique identifier for tracking the batch job
        - status: Initial status ("pending")
        - total: Total number of operations in the batch
        - message: Confirmation message

    Example request:
        {
            "operations": [
                {
                    "operation_id": "stats_1",
                    "operation_type": "descriptive_stats",
                    "params": {"data": [1, 2, 3, 4, 5]}
                },
                {
                    "operation_id": "corr_1",
                    "operation_type": "correlation",
                    "params": {"x": [1, 2, 3], "y": [2, 4, 6]}
                }
            ],
            "max_concurrency": 5
        }
    """
    # Create the batch job in the service
    job = analytics_batch_service.create_batch_job(request.operations)

    # Schedule background processing
    background_tasks.add_task(
        analytics_batch_service.process_batch,
        job.batch_id,
        request.operations,
        request.max_concurrency,
    )

    return {
        "batch_id": job.batch_id,
        "status": job.status.value,
        "total": job.total,
        "message": "Batch submitted successfully",
    }


@router.get("/{batch_id}", response_model=AnalyticsBatchStatus)
async def get_batch_status(batch_id: str) -> AnalyticsBatchStatus:
    """Get the status of a batch analytics job.

    Returns the current status of a batch job including:
    - Overall status (pending, running, completed, partial, failed, cancelled)
    - Progress counters (total, completed, failed)
    - Individual operation results (if available)
    - Timing information

    Args:
        batch_id: The unique identifier of the batch job.

    Returns:
        AnalyticsBatchStatus with full job details.

    Raises:
        HTTPException 404: If the batch job is not found.
    """
    job = analytics_batch_service.get_batch_job(batch_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail=f"Batch job not found: {batch_id}",
        )
    return job


@router.get("/{batch_id}/results", response_model=dict[str, Any])
async def get_batch_results(batch_id: str) -> dict[str, Any]:
    """Get the results of a completed batch analytics job.

    Returns the results of all completed operations in the batch.
    This endpoint is useful for retrieving results separately from status,
    especially for large batches.

    Args:
        batch_id: The unique identifier of the batch job.

    Returns:
        Dictionary containing:
        - batch_id: The batch job identifier
        - status: Current status of the batch job
        - total: Total number of operations
        - completed: Number of completed operations
        - failed: Number of failed operations
        - results: Dictionary of operation results keyed by operation_id

    Raises:
        HTTPException 404: If the batch job is not found.

    Example response:
        {
            "batch_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "completed",
            "total": 3,
            "completed": 2,
            "failed": 1,
            "results": {
                "stats_1": {
                    "operation_id": "stats_1",
                    "operation_type": "descriptive_stats",
                    "status": "completed",
                    "result": {"mean": 3.0, "std": 1.58}
                }
            }
        }
    """
    job = analytics_batch_service.get_batch_job(batch_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail=f"Batch job not found: {batch_id}",
        )

    # Convert results to dict format for JSON serialization
    results_dict = {
        op_id: {
            "operation_id": result.operation_id,
            "operation_type": result.operation_type.value,
            "status": result.status,
            "result": result.result,
            "error": result.error,
            "started_at": result.started_at.isoformat() if result.started_at else None,
            "completed_at": result.completed_at.isoformat() if result.completed_at else None,
        }
        for op_id, result in job.results.items()
    }

    return {
        "batch_id": job.batch_id,
        "status": job.status.value,
        "total": job.total,
        "completed": job.completed,
        "failed": job.failed,
        "results": results_dict,
    }


@router.delete("/{batch_id}", response_model=dict[str, Any])
async def delete_batch(batch_id: str) -> dict[str, Any]:
    """Cancel and/or delete a batch analytics job.

    If the job is still running or pending, it will be cancelled first.
    Then the job is removed from storage.

    Args:
        batch_id: The unique identifier of the batch job.

    Returns:
        Dictionary containing:
        - batch_id: The batch job identifier
        - status: The final status of the job before deletion
        - deleted: Always True if successful
        - message: Confirmation message

    Raises:
        HTTPException 404: If the batch job is not found.

    Note:
        - Pending jobs are cancelled immediately
        - Running jobs are marked as cancelled (in-flight operations may complete)
        - Completed/failed/partial jobs are deleted directly
    """
    # First, check if the job exists
    job = analytics_batch_service.get_batch_job(batch_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail=f"Batch job not found: {batch_id}",
        )

    # Get the status before any modifications
    original_status = job.status.value

    # Cancel the job if it's still running or pending
    analytics_batch_service.cancel_batch_job(batch_id)

    # Get the updated status after cancellation
    job = analytics_batch_service.get_batch_job(batch_id)
    final_status = job.status.value if job else original_status

    # Delete the job from storage
    analytics_batch_service.delete_batch_job(batch_id)

    return {
        "batch_id": batch_id,
        "status": final_status,
        "deleted": True,
        "message": "Batch job deleted successfully",
    }