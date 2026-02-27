---
title: "feat: Wire Temporal to AutonomousAgentService + File-Based Context Sync"
type: feat
date: 2026-02-26
status: ready
source: docs/plans/2026-02-26-feat-temporal-agent-wiring-and-context-sync-plan.md
---

# Plan: Wire Temporal to AutonomousAgentService + File-Based Context Sync

## Task Description

Two complementary workstreams to strengthen KAI's agent harness:

**Workstream A (Temporal Wiring):** Fix latent model bugs in `AgentTask` and `AgentResult`, then wire the Temporal worker's `chat` activity to use `AutonomousAgentService` instead of `AnalysisService`. This gives Temporal-dispatched work the same 40+ tools available to CLI and REST API. Add `autonomous_chat` as a new activity alongside `chat` for safe migration.

**Workstream B (File-Based Context Sync):** Add a `kai context sync` CLI command that materializes database schema, glossary, and instructions as searchable markdown files. Create two new agent tools (`search_context_files`, `read_context_file`) for cross-domain context discovery. Add a `suggest_follow_ups` tool to replace the existing heuristic suggestion tool.

Key architecture decisions:
- Typesense stays — file-based context complements it, doesn't replace it
- New `autonomous_chat` activity alongside old `chat` for backward compatibility
- `CONTEXT_DIR` env var (default `./context/`) for Docker portability
- Delete-and-recreate strategy for context file sync (prevents stale files)
- Python `pathlib` for search (no subprocess, no shell injection)

## Objective

1. All three entry points (CLI, REST API, Temporal Worker) use `AutonomousAgentService` with the full 40+ tool harness
2. Agent gains cross-domain context search capability via file-based context tools
3. Follow-up suggestions improve user engagement after analysis
4. Zero breaking changes to existing callers

## Relevant Files

### Existing Files to Modify

- `app/modules/autonomous_agent/models.py` — Add `session_id` to `AgentTask` (line 41), default `mission_id` in `AgentResult` (line 193)
- `app/temporal/activities.py` — Wire `chat()` to `AutonomousAgentService` (line 121), add `autonomous_chat` activity
- `app/worker_main.py` — Register `autonomous_chat` activity (line 278)
- `app/modules/autonomous_agent/service.py` — Wire new tools into `_build_tools()` (line 375)
- `app/modules/autonomous_agent/cli/context.py` — Add `sync` command to existing context group
- `app/modules/autonomous_agent/cli/query.py` — Add suggestions rendering in `_render_stream`
- `app/modules/autonomous_agent/tools/__init__.py` — Export new tools

### New Files to Create

- `app/modules/autonomous_agent/context_sync.py` — Core sync logic (service layer)
- `app/modules/autonomous_agent/templates/context/columns.md.j2` — Jinja2 template for table columns
- `app/modules/autonomous_agent/templates/context/preview.md.j2` — Jinja2 template for sample rows
- `app/modules/autonomous_agent/templates/context/glossary.md.j2` — Jinja2 template for glossary terms
- `app/modules/autonomous_agent/templates/context/instruction.md.j2` — Jinja2 template for instructions
- `app/modules/autonomous_agent/tools/context_file_tools.py` — `search_context_files` + `read_context_file` tools
- `app/modules/autonomous_agent/tools/followup_tools.py` — `suggest_follow_ups` tool

### Test Files to Create

- `tests/modules/autonomous_agent/test_models_fix.py` — Model fix unit tests
- `tests/temporal/test_activities_wiring.py` — Activity wiring tests
- `tests/modules/autonomous_agent/test_context_sync.py` — Sync logic tests
- `tests/modules/autonomous_agent/tools/test_context_file_tools.py` — File tool tests
- `tests/modules/autonomous_agent/tools/test_followup_tools.py` — Follow-up tool tests

## Step by Step Tasks

### Phase 1: Fix Model Bugs (BLOCKING — must complete first)

### 1. Fix `AgentTask` model — add `session_id` field
- **Task ID:** task-1-agenttask-session-id
- **Depends On:** none
- **Assigned To:** builder-backend
- **Agent Type:** general-purpose
- **Parallel:** false
- **File:** `app/modules/autonomous_agent/models.py`
- **What to do:**
  - Add `session_id: str = ""` field to `AgentTask` dataclass AFTER `db_connection_id` and BEFORE `mode`
  - Add `__post_init__` method: if `not self.session_id`, set `self.session_id = self.id`
  - Field ordering is critical: `session_id` has a default, so it must come after the 3 required positional fields (`id`, `prompt`, `db_connection_id`)
