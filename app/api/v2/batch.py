"""Batch processing API endpoints."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api/v2/analysis", tags=["Batch Processing"])


class AnalysisRequest(BaseModel):
    """Single analysis request."""

    prompt: str
    database_alias: str | None = None
    options: dict[str, Any] = Field(default_factory=dict)


class BatchRequest(BaseModel):
    """Batch analysis request."""

    requests: list[AnalysisRequest]
    max_concurrency: int = 5


class BatchStatus(BaseModel):
    """Batch job status."""

    batch_id: str
    status: str
    total: int
    completed: int
    failed: int
    results: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


_batch_jobs: dict[str, BatchStatus] = {}


async def process_batch(batch_id: str, requests: list[AnalysisRequest]) -> None:
    """Process batch requests."""
    job = _batch_jobs[batch_id]
    job.status = "running"
    job.updated_at = datetime.utcnow()

    for i, request in enumerate(requests):
        try:
            await asyncio.sleep(0.5)

            job.results[f"request_{i}"] = {
                "status": "completed",
                "prompt": request.prompt,
                "result": {"message": f"Processed: {request.prompt[:50]}..."},
            }
            job.completed += 1

        except Exception as e:
            job.results[f"request_{i}"] = {
                "status": "failed",
                "prompt": request.prompt,
                "error": str(e),
            }
            job.failed += 1

        job.updated_at = datetime.utcnow()

    job.status = "completed" if job.failed == 0 else "partial"
    job.updated_at = datetime.utcnow()


@router.post("/batch", response_model=dict)
async def create_batch(
    request: BatchRequest,
    background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    """Submit a batch of analysis requests."""
    batch_id = str(uuid.uuid4())
    now = datetime.utcnow()

    job = BatchStatus(
        batch_id=batch_id,
        status="pending",
        total=len(request.requests),
        completed=0,
        failed=0,
        created_at=now,
        updated_at=now,
    )
    _batch_jobs[batch_id] = job

    background_tasks.add_task(process_batch, batch_id, request.requests)

    return {
        "batch_id": batch_id,
        "status": "pending",
        "total": len(request.requests),
        "message": "Batch submitted successfully",
    }


@router.get("/batch/{batch_id}")
async def get_batch_status(batch_id: str) -> BatchStatus:
    """Get batch job status."""
    if batch_id not in _batch_jobs:
        raise HTTPException(404, f"Batch {batch_id} not found")
    return _batch_jobs[batch_id]


@router.get("/batch/{batch_id}/results")
async def get_batch_results(batch_id: str) -> dict[str, Any]:
    """Get batch job results."""
    if batch_id not in _batch_jobs:
        raise HTTPException(404, f"Batch {batch_id} not found")

    job = _batch_jobs[batch_id]
    return {
        "batch_id": batch_id,
        "status": job.status,
        "results": job.results,
    }
