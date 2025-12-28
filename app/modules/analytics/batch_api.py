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
