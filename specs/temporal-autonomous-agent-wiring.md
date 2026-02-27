# Plan: Wire Temporal Activities to AutonomousAgentService

**Status:** Draft
**Branch:** `feat/temporal-autonomous-agent`
**Author:** Claude
**Date:** 2026-02-26

---

## Problem Statement

The Temporal worker's `chat` activity (`app/temporal/activities.py:121`) uses `AnalysisService.create_comprehensive_analysis()` — a simpler, fixed pipeline (Prompt → SQL Gen → Execute → Analysis) that **completely bypasses** the autonomous agent harness. This means Temporal-dispatched work gets:

- No context platform tools (published instructions, glossary, semantic search)
- No 40+ agent tools (schema exploration, skills, memory, MDL, verified SQL cache)
- No DeepAgents multi-step reasoning with tool selection
- No memory context injection (Letta or Typesense)
- No telemetry tracking for asset reuse KPIs

Meanwhile, the CLI (`kai query run`) and REST API (`POST /agent/sessions/{id}/tasks`) both use `AutonomousAgentService` and get the full tool harness.

Similarly, `sync_config()` writes to old repositories (`InstructionsRepository`, `ContextStoreRepository`) instead of context platform assets with lifecycle governance.

---

## Goal

Make the Temporal worker use `AutonomousAgentService` for `chat` activities, giving it feature parity with CLI/API entry points. All three surfaces should share the same agent harness and tools.

---

## Pre-existing Model Bugs (Must Fix First)

During research, two latent bugs were found in `app/modules/autonomous_agent/models.py` that would crash any caller of `AutonomousAgentService.execute()`:

### Bug 1: `AgentTask` missing `session_id` field

`service.py:550` and `service.py:709` reference `task.session_id`, but `AgentTask` has no `session_id` field:

```python
# models.py (current)
@dataclass
class AgentTask:
    id: str
    prompt: str
    db_connection_id: str
    mode: ... = "full_autonomy"
    context: dict | None = None
    metadata: dict | None = None
    created_at: str = ...
    # ❌ No session_id field
```

Callers that **pass** `session_id`:
- `api/endpoints.py:318` — `AgentTask(..., session_id=session_id, ...)`

Callers that **don't** (would crash on `task.session_id`):
- `cli/query.py:229` — one-shot `_run_task()`
- `cli/query.py:345` — interactive mode (uses `task.id` as de facto session ID)

**Fix:** Add `session_id: str = ""` to `AgentTask`, defaulting to `task.id` via `__post_init__`.

### Bug 2: `AgentResult` requires `mission_id` but callers don't provide it

`AgentResult.mission_id` is a **required** positional field (no default), but all `AgentResult(...)` constructions in `service.py` omit it:

```python
# service.py:677
return AgentResult(
    task_id=task.id,
    status="completed",         # ❌ missing mission_id
    final_answer=final_answer,
    ...
)
```

**Fix:** Give `mission_id` a default value: `mission_id: str = ""`.

---

## Implementation Tasks

### Task 1: Fix `AgentTask` model — add `session_id` field
**File:** `app/modules/autonomous_agent/models.py`

```python
@dataclass
class AgentTask:
    """Task submitted to the autonomous agent."""
    id: str
    prompt: str
    db_connection_id: str
    session_id: str = ""          # ← ADD: defaults to empty, auto-filled
    mode: ... = "full_autonomy"
    context: dict | None = None
    metadata: dict | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        if not self.session_id:
            self.session_id = self.id
```

**Rationale:** When CLI creates `AgentTask(id="cli_abc123", ...)` without `session_id`, `__post_init__` auto-fills it from `id`. The API can still pass `session_id` explicitly. The Temporal activity will pass `conversation_id`.

**Impact:** Zero breaking changes — all existing callers work as-is.

---

### Task 2: Fix `AgentResult` model — make `mission_id` optional
**File:** `app/modules/autonomous_agent/models.py`

```python
@dataclass
class AgentResult:
    """Result from autonomous agent execution."""
    task_id: str
    mission_id: str = ""          # ← CHANGE: was required, now defaults to ""
    status: Literal["completed", "failed", "partial"] = "completed"
    final_answer: str = ""
    ...
```

**Rationale:** `mission_id` is a traceability field for proactive missions. Non-mission executions (simple chat) don't have one. Making it default-empty fixes the crash without losing the field's purpose.

**Impact:** All existing `AgentResult(task_id=..., status=..., ...)` calls stop crashing. No other changes needed.

---

### Task 3: Wire `KaiActivities.chat()` to use `AutonomousAgentService`
**File:** `app/temporal/activities.py`

**Current code (line 120-138):**
```python
@activity.defn
async def chat(self, prompt_text, connection_id, conversation_id=None):
    storage = Storage(self.settings)
    service = AnalysisService(storage)
    prompt_req = PromptRequest(...)
    result = await service.create_comprehensive_analysis(prompt_request=prompt_req, use_deep_agent=True)
    return result
```

