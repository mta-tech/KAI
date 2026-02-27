# Plan: Temporal E2E Streaming with SSE Callback

**Status:** Ready
**Branch:** `feat/agentic-context-platform`
**Author:** Claude
**Date:** 2026-02-27
**Origin:** `docs/brainstorms/2026-02-27-temporal-e2e-streaming-brainstorm.md`

---

## Task Description

Build a real end-to-end integration test where KAI runs as a Temporal worker, receives NL-to-Analysis prompts via the Temporal API, streams execution events back via SSE callback, and returns the final result through Temporal workflow completion.

This validates the production remote-control architecture: workers on-prem/edge, users dispatch from cloud/mobile. The streaming plane (SSE callback) runs alongside the control plane (Temporal) to deliver real-time token/tool events to subscribers.

Test query: `"Tampilkan top 5 provinsi dengan rata-rata modal awal koperasi tertinggi"`

## Objective

1. Create `KaiChatWorkflow` — the first Temporal workflow in the codebase
2. Create `chat_streaming` activity with callback URL support and heartbeat
3. Build a standalone SSE callback receiver for streaming events
4. Deliver an E2E test script (Python SDK) and Temporal CLI documentation
5. Validate the full pipeline: Temporal dispatch → agent execution → SQL against real DB → streaming events → final result

## Relevant Files

### Existing Files (Modify)

| File | Line | What Changes |
|------|------|-------------|
| `app/temporal/activities.py` | 125 | Add `chat_streaming` method to `KaiActivities` class |
| `app/worker_main.py` | 275 | Register `KaiChatWorkflow` in `Worker()` constructor |

### Existing Files (Reference Only)

| File | Line | What to Reference |
|------|------|------------------|
| `app/temporal/activities.py` | 126 | `chat()` method — pattern for connection lookup, Storage init, AgentTask construction |
| `app/modules/autonomous_agent/service.py` | 720 | `stream_execute()` — async generator yielding streaming events |
| `app/modules/autonomous_agent/models.py` | 41 | `AgentTask` dataclass definition |
| `app/modules/autonomous_agent/models.py` | 198 | `AgentResult` dataclass definition |
| `app/modules/autonomous_agent/api/endpoints.py` | 271 | SSE event format pattern: `f"event: {type}\ndata: {json}\n\n"` |
| `tests/temporal/test_activities_wiring.py` | 8 | Test mocking pattern: `_make_activities()` with patched Settings |
| `cookbook/utils/__init__.py` | 1 | Cookbook utility patterns |

### New Files (Create)

| File | Description |
|------|-------------|
| `app/temporal/workflows.py` | `KaiChatWorkflow` with `@workflow.defn` |
| `app/temporal/sse_callback.py` | Standalone FastAPI SSE callback receiver (port 8092) |
| `cookbook/temporal_e2e_streaming.py` | E2E test script with Python SDK + SSE subscriber |
| `docs/tutorials/temporal-e2e-test.md` | Setup guide with Temporal CLI commands |

## Step by Step Tasks

### 1. Create Temporal Workflow Definition
- **Task ID:** workflow-definition
- **Depends On:** none
- **Assigned To:** builder-temporal
- **Agent Type:** general-purpose
- **Parallel:** false

Create `app/temporal/workflows.py` with:

```python
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
            args=[input.prompt, input.connection_id, input.conversation_id, input.callback_url],
            start_to_close_timeout=timedelta(minutes=15),
            heartbeat_timeout=timedelta(seconds=60),
        )
```

