# Session Endpoint Design

**Date:** 2024-11-28
**Status:** Approved
**Author:** Claude (AI-assisted design)

## Overview

Build a session endpoint where users can ask multiple NL → SQL → Analysis queries with the agent remembering/recalling previous prompts and completions. Responses returned via SSE streaming.

## Requirements

| Aspect | Decision |
|--------|----------|
| **Session Scope** | Multi-query conversation (remembers all Q&As) |
| **SSE Events** | Chunked text + status updates (ChatGPT-style) |
| **Memory** | Summarized context (compress old, keep recent full) |
| **Lifecycle** | Full CRUD (create, get, list, resume, close/delete) |
| **Storage** | Typesense (existing) |
| **Architecture** | LangGraph Session Graph with checkpointing |

---

## 1. Session State & Graph Architecture

### Session State Model

```python
class SessionState(TypedDict):
    session_id: str
    db_connection_id: str
    messages: list[Message]          # Full recent messages
    summary: str | None              # Compressed older context
    current_query: str | None        # Active NL query
    current_sql: str | None          # Generated SQL
    current_results: list[dict] | None  # Execution results
    current_analysis: dict | None    # Analysis output
    status: Literal["idle", "processing", "error", "closed"]
    metadata: dict                   # Custom session metadata
    created_at: datetime
    updated_at: datetime
```

### Graph Flow

```
[START] → check_session_exists
              ↓
        load_or_create_session
              ↓
        receive_query ←──────────┐
              ↓                  │
        build_context (summary)  │
              ↓                  │
        generate_sql ───stream──→│ SSE
              ↓                  │
        execute_sql ───stream───→│ SSE
              ↓                  │
        generate_analysis ──────→│ SSE
              ↓                  │
        summarize_if_needed      │
              ↓                  │
        save_checkpoint          │
              ↓                  │
        [await_next_query] ──────┘
```

---

## 2. API Endpoints

### Session CRUD Endpoints

```
POST   /api/v1/sessions                    → Create new session
GET    /api/v1/sessions                    → List sessions (by db_connection_id)
GET    /api/v1/sessions/{session_id}       → Get session details + history
DELETE /api/v1/sessions/{session_id}       → Close/delete session
```

### Query Endpoint (SSE Streaming)

```
POST   /api/v1/sessions/{session_id}/query/stream
       Body: { "query": "Show me top 10 customers by revenue" }
       Response: text/event-stream
```

### SSE Event Types

```
event: status
data: {"step": "building_context", "message": "Loading conversation history..."}

event: status
data: {"step": "generating_sql", "message": "Analyzing your question..."}

event: chunk
data: {"type": "sql", "content": "SELECT c.name, SUM(o.total)..."}

event: status
data: {"step": "executing_sql", "message": "Running query..."}

event: chunk
data: {"type": "results", "content": {"rows": [...], "columns": [...]}}

event: status
data: {"step": "analyzing", "message": "Generating insights..."}

event: chunk
data: {"type": "analysis", "content": "The data shows that..."}

event: done
data: {"message_id": "msg_123", "tokens_used": 1250}
```

---

## 3. Memory & Summarization Strategy

### Message Model

```python
class Message(TypedDict):
    id: str
    role: Literal["human", "assistant"]
    query: str                    # Original NL question
    sql: str | None               # Generated SQL
    results_summary: str | None   # Brief description of results
    analysis: str | None          # Full analysis text
    timestamp: datetime
```

### Summarization Rules

- **Recent window**: Keep last 3 messages in full detail
- **Older messages**: Summarize into a rolling context summary
- **Trigger**: Summarize when messages exceed 5 OR token count > 2000

### Summary Prompt

```
Given the conversation history below, create a concise summary that captures:
1. Key questions asked and their intent
2. Important findings/insights discovered
3. Any constraints or filters the user specified
4. SQL patterns that worked well

Keep the summary under 500 tokens.
```

### Context Building

```python
def build_context(state: SessionState) -> str:
    context_parts = []

    if state["summary"]:
        context_parts.append(f"Previous context:\n{state['summary']}")

    for msg in state["messages"][-3:]:  # Last 3 full messages
        context_parts.append(f"Q: {msg['query']}\nSQL: {msg['sql']}\nResult: {msg['results_summary']}")

    return "\n\n".join(context_parts)
```

---

## 4. Checkpointing & Storage (Typesense)

### Typesense Collection Schema

```python
sessions_schema = {
    "name": "sessions",
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "db_connection_id", "type": "string", "facet": True},
        {"name": "status", "type": "string", "facet": True},
        {"name": "summary", "type": "string", "optional": True},
        {"name": "messages", "type": "string"},  # JSON stringified
        {"name": "checkpoint", "type": "string"},  # LangGraph checkpoint blob
        {"name": "metadata", "type": "object", "optional": True},
        {"name": "created_at", "type": "int64"},
        {"name": "updated_at", "type": "int64"},
    ]
}
```