- **Code:**
  ```python
  @dataclass
  class AgentTask:
      """Task submitted to the autonomous agent."""
      id: str
      prompt: str
      db_connection_id: str
      session_id: str = ""
      mode: Literal["analysis", "query", "script", "full_autonomy"] = "full_autonomy"
      context: dict | None = None
      metadata: dict | None = None
      created_at: str = field(default_factory=lambda: datetime.now().isoformat())

      def __post_init__(self):
          if not self.session_id:
              self.session_id = self.id
  ```
- **Acceptance Criteria:**
  - [ ] `AgentTask(id="test", prompt="q", db_connection_id="c")` has `session_id == "test"`
  - [ ] `AgentTask(id="test", prompt="q", db_connection_id="c", session_id="explicit")` has `session_id == "explicit"`
  - [ ] No existing callers break (all use keyword arguments)

### 2. Fix `AgentResult` model — make `mission_id` optional
- **Task ID:** task-2-agentresult-mission-id
- **Depends On:** none
- **Assigned To:** builder-backend
- **Agent Type:** general-purpose
- **Parallel:** true (with Task 1)
- **File:** `app/modules/autonomous_agent/models.py`
- **What to do:**
  - Change `mission_id: str` (required positional) to `mission_id: str = ""` (optional with default)
  - This must come AFTER `task_id` (required) to maintain valid dataclass ordering
- **Code:**
  ```python
  @dataclass
  class AgentResult:
      """Result from autonomous agent execution."""
      task_id: str
      mission_id: str = ""          # was required, now defaults to ""
      status: Literal["completed", "failed", "partial"] = "completed"
      final_answer: str = ""
      # ... rest unchanged
  ```
- **Acceptance Criteria:**
  - [ ] `AgentResult(task_id="t1", status="completed", final_answer="ans")` works without `mission_id`
  - [ ] `AgentResult(task_id="t1", mission_id="m1")` preserves explicit value

### 3. Write unit tests for model fixes
- **Task ID:** task-3-model-tests
- **Depends On:** task-1-agenttask-session-id, task-2-agentresult-mission-id
- **Assigned To:** builder-backend
- **Agent Type:** general-purpose
- **Parallel:** false
- **File:** `tests/modules/autonomous_agent/test_models_fix.py`
- **What to do:**
  - Test `AgentTask` session_id auto-fill from `id`
  - Test `AgentTask` explicit session_id preservation
  - Test `AgentResult` without mission_id defaults to ""
  - Test `AgentResult` with explicit mission_id
  - Test keyword vs positional construction (verify no field ordering bugs)
  - Run tests: `uv run pytest tests/modules/autonomous_agent/test_models_fix.py -v`
- **Acceptance Criteria:**
  - [ ] All tests pass
  - [ ] No regressions in existing test suite

---

### Phase 2: Wire Temporal Activity

### 4. Wire `KaiActivities.chat()` to use `AutonomousAgentService`
- **Task ID:** task-4-wire-chat
- **Depends On:** task-1-agenttask-session-id, task-2-agentresult-mission-id
- **Assigned To:** builder-backend
- **Agent Type:** general-purpose
- **Parallel:** false
- **File:** `app/temporal/activities.py`
- **What to do:**
  - Replace the `chat` method body (line 121-138) to use `AutonomousAgentService` instead of `AnalysisService`
  - Import: `AutonomousAgentService`, `AgentTask`, `SQLDatabase`, `LLMConfig`, `DatabaseConnectionRepository`
  - Resolve `db_connection` from `connection_id` via `DatabaseConnectionRepository`
  - Create `LLMConfig` from `self.settings.CHAT_FAMILY` and `self.settings.CHAT_MODEL`
  - Create `SQLDatabase.get_sql_engine(db_connection, False)`
  - Create `AutonomousAgentService(db_connection, database, storage, llm_config)`
  - Map `conversation_id` to `session_id` (fallback: `f"temporal_{uuid.uuid4().hex[:8]}"`)
  - Create `AgentTask` with `mode="full_autonomy"`, `metadata={"source": "temporal_worker"}`
  - Call `await service.execute(task)`
  - Return dict with: `task_id`, `status`, `final_answer`, `sql_queries`, `execution_time_ms`, `error`, `mission_id`, `stages_completed`
