---
title: "feat: Wire Temporal to AutonomousAgentService + nao-Inspired File-Based Context Sync"
type: feat
status: active
date: 2026-02-26
origin: specs/temporal-autonomous-agent-wiring.md
---

# Wire Temporal to AutonomousAgentService + nao-Inspired File-Based Context Sync

## Overview

Two complementary workstreams that strengthen KAI's agent harness:

**Workstream A** fixes latent model bugs and wires the Temporal worker's `chat` activity to use `AutonomousAgentService` instead of `AnalysisService`, giving Temporal-dispatched work the same 40+ tools available to CLI and REST API.

**Workstream B** adds nao-inspired file-based context materialization — a `kai context sync` CLI command that writes database schema, glossary, and instructions as searchable markdown files, plus two new agent tools (`search_context_files`, `read_context_file`) for cross-domain context discovery. A follow-up suggestions tool rounds out the UX improvements.

Together, these changes ensure all three entry points (CLI, API, Temporal) share the same agent harness, and the agent gains a new cross-domain search capability complementing Typesense's vector search.

## Problem Statement / Motivation

### Temporal Worker Gap

The Temporal worker's `chat` activity (`app/temporal/activities.py:121`) uses `AnalysisService.create_comprehensive_analysis()` — a simple fixed pipeline (Prompt -> SQL Gen -> Execute -> Analyze) that **completely bypasses** the autonomous agent harness. This means Temporal-dispatched work gets:

- No context platform tools (published instructions, glossary, semantic search)
- No 40+ agent tools (schema exploration, skills, memory, MDL, verified SQL cache)
- No DeepAgents multi-step reasoning with tool selection
- No memory context injection (Letta or Typesense)
- No telemetry tracking for asset reuse KPIs

Meanwhile, CLI (`kai query run`) and REST API (`POST /agent/sessions/{id}/tasks`) both use `AutonomousAgentService` and get the full tool harness.

### Context Discovery Gap

The agent currently discovers context through Typesense queries (per-tool, per-collection). There is no way to search **across** all context types at once. The nao project demonstrates that file-based context (markdown files on disk) enables:

- **Cross-domain grep** — find related instructions, glossary terms, and schema in one search
- **Git versionability** — track context changes over time
- **Implicit LLM caching** — Gemini's implicit caching already works for repeated file content (free, automatic)
- **Human readability** — context files are browseable and editable

### Pre-existing Model Bugs

Two latent bugs in `app/modules/autonomous_agent/models.py` would crash any caller of `AutonomousAgentService.execute()`:

1. **`AgentTask` missing `session_id` field** — `service.py:550` and `service.py:709` reference `task.session_id`, but `AgentTask` has no such field. CLI callers crash with `AttributeError`.

2. **`AgentResult.mission_id` required but never provided** — `mission_id: str` at line 196 has no default, but both `AgentResult(...)` constructions in `service.py:677` and `service.py:685` omit it. Raises `TypeError` at construction time.

## Proposed Solution

### Architecture Decisions

1. **Typesense stays** — File-based context COMPLEMENTS Typesense, doesn't replace it. Typesense handles vector/semantic search (memory, skills, verified SQL cache). Files handle cross-domain search and versionability.

2. **New activity alongside old** — Add `autonomous_chat` as a new Temporal activity. Keep `chat` for backward compatibility with in-flight workflows. Workflows migrate to `autonomous_chat` at their own pace.

3. **`CONTEXT_DIR` env var** — Context files written to a configurable directory (default `./context/`), resolved at sync time and injected into tools via `AutonomousAgentService` constructor.

4. **Gemini implicit caching is free** — No code changes needed. `ChatGoogleGenerativeAI` already benefits from Gemini's automatic input caching (>32K tokens, identical prefix). Explicit caching (90% discount) would require bypassing LangChain — deferred.

