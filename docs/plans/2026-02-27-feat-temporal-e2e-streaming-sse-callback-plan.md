---
title: "feat: Temporal E2E Streaming with SSE Callback"
type: feat
status: active
date: 2026-02-27
origin: docs/brainstorms/2026-02-27-temporal-e2e-streaming-brainstorm.md
---

# feat: Temporal E2E Streaming with SSE Callback

## Overview

Build a real end-to-end integration test where KAI runs as a Temporal worker, receives NL-to-Analysis prompts via the Temporal API, streams execution events back via SSE callback, and returns the final result through Temporal workflow completion. This validates the production remote-control architecture where workers run on-prem/edge and users dispatch work from cloud/mobile.

Test query: `"Tampilkan top 5 provinsi dengan rata-rata modal awal koperasi tertinggi"`

## Problem Statement / Motivation

KAI has Temporal activities (`app/temporal/activities.py`) and a worker (`app/worker_main.py`) but:
- **No Temporal workflow exists** — only activities are registered, so `temporal workflow execute` fails
- **No streaming from activities** — `chat` activity calls `service.execute()` (non-streaming), not `stream_execute()`
- **No heartbeat** — long-running activities don't call `activity.heartbeat()`, so Temporal can't distinguish "working" from "dead"
- **No streaming channel** — no mechanism for activities to push real-time events back to callers
- **No E2E validation** — existing tests are unit-level mocks, not real pipeline execution

(see brainstorm: `docs/brainstorms/2026-02-27-temporal-e2e-streaming-brainstorm.md`)

## Proposed Solution

### Architecture

```
┌─────────────────┐      ┌──────────────┐      ┌──────────────────┐
│  Test Script     │─────▶│   Temporal   │─────▶│   KAI Worker     │
│  (Python SDK)    │      │  Dev Server  │      │ (worker_main.py) │
│                  │      │              │      │                  │
│  SSE ◀───────────│◀─────│──────────────│◀─────│  stream_execute  │
│  subscriber      │ GET  │  Callback    │ POST │  → POST events   │
│                  │  SSE │  Receiver    │      │  → heartbeat()   │
└─────────────────┘      └──────────────┘      └──────────────────┘
```

**Control plane:** Temporal orchestrates workflow dispatch, retry, and result delivery.
**Streaming plane:** Activity POSTs events to callback URL; clients subscribe via SSE endpoint.

### Component Breakdown

| Component | File | Status |
|-----------|------|--------|
| `KaiChatWorkflow` | `app/temporal/workflows.py` | **New file** |
| `chat_streaming` activity | `app/temporal/activities.py` | **New activity** |
| SSE callback receiver | `app/temporal/sse_callback.py` | **New file** |
| Worker registration | `app/worker_main.py` | **Modify** |
| E2E test script | `cookbook/temporal_e2e_streaming.py` | **New file** |
| CLI test docs | `docs/tutorials/temporal-e2e-test.md` | **New file** |

## Technical Approach

### Phase 1: Temporal Workflow Definition

**Deliverable:** `app/temporal/workflows.py`

Create a `KaiChatWorkflow` that wraps the streaming chat activity.

```python
# app/temporal/workflows.py
from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from app.temporal.activities import KaiActivities


@dataclass
class KaiChatInput:
    prompt: str
    connection_id: str
    conversation_id: str | None = None
    callback_url: str | None = None


@workflow.defn
class KaiChatWorkflow:
    @workflow.run
    async def run(self, input: KaiChatInput) -> dict:
        return await workflow.execute_activity_method(
            KaiActivities.chat_streaming,
            args=[
                input.prompt,
                input.connection_id,
                input.conversation_id,
                input.callback_url,
            ],
            start_to_close_timeout=timedelta(minutes=15),
            heartbeat_timeout=timedelta(seconds=60),
        )
```

