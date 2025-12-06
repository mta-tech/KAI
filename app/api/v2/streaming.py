"""SSE streaming API endpoints."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any, AsyncGenerator

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse


router = APIRouter(prefix="/api/v2", tags=["Streaming"])


async def event_generator(
    task_id: str,
    total_steps: int = 5,
) -> AsyncGenerator[dict[str, Any], None]:
    """Generate SSE events for a task."""
    for i in range(total_steps):
        yield {
            "event": "progress",
            "data": json.dumps({
                "task_id": task_id,
                "step": i + 1,
                "total_steps": total_steps,
                "message": f"Processing step {i + 1} of {total_steps}",
                "timestamp": datetime.utcnow().isoformat(),
            }),
        }
        await asyncio.sleep(0.5)

    yield {
        "event": "complete",
        "data": json.dumps({
            "task_id": task_id,
            "status": "completed",
            "message": "Task completed successfully",
            "timestamp": datetime.utcnow().isoformat(),
        }),
    }


@router.get("/analysis/{task_id}/stream")
async def stream_analysis(task_id: str) -> EventSourceResponse:
    """Stream analysis progress via SSE."""
    return EventSourceResponse(event_generator(task_id))


async def notebook_event_generator(
    run_id: str,
    cells: list[str],
) -> AsyncGenerator[dict[str, Any], None]:
    """Generate SSE events for notebook execution."""
    for i, cell in enumerate(cells):
        yield {
            "event": "cell_start",
            "data": json.dumps({
                "run_id": run_id,
                "cell": cell,
                "index": i,
                "timestamp": datetime.utcnow().isoformat(),
            }),
        }
        await asyncio.sleep(1)

        yield {
            "event": "cell_complete",
            "data": json.dumps({
                "run_id": run_id,
                "cell": cell,
                "index": i,
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat(),
            }),
        }

    yield {
        "event": "complete",
        "data": json.dumps({
            "run_id": run_id,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
        }),
    }


@router.get("/notebooks/{run_id}/stream")
async def stream_notebook_execution(run_id: str) -> EventSourceResponse:
    """Stream notebook execution progress via SSE."""
    cells = ["query_1", "viz_1", "summary"]
    return EventSourceResponse(notebook_event_generator(run_id, cells))