### LangGraph Checkpointer Integration

```python
from langgraph.checkpoint.base import BaseCheckpointSaver

class TypesenseCheckpointer(BaseCheckpointSaver):
    """Custom checkpointer that persists to Typesense."""

    def __init__(self, storage: Storage):
        self.storage = storage

    async def aget(self, config: RunnableConfig) -> Checkpoint | None:
        session_id = config["configurable"]["session_id"]
        doc = await self.storage.find_by_id("sessions", session_id)
        if doc and doc.get("checkpoint"):
            return self._deserialize(doc["checkpoint"])
        return None

    async def aput(self, config: RunnableConfig, checkpoint: Checkpoint) -> None:
        session_id = config["configurable"]["session_id"]
        await self.storage.update_or_create("sessions", session_id, {
            "checkpoint": self._serialize(checkpoint),
            "updated_at": int(time.time())
        })
```

### Session Resume Flow

```
GET /sessions/{id} → Load checkpoint → Restore graph state → Ready for next query
```

---

## 5. SSE Streaming Implementation

### Stream Generator

```python
async def stream_session_query(
    session_id: str,
    query: str,
    graph: CompiledGraph,
    checkpointer: TypesenseCheckpointer
) -> AsyncGenerator[str, None]:

    config = {"configurable": {"session_id": session_id}}

    # Stream events from LangGraph
    async for event in graph.astream_events(
        {"current_query": query},
        config=config,
        version="v2"
    ):
        if event["event"] == "on_chain_start":
            node = event["name"]
            yield f"event: status\ndata: {json.dumps({'step': node, 'message': STATUS_MESSAGES[node]})}\n\n"

        elif event["event"] == "on_chat_model_stream":
            chunk = event["data"]["chunk"].content
            if chunk:
                yield f"event: chunk\ndata: {json.dumps({'type': 'text', 'content': chunk})}\n\n"

        elif event["event"] == "on_chain_end":
            node = event["name"]
            output = event["data"]["output"]

            if node == "generate_sql" and output.get("current_sql"):
                yield f"event: chunk\ndata: {json.dumps({'type': 'sql', 'content': output['current_sql']})}\n\n"

            elif node == "execute_sql" and output.get("current_results"):
                yield f"event: chunk\ndata: {json.dumps({'type': 'results', 'content': output['current_results']})}\n\n"

            elif node == "generate_analysis" and output.get("current_analysis"):
                yield f"event: chunk\ndata: {json.dumps({'type': 'analysis', 'content': output['current_analysis']})}\n\n"

    # Final done event
    yield f"event: done\ndata: {json.dumps({'session_id': session_id, 'status': 'complete'})}\n\n"
```

### FastAPI Endpoint

```python
@router.post("/sessions/{session_id}/query/stream")
async def query_session_stream(
    session_id: str,
    body: SessionQueryRequest,
    service: SessionService = Depends(get_session_service)
) -> StreamingResponse:

    return StreamingResponse(
        service.stream_query(session_id, body.query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
```

---

## 6. Module Structure & File Organization

### New Module Location

```
/services/KAI/app/modules/session/
├── __init__.py
├── models/
│   └── __init__.py          # SessionState, Message, SessionMetadata
├── repositories/
│   └── __init__.py          # SessionRepository (Typesense CRUD)
├── services/
│   └── __init__.py          # SessionService (orchestrates graph + streaming)
├── graph/
│   ├── __init__.py          # Compiled session graph
│   ├── state.py             # SessionState TypedDict
│   ├── nodes.py             # Graph nodes (build_context, generate_sql, etc.)
│   └── checkpointer.py      # TypesenseCheckpointer
└── constants.py             # STATUS_MESSAGES, config defaults
```

### API Integration

```python
# /services/KAI/app/api/__init__.py (add to existing)
from app.modules.session.services import SessionService

router.post("/sessions", ...)(create_session)
router.get("/sessions", ...)(list_sessions)
router.get("/sessions/{session_id}", ...)(get_session)
router.delete("/sessions/{session_id}", ...)(delete_session)
router.post("/sessions/{session_id}/query/stream", ...)(query_session_stream)
```

### Dependencies on Existing Modules

```
session/
  ├── uses → sql_generation/   (SQL agent/tools)
  ├── uses → analysis/         (Analysis generation)
  ├── uses → context_store/    (Few-shot examples)
  └── uses → database_connection/  (DB access)
```

---

## Next Steps

1. Create session module directory structure
2. Implement SessionState and Message models
3. Implement TypesenseCheckpointer
4. Build LangGraph session graph with nodes
5. Implement SessionRepository (Typesense CRUD)
6. Implement SessionService with streaming
7. Add API endpoints
8. Write tests
9. Integration testing with existing SQL generation