**Key decisions:**
- `KaiChatInput` as a `@dataclass` (Temporal's default serializer handles dataclasses)
- `callback_url` is optional — without it, the activity runs non-streaming
- `start_to_close_timeout=15min` — generous for complex multi-step analysis
- `heartbeat_timeout=60s` — if no heartbeat for 60s, Temporal considers the activity stuck
- Returns `dict` (same as existing `chat` activity returns)

**Modify `app/worker_main.py`:**

```python
# Add import
from app.temporal.workflows import KaiChatWorkflow

# In start_worker(), add to Worker constructor:
worker = Worker(
    client,
    task_queue=config.task_queue,
    activities=[...],  # existing
    workflows=[KaiChatWorkflow],  # ADD THIS
)
```

### Phase 2: Streaming Activity

**Deliverable:** New `chat_streaming` method in `app/temporal/activities.py`

```python
@activity.defn
async def chat_streaming(
    self,
    prompt_text: str,
    connection_id: str,
    conversation_id: str | None = None,
    callback_url: str | None = None,
) -> dict:
    """Execute agent with streaming events posted to callback_url."""
    storage = Storage(self.settings)

    # Look up connection (same as existing chat activity)
    repo = DatabaseConnectionRepository(storage)
    db_connection = repo.find_by_id(connection_id)
    if not db_connection:
        raise ValueError(f"Connection {connection_id} not found")

    database = SQLDatabase.get_sql_engine(...)

    session_id = conversation_id or f"temporal_{uuid.uuid4().hex[:8]}"
    task = AgentTask(
        id=uuid.uuid4().hex,
        prompt=prompt_text,
        db_connection_id=connection_id,
        session_id=session_id,
        mode="full_autonomy",
        metadata={"source": "temporal_worker"},
    )

    service = AutonomousAgentService(
        db_connection=db_connection,
        database=database,
        storage=storage,
    )

    if callback_url:
        return await self._execute_with_streaming(service, task, callback_url)
    else:
        # Fallback to non-streaming
        result = await service.execute(task)
        return self._serialize_result(result)

async def _execute_with_streaming(
    self,
    service: AutonomousAgentService,
    task: AgentTask,
    callback_url: str,
) -> dict:
    """Stream events to callback_url, heartbeat to Temporal."""
    import httpx

    events_sent = 0
    events_failed = 0
    final_result = None

    async with httpx.AsyncClient(timeout=3.0) as client:
        async for event in service.stream_execute(task):
            event_type = event.get("type", "unknown")

            # POST event to callback
            try:
                await client.post(
                    callback_url,
                    json={"session_id": task.session_id, "event": event},
                )
                events_sent += 1
            except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError):
                events_failed += 1

            # Heartbeat to Temporal every 5 events
            if (events_sent + events_failed) % 5 == 0:
                activity.heartbeat(
                    f"events_sent={events_sent}, events_failed={events_failed}"
                )

            # Capture final result from "done" event
            if event_type == "done":
                final_result = event.get("result", {})

    # Send completion event
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                callback_url,
                json={
                    "session_id": task.session_id,
                    "event": {"type": "done", "result": final_result},
                },
            )
    except Exception:
        pass

    return final_result or {"task_id": task.id, "status": "completed"}
```

**Key design choices:**
- Callback POST failures are swallowed (log, don't crash) — activity continues regardless
- Short timeout (3s) per POST — prevents slow callback from blocking the agent
- Heartbeat every 5 events — keeps Temporal informed without flooding
- Falls back to `execute()` when no `callback_url` — backward compatible
- `_serialize_result` reuses existing pattern from `chat` activity

### Phase 3: SSE Callback Receiver

**Deliverable:** `app/temporal/sse_callback.py`

A standalone FastAPI app that:
1. Receives POSTed events from the activity (callback receiver)
2. Serves SSE subscriptions per session (event streaming to clients)

```python
# app/temporal/sse_callback.py
"""
Lightweight SSE callback receiver for Temporal streaming.

Usage:
    uv run python -m app.temporal.sse_callback

Endpoints:
    POST /events/{session_id}  - Receive events from activity
    GET  /stream/{session_id}  - SSE subscription for clients
"""
import asyncio
import json
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


# In-memory event channels (single-process)
_channels: dict[str, asyncio.Queue] = {}


def _get_channel(session_id: str) -> asyncio.Queue:
    if session_id not in _channels:
        _channels[session_id] = asyncio.Queue()
    return _channels[session_id]


class CallbackEvent(BaseModel):
    session_id: str
    event: dict


app = FastAPI(title="KAI SSE Callback Receiver")


@app.post("/events/{session_id}")
async def receive_event(session_id: str, payload: CallbackEvent):
    """Receive streaming events from Temporal activity."""
    channel = _get_channel(session_id)
    await channel.put(payload.event)
    return {"status": "ok"}


@app.get("/stream/{session_id}")
async def stream_events(session_id: str):
    """SSE endpoint for clients to subscribe to streaming events."""
    channel = _get_channel(session_id)

    async def event_generator():
        while True:
            try:
                event = await asyncio.wait_for(channel.get(), timeout=300)
                event_type = event.get("type", "message")
                yield f"event: {event_type}\ndata: {json.dumps(event)}\n\n"
                if event_type == "done":
                    break
            except asyncio.TimeoutError:
                yield f"event: timeout\ndata: {json.dumps({'type': 'timeout'})}\n\n"
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8092)
```

**Key decisions:**
- **Separate process on port 8092** — decoupled from the KAI API and the worker
- **In-memory `asyncio.Queue`** — sufficient for single-process test scenarios. NOT production-grade (would need Redis pub/sub for multi-replica). Documented as a limitation.
- **5-minute timeout** — SSE connection closes if no events for 5 min (prevents resource leak)
- **Clean shutdown** — stream ends when "done" event is received

### Phase 4: E2E Test Script

**Deliverable:** `cookbook/temporal_e2e_streaming.py`

```python
"""
Temporal E2E Streaming Test

Prerequisites:
    1. temporal server start-dev
    2. uv run python -m app.temporal.sse_callback   (port 8092)
    3. uv run python -m app.worker_main             (connects to Temporal)
    4. Typesense running (docker compose up typesense -d)
    5. PostgreSQL with koperasi data accessible

Usage:
    uv run python cookbook/temporal_e2e_streaming.py \
        --connection-id <your-connection-id> \
        --prompt "Tampilkan top 5 provinsi dengan rata-rata modal awal koperasi tertinggi"
"""
```

Script flow:
1. Parse args (connection_id, prompt, temporal_host, callback_host)
2. Connect to Temporal via `temporalio.client.Client`
3. Start SSE subscription in background task (via `httpx_sse` or raw `httpx`)
4. Execute workflow: `client.execute_workflow(KaiChatWorkflow.run, input, ...)`
5. Collect SSE events in background task
6. Print streaming events as they arrive (with timestamps)
7. On workflow completion, validate:
   - `result["status"]` is not `"failed"`
   - `result["final_answer"]` is non-empty string
   - `result["sql_queries"]` is non-empty list
   - At least one SSE event of type `token` was received
   - At least one SSE event of type `tool_start` was received
8. Print summary: events received, execution time, final answer preview

### Phase 5: Temporal CLI Documentation

**Deliverable:** Section in `cookbook/temporal_e2e_streaming.py` docstring + `docs/tutorials/temporal-e2e-test.md`

```bash
# Start workflow via Temporal CLI
temporal workflow execute \
    --type KaiChatWorkflow \
    --task-queue kai-agent-queue \
    --workflow-id "test-$(date +%s)" \
    --input '{"prompt": "Tampilkan top 5 provinsi dengan rata-rata modal awal koperasi tertinggi", "connection_id": "your-connection-id", "callback_url": "http://localhost:8092/events/test-session-1"}'

# Check workflow status
temporal workflow describe --workflow-id "test-..."

# Get workflow result
temporal workflow show --workflow-id "test-..."

# List recent workflows
temporal workflow list --query 'WorkflowType="KaiChatWorkflow"'
```

## System-Wide Impact

### Interaction Graph

```
temporal workflow execute (or Python SDK)
  └─ Temporal Server dispatches to Worker
       └─ KaiChatWorkflow.run()
            └─ workflow.execute_activity_method(chat_streaming)
                 └─ KaiActivities.chat_streaming()
                      ├─ Storage() → Typesense (schema, memory, skills)
                      ├─ DatabaseConnectionRepository.find_by_id()
                      ├─ SQLDatabase.get_sql_engine() → PostgreSQL
                      ├─ AutonomousAgentService.stream_execute()
                      │    ├─ DeepAgent (LangGraph) → LLM API
                      │    ├─ 40+ tools (SQL, schema, glossary, etc.)
                      │    └─ Yields streaming events
                      ├─ httpx.post(callback_url) per event
                      └─ activity.heartbeat() every 5 events
```

### Error Propagation

- **LLM API failure** → `stream_execute` yields `{"type": "error"}` → activity returns error result → workflow completes with error status
- **Database query failure** → SQL tool returns error → agent handles internally → may retry or report
- **Callback URL unreachable** → `httpx` exception caught → `events_failed` counter incremented → activity continues → final result includes delivery stats
- **Worker crash** → Temporal detects missing heartbeat after 60s → retries activity on another worker (or same worker after restart)
- **Typesense down** → `Storage()` constructor fails → activity raises exception → Temporal retries

### State Lifecycle Risks

- **Partial event delivery:** If callback fails after 50 events, client sees partial stream. Mitigated by "done" event containing full result.
- **Duplicate events on retry:** If Temporal retries the activity, the new attempt re-sends all events. Client should handle duplicates (or clear buffer on retry). Acceptable for test scenario.
- **Orphaned SSE channels:** If workflow fails before "done" event, SSE client hangs until 5-minute timeout. Acceptable for test scenario.

### API Surface Parity

- `chat` activity: non-streaming, no callback — **unchanged**
- `autonomous_chat` activity: non-streaming, no callback — **unchanged**
- `chat_streaming` activity: **new** — streaming with optional callback
- `KaiChatWorkflow`: **new** — wraps `chat_streaming`

No breaking changes to existing activities or API endpoints.

## Acceptance Criteria

### Functional Requirements

- [ ] `KaiChatWorkflow` is defined with `@workflow.defn` in `app/temporal/workflows.py`
- [ ] `chat_streaming` activity exists in `app/temporal/activities.py`
- [ ] Worker registers both workflow and activities in `app/worker_main.py`
- [ ] Activity calls `stream_execute()` when `callback_url` is provided
- [ ] Activity falls back to `execute()` when `callback_url` is `None`
- [ ] Activity POSTs each streaming event to `callback_url` with `{session_id, event}` JSON
- [ ] Activity calls `activity.heartbeat()` every 5 events
- [ ] Activity continues execution even if callback POST fails
- [ ] SSE callback receiver accepts POST on `/events/{session_id}`
- [ ] SSE callback receiver serves SSE stream on `GET /stream/{session_id}`

### E2E Test Requirements

- [ ] Workflow starts and is visible in Temporal (`temporal workflow list`)
- [ ] Activity heartbeats show progress in Temporal workflow history
- [ ] SSE endpoint receives streaming events (`tool_start`, `token`, `tool_end`)
- [ ] Agent generates valid SQL and executes against real PostgreSQL database
- [ ] Workflow completes with `AgentResult` dict containing non-empty `final_answer`
- [ ] `sql_queries` list in result is non-empty
- [ ] Test is repeatable (can run multiple times with same connection)
- [ ] Both Python SDK script AND Temporal CLI commands work

### Non-Functional Requirements

- [ ] Callback POST timeout is 3 seconds (doesn't block agent execution)
- [ ] SSE connection timeout is 5 minutes (prevents resource leaks)
- [ ] No breaking changes to existing `chat` or `autonomous_chat` activities

## Success Metrics

- Workflow completes with status `completed` (not `failed`)
- Streaming events are received by SSE subscriber before workflow completion
- Total execution time is within 2x of direct CLI execution time (overhead from Temporal + SSE is minimal)
- Test can be run by a new developer following the tutorial with < 5 minutes setup

## Dependencies & Risks

| Dependency | Required | Risk |
|-----------|----------|------|
| Temporal dev server CLI | Must be installed | Low — `brew install temporal` or `go install` |
| Running Typesense | Must be running | Low — already part of dev workflow |
| PostgreSQL with koperasi data | Must be accessible | Low — user confirmed existing |
| KAI database connection registered | Must exist in Typesense | Medium — user must have run `kai connection create` |
| LLM API key configured | Must be set in `.env` | Low — existing requirement |
| `temporalio>=1.4.0` | Already in `pyproject.toml` | None |
| `httpx>=0.27.0` | Already in `pyproject.toml` | None |

**Risk: LLM cost per test run.** Each E2E test triggers a full agent analysis with LLM calls. Cost depends on model (Gemini Flash is cheapest). Not suitable for CI — this is a manual integration test.

## Alternative Approaches Considered

### 1. Pure Temporal (signals + queries, no SSE)

Activity signals workflow with events; client polls workflow queries.
**Rejected:** Temporal queries are poll-based (~50-200ms latency), not push-based. Not suitable for token-by-token streaming. (see brainstorm)

### 2. WebSocket instead of SSE

Full WebSocket connection between cloud and client.
**Rejected:** Would duplicate Temporal's orchestration (queuing, retry, routing). SSE is simpler for server-to-client push. (see brainstorm)

### 3. Redis pub/sub for event channel

Activity publishes to Redis; SSE endpoint subscribes.
**Deferred:** Adds infrastructure dependency. `asyncio.Queue` is sufficient for single-process test scenario. Can upgrade to Redis for production multi-replica deployment.

### 4. `temporalio.testing.WorkflowEnvironment`

In-process Temporal server for pytest.
**Deferred:** Good for unit/integration tests but doesn't validate real network topology. The cookbook script with real Temporal dev server is more valuable for E2E validation. Can add pytest-based tests later.

## Implementation Phases

### Phase 1: Workflow + Activity (Foundation)

**Files:**
- `app/temporal/workflows.py` — new file, `KaiChatWorkflow`
- `app/temporal/activities.py` — add `chat_streaming` method
- `app/worker_main.py` — register workflow

**Success criteria:** `temporal workflow execute --type KaiChatWorkflow` dispatches to worker and returns result (without streaming).

**Estimated effort:** Small

### Phase 2: SSE Callback Receiver

**Files:**
- `app/temporal/sse_callback.py` — new file, standalone FastAPI app

**Success criteria:** `POST /events/{session_id}` + `GET /stream/{session_id}` work. Can verify with `curl`.

**Estimated effort:** Small

### Phase 3: Streaming Integration

**Files:**
- `app/temporal/activities.py` — wire `stream_execute()` + httpx callback + heartbeat

**Success criteria:** Activity POSTs streaming events to callback URL. SSE subscribers see events in real-time.

**Estimated effort:** Medium (requires careful async integration)

### Phase 4: E2E Test Script + Tutorial

**Files:**
- `cookbook/temporal_e2e_streaming.py` — test script
- `docs/tutorials/temporal-e2e-test.md` — setup guide

**Success criteria:** New developer can follow tutorial, run test, and see streaming events + final result.

**Estimated effort:** Medium

## File Inventory

| Action | File Path | Description |
|--------|-----------|-------------|
| CREATE | `app/temporal/workflows.py` | `KaiChatWorkflow` definition |
| MODIFY | `app/temporal/activities.py` | Add `chat_streaming` activity method |
| MODIFY | `app/worker_main.py` | Register `KaiChatWorkflow` in Worker |
| CREATE | `app/temporal/sse_callback.py` | Standalone SSE callback receiver |
| CREATE | `cookbook/temporal_e2e_streaming.py` | E2E test script |
| CREATE | `docs/tutorials/temporal-e2e-test.md` | Setup and usage tutorial |

## Sources & References

### Origin

- **Brainstorm document:** [docs/brainstorms/2026-02-27-temporal-e2e-streaming-brainstorm.md](docs/brainstorms/2026-02-27-temporal-e2e-streaming-brainstorm.md) — Key decisions: Temporal for control plane + SSE for streaming, `KaiChatWorkflow` wrapping chat activity, callback_url passed through workflow input, activity heartbeats for Temporal visibility.

### Internal References

- Existing activities: `app/temporal/activities.py` (chat activity pattern at line 125)
- Worker startup: `app/worker_main.py` (Worker constructor at line 275)
- Streaming service: `app/modules/autonomous_agent/service.py` (stream_execute at line 720)
- Agent models: `app/modules/autonomous_agent/models.py` (AgentTask at line 41, AgentResult at line 198)
- Existing SSE patterns: `app/modules/autonomous_agent/api/endpoints.py` (SSE format at line 271)
- Existing activity tests: `tests/temporal/test_activities_wiring.py` (mock patterns)
- Cookbook patterns: `cookbook/utils/__init__.py` (KAIAPIClient, helpers)

### External References

- [Temporal Python SDK — Workflows](https://docs.temporal.io/develop/python/core-application#develop-workflows)
- [Temporal Python SDK — Activity Heartbeats](https://docs.temporal.io/develop/python/failure-detection#activity-heartbeats)
- [Temporal CLI — workflow execute](https://docs.temporal.io/cli/workflow/execute)
- [SSE Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
