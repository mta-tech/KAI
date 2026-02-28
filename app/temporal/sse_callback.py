"""Standalone FastAPI app that acts as the SSE callback receiver for Temporal streaming.

Usage::

    uv run python -m app.temporal.sse_callback
"""

from __future__ import annotations

import asyncio
import json

import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# In-memory event channels keyed by session id
# ---------------------------------------------------------------------------

_channels: dict[str, asyncio.Queue] = {}


def _get_channel(session_id: str) -> asyncio.Queue:
    """Return the queue for *session_id*, creating one if it does not exist."""
    if session_id not in _channels:
        _channels[session_id] = asyncio.Queue()
    return _channels[session_id]


# ---------------------------------------------------------------------------
# Pydantic model
# ---------------------------------------------------------------------------


class CallbackEvent(BaseModel):
    session_id: str
    event: dict


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(title="KAI SSE Callback Receiver")


@app.post("/events/{session_id}")
async def receive_event(session_id: str, body: CallbackEvent):
    """Accept a callback event and push it to the session's queue."""
    channel = _get_channel(session_id)
    await channel.put(body.event)
    return {"status": "ok"}


@app.get("/stream/{session_id}")
async def stream_events(session_id: str):
    """Stream events for *session_id* using Server-Sent Events."""

    async def _generate():
        channel = _get_channel(session_id)
        while True:
            try:
                event: dict = await asyncio.wait_for(channel.get(), timeout=300)
            except asyncio.TimeoutError:
                yield "event: timeout\ndata: {}\n\n"
                break

            event_type = event.get("type", "message")
            yield f"event: {event_type}\ndata: {json.dumps(event)}\n\n"

            if event_type == "done":
                break

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8092)