5. **`suggest_follow_ups` replaces heuristic `suggest_questions`** — The existing `suggestions_tools.py` generates heuristic suggestions from DataFrame columns. The new LLM-powered tool produces richer, contextual suggestions. Register only the new tool to avoid agent confusion from overlapping tools.

## Technical Approach

### Architecture

```
Entry Points (all three converge on AutonomousAgentService):

  CLI (kai query run)  ──┐
  REST API (/agent/*)  ──┼──> AutonomousAgentService.execute() / stream_execute()
  Temporal (autonomous_chat) ─┘         │
                                        ├── 40+ tools (SQL, schema, glossary, skills, memory, ...)
                                        ├── Context Platform tools (published assets)
                                        ├── File-based context tools (search_context_files, read_context_file)  [NEW]
                                        ├── suggest_follow_ups tool  [NEW]
                                        ├── Memory injection (Letta or Typesense)
                                        └── DeepAgents multi-step reasoning

  kai context sync ──> Materializes schema/glossary/instructions as markdown files
                       └── context/{db_alias}/tables/{table}/columns.md
                       └── context/{db_alias}/tables/{table}/preview.md
                       └── context/glossary/{term}.md
                       └── context/instructions/{rule_key}.md
```

### Implementation Phases

#### Phase 1: Fix Model Bugs (Blocking — must complete first)

**Task 1: Add `session_id` to `AgentTask`**
**File:** `app/modules/autonomous_agent/models.py:41`

```python
@dataclass
class AgentTask:
    """Task submitted to the autonomous agent."""
    id: str
    prompt: str
    db_connection_id: str
    session_id: str = ""          # NEW: defaults to empty, auto-filled
    mode: Literal["analysis", "query", "script", "full_autonomy"] = "full_autonomy"
    context: dict | None = None
    metadata: dict | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        if not self.session_id:
            self.session_id = self.id
```

Field ordering is valid: `session_id: str = ""` has a default and comes after the three required positional fields (`id`, `prompt`, `db_connection_id`). All existing callers use keyword arguments (verified: `cli/query.py:229`, `cli/query.py:345`, `api/endpoints.py:316`), so no positional argument corruption risk.

**Impact:** Zero breaking changes — all existing callers work as-is. CLI gets auto-fill from `task.id`. API continues passing explicit `session_id`. Temporal will pass `conversation_id`.

**Task 2: Make `AgentResult.mission_id` optional**
**File:** `app/modules/autonomous_agent/models.py:193`

```python
@dataclass
class AgentResult:
    """Result from autonomous agent execution."""
    task_id: str
    mission_id: str = ""          # CHANGE: was required, now defaults to ""
    status: Literal["completed", "failed", "partial"] = "completed"
    final_answer: str = ""
    # ... rest unchanged
```

**Impact:** All existing `AgentResult(task_id=..., status=..., ...)` calls stop crashing. No other changes needed.

**Tests for Phase 1:**
- `tests/modules/autonomous_agent/test_models.py`
  - `AgentTask()` without `session_id` auto-fills from `id`
  - `AgentTask(session_id="explicit")` preserves explicit value
  - `AgentResult()` without `mission_id` defaults to `""`
  - Keyword construction matches positional construction (no field ordering bugs)

---

#### Phase 2: Wire Temporal Activity (Core integration)

**Task 3: Wire `KaiActivities.chat()` to use `AutonomousAgentService`**
**File:** `app/temporal/activities.py:121`

Replace `AnalysisService` with `AutonomousAgentService`:

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

    # Convert AgentResult -> dict for Temporal serialization
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
- `mode="full_autonomy"` for best agent behavior
- Returns a simple dict (Temporal requires JSON-serializable return values)
- No streaming — Temporal activities are request/response
- No heartbeat needed yet (max runtime 180s, typical Temporal timeout is 300s+)

**Task 4: Add `autonomous_chat` activity for safe migration**
**File:** `app/temporal/activities.py`

Add as a new activity alongside `chat()` with the same implementation. This allows the control plane to switch workflow definitions gradually without breaking in-flight workflows.

**File:** `app/worker_main.py:278`

