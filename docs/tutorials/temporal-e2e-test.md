# Temporal E2E Streaming Test Tutorial

This tutorial walks through running the full end-to-end Temporal streaming test for KAI. The test exercises the complete pipeline from workflow submission through real-time SSE event delivery.

## Architecture

KAI uses a three-process architecture for Temporal-based streaming:

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│ Client/Test  │─────▶│   Temporal   │─────▶│   KAI Worker    │
│              │      │   Server     │      │ (on-prem/edge)  │
│              │      │              │      │                 │
│  SSE ◀───────│◀─────│──────────────│◀─────│  activity runs  │
│  endpoint    │ POST │  callback    │ POST │  agent + stream │
└─────────────┘      └──────────────┘      └─────────────────┘
```

### Process Roles

**Temporal Dev Server** — orchestrates workflow execution and task routing. Receives workflow start requests from clients and dispatches activity tasks to workers polling the `kai-agent-queue` task queue.

**KAI Worker** (`app/worker_main.py`) — runs on-prem or at the edge. Polls Temporal for tasks, executes the `KaiChatWorkflow` and all registered activities (`chat_streaming`, `chat`, `scan_schema`, `store_connection`, `test_connection`, `autonomous_chat`, `sync_config`, `generate_mdl`). Also exposes a health endpoint on port 8091 (`/healthz`, `/readyz`).

**SSE Callback Receiver** (`app/temporal/sse_callback.py`) — a standalone FastAPI app on port 8092. Accepts streaming events POSTed by the worker activity and re-serves them as Server-Sent Events to any connected client. Each session is isolated by `session_id`.

### Data Flow

1. A client submits `KaiChatWorkflow` to Temporal with a `callback_url` pointing at the SSE receiver.
2. Temporal schedules the `chat_streaming` activity on the KAI worker.
3. The worker executes the NL-to-SQL agent via `AutonomousAgentService.stream_execute()`.
4. For every streaming event produced by the agent, the activity POSTs the event to the `callback_url`.
5. The SSE receiver pushes the event onto an in-memory queue keyed by `session_id`.
6. A client subscribed to `GET /stream/{session_id}` receives the event in real time.
7. When the agent finishes, a `done` event is sent, closing the SSE stream.

The activity sends a Temporal heartbeat every 5 events so Temporal knows the activity is still alive. The activity timeout is 15 minutes (`start_to_close_timeout`) with a 60-second `heartbeat_timeout`.

---

## Prerequisites

### Tools

- **Temporal CLI** — install via Homebrew or the install script:

  ```bash
  brew install temporal
  # or
  curl -sSf https://temporal.download/cli.sh | sh
  ```

- **uv** — the project package manager (`pip install uv` or `brew install uv`).

### Services

- **Typesense** must be running for vector search and document storage:

  ```bash
  docker compose up typesense -d
  ```

- **PostgreSQL** with your target dataset must be accessible from the machine running the KAI worker.

### Database Connection

A KAI database connection record must exist for the connection ID you will use. Register one if you have not already:

```bash
uv run kai connection create "postgresql://user:pass@host:5432/dbname" -a mydb
```

Note the connection ID printed after creation — you will pass it as `--connection-id` to the test script.

### Environment Variables

Create or populate `.env.local` in the project root with at minimum:

```bash
# LLM provider (choose one)
GOOGLE_API_KEY=your-google-api-key
# or
OPENAI_API_KEY=your-openai-api-key

# Model selection
CHAT_FAMILY=google          # google | openai | ollama | openrouter
CHAT_MODEL=gemini-2.0-flash # e.g. gpt-4o-mini, gemini-2.0-flash

# Credential encryption (required)
ENCRYPT_KEY=your-fernet-key

# Typesense (use 'typesense' if running inside Docker network)
TYPESENSE_HOST=localhost
```

Generate a Fernet key if needed:

```bash
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Optional worker environment variable:

```bash
# Temporal server address (defaults to localhost:7233)
TEMPORAL_HOST=localhost:7233
```

---

## Quick Start

Open four terminal tabs in the project root and run one command per tab in order.

### Tab 1 — Temporal Dev Server

```bash
temporal server start-dev
```

Temporal listens for gRPC on port 7233. The web UI is available at `http://localhost:8233` and lets you inspect workflow executions, history, and activity results.

### Tab 2 — SSE Callback Receiver

```bash
uv run python -m app.temporal.sse_callback
```

The receiver starts a FastAPI app on port 8092 with two endpoints:

- `POST /events/{session_id}` — accepts event payloads from the worker activity.
- `GET /stream/{session_id}` — serves those events as an SSE stream to clients.

Events are held in an in-memory `asyncio.Queue` per session. The stream closes when a `done` or `timeout` event is received, or after a 300-second idle timeout.

### Tab 3 — KAI Worker

```bash
uv run python -m app.worker_main
```

The worker connects to Temporal at `localhost:7233` (or the value of `TEMPORAL_HOST`) and registers `KaiChatWorkflow` on the `kai-agent-queue` task queue. It also starts a health check server on port 8091. Once running you will see:

