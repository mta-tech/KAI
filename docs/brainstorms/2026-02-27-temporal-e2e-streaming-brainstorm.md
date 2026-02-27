# Temporal E2E Test with Streaming via SSE Callback

**Date:** 2026-02-27
**Status:** Brainstorm Complete
**Author:** KAI Team

## What We're Building

A real end-to-end integration test where:

1. **KAI Worker** runs as a Temporal worker (simulating on-prem/edge deployment)
2. **User sends a prompt** via Temporal API (simulating cloud/mobile app)
3. **Agent executes** the full NL-to-Analysis pipeline against a real PostgreSQL database
4. **Streaming events** flow back to the caller via SSE callback during execution
5. **Final result** is returned via Temporal workflow completion

Test query: `"Tampilkan top 5 provinsi dengan rata-rata modal awal koperasi tertinggi"`

## Why This Approach

### Architecture: Remote Control Pattern

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│ Cloud/Mobile │─────▶│   Temporal   │─────▶│   KAI Worker    │
│   (Client)   │      │   Server     │      │ (on-prem/edge)  │
│              │      │              │      │                 │
│  SSE ◀───────│◀─────│──────────────│◀─────│  activity runs  │
│  endpoint    │ POST │  callback    │ POST │  agent + stream │
└─────────────┘      └──────────────┘      └─────────────────┘
```

**Why Temporal for orchestration (not WebSocket):**

- Workers long-poll outbound — works behind corporate firewalls/NAT without inbound ports
- Built-in task queuing — prompts wait if worker is offline, auto-dispatched when it reconnects
- Durable execution — if worker crashes mid-analysis, Temporal retries on another worker
- Multi-tenancy via task queues — `kai-{ORG_ID}-queue` already implemented
- Worker health monitoring — heartbeat/registration already built in `worker_main.py`
- Retry policies, timeouts, workflow history — production-grade out of the box

**Why SSE callback for streaming (not Temporal signals):**

- Temporal queries are poll-based (~50-200ms latency per round-trip), not push-based
- Token-by-token streaming requires sub-millisecond delivery — Temporal isn't designed for this
- SSE is HTTP-based, stateless, works with mobile/web natively
- Activity POSTs events to cloud callback URL — simple, decoupled
- Cloud exposes SSE endpoint per session — clients subscribe for real-time updates

**Why not full custom WebSocket:**

- Would duplicate Temporal's orchestration (queuing, retry, routing, health monitoring)
- Months of engineering vs. Temporal's existing infrastructure
- WebSocket only needed for streaming — SSE is simpler for server-to-client push

## Key Decisions

### 1. Workflow Design

Create a `KaiChatWorkflow` with:
- `@workflow.defn` wrapping the `chat` activity
- Input: `KaiChatInput(prompt, connection_id, conversation_id, callback_url)`
- The `callback_url` is passed to the activity for SSE event posting
- Workflow returns `AgentResult` dict on completion

### 2. Streaming Mechanism

**Activity → Cloud callback flow:**

```
Activity starts agent execution
  │
  ├─ agent streams event (token/tool_start/tool_end)
  │    └─ POST to callback_url with event JSON
  │
  ├─ activity.heartbeat(progress_summary)  # for Temporal visibility
  │
  └─ activity completes → returns AgentResult
```

**Cloud SSE endpoint flow:**

```
Client subscribes to GET /stream/{session_id} (SSE)
  │
  ├─ Cloud receives POST from activity callback
  │    └─ Pushes event to SSE subscribers for that session_id
  │
  └─ On workflow completion → sends "done" event with result
```

### 3. Test Infrastructure

- **Temporal:** `temporal server start-dev` (lightweight CLI dev server)
- **Database:** Existing local PostgreSQL with koperasi data (already connected to KAI)
- **Typesense:** Existing local instance (required for schema/skills/memory)
- **KAI Worker:** Started via `uv run python -m app.worker_main`

### 4. Test Deliverables

**Python SDK test script** (`cookbook/temporal_e2e_test.py`):
- Connects to Temporal
- Starts workflow with prompt + callback URL
- Subscribes to SSE endpoint for streaming events
- Validates: workflow completes, final_answer is non-empty, SQL queries were executed
- Prints streaming events in real-time

**Temporal CLI commands** (documented):
- `temporal workflow execute` with JSON input
- Manual workflow inspection and result retrieval

### 5. Success Criteria

- [ ] Workflow starts and is visible in Temporal
- [ ] Activity heartbeats show progress
- [ ] SSE endpoint receives streaming events (tool_start, token, tool_end)
- [ ] Agent generates valid SQL and executes against real database
- [ ] Workflow completes with `AgentResult` containing non-empty `final_answer`
- [ ] `sql_queries` list in result is non-empty
- [ ] Test is repeatable (can run multiple times)

## Comparison: Temporal vs WebSocket (Decision Record)

| Concern | Temporal | WebSocket | Decision |
|---------|----------|-----------|----------|
| NAT/Firewall traversal | Built-in (outbound long-poll) | Must build outbound WS | Temporal |
| Offline queuing | Built-in (durable task queue) | Must build (Redis/DB queue) | Temporal |
| Crash recovery | Automatic retry on another worker | Must build | Temporal |
| Multi-tenancy | Task queues per org | Must build routing | Temporal |
| Worker health | Heartbeat + registration | Must build | Temporal |
| Token streaming | Not designed for this | Excellent (push, low-latency) | WebSocket/SSE |
| Mobile support | No native SDK (needs cloud API) | Native on all platforms | SSE |
| Infrastructure | Temporal server (or Cloud SaaS) | WS server + Redis + auth | Temporal simpler |

**Result:** Temporal for control plane + SSE for streaming. Best of both worlds.

## Scope

### In Scope

- `KaiChatWorkflow` definition with callback_url support
- Modified `chat` activity to POST streaming events to callback
- Python test script for E2E validation
- Temporal CLI command documentation
- SSE callback receiver (simple FastAPI endpoint for testing)

### Out of Scope (Future)

- Production SSE infrastructure (load balancing, auth, rate limiting)
- Mobile SDK integration
- Multi-worker failover testing
- Temporal Cloud deployment
- WebSocket fallback for environments where SSE isn't supported

## Open Questions

_None - all questions resolved during brainstorm._