Register the new activity:

```python
worker = Worker(
    client,
    task_queue=config.task_queue,
    activities=[
        activities.store_connection,
        activities.test_connection,
        activities.scan_schema,
        activities.chat,                  # Keep old for backward compat
        activities.autonomous_chat,       # New: full agent harness
        activities.sync_config,
        activities.generate_mdl,
    ],
)
```

**Tests for Phase 2:**
- `tests/temporal/test_activities.py`
  - Mock `AutonomousAgentService.execute()`, verify `chat()` constructs correct `AgentTask`
  - Verify `conversation_id` maps to `session_id`
  - Verify `AgentResult` is serialized to dict correctly
  - Verify `autonomous_chat` has identical behavior to new `chat`
- Integration: `python -c "from app.temporal.activities import KaiActivities"` succeeds

---

#### Phase 3: File-Based Context Sync (New capability)

**Task 5: Create `kai context sync` CLI command**
**File:** `app/modules/autonomous_agent/cli/context.py` (add to existing command group)

```python
@context.command("sync")
@click.option("--db", "-d", required=True, help="Database connection alias")
@click.option("--output-dir", default=None, help="Output directory (default: CONTEXT_DIR or ./context)")
@click.option("--include-preview", is_flag=True, default=True, help="Include sample row previews")
@click.option("--preview-rows", type=int, default=5, help="Number of preview rows per table")
def sync_context(db, output_dir, include_preview, preview_rows):
    """Materialize database schema as searchable markdown files.

    Creates context files that the agent can search across all context types at once.
    Files are git-versionable and complement Typesense's vector search.

    Examples:

        kai context sync --db mydb

        kai context sync --db mydb --output-dir ./context --preview-rows 10
    """
```

**Directory structure produced:**

```
context/
  {db_alias}/
    tables/
      {table_name}/
        columns.md      # Schema + types + descriptions + column details
        preview.md      # 5 sample rows (truncated, no BLOBs)
    glossary/
      {term_key}.md     # Business term definitions
    instructions/
      {rule_key}.md     # SQL generation rules
```

**File format — `columns.md` example:**

```markdown
# Table: orders

**Description:** Customer order records with line items and payment status.

## Columns

| Column | Type | Description | Primary Key | Nullable |
|--------|------|-------------|-------------|----------|
| id | integer | Order identifier | Yes | No |
| customer_id | integer | FK to customers.id | No | No |
| order_date | timestamp | When order was placed | No | No |
| total_amount | decimal(10,2) | Order total in USD | No | No |
| status | varchar(20) | Order status | No | No |

## Low Cardinality Columns

- **status**: `pending`, `shipped`, `delivered`, `cancelled`, `returned`

## Foreign Keys

- `customer_id` -> `customers.id`
```

**Implementation details:**

- Uses `TableDescriptionService` for schema data (same source as existing scan)
- Uses `ContextAssetService` for glossary/instruction assets (published state only)
- Uses Jinja2 templates for rendering (customizable, stored in `app/modules/autonomous_agent/templates/context/`)
- **Delete-and-recreate strategy** — clears target directory before writing to prevent stale files
- `db_alias` sanitized to filesystem-safe name (alphanumeric + hyphens only)
- Column values truncated to 100 chars in preview, BLOBs excluded
- Large tables (200+ columns) generate a single `columns.md` — the agent tool will handle token budget

**New files:**

| File | Purpose |
|------|---------|
| `app/modules/autonomous_agent/cli/context.py` | Add `sync` command to existing group |
| `app/modules/autonomous_agent/context_sync.py` | Core sync logic (service layer) |
| `app/modules/autonomous_agent/templates/context/columns.md.j2` | Jinja2 template for columns |
| `app/modules/autonomous_agent/templates/context/preview.md.j2` | Jinja2 template for preview |
| `app/modules/autonomous_agent/templates/context/glossary.md.j2` | Jinja2 template for glossary |
| `app/modules/autonomous_agent/templates/context/instruction.md.j2` | Jinja2 template for instructions |