```
KAI Worker Configuration:
  Temporal Host: localhost:7233
  Task Queue: kai-agent-queue
  Multi-tenant: False

Starting health server on port 8091...
Connecting to Temporal at localhost:7233...

Starting KAI Temporal Worker on queue 'kai-agent-queue'...
Worker is healthy and ready to process tasks
```

### Tab 4 — E2E Test Script

```bash
uv run python cookbook/temporal_e2e_streaming.py \
    --connection-id YOUR_CONNECTION_ID
```

The script uses a default prompt in Indonesian. Customize the prompt and other options as needed:

```bash
uv run python cookbook/temporal_e2e_streaming.py \
    --connection-id YOUR_CONNECTION_ID \
    --prompt "Show the top 5 provinces by average initial cooperative capital" \
    --temporal-host localhost:7233 \
    --callback-host http://localhost:8092
```

#### What the Script Does

1. Connects to the Temporal server using the Python SDK.
2. Generates a unique `session_id` (e.g. `e2e-test-a1b2c3d4`) and derives the `callback_url` and `stream_url` from it.
3. Starts an SSE consumer background task that connects to `GET /stream/{session_id}` before the workflow starts, so no early events are missed.
4. Submits `KaiChatWorkflow` with `KaiChatInput(prompt, connection_id, conversation_id, callback_url)`.
5. Prints each SSE event as it arrives with a timestamp and event type.
6. After the workflow returns, validates the result:
   - `status` is not `"failed"`.
   - `final_answer` is a non-empty string.
   - `sql_queries` (when present) is a non-empty list.
   - At least one SSE event was received.
7. Prints a summary including execution time, event count, SQL query count, and a preview of the final answer.

#### Example Output

```
======================================================================
KAI Temporal E2E Streaming Test
======================================================================
Session ID     : e2e-test-a1b2c3d4
Workflow ID    : e2e-e2e-test-a1b2c3d4
Connection ID  : abc123
Prompt         : Tampilkan top 5 provinsi dengan rata-rata modal awal koperasi tertinggi
Temporal host  : localhost:7233
Callback URL   : http://localhost:8092/events/e2e-test-a1b2c3d4
SSE stream URL : http://localhost:8092/stream/e2e-test-a1b2c3d4
======================================================================

[init] Connecting to Temporal server ...
[init] Connected.

[stream] Starting SSE consumer background task ...
[workflow] Starting KaiChatWorkflow ...

[12:34:01.123] SSE event type='thinking': {"type": "thinking", "content": "..."}
[12:34:03.456] SSE event type='sql': {"type": "sql", "query": "SELECT ..."}
[12:34:05.789] SSE event type='result': {"type": "result", "data": [...]}
[12:34:06.012] SSE event type='done': {"type": "done", "result": {...}}

======================================================================
Workflow completed
======================================================================
[validation] SSE events received  : 4  (PASS)
[PASS] All validations passed.

Summary
----------------------------------------------------------------------
  Execution time   : 12.34s
  Workflow status  : completed
  SSE events total : 4
  SQL queries      : 1
  Final answer     : 'Berikut adalah 5 provinsi dengan rata-rata modal awal...'
----------------------------------------------------------------------
```

---

## Using the Temporal CLI

You can also trigger and inspect the workflow directly using the Temporal CLI without the Python test script.

### Execute a Workflow

```bash
temporal workflow execute \
  --type KaiChatWorkflow \
  --task-queue kai-agent-queue \
  --workflow-id "test-$(date +%s)" \
  --input '{
    "prompt": "Tampilkan top 5 provinsi dengan rata-rata modal awal koperasi tertinggi",
    "connection_id": "YOUR_CONNECTION_ID",
    "callback_url": "http://localhost:8092/events/test-1"
  }'
```

The `conversation_id` field is optional; omit it and the worker will generate a session ID automatically (`temporal_<8 hex chars>`).

To also receive SSE events while the CLI command is running, open a second terminal and connect with `curl` or any SSE client before running the `execute` command above:

```bash
curl -N http://localhost:8092/stream/test-1
```

### Check Workflow Status

```bash
temporal workflow describe --workflow-id "test-1234567890"
```

### View Workflow History

```bash
temporal workflow show --workflow-id "test-1234567890"
```

The history includes all activity schedule, start, and completion events along with input and output payloads.

### List KaiChat Workflows

```bash
temporal workflow list --query 'WorkflowType="KaiChatWorkflow"'
```

### Cancel a Running Workflow

```bash
temporal workflow cancel --workflow-id "test-1234567890"
```

---

## Architecture — Deeper Explanation

### Dual-Plane Design

KAI separates the **control plane** (Temporal) from the **data plane** (SSE) deliberately:

- **Temporal** handles workflow orchestration, retry logic, state persistence, and task routing. It provides durable execution guarantees: if the worker crashes mid-activity, Temporal will reschedule the activity from its last heartbeat checkpoint once the worker recovers.
- **SSE callbacks** carry the real-time token stream. This is a fire-and-forget side channel. If an SSE event POST fails (connection refused, timeout), the activity increments `events_failed` but continues executing. The workflow result is always returned through the Temporal return value regardless of SSE delivery.

### Why Temporal for On-Prem/Edge Workers

- **NAT traversal** — the worker initiates an outbound connection to Temporal and long-polls for tasks. No inbound ports need to be opened on the worker's network.
- **Offline queuing** — if the worker is temporarily unavailable, tasks accumulate in the Temporal task queue and are delivered once the worker reconnects.
- **Automatic retry** — failed activities are retried according to the retry policy without any client involvement.
- **Multi-tenancy** — when `ORG_ID` is set, the worker uses an org-specific task queue (`kai-{org_id}-queue`) and registers with a control plane, enabling multiple isolated organizations on a shared Temporal cluster.

### Why SSE for Streaming

- **HTTP-based** — SSE works over standard HTTP/1.1 without WebSocket upgrades, making it compatible with proxies, load balancers, and mobile clients.
- **Real-time token delivery** — the agent produces events incrementally (thinking, SQL generation, result rows, final answer). SSE delivers them as they are produced rather than waiting for the full response.
- **Session isolation** — the SSE receiver maintains one `asyncio.Queue` per `session_id`. Multiple concurrent workflows produce independent streams with no cross-talk.

### Activity Heartbeating

The `chat_streaming` activity sends a Temporal heartbeat every 5 events:

```python
if (events_sent + events_failed) % 5 == 0:
    activity.heartbeat(f"events_sent={events_sent}, events_failed={events_failed}")
```

The `heartbeat_timeout` is 60 seconds. If the activity stops heartbeating for 60 seconds (e.g. the agent is stuck), Temporal marks the activity as failed and reschedules it. The `start_to_close_timeout` of 15 minutes is the hard upper bound for the entire activity execution.

---

## Troubleshooting

### Worker not connecting to Temporal

**Symptom:** `ConnectionRefusedError` or `grpc._channel._InactiveRpcError` when starting the worker.

**Fix:** Ensure the Temporal dev server is running (`temporal server start-dev`) and that `TEMPORAL_HOST` matches the server address. The default is `localhost:7233`.

```bash
# Verify Temporal is reachable
temporal operator cluster health
```

### Callback URL unreachable from worker

**Symptom:** `events_failed` keeps incrementing in activity heartbeats. SSE stream shows no events.

**Fix:** The SSE receiver must be running on port 8092 before the workflow starts. Verify:

```bash
curl -s http://localhost:8092/docs | head -5
```

If the worker is running inside Docker and the SSE receiver is on the host, replace `localhost` with `host.docker.internal` in the `callback_url`.

### Typesense not running

**Symptom:** Worker activity fails immediately with a connection error mentioning port 8108.

**Fix:**

```bash
docker compose up typesense -d
# Verify
curl http://localhost:8108/health
```

### No database connection found

**Symptom:** Activity raises `ValueError: Connection YOUR_CONNECTION_ID not found`.

**Fix:** Register the connection first and use the correct connection ID:

```bash
uv run kai connection create "postgresql://user:pass@host:5432/dbname" -a mydb
# List existing connections
uv run kai connection list
```

### Workflow timeout

**Symptom:** Temporal shows the workflow as `TimedOut`. The activity `start_to_close_timeout` is 15 minutes.

**Cause:** The agent is taking longer than 15 minutes to execute. This can happen with very large schemas or complex multi-step reasoning.

**Fix:** Check `AGENT_MAX_ITERATIONS` in your `.env.local` (default 20). If execution is genuinely slow, the timeout can be raised by modifying `start_to_close_timeout` in `app/temporal/workflows.py`. Also confirm the database connection is performant and that SQL execution is not hanging (`SQL_EXECUTION_TIMEOUT` defaults to 60 seconds).

### SSE stream shows no events but workflow completes successfully

**Symptom:** The E2E test reports `No SSE events were received` but the workflow returns a valid result.

**Cause:** The SSE consumer connected to the stream *after* all events were already posted. This can happen if the workflow is very fast or the SSE consumer startup was delayed.

**Fix:** The test script already inserts a 300ms delay after starting the SSE consumer task before submitting the workflow. If races still occur in CI environments, increase the sleep in `cookbook/temporal_e2e_streaming.py`:

```python
await asyncio.sleep(1.0)  # was 0.3
```

### LLM API key not set

**Symptom:** Activity fails with an authentication error or `ValueError: Missing required config value`.

**Fix:** Ensure `GOOGLE_API_KEY` or `OPENAI_API_KEY` and the corresponding `CHAT_FAMILY`/`CHAT_MODEL` are set in `.env.local`. Confirm the settings are loading:

```bash
uv run python -c "from app.server.config import get_settings; s = get_settings(); print(s.CHAT_FAMILY, s.CHAT_MODEL)"
```