- **Acceptance Criteria:**
  - [ ] `chat()` now uses `AutonomousAgentService.execute()` instead of `AnalysisService`
  - [ ] `conversation_id` correctly maps to `session_id`
  - [ ] Returns JSON-serializable dict

### 5. Add `autonomous_chat` activity for safe migration
- **Task ID:** task-5-autonomous-chat
- **Depends On:** task-4-wire-chat
- **Assigned To:** builder-backend
- **Agent Type:** general-purpose
- **Parallel:** false
- **Files:** `app/temporal/activities.py`, `app/worker_main.py`
- **What to do:**
  - Add `autonomous_chat` method to `KaiActivities` with `@activity.defn` decorator
  - Same implementation as the new `chat()` — identical body
  - In `app/worker_main.py` line 278, add `activities.autonomous_chat` to the worker activity list
  - Keep `activities.chat` in the list for backward compatibility
- **Acceptance Criteria:**
  - [ ] `autonomous_chat` activity registered and callable
  - [ ] Old `chat` activity still works
  - [ ] `python -c "from app.temporal.activities import KaiActivities; print('OK')"` succeeds

### 6. Write tests for Temporal activity wiring
- **Task ID:** task-6-temporal-tests
- **Depends On:** task-5-autonomous-chat
- **Assigned To:** builder-backend
- **Agent Type:** general-purpose
- **Parallel:** false
- **File:** `tests/temporal/test_activities_wiring.py`
- **What to do:**
  - Mock `AutonomousAgentService.execute()` to return a known `AgentResult`
  - Mock `DatabaseConnectionRepository.find_by_id()` to return a test connection
  - Mock `SQLDatabase.get_sql_engine()` to return a mock database
  - Test `chat()` constructs correct `AgentTask` with session_id from conversation_id
  - Test `chat()` serializes `AgentResult` to dict correctly
  - Test `autonomous_chat()` has identical behavior
  - Test `chat()` raises `ValueError` when connection_id not found
  - Run: `uv run pytest tests/temporal/test_activities_wiring.py -v`
- **Acceptance Criteria:**
  - [ ] All tests pass
  - [ ] Import integration test passes

---

### Phase 3: File-Based Context Sync (can start after Phase 1)

### 7. Create context sync service
- **Task ID:** task-7-context-sync-service
- **Depends On:** task-1-agenttask-session-id (only needs Phase 1 done)
- **Assigned To:** builder-context
- **Agent Type:** general-purpose
- **Parallel:** true (with Phase 2 tasks)
- **Files:** `app/modules/autonomous_agent/context_sync.py`, Jinja2 templates
- **What to do:**
  - Create `ContextSyncService` class with `sync(db_connection_id, output_dir, include_preview, preview_rows)` method
  - Use `TableDescriptionService` to get schema data
  - Use `ContextAssetService` to get published glossary and instruction assets
  - Create Jinja2 templates in `app/modules/autonomous_agent/templates/context/`:
    - `columns.md.j2` — Table name, description, columns table (name, type, description, PK, nullable), low cardinality columns, foreign keys
    - `preview.md.j2` — Table name, sample rows as markdown table (5 rows default, values truncated to 100 chars, BLOBs excluded)
    - `glossary.md.j2` — Term name, definition, related tables, examples
    - `instruction.md.j2` — Rule name, content, conditions, priority
  - Delete-and-recreate strategy: clear `{output_dir}/{db_alias}/` before writing
  - Sanitize `db_alias` to filesystem-safe name: `re.sub(r'[^a-zA-Z0-9_-]', '-', alias)`
  - Directory structure:
    ```
    context/{db_alias}/tables/{table_name}/columns.md
    context/{db_alias}/tables/{table_name}/preview.md
    context/{db_alias}/glossary/{term_key}.md
    context/{db_alias}/instructions/{rule_key}.md
    ```
  - For preview rows, use `SQLDatabase.run_sql(f"SELECT * FROM {table} LIMIT {preview_rows}")` with proper quoting
