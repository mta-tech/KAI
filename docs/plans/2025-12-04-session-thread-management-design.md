# Session & Thread Management for Autonomous Agent

**Date:** 2025-12-04
**Status:** Design Approved
**Author:** Claude (AI Assistant)

## Overview

Add session/thread management to the autonomous agent (kai-agent) enabling:
1. **Resumable analysis sessions** - Resume interrupted tasks or continue conversations
2. **Hierarchical memory learning** - Session-specific + shared database-level memories
3. **Organized results storage** - Results isolated by database and session

## Architecture Decision

**Chosen approach:** Unified Session Model

Merge autonomous agent into the existing session pattern, reusing `session_id` as `thread_id` for LangGraph checkpointing. Single checkpointer (TypeSense), unified memory injection.

## Core Concepts

### Session ID & Thread ID

| Term | Definition |
|------|------------|
| `session_id` | Unique identifier for a conversation/analysis session |
| `thread_id` | LangGraph config key, maps 1:1 with `session_id` |
| `task_id` | Individual execution within a session |

**Relationship:** One session contains many tasks (like a conversation with many messages).

## Data Models

### AgentSession (New)

```python
@dataclass
class AgentSession:
    """Persistent session for autonomous agent."""
    id: str                          # session_id (UUID)
    db_connection_id: str            # which database
    status: Literal["active", "paused", "completed", "failed"]
    mode: Literal["analysis", "query", "script", "full_autonomy"]
    recursion_limit: int = 100       # configurable per session
    title: str | None = None         # auto-generated or user-provided
    created_at: str
    updated_at: str
    metadata: dict | None = None
```

### AgentTask (Updated)

```python
@dataclass
class AgentTask:
    """Task submitted to the autonomous agent."""
    id: str                          # task_id (unique per execution)
    session_id: str                  # NEW: links to AgentSession
    prompt: str
    db_connection_id: str
    mode: Literal[...] = "full_autonomy"
    context: dict | None = None
    metadata: dict | None = None
    created_at: str
```

## Hierarchical Memory Architecture

```
┌─────────────────────────────────────────────────────┐
│  Database Connection Level (db_connection_id)       │
│  ┌─────────────────────────────────────────────┐   │
│  │  Shared Memories (cross-session)            │   │
│  │  - business_facts, user_preferences         │   │
│  │  - corrections, data_insights               │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐               │
│  │  Session A   │  │  Session B   │               │
│  │  - context   │  │  - context   │               │
│  │  - working   │  │  - working   │               │
│  │    memory    │  │    memory    │               │
│  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────┘
```

### Memory Namespaces

| Namespace | Scope | Purpose |
|-----------|-------|---------|
| `user_preferences` | db_connection | Date formats, styles (shared) |
| `business_facts` | db_connection | Business rules (shared) |
| `data_insights` | db_connection | Patterns discovered (shared) |
| `corrections` | db_connection | Mistakes corrected (shared) |
| `session_context` | session_id | Current analysis context (isolated) |
| `session_working` | session_id | Intermediate results (isolated) |

## Results Directory Structure

```
./agent_results/
├── {db_connection_id}/
│   ├── {session_id_1}/
│   │   ├── report_20241203_143022.md
│   │   ├── analysis_revenue.xlsx
│   │   └── chart_sales_trend.png
│   ├── {session_id_2}/
│   │   └── ...
│   └── shared/
│       └── ...
└── {another_db_connection_id}/
    └── ...
```

## API Endpoints

```
POST   /agent/sessions              → Create new session
GET    /agent/sessions              → List sessions (filter by db_connection_id)
GET    /agent/sessions/{id}         → Get session details + history
DELETE /agent/sessions/{id}         → Delete session and its checkpoints
POST   /agent/sessions/{id}/execute → Execute task within session (resumable)
GET    /agent/sessions/{id}/stream  → Stream execution with SSE
```

## Service Layer Changes

### AutonomousAgentService Updates

```python
class AutonomousAgentService:
    def __init__(
        self,
        db_connection: DatabaseConnection,
        database: SQLDatabase,
        base_results_dir: str = "./agent_results",  # renamed
        llm_config=None,
        checkpointer=None,              # TypesenseCheckpointer
        storage: Storage = None,
        session_repository=None,        # NEW: for session CRUD
    ):
        self.base_results_dir = base_results_dir

    def _get_session_results_dir(self, session_id: str) -> str:
        """Get results directory for a specific session."""
        return os.path.join(
            self.base_results_dir,
            self.db_connection.id,
            session_id
        )
```