**New code:**
```python
@activity.defn
async def chat(self, prompt_text: str, connection_id: str, conversation_id: str | None = None) -> dict:
    import uuid
    from app.modules.database_connection.repositories import DatabaseConnectionRepository
    from app.modules.autonomous_agent.service import AutonomousAgentService
    from app.modules.autonomous_agent.models import AgentTask
    from app.utils.sql_database.sql_database import SQLDatabase
    from app.modules.sql_generation.models import LLMConfig

    storage = Storage(self.settings)

    # Resolve database connection
    db_repo = DatabaseConnectionRepository(storage)
    db_connection = db_repo.find_by_id(connection_id)
    if not db_connection:
        raise ValueError(f"Connection {connection_id} not found")

    # Configure LLM from settings
    llm_config = LLMConfig(
        model_family=self.settings.CHAT_FAMILY,
        model_name=self.settings.CHAT_MODEL,
    )

    # Create SQL engine and autonomous service
    database = SQLDatabase.get_sql_engine(db_connection, False)
    service = AutonomousAgentService(
        db_connection=db_connection,
        database=database,
        storage=storage,
        llm_config=llm_config,
    )

    # Create agent task
    session_id = conversation_id or f"temporal_{uuid.uuid4().hex[:8]}"
    task = AgentTask(
        id=f"temporal_{uuid.uuid4().hex[:8]}",
        prompt=prompt_text,
        db_connection_id=connection_id,
        session_id=session_id,
        mode="full_autonomy",
        metadata={"source": "temporal_worker"},
    )

    # Execute with full tool harness
    result = await service.execute(task)

    # Convert AgentResult → dict for Temporal serialization
    return {
        "task_id": result.task_id,
        "status": result.status,
        "final_answer": result.final_answer,
        "sql_queries": result.sql_queries,
        "execution_time_ms": result.execution_time_ms,
        "error": result.error,
        "mission_id": result.mission_id,
        "stages_completed": result.stages_completed,
    }
```

**Key decisions:**
- `conversation_id` maps to `session_id` for checkpointer continuity
- `mode="full_autonomy"` to match the best agent behavior
- Returns a simple dict (Temporal requires JSON-serializable return values)
- No streaming — Temporal activities are request/response

---

### Task 4: Add `autonomous_chat` activity (optional, safe migration)
**File:** `app/temporal/activities.py`

Instead of replacing `chat()` directly, add a new `autonomous_chat` activity alongside the existing one. This allows gradual migration — the control plane can switch workflow definitions to use the new activity without breaking existing in-flight workflows.

```python
@activity.defn
async def autonomous_chat(self, prompt_text: str, connection_id: str, conversation_id: str | None = None) -> dict:
    """Chat using the full autonomous agent harness with all tools."""
    # ... same implementation as Task 3 ...
```

Also register it in `worker_main.py`:
```python
worker = Worker(
    client,
    task_queue=config.task_queue,
    activities=[
        activities.store_connection,
        activities.test_connection,
        activities.scan_schema,
        activities.chat,                  # Keep old for in-flight workflows
        activities.autonomous_chat,       # New: full agent harness
        activities.sync_config,
        activities.generate_mdl,
    ],
)
```

**Decision:** Whether to add `autonomous_chat` separately vs replace `chat` inline depends on whether there are in-flight Temporal workflows that expect the old `chat` return shape. If the system is not yet in production with Temporal, replacing inline is simpler.

---

### Task 5: Update `sync_config` to route through context platform (P2 — optional)
**File:** `app/temporal/activities.py`

Currently `sync_config()` writes instructions to `InstructionsRepository` and glossary to `ContextStoreRepository`. These are the **old** unversioned stores. The context platform provides lifecycle-managed equivalents.

**Proposed change:** Route synced items through `ContextAssetService` as draft assets, so they enter the lifecycle (draft → verified → published) and become available to the agent via context platform tools.

```python
# Instead of:
repo = InstructionsRepository(storage)
repo.insert({"instruction": inst["content"], ...})

# Route through context platform:
from app.modules.context_platform.services.asset_service import ContextAssetService
from app.modules.context_platform.models.asset import ContextAssetType

asset_service = ContextAssetService(storage)
asset_service.create_asset(
    db_connection_id=connection_id,
    asset_type=ContextAssetType.INSTRUCTION,
    name=inst.get("name", "Synced Instruction"),
    content=inst["content"],
    canonical_key=inst.get("id", "synced-instruction"),
    created_by="temporal_sync",
)
```

**Note:** This is a separate task and lower priority. The old repos still work, and the agent has tools for both old and new systems. Defer unless specifically requested.

---

## Files Changed Summary

| File | Change | Risk |
|------|--------|------|
| `app/modules/autonomous_agent/models.py` | Add `session_id` to `AgentTask`, default `mission_id` in `AgentResult` | Low — backward compatible |
| `app/temporal/activities.py` | Replace `AnalysisService` with `AutonomousAgentService` in `chat()` | Medium — changes return shape |
| `app/worker_main.py` | Register `autonomous_chat` if adding new activity | Low — additive |

---

## Testing Plan

1. **Unit: Model fixes** — Verify `AgentTask()` without `session_id` auto-fills from `id`; `AgentResult()` without `mission_id` defaults to `""`
2. **Unit: Activity** — Mock `AutonomousAgentService.execute()` and verify `chat()` constructs correct `AgentTask` and serializes `AgentResult` to dict
3. **Integration: Import check** — `python -c "from app.temporal.activities import KaiActivities"` succeeds
4. **E2E: Manual** — Start Temporal worker, dispatch a `chat` activity via `temporal workflow execute`, verify full agent tools are used (look for context platform tool calls in logs)

---

## Execution Order

```
Task 1 (fix AgentTask.session_id)
    ↓
Task 2 (fix AgentResult.mission_id)
    ↓
Task 3 (wire chat() to AutonomousAgentService)
    ↓
Task 4 (optional: add autonomous_chat activity)
    ↓
Task 5 (optional/P2: route sync_config through context platform)
```

Tasks 1 and 2 must come first as they fix crashes that block Task 3. Task 4 is optional depending on migration strategy. Task 5 is deferred.