- **Acceptance Criteria:**
  - [ ] Sync creates expected directory structure
  - [ ] Templates render correct markdown
  - [ ] Stale files removed on re-sync
  - [ ] `db_alias` sanitized (no slashes, spaces, special chars)
  - [ ] Large tables (200+ columns) handled without error
  - [ ] Preview rows truncated, BLOBs excluded

### 8. Add `kai context sync` CLI command
- **Task ID:** task-8-context-sync-cli
- **Depends On:** task-7-context-sync-service
- **Assigned To:** builder-context
- **Agent Type:** general-purpose
- **Parallel:** false
- **File:** `app/modules/autonomous_agent/cli/context.py`
- **What to do:**
  - Add `sync` command to existing `@context.group()` in `context.py`
  - Options: `--db/-d` (required), `--output-dir` (default from `CONTEXT_DIR` env var or `./context`), `--include-preview` (flag, default True), `--preview-rows` (int, default 5)
  - Resolve `db` via `_resolve_db_identifier()`
  - Call `ContextSyncService.sync()`
  - Display progress with Rich console: table count, file count, glossary count, instruction count
  - Show total time elapsed
- **Acceptance Criteria:**
  - [ ] `kai context sync --db mydb` creates files in `./context/mydb/`
  - [ ] `kai context sync --db mydb --output-dir /tmp/ctx` writes to specified dir
  - [ ] Progress output shows counts

### 9. Create file-based context agent tools
- **Task ID:** task-9-context-file-tools
- **Depends On:** task-7-context-sync-service
- **Assigned To:** builder-context
- **Agent Type:** general-purpose
- **Parallel:** true (with Task 8)
- **Files:** `app/modules/autonomous_agent/tools/context_file_tools.py`, `app/modules/autonomous_agent/service.py`
- **What to do:**
  - Create `create_search_context_files_tool(context_dir, db_alias)`:
    - Uses `pathlib.Path.rglob("*.md")` to find all markdown files under `context_dir/db_alias/`
    - Reads each file and searches for `query` string (case-insensitive)
    - Returns JSON with: matching file paths, line numbers, excerpts (3 lines around match)
    - Optional `file_type` filter: "tables", "glossary", "instructions"
    - Limit results to 20 matches
  - Create `create_read_context_file_tool(context_dir, db_alias)`:
    - Reads a file at `context_dir/db_alias/{path}`
    - **Security:** Resolve path and verify it starts with `context_dir/db_alias/` (no `..` traversal)
    - Returns file content as string, or error JSON if not found
  - Wire into `_build_tools()` in `service.py` (line ~437, after context platform tools):
    - Check if `os.path.isdir(os.path.join(context_dir, db_alias))`
    - Only register tools if context directory exists
    - `context_dir = os.environ.get("CONTEXT_DIR", "./context")`
    - `db_alias = getattr(self.db_connection, 'alias', '') or self.db_connection.id`
  - Export new tools from `tools/__init__.py`
- **Acceptance Criteria:**
  - [ ] `search_context_files("revenue")` finds matches across tables, glossary, instructions
  - [ ] `read_context_file("tables/orders/columns.md")` returns file content
  - [ ] `read_context_file("../../etc/passwd")` is blocked (path traversal)
  - [ ] Tools not registered when context dir doesn't exist
  - [ ] Results scoped to current `db_alias` only

### 10. Write tests for context sync and file tools
- **Task ID:** task-10-context-tests
- **Depends On:** task-8-context-sync-cli, task-9-context-file-tools
- **Assigned To:** builder-context
- **Agent Type:** general-purpose
- **Parallel:** false
- **Files:** `tests/modules/autonomous_agent/test_context_sync.py`, `tests/modules/autonomous_agent/tools/test_context_file_tools.py`
- **What to do:**
  - Test sync service creates correct directory structure with tmp dir
  - Test stale file cleanup on re-sync
  - Test `db_alias` sanitization
  - Test `search_context_files` finds matches across types
  - Test `read_context_file` reads correct content
  - Test path traversal attack is blocked
  - Test empty context dir returns graceful empty result
  - Run: `uv run pytest tests/modules/autonomous_agent/test_context_sync.py tests/modules/autonomous_agent/tools/test_context_file_tools.py -v`
- **Acceptance Criteria:**
  - [ ] All tests pass
  - [ ] No regressions

---

### Phase 4: Follow-up Suggestions