**Task 6: Create file-based context agent tools**
**File:** `app/modules/autonomous_agent/tools/context_file_tools.py` (new)

Two tools:

```python
def create_search_context_files_tool(context_dir: str, db_alias: str):
    """Create a tool to search across all context files."""

    def search_context_files(query: str, file_type: str | None = None) -> str:
        """Search for context across all schema, glossary, and instruction files.

        Performs text search across all context files for the current database.
        Use this to find related context across different types (tables, glossary,
        instructions) in a single search.

        Args:
            query: Search term or phrase (e.g. "revenue", "customer status").
            file_type: Optional filter: "tables", "glossary", "instructions".

        Returns:
            JSON with matching files and relevant line excerpts.
        """
```

```python
def create_read_context_file_tool(context_dir: str, db_alias: str):
    """Create a tool to read a specific context file."""

    def read_context_file(path: str) -> str:
        """Read a specific context file for detailed information.

        Use after search_context_files to read full details of a specific file.

        Args:
            path: Relative path within context directory
                  (e.g. "tables/orders/columns.md").

        Returns:
            Full file content as string, or error if not found.
        """
```

**Security:**
- `read_context_file` validates path stays within `context_dir/{db_alias}/` (no path traversal)
- `search_context_files` uses Python `pathlib` glob + string matching (no subprocess, no injection risk)
- Results scoped to current `db_alias` only (no cross-tenant leakage)

**Wire into `_build_tools()`:**
**File:** `app/modules/autonomous_agent/service.py:375`

```python
# File-based context tools (if context directory exists)
context_dir = os.environ.get("CONTEXT_DIR", "./context")
db_alias = getattr(self.db_connection, 'alias', '') or self.db_connection.id
if os.path.isdir(os.path.join(context_dir, db_alias)):
    from app.modules.autonomous_agent.tools.context_file_tools import (
        create_search_context_files_tool,
        create_read_context_file_tool,
    )
    tools.append(create_search_context_files_tool(context_dir, db_alias))
    tools.append(create_read_context_file_tool(context_dir, db_alias))
```

Conditional registration: tools only appear if `context/{db_alias}/` exists. This means `kai context sync` must run before the agent benefits from file-based context.

**Tests for Phase 3:**
- `tests/modules/autonomous_agent/test_context_sync.py`
  - Sync creates expected directory structure
  - Stale files are cleaned up on re-sync
  - `db_alias` sanitization (special chars, slashes)
  - Large table handling (200+ columns)
  - Preview row truncation and BLOB exclusion
- `tests/modules/autonomous_agent/tools/test_context_file_tools.py`
  - `search_context_files` finds matches across file types
  - `read_context_file` reads correct file content
  - Path traversal attack blocked
  - Returns empty gracefully when no context dir exists
  - `file_type` filter works correctly

---

#### Phase 4: Follow-up Suggestions Tool (UX enhancement)

**Task 7: Create `suggest_follow_ups` tool**
**File:** `app/modules/autonomous_agent/tools/followup_tools.py` (new)

```python
def create_suggest_follow_ups_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create a tool that generates contextual follow-up questions."""

    def suggest_follow_ups(
        original_question: str,
        analysis_summary: str,
        data_columns: list[str] | None = None,
    ) -> str:
        """Generate 3-5 contextual follow-up questions based on the analysis.

        Call this after completing an analysis to suggest next steps.
        Questions should help the user drill deeper, compare, or explore
        related dimensions.

        Args:
            original_question: The user's original question.
            analysis_summary: Brief summary of what was found.
            data_columns: Optional list of column names from the query results.

        Returns:
            JSON with suggested follow-up questions and categories.
        """
```

**Categories:** `drill_down`, `compare`, `trend`, `filter`, `aggregate` (matches existing `SuggestedQuestion` model in `models.py:185`).

**Replaces:** `suggest_questions` from `suggestions_tools.py`. Remove the old heuristic tool from `_build_tools()` and register the new LLM-powered one instead.