Key constraints:
- `KaiChatInput` must be a `@dataclass` (Temporal's default serializer)
- `callback_url` optional — falls back to non-streaming when `None`
- `heartbeat_timeout=60s` — activity must heartbeat within 60s or Temporal considers it stuck
- Must use `workflow.unsafe.imports_passed_through()` for activity imports (Temporal sandbox requirement)

**Acceptance Criteria:**
- [ ] `app/temporal/workflows.py` exists with `KaiChatWorkflow` class
- [ ] `KaiChatInput` dataclass has all 4 fields (prompt, connection_id, conversation_id, callback_url)
- [ ] Workflow calls `chat_streaming` activity method

---

### 2. Create Streaming Activity
- **Task ID:** streaming-activity
- **Depends On:** none
- **Assigned To:** builder-temporal
- **Agent Type:** general-purpose
- **Parallel:** true (can run alongside task 1)

Add `chat_streaming` method to `KaiActivities` class in `app/temporal/activities.py`.

Follow the existing `chat` method pattern at line 126 for connection lookup and Storage initialization.

Key behavior:
- When `callback_url` is provided: use `service.stream_execute(task)` and POST each event to `callback_url` via `httpx.AsyncClient(timeout=3.0)`
- When `callback_url` is `None`: fall back to `service.execute(task)` (non-streaming)
- Call `activity.heartbeat()` every 5 events with progress string
- Catch `httpx.ConnectError`, `httpx.TimeoutException`, `httpx.HTTPStatusError` — log and continue, never crash
- Track `events_sent` and `events_failed` counters
- Capture final result from the `"done"` event yielded by `stream_execute()`
- POST body format: `{"session_id": task.session_id, "event": <event_dict>}`
- Send a final `{"type": "done", "result": final_result}` event after stream ends

Also add a `_execute_with_streaming` helper method (private) that encapsulates the streaming + callback logic.

Reference `app/modules/autonomous_agent/service.py:720` for `stream_execute()` signature and event types (`token`, `tool_start`, `tool_end`, `done`, `error`).

**Acceptance Criteria:**
- [ ] `chat_streaming` activity method exists on `KaiActivities`
- [ ] Uses `stream_execute()` when `callback_url` provided
- [ ] Falls back to `execute()` when `callback_url` is `None`
- [ ] POSTs events to `callback_url` with `{session_id, event}` JSON
- [ ] Calls `activity.heartbeat()` every 5 events
- [ ] Continues execution even if callback POST fails
- [ ] Returns dict matching existing `chat` activity return format

---

### 3. Register Workflow in Worker
- **Task ID:** worker-registration
- **Depends On:** workflow-definition, streaming-activity
- **Assigned To:** builder-temporal
- **Agent Type:** general-purpose
- **Parallel:** false

Modify `app/worker_main.py`:

1. Add import: `from app.temporal.workflows import KaiChatWorkflow`
2. At line 275, add `workflows=[KaiChatWorkflow]` to the `Worker()` constructor
3. Add `chat_streaming` to the activities list

The Worker constructor currently (line 275-287):
```python
worker = Worker(
    client,
    task_queue=config.task_queue,
    activities=[
        activities.store_connection,
        activities.test_connection,
        activities.scan_schema,
        activities.chat,
        activities.autonomous_chat,
        activities.sync_config,
        activities.generate_mdl,
    ],
)
```

Should become:
```python
worker = Worker(
    client,
    task_queue=config.task_queue,
    activities=[
        activities.store_connection,
        activities.test_connection,
        activities.scan_schema,
        activities.chat,
        activities.autonomous_chat,
        activities.chat_streaming,
        activities.sync_config,
        activities.generate_mdl,
    ],
    workflows=[KaiChatWorkflow],
)
```

**Acceptance Criteria:**
- [ ] `KaiChatWorkflow` is imported in `worker_main.py`
- [ ] `workflows=[KaiChatWorkflow]` added to Worker constructor
- [ ] `activities.chat_streaming` added to activities list
- [ ] Worker starts without import errors

---

### 4. Create SSE Callback Receiver
- **Task ID:** sse-callback
- **Depends On:** none
- **Assigned To:** builder-sse
- **Agent Type:** general-purpose
- **Parallel:** true (independent of tasks 1-3)

Create `app/temporal/sse_callback.py` — a standalone FastAPI app on port 8092.

Two endpoints:
- `POST /events/{session_id}` — receives POSTed events from the activity, pushes to `asyncio.Queue`
- `GET /stream/{session_id}` — SSE endpoint that reads from Queue and yields events to subscriber

Design:
- Module-level `dict[str, asyncio.Queue]` for event channels (single-process only)
- `CallbackEvent` Pydantic model: `{session_id: str, event: dict}`
- SSE response uses `StreamingResponse` with `media_type="text/event-stream"`
- SSE format: `event: {type}\ndata: {json}\n\n` (matches pattern in `app/modules/autonomous_agent/api/endpoints.py:271`)
- 5-minute timeout on `asyncio.wait_for(channel.get())` — prevents resource leaks
- Stream ends when `"done"` event type received
- Runnable as `uv run python -m app.temporal.sse_callback`
- Add `__main__` block with `uvicorn.run(app, host="0.0.0.0", port=8092)`

**Acceptance Criteria:**
- [ ] `app/temporal/sse_callback.py` exists and is runnable
- [ ] POST `/events/{session_id}` accepts `{session_id, event}` JSON
- [ ] GET `/stream/{session_id}` returns SSE stream
- [ ] Events posted via POST appear in GET stream
- [ ] Stream ends on "done" event
- [ ] 5-minute timeout closes idle connections

---

### 5. Create E2E Test Script
- **Task ID:** e2e-test-script
- **Depends On:** workflow-definition, streaming-activity, worker-registration, sse-callback
- **Assigned To:** builder-test
- **Agent Type:** general-purpose
- **Parallel:** false

Create `cookbook/temporal_e2e_streaming.py`.

Script flow:
1. Parse CLI args: `--connection-id` (required), `--prompt` (default: koperasi query), `--temporal-host` (default: `localhost:7233`), `--callback-host` (default: `http://localhost:8092`)
2. Connect to Temporal: `client = await Client.connect(temporal_host)`
3. Generate `session_id = f"e2e-test-{uuid.uuid4().hex[:8]}"`
4. Build callback URL: `f"{callback_host}/events/{session_id}"`
5. Start SSE subscription in background asyncio task via raw `httpx.AsyncClient` streaming (GET `{callback_host}/stream/{session_id}`)
6. Execute workflow: `result = await client.execute_workflow(KaiChatWorkflow.run, KaiChatInput(...), id=f"e2e-{session_id}", task_queue="kai-agent-queue")`
7. Collect SSE events from background task
8. Print streaming events as they arrive with timestamps and event type
9. On workflow completion, validate:
   - `result["status"]` is not `"failed"`
   - `result["final_answer"]` is non-empty string
   - `result["sql_queries"]` is non-empty list (if present)
   - At least one SSE event received
10. Print summary: total events, execution time, final answer preview (first 200 chars)

Include comprehensive docstring with prerequisites:
```
Prerequisites:
    1. temporal server start-dev
    2. uv run python -m app.temporal.sse_callback
    3. uv run python -m app.worker_main
    4. Typesense running (docker compose up typesense -d)
    5. PostgreSQL with koperasi data accessible
    6. Database connection registered via `kai connection create`
```

Import `KaiChatWorkflow` and `KaiChatInput` from `app.temporal.workflows` for type-safe workflow execution.

**Acceptance Criteria:**
- [ ] `cookbook/temporal_e2e_streaming.py` exists and is runnable
- [ ] Connects to Temporal and starts workflow
- [ ] Subscribes to SSE stream and collects events
- [ ] Prints streaming events in real-time
- [ ] Validates workflow result (final_answer non-empty)
- [ ] Prints summary with event count and execution time
- [ ] Has clear docstring with prerequisites

---

### 6. Create Tutorial Documentation
- **Task ID:** tutorial-docs
- **Depends On:** e2e-test-script
- **Assigned To:** builder-test
- **Agent Type:** general-purpose
- **Parallel:** false

Create `docs/tutorials/temporal-e2e-test.md` with:

1. **Prerequisites** section — what to install and configure
2. **Quick Start** — step-by-step commands to run the test (4 terminal tabs)
3. **Temporal CLI** commands:
   ```bash
   temporal workflow execute --type KaiChatWorkflow --task-queue kai-agent-queue \
     --workflow-id "test-$(date +%s)" \
     --input '{"prompt": "...", "connection_id": "...", "callback_url": "http://localhost:8092/events/test-1"}'
   temporal workflow describe --workflow-id "test-..."
   temporal workflow show --workflow-id "test-..."
   temporal workflow list --query 'WorkflowType="KaiChatWorkflow"'
   ```
4. **Architecture** diagram explaining the 3-process setup
5. **Troubleshooting** common issues

**Acceptance Criteria:**
- [ ] `docs/tutorials/temporal-e2e-test.md` exists
- [ ] Contains both Python SDK and Temporal CLI instructions
- [ ] A developer can follow it and run the test successfully

---

### 7. Validate Full E2E Pipeline
- **Task ID:** e2e-validation
- **Depends On:** e2e-test-script, tutorial-docs
- **Assigned To:** builder-test
- **Agent Type:** general-purpose
- **Parallel:** false

Run the complete E2E test and verify all acceptance criteria:

1. Start Temporal dev server: `temporal server start-dev`
2. Start SSE callback: `uv run python -m app.temporal.sse_callback`
3. Start KAI worker: `uv run python -m app.worker_main`
4. Run test script: `uv run python cookbook/temporal_e2e_streaming.py --connection-id <id>`
5. Verify:
   - Workflow visible in Temporal (`temporal workflow list`)
   - SSE events received (tool_start, token, tool_end)
   - Workflow completes with non-empty final_answer
   - SQL queries were executed against real database

**Note:** This task requires manual infrastructure. The builder should verify the code compiles and the logic is correct, but actual E2E execution depends on the user's local environment.

**Acceptance Criteria:**
- [ ] All code files pass syntax check (`python -c "import app.temporal.workflows"`)
- [ ] Worker starts without import errors
- [ ] SSE callback receiver starts on port 8092
- [ ] Test script runs without Python errors (may need mock for actual execution)

## Acceptance Criteria

### Functional Requirements
- [ ] `KaiChatWorkflow` defined with `@workflow.defn` in `app/temporal/workflows.py`
- [ ] `chat_streaming` activity exists in `app/temporal/activities.py`
- [ ] Worker registers both workflow and all activities in `app/worker_main.py`
- [ ] Activity uses `stream_execute()` when `callback_url` provided
- [ ] Activity falls back to `execute()` when `callback_url` is `None`
- [ ] Activity POSTs events to callback with `{session_id, event}` JSON
- [ ] Activity calls `activity.heartbeat()` every 5 events
- [ ] Activity continues if callback POST fails
- [ ] SSE receiver accepts POST on `/events/{session_id}`
- [ ] SSE receiver serves SSE stream on `GET /stream/{session_id}`

### E2E Test Requirements
- [ ] E2E script connects to Temporal and starts workflow
- [ ] E2E script subscribes to SSE and collects events
- [ ] E2E script validates result (final_answer, sql_queries)
- [ ] Both Python SDK and Temporal CLI documented

### Non-Functional Requirements
- [ ] Callback POST timeout is 3 seconds
- [ ] SSE connection timeout is 5 minutes
- [ ] No breaking changes to existing `chat` or `autonomous_chat` activities

## Team Orchestration

As the team lead, coordinate the builders to implement all tasks sequentially (tasks 1-3 must be sequential, task 4 can parallel with 1-3, tasks 5-7 are sequential after all prior).

### Team Members

#### Temporal Builder
- **Name:** builder-temporal
- **Role:** Backend (Temporal workflow + activity + worker registration)
- **Agent Type:** general-purpose
- **Resume:** true

Handles tasks 1, 2, 3 — the core Temporal infrastructure. Must understand Temporal Python SDK patterns (`@workflow.defn`, `@activity.defn`, `workflow.execute_activity_method`, `activity.heartbeat`).

#### SSE Builder
- **Name:** builder-sse
- **Role:** Backend (SSE callback receiver)
- **Agent Type:** general-purpose
- **Resume:** true

Handles task 4 — standalone FastAPI app. Can run in parallel with Temporal builder since SSE receiver is independent.

#### Test Builder
- **Name:** builder-test
- **Role:** Test + Docs (E2E script + tutorial)
- **Agent Type:** general-purpose
- **Resume:** true

Handles tasks 5, 6, 7 — test script, documentation, and validation. Runs after all infrastructure is in place.

### Execution Strategy

```
Phase 1 (Parallel):
  builder-temporal: Task 1 (workflow) → Task 2 (activity) → Task 3 (worker reg)
  builder-sse:      Task 4 (SSE callback receiver)

Phase 2 (Sequential):
  builder-test:     Task 5 (E2E script) → Task 6 (tutorial) → Task 7 (validation)
```

## Validation Commands

```bash
# Verify imports work
uv run python -c "from app.temporal.workflows import KaiChatWorkflow, KaiChatInput; print('Workflow OK')"
uv run python -c "from app.temporal.activities import KaiActivities; print('Activities OK')"
uv run python -c "from app.temporal.sse_callback import app; print('SSE Callback OK')"

# Start SSE callback and verify
uv run python -m app.temporal.sse_callback &
curl -X POST http://localhost:8092/events/test-1 -H "Content-Type: application/json" -d '{"session_id":"test-1","event":{"type":"token","content":"hello"}}'

# Start worker (requires Temporal server)
temporal server start-dev &
uv run python -m app.worker_main

# Run E2E test
uv run python cookbook/temporal_e2e_streaming.py --connection-id <your-connection-id>
```