### New AgentSessionRepository

```python
class AgentSessionRepository:
    def create(db_connection_id, mode, recursion_limit, metadata) -> session_id
    def get(session_id) -> AgentSession | None
    def list(db_connection_id, status, limit) -> list[AgentSession]
    def update(session) -> None
    def delete(session_id) -> None
```

## Execution Flow

### Resume Detection

```python
async def execute(self, task: AgentTask) -> AgentResult:
    session = await self.session_repository.get(task.session_id)
    session_results_dir = self._get_session_results_dir(task.session_id)
    os.makedirs(session_results_dir, exist_ok=True)

    agent = self.create_agent(task.mode, session_results_dir)

    config = {
        "configurable": {"thread_id": task.session_id},
        "recursion_limit": session.recursion_limit,
    }

    # Check for existing checkpoint (resume scenario)
    existing_checkpoint = await self.checkpointer.aget(config)
    is_resume = existing_checkpoint is not None

    if is_resume:
        logger.info(f"Resuming session {task.session_id} from checkpoint")
        input_state = {"messages": [{"role": "user", "content": task.prompt}]}
    else:
        logger.info(f"Starting new session {task.session_id}")
        input_state = {"messages": [{"role": "user", "content": augmented_prompt}]}
```

### Session Status Transitions

```
┌─────────┐  create   ┌────────┐  execute  ┌──────────┐
│  (new)  │ ────────► │ active │ ────────► │ running  │
└─────────┘           └────────┘           └──────────┘
                           │                    │
                           │ pause              │ complete/error
                           ▼                    ▼
                      ┌────────┐           ┌───────────┐
                      │ paused │           │ completed │
                      └────────┘           │  /failed  │
                           │               └───────────┘
                           │ resume
                           ▼
                      ┌──────────┐
                      │ running  │
                      └──────────┘
```

## Learning Integration Changes

### Updated Agent Naming

```python
def get_agent_name(db_connection_id: str, session_id: str | None = None) -> str:
    """Generate Letta agent name with optional session scope."""
    sanitized_db = db_connection_id.replace("-", "_")
    if session_id:
        sanitized_session = session_id.replace("-", "_")[:8]
        return f"kai_agent_{sanitized_db}_{sanitized_session}"
    return f"kai_agent_{sanitized_db}"
```

### Memory Block Injection

| Block Type | Scope | Injection |
|------------|-------|-----------|
| `core_memory` | db_connection | Always injected (shared knowledge) |
| `session_memory` | session_id | Injected for current session only |
| `archival_memory` | db_connection | Searched semantically (shared) |

### Updated Learning Context

```python
@contextmanager
def learning_context(db_connection_id: str, session_id: str | None = None):
    """Wrap agent execution with memory injection."""
    client = get_learning_client()
    if client is None:
        yield
        return

    agent_name = get_agent_name(db_connection_id, session_id)
    memory_blocks = get_memory_blocks(include_session=session_id is not None)

    with learning(agent=agent_name, client=client, memory=memory_blocks):
        yield
```

## Cleanup on Session Delete

1. Remove session from `agent_sessions` collection
2. Remove checkpoint from checkpointer
3. Delete `{base_results_dir}/{db_id}/{session_id}/` directory
4. Clear session-scoped memories from memory backend

## Files to Modify

| File | Changes |
|------|---------|
| `app/modules/autonomous_agent/models.py` | Add `AgentSession`, update `AgentTask` |
| `app/modules/autonomous_agent/service.py` | Add session support, results_dir scoping |
| `app/modules/autonomous_agent/repositories.py` | NEW: `AgentSessionRepository` |
| `app/modules/autonomous_agent/learning.py` | Session-aware agent naming |
| `app/modules/memory/backends/base.py` | Add optional `session_id` parameter |
| `app/modules/memory/backends/typesense.py` | Session-scoped memory storage |
| `app/modules/memory/services/__init__.py` | Session-aware recall |
| `app/server/routes/agent.py` | NEW: Session management endpoints |

## Persistence

- **Sessions:** TypeSense collection `agent_sessions`
- **Checkpoints:** TypeSense via `TypesenseCheckpointer` (existing)
- **Memories:** TypeSense or Letta (existing backends)
- **Results:** Filesystem `./agent_results/{db_id}/{session_id}/`