**Stream integration:** The follow-up suggestions appear in the agent's final answer using the existing `<suggestions>` XML tag pattern that the streaming parser already handles (`service.py:17` `TagStreamParser`).

**CLI rendering:** Add handler for suggestions in `cli/query.py:32` `_render_stream`:

```python
elif event["type"] == "suggestions":
    console.print("\n[bold cyan]Suggested follow-ups:[/bold cyan]")
    for q in event.get("questions", []):
        console.print(f"  [dim]>[/dim] {q['question']}")
```

**Tests for Phase 4:**
- `tests/modules/autonomous_agent/tools/test_followup_tools.py`
  - Tool returns valid JSON with 3-5 questions
  - Each question has `question`, `category`, `rationale` fields
  - Categories are valid enum values

---

## System-Wide Impact

### Interaction Graph

```
Temporal Workflow dispatches chat activity
  → KaiActivities.chat() / autonomous_chat()
    → AutonomousAgentService.__init__() (creates Storage, SQLDatabase)
      → AutonomousAgentService.execute(task)
        → _build_tools() (40+ tools including new context file tools)
        → create_agent() (LangGraph DeepAgent)
        → Memory injection (Letta or Typesense)
        → agent.ainvoke() (multi-step reasoning with tool calls)
          → Tool calls trigger: SQL queries, schema lookups, context searches
        → Memory capture (Letta or legacy)
      → Returns AgentResult
    → Serializes to dict for Temporal
  → Workflow receives result dict
```

### Error & Failure Propagation

| Error Source | Current Behavior | After Change |
|---|---|---|
| `AgentTask` missing `session_id` | `AttributeError` crash | Auto-filled from `task.id` |
| `AgentResult` missing `mission_id` | `TypeError` crash | Defaults to `""` |
| `connection_id` not found | `AnalysisService` returns error dict | `ValueError` raised, Temporal retries |
| Agent execution timeout (180s) | N/A (AnalysisService is fast) | Agent stops, returns partial result |
| Context file not found | N/A | Tool returns `{"success": false, "error": "..."}` |
| Stale context files | N/A | Delete-and-recreate on sync |

### State Lifecycle Risks

- **Temporal retries create new sessions:** If `conversation_id` is `None`, each retry generates a new `session_id = f"temporal_{uuid.uuid4().hex[:8]}"`. Memory writes may duplicate. **Mitigation:** Document that control plane should pass stable `conversation_id` (e.g., Temporal workflow ID).
- **In-memory checkpointer is ephemeral:** Multi-turn Temporal conversations do NOT resume LangGraph checkpoint state — only semantic memory via Letta/Typesense is preserved. **Mitigation:** Acceptable for v1. Future: PostgreSQL-backed checkpointer.
- **Context files stale after schema change:** If tables are added/dropped between syncs, context files are stale. **Mitigation:** Delete-and-recreate strategy. Document that `kai context sync` should run after schema changes.

### API Surface Parity

After this change, all three surfaces share the same code path:

| Surface | Service | Tools | Memory | Streaming |
|---|---|---|---|---|
| CLI | AutonomousAgentService | 40+ | Yes | Yes (stream_execute) |
| REST API | AutonomousAgentService | 40+ | Yes | Yes (SSE) |
| Temporal | AutonomousAgentService | 40+ | Yes | No (execute only) |

### Integration Test Scenarios

1. **Temporal chat with full agent harness:** Dispatch `autonomous_chat` via Temporal, verify agent uses schema tools and context platform tools (check logs for tool call events).
2. **Context sync → agent search:** Run `kai context sync --db mydb`, then ask agent a question — verify `search_context_files` appears in tool call logs.
3. **Follow-up suggestions in CLI:** Run `kai query run "..."` — verify suggestions rendered after analysis.
4. **Temporal retry idempotency:** Dispatch `autonomous_chat` with `conversation_id="stable-123"`, kill mid-execution, retry — verify same `session_id` used.
5. **Stale context cleanup:** Sync, drop a table, re-sync — verify old table's files are removed.