### 11. Create `suggest_follow_ups` tool
- **Task ID:** task-11-followup-tool
- **Depends On:** task-1-agenttask-session-id (only needs Phase 1 done)
- **Assigned To:** builder-ux
- **Agent Type:** general-purpose
- **Parallel:** true (with Phase 2 and Phase 3)
- **Files:** `app/modules/autonomous_agent/tools/followup_tools.py`, `app/modules/autonomous_agent/service.py`
- **What to do:**
  - Create `create_suggest_follow_ups_tool(db_connection, storage)`:
    - Args: `original_question: str`, `analysis_summary: str`, `data_columns: list[str] | None = None`
    - Generates 3-5 follow-up questions using LLM call
    - Categories: `drill_down`, `compare`, `trend`, `filter`, `aggregate` (matches `SuggestedQuestion` model in `models.py:185`)
    - Returns JSON with `questions` array, each with `question`, `category`, `rationale`
    - Uses `ChatModel().get_model()` for a lightweight LLM call
  - Wire into `_build_tools()` in `service.py`
  - **Replace** `create_suggestions_tool` (from `suggestions_tools.py`) registration in `_build_tools()` with the new tool (if it's currently registered)
  - Export from `tools/__init__.py`
- **Acceptance Criteria:**
  - [ ] Tool returns valid JSON with 3-5 questions
  - [ ] Each question has `question`, `category`, `rationale`
  - [ ] Categories are valid enum values

### 12. Add CLI rendering for follow-up suggestions
- **Task ID:** task-12-cli-suggestions
- **Depends On:** task-11-followup-tool
- **Assigned To:** builder-ux
- **Agent Type:** general-purpose
- **Parallel:** false
- **File:** `app/modules/autonomous_agent/cli/query.py`
- **What to do:**
  - In the `_render_stream` function (around line 32), add handler for `suggestions` event type
  - Render suggestions with Rich formatting:
    ```python
    elif event["type"] == "suggestions":
        console.print("\n[bold cyan]Suggested follow-ups:[/bold cyan]")
        for q in event.get("questions", []):
            console.print(f"  [dim]>[/dim] {q['question']}")
    ```
- **Acceptance Criteria:**
  - [ ] Suggestions render in CLI after analysis
  - [ ] Graceful handling when no suggestions present

### 13. Write tests for follow-up tools
- **Task ID:** task-13-followup-tests
- **Depends On:** task-11-followup-tool
- **Assigned To:** builder-ux
- **Agent Type:** general-purpose
- **Parallel:** true (with Task 12)
- **File:** `tests/modules/autonomous_agent/tools/test_followup_tools.py`
- **What to do:**
  - Mock LLM call, verify tool returns correct JSON structure
  - Test 3-5 questions generated
  - Test categories are valid
  - Run: `uv run pytest tests/modules/autonomous_agent/tools/test_followup_tools.py -v`
- **Acceptance Criteria:**
  - [ ] All tests pass

---

### Phase 5: Final Validation

### 14. Run full test suite and import check
- **Task ID:** task-14-final-validation
- **Depends On:** task-3-model-tests, task-6-temporal-tests, task-10-context-tests, task-13-followup-tests
- **Assigned To:** builder-backend
- **Agent Type:** general-purpose
- **Parallel:** false
- **What to do:**
  - Run: `uv run pytest -x --tb=short` (full test suite, stop on first failure)
  - Run: `python -c "from app.temporal.activities import KaiActivities; print('Import OK')"`
  - Run: `python -c "from app.modules.autonomous_agent.service import AutonomousAgentService; print('Service OK')"`
  - Run: `python -c "from app.modules.autonomous_agent.context_sync import ContextSyncService; print('Sync OK')"`
  - Verify no regressions (baseline: 63 passing)
- **Acceptance Criteria:**
  - [ ] All imports succeed
  - [ ] Test suite passes with no regressions
  - [ ] All new tests pass

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

- [ ] No new dependencies added (Jinja2 already available via LangChain)
- [ ] Context sync handles 500+ tables without timeout
- [ ] `search_context_files` uses Python pathlib (no subprocess, no shell injection risk)
- [ ] `read_context_file` validates path stays within allowed directory
- [ ] Temporal activity works in Docker container (`CONTEXT_DIR` env var)

### Quality Gates

- [ ] Unit tests for all model changes, new tools, and sync logic
- [ ] Integration test: import checks succeed
- [ ] Existing test suite passes (63+ passing, no regressions)

## Team Orchestration

As the team lead, you orchestrate three builders working in parallel after Phase 1 completes.

### Execution Strategy

```
Phase 1 (Sequential - BLOCKING):
  builder-backend: Task 1 + Task 2 + Task 3
      ↓ (Phase 1 complete — unblocks all)
Phase 2-4 (PARALLEL):
  builder-backend: Task 4 → Task 5 → Task 6    (Temporal wiring)
  builder-context:  Task 7 → Task 8 + Task 9 → Task 10  (Context sync)
  builder-ux:       Task 11 → Task 12 + Task 13  (Follow-up suggestions)
      ↓ (All complete)
Phase 5 (Sequential):
  builder-backend: Task 14  (Final validation)
```

### Team Members

#### Backend Builder
- **Name:** builder-backend
- **Role:** backend
- **Agent Type:** general-purpose
- **Model:** sonnet
- **Resume:** true
- **Responsibilities:** Model bug fixes (Tasks 1-3), Temporal activity wiring (Tasks 4-6), final validation (Task 14)

#### Context Builder
- **Name:** builder-context
- **Role:** backend
- **Agent Type:** general-purpose
- **Model:** sonnet
- **Resume:** true
- **Responsibilities:** Context sync service (Task 7), CLI command (Task 8), file-based context tools (Task 9), context tests (Task 10)

#### UX Builder
- **Name:** builder-ux
- **Role:** backend
- **Agent Type:** general-purpose
- **Model:** sonnet
- **Resume:** true
- **Responsibilities:** Follow-up suggestions tool (Task 11), CLI rendering (Task 12), follow-up tests (Task 13)

## Validation Commands

```bash
# Phase 1: Model fix tests
uv run pytest tests/modules/autonomous_agent/test_models_fix.py -v

# Phase 2: Temporal activity tests
uv run pytest tests/temporal/test_activities_wiring.py -v

# Phase 3: Context sync tests
uv run pytest tests/modules/autonomous_agent/test_context_sync.py tests/modules/autonomous_agent/tools/test_context_file_tools.py -v

# Phase 4: Follow-up tool tests
uv run pytest tests/modules/autonomous_agent/tools/test_followup_tools.py -v

# Phase 5: Full test suite
uv run pytest -x --tb=short

# Import checks
python -c "from app.temporal.activities import KaiActivities; print('OK')"
python -c "from app.modules.autonomous_agent.service import AutonomousAgentService; print('OK')"
python -c "from app.modules.autonomous_agent.context_sync import ContextSyncService; print('OK')"
```

## Notes

- The existing `suggestions_tools.py` has a heuristic `suggest_questions` tool. Task 11 replaces it with an LLM-powered `suggest_follow_ups` tool. Check if `suggest_questions` is currently registered in `_build_tools()` — if so, remove it when adding the new tool.
- The `DatabaseConnectionRepository` in `activities.py` needs the correct import path — verify by checking existing imports in `app/modules/database_connection/repositories/`.
- Jinja2 is already available as a transitive dependency of LangChain. No need to add it to `pyproject.toml`.
- The `AnalysisService` import and `PromptRequest` import in `activities.py` can be removed after wiring, but keep them if the old `chat` needs to remain as a fallback.

---

## Checklist Summary

### Phase 1: Model Bug Fixes (BLOCKING)
- [ ] Task 1: Add `session_id` to `AgentTask`
- [ ] Task 2: Make `mission_id` optional in `AgentResult`
- [ ] Task 3: Unit tests for model fixes

### Phase 2: Temporal Wiring
- [ ] Task 4: Wire `chat()` to `AutonomousAgentService`
- [ ] Task 5: Add `autonomous_chat` activity
- [ ] Task 6: Temporal activity tests

### Phase 3: File-Based Context Sync
- [ ] Task 7: Context sync service + Jinja2 templates
- [ ] Task 8: `kai context sync` CLI command
- [ ] Task 9: `search_context_files` + `read_context_file` tools
- [ ] Task 10: Context sync + file tool tests

### Phase 4: Follow-up Suggestions
- [ ] Task 11: `suggest_follow_ups` tool
- [ ] Task 12: CLI rendering for suggestions
- [ ] Task 13: Follow-up tool tests

### Phase 5: Final Validation
- [ ] Task 14: Full test suite + import checks