## Acceptance Criteria

### Functional Requirements

- [ ] `AgentTask()` without `session_id` auto-fills from `id` via `__post_init__`
- [ ] `AgentResult()` without `mission_id` defaults to `""`
- [ ] `KaiActivities.chat()` uses `AutonomousAgentService.execute()` instead of `AnalysisService`
- [ ] `autonomous_chat` activity registered in `worker_main.py` and callable via Temporal
- [ ] `kai context sync --db {alias}` creates expected directory structure with markdown files
- [ ] Context files include: columns.md (schema), preview.md (sample rows), glossary/*.md, instructions/*.md
- [ ] `search_context_files` tool finds matches across all context file types
- [ ] `read_context_file` tool reads specific context files with path traversal protection
- [ ] `suggest_follow_ups` tool generates 3-5 contextual questions after analysis
- [ ] Follow-up suggestions render in CLI output
- [ ] Old `chat` activity still works for backward compatibility
- [ ] All three entry points (CLI, API, Temporal) use `AutonomousAgentService`

### Non-Functional Requirements

- [ ] No new dependencies added (Jinja2 already in project via LangChain)
- [ ] Context sync handles 500+ tables without timeout
- [ ] `search_context_files` uses Python pathlib (no subprocess, no shell injection risk)
- [ ] `read_context_file` validates path stays within allowed directory
- [ ] Temporal activity works in Docker container (context dir configurable via `CONTEXT_DIR` env var)

### Quality Gates

- [ ] Unit tests for all model changes, new tools, and sync logic
- [ ] Integration test: `python -c "from app.temporal.activities import KaiActivities"` succeeds
- [ ] Existing test suite passes (63 passing, no regressions)
- [ ] Manual E2E: Start Temporal worker, dispatch `autonomous_chat`, verify agent tools used in logs

## Success Metrics

- **Feature parity:** Temporal worker uses same tool set as CLI/API (40+ tools)
- **Context coverage:** `kai context sync` materializes all table schemas, published glossary terms, and published instructions
- **Cross-domain search:** Agent can find related context across tables/glossary/instructions in a single tool call
- **Follow-up engagement:** Agent generates contextual follow-up suggestions after every analysis

## Dependencies & Prerequisites

| Dependency | Status | Notes |
|---|---|---|
| Context platform tools in `_build_tools()` | Done | Committed in `59a6581` |
| `context_platform_tools.py` | Done | 4 tool factories created |
| Typesense running | Required | For all Storage operations |
| Temporal server | Required | For Phase 2 testing |
| Jinja2 | Available | Already in dependencies via LangChain |

## Risk Analysis & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Temporal return shape breaks control plane | Medium | High | Add `autonomous_chat` alongside `chat`, don't replace inline |
| Context files grow too large for LLM context | Low | Medium | Truncate preview rows, limit column count per file |
| Stale context files mislead agent | Medium | Medium | Delete-and-recreate on sync, document re-sync requirement |
| Concurrent sync race condition | Low | Low | Single-writer assumption, document in CLI help |
| `session_id` field ordering breaks positional callers | Very Low | High | All callers verified to use keyword args |

## Files Changed Summary

| File | Change | Phase | Risk |
|------|--------|-------|------|
| `app/modules/autonomous_agent/models.py` | Add `session_id` to `AgentTask`, default `mission_id` in `AgentResult` | 1 | Low |
| `app/temporal/activities.py` | Wire `chat` + add `autonomous_chat` using `AutonomousAgentService` | 2 | Medium |
| `app/worker_main.py` | Register `autonomous_chat` activity | 2 | Low |
| `app/modules/autonomous_agent/cli/context.py` | Add `sync` command | 3 | Low |
| `app/modules/autonomous_agent/context_sync.py` | Core sync logic (new) | 3 | Low |
| `app/modules/autonomous_agent/templates/context/*.md.j2` | Jinja2 templates (new) | 3 | Low |
| `app/modules/autonomous_agent/tools/context_file_tools.py` | `search_context_files` + `read_context_file` (new) | 3 | Low |
| `app/modules/autonomous_agent/service.py` | Wire new tools into `_build_tools()` | 3 | Low |
| `app/modules/autonomous_agent/tools/followup_tools.py` | `suggest_follow_ups` tool (new) | 4 | Low |
| `app/modules/autonomous_agent/cli/query.py` | Add suggestions rendering | 4 | Low |
| `tests/modules/autonomous_agent/test_models.py` | Model fix tests | 1 | None |
| `tests/temporal/test_activities.py` | Activity wiring tests | 2 | None |
| `tests/modules/autonomous_agent/test_context_sync.py` | Sync logic tests | 3 | None |
| `tests/modules/autonomous_agent/tools/test_context_file_tools.py` | File tool tests | 3 | None |
| `tests/modules/autonomous_agent/tools/test_followup_tools.py` | Follow-up tool tests | 4 | None |

## Execution Order

```
Phase 1: Fix Model Bugs (BLOCKING)
  Task 1: AgentTask.session_id ──┐
  Task 2: AgentResult.mission_id ─┤
                                  ↓
Phase 2: Wire Temporal Activity
  Task 3: Wire chat() ──────────┐
  Task 4: Add autonomous_chat() ─┤
                                  ↓
Phase 3: File-Based Context Sync (PARALLEL with Phase 2 after Phase 1)
  Task 5: kai context sync CLI ─┐
  Task 6: Agent tools ───────────┤
                                  ↓
Phase 4: Follow-up Suggestions (PARALLEL with Phase 3)
  Task 7: suggest_follow_ups tool
```

Phases 3 and 4 can proceed in parallel with Phase 2 after Phase 1 completes. All phases can be done by a single developer.

## Future Considerations

- **PostgreSQL-backed checkpointer** for Temporal: Enables true multi-turn conversation resumption across worker restarts
- **Temporal heartbeat** for long-running agent executions: Add `activity.heartbeat()` calls if max runtime exceeds 60s
- **Explicit Gemini caching** (90% discount): Requires direct `google.genai.Client().caches.create()`, bypassing LangChain. Defer unless cost savings justify the complexity.
- **Auto-sync on schema change** via Temporal workflow: Trigger `kai context sync` automatically when `scan_schema` activity completes
- **Hybrid search across files and Typesense**: Combine file-based grep results with Typesense vector search for best-of-both-worlds context retrieval

## Sources & References

### Origin

- **Spec document:** [specs/temporal-autonomous-agent-wiring.md](../../specs/temporal-autonomous-agent-wiring.md) — Temporal wiring tasks 1-4
- **nao analysis:** Research session comparing nao's file-based context approach with KAI's Typesense architecture

### Internal References

- `app/temporal/activities.py:121` — Current `chat()` activity using `AnalysisService`
- `app/modules/autonomous_agent/service.py:375` — `_build_tools()` method (tool registration)
- `app/modules/autonomous_agent/service.py:545` — `execute()` method (references `task.session_id`)
- `app/modules/autonomous_agent/models.py:41` — `AgentTask` dataclass (missing `session_id`)
- `app/modules/autonomous_agent/models.py:193` — `AgentResult` dataclass (required `mission_id`)
- `app/modules/autonomous_agent/cli/context.py` — Existing context CLI commands
- `app/modules/autonomous_agent/tools/context_platform_tools.py` — Context platform tools (already integrated)
- `app/modules/autonomous_agent/tools/suggestions_tools.py` — Existing heuristic suggestions (to be replaced)
- `app/worker_main.py:275` — Worker activity registration

### External References

- nao project: `~/project/self/bmad-new/nao` — File-based context sync, Jinja2 templates, grep tool
- Gemini implicit caching: Automatic for repeated content >32K tokens, no code changes needed
