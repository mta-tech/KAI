# Session & Thread Management Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add persistent session/thread management to the autonomous agent enabling resumable analysis and hierarchical memory learning.

**Architecture:** Unified Session Model - extend AutonomousAgentService with AgentSession for checkpointing via TypeSense. Session-scoped results directories. Hierarchical memory with session-level and database-level namespaces.

**Tech Stack:** Python 3.11+, LangGraph, TypeSense, Pydantic dataclasses

---

## Pre-Implementation Setup

### Task 0: Create Feature Branch

**Step 1: Create and checkout feature branch**

Run:
```bash
cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI
git checkout -b feat/session-management
```

Expected: Switched to new branch 'feat/session-management'

---

## Phase 1: Data Models

### Task 1: Add AgentSession Model

**Files:**
- Modify: `app/modules/autonomous_agent/models.py`
- Test: `tests/modules/autonomous_agent/test_models.py`

**Step 1: Write the failing test**

Create test file if not exists, add test:

```python
# tests/modules/autonomous_agent/test_models.py
import pytest
from datetime import datetime
from app.modules.autonomous_agent.models import AgentSession


def test_agent_session_creation():
    """Should create AgentSession with required fields."""
    session = AgentSession(
        id="sess_123",
        db_connection_id="db_456",
        status="active",
        mode="full_autonomy",
    )
    assert session.id == "sess_123"
    assert session.db_connection_id == "db_456"
    assert session.status == "active"
    assert session.mode == "full_autonomy"
    assert session.recursion_limit == 100  # default
    assert session.title is None


def test_agent_session_with_custom_recursion_limit():
    """Should allow custom recursion_limit."""
    session = AgentSession(
        id="sess_123",
        db_connection_id="db_456",
        status="active",
        mode="analysis",
        recursion_limit=200,
    )
    assert session.recursion_limit == 200
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/modules/autonomous_agent/test_models.py -v`

Expected: FAIL with "cannot import name 'AgentSession'"

**Step 3: Write minimal implementation**

Add to `app/modules/autonomous_agent/models.py` after the imports:

```python
@dataclass
class AgentSession:
    """Persistent session for autonomous agent."""
    id: str
    db_connection_id: str
    status: Literal["active", "paused", "running", "completed", "failed"]
    mode: Literal["analysis", "query", "script", "full_autonomy"] = "full_autonomy"
    recursion_limit: int = 100
    title: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict | None = None
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/modules/autonomous_agent/test_models.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add app/modules/autonomous_agent/models.py tests/modules/autonomous_agent/test_models.py
git commit -m "feat(agent): add AgentSession model for persistent sessions"
```

---

### Task 2: Update AgentTask Model with session_id

**Files:**
- Modify: `app/modules/autonomous_agent/models.py:7-15`
- Test: `tests/modules/autonomous_agent/test_models.py`

**Step 1: Write the failing test**

Add to test file:

```python
def test_agent_task_with_session_id():
    """Should create AgentTask with session_id."""
    task = AgentTask(
        id="task_789",
        session_id="sess_123",
        prompt="Analyze revenue trends",
        db_connection_id="db_456",
    )
    assert task.id == "task_789"
    assert task.session_id == "sess_123"
    assert task.prompt == "Analyze revenue trends"
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/modules/autonomous_agent/test_models.py::test_agent_task_with_session_id -v`

Expected: FAIL with "unexpected keyword argument 'session_id'"

**Step 3: Write minimal implementation**

Update `AgentTask` in `app/modules/autonomous_agent/models.py`:

```python
@dataclass
class AgentTask:
    """Task submitted to the autonomous agent."""
    id: str
    session_id: str  # NEW: links to AgentSession
    prompt: str
    db_connection_id: str
    mode: Literal["analysis", "query", "script", "full_autonomy"] = "full_autonomy"
    context: dict | None = None
    metadata: dict | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/modules/autonomous_agent/test_models.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add app/modules/autonomous_agent/models.py tests/modules/autonomous_agent/test_models.py
git commit -m "feat(agent): add session_id to AgentTask model"
```

---

## Phase 2: Session Repository

### Task 3: Create AgentSessionRepository

**Files:**
- Create: `app/modules/autonomous_agent/repositories/__init__.py`
- Test: `tests/modules/autonomous_agent/test_repositories.py`

**Step 1: Write the failing test**

```python
# tests/modules/autonomous_agent/test_repositories.py
import pytest
from unittest.mock import MagicMock
from app.modules.autonomous_agent.repositories import AgentSessionRepository
from app.modules.autonomous_agent.models import AgentSession


@pytest.fixture
def mock_storage():
    return MagicMock()


@pytest.fixture
def repository(mock_storage):
    return AgentSessionRepository(storage=mock_storage)


def test_create_session(repository, mock_storage):
    """Should create a new session and return session_id."""
    mock_storage.upsert.return_value = None

    session_id = repository.create(
        db_connection_id="db_123",
        mode="full_autonomy",
    )

    assert session_id is not None
    assert session_id.startswith("sess_")
    mock_storage.upsert.assert_called_once()


def test_get_session(repository, mock_storage):
    """Should return session by id."""
    mock_storage.find_by_id.return_value = {
        "id": "sess_123",
        "db_connection_id": "db_456",
        "status": "active",
        "mode": "full_autonomy",
        "recursion_limit": 100,
        "created_at": "2024-12-04T10:00:00",
        "updated_at": "2024-12-04T10:00:00",
    }

    session = repository.get("sess_123")

    assert session is not None
    assert session.id == "sess_123"
    assert session.db_connection_id == "db_456"


def test_get_session_not_found(repository, mock_storage):
    """Should return None when session not found."""
    mock_storage.find_by_id.return_value = None

    session = repository.get("nonexistent")

    assert session is None
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/modules/autonomous_agent/test_repositories.py -v`

Expected: FAIL with "No module named 'app.modules.autonomous_agent.repositories'"

**Step 3: Write minimal implementation**

Create `app/modules/autonomous_agent/repositories/__init__.py`:

```python
"""Repository for AgentSession persistence."""
import uuid
from datetime import datetime
from typing import Any

from app.modules.autonomous_agent.models import AgentSession

AGENT_SESSION_COLLECTION = "agent_sessions"


class AgentSessionRepository:
    """Repository for managing AgentSession in TypeSense."""

    def __init__(self, storage: Any):
        """Initialize with TypeSense storage.

        Args:
            storage: TypeSense storage instance
        """
        self.storage = storage
        self.collection = AGENT_SESSION_COLLECTION

    def create(
        self,
        db_connection_id: str,
        mode: str = "full_autonomy",
        recursion_limit: int = 100,
        title: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        """Create a new session.

        Args:
            db_connection_id: Database connection ID
            mode: Agent mode
            recursion_limit: Max recursion for LangGraph
            title: Optional session title
            metadata: Optional metadata

        Returns:
            Created session ID
        """
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()

        doc = {
            "id": session_id,
            "db_connection_id": db_connection_id,
            "status": "active",
            "mode": mode,
            "recursion_limit": recursion_limit,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "metadata": metadata,
        }

        self.storage.upsert(self.collection, doc)
        return session_id

    def get(self, session_id: str) -> AgentSession | None:
        """Get session by ID.

        Args:
            session_id: Session ID

        Returns:
            AgentSession if found, None otherwise
        """
        doc = self.storage.find_by_id(self.collection, session_id)
        if not doc:
            return None

        return AgentSession(
            id=doc["id"],
            db_connection_id=doc["db_connection_id"],
            status=doc["status"],
            mode=doc.get("mode", "full_autonomy"),
            recursion_limit=doc.get("recursion_limit", 100),
            title=doc.get("title"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            metadata=doc.get("metadata"),
        )

    def list(
        self,
        db_connection_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[AgentSession]:
        """List sessions with optional filters.

        Args:
            db_connection_id: Filter by database connection
            status: Filter by status
            limit: Maximum results

        Returns:
            List of AgentSession
        """
        filters = {}
        if db_connection_id:
            filters["db_connection_id"] = db_connection_id
        if status:
            filters["status"] = status

        docs = self.storage.search(
            self.collection,
            query="*",
            filter_by=filters,
            limit=limit,
            sort_by="created_at:desc",
        )

        return [
            AgentSession(
                id=doc["id"],
                db_connection_id=doc["db_connection_id"],
                status=doc["status"],
                mode=doc.get("mode", "full_autonomy"),
                recursion_limit=doc.get("recursion_limit", 100),
                title=doc.get("title"),
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
                metadata=doc.get("metadata"),
            )
            for doc in docs
        ]

    def update(self, session: AgentSession) -> None:
        """Update session.

        Args:
            session: Session to update
        """
        doc = {
            "id": session.id,
            "db_connection_id": session.db_connection_id,
            "status": session.status,
            "mode": session.mode,
            "recursion_limit": session.recursion_limit,
            "title": session.title,
            "created_at": session.created_at,
            "updated_at": datetime.now().isoformat(),
            "metadata": session.metadata,
        }
        self.storage.upsert(self.collection, doc)

    def delete(self, session_id: str) -> bool:
        """Delete session.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted, False if not found
        """
        return self.storage.delete(self.collection, session_id)


__all__ = ["AgentSessionRepository", "AGENT_SESSION_COLLECTION"]
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/modules/autonomous_agent/test_repositories.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add app/modules/autonomous_agent/repositories/ tests/modules/autonomous_agent/test_repositories.py
git commit -m "feat(agent): add AgentSessionRepository for session persistence"
```

---

## Phase 3: Service Layer Updates

### Task 4: Add Session Results Directory Helper

**Files:**
- Modify: `app/modules/autonomous_agent/service.py`
- Test: `tests/modules/autonomous_agent/test_service.py`

**Step 1: Write the failing test**

```python
# Add to tests/modules/autonomous_agent/test_service.py (create if needed)
import pytest
from unittest.mock import MagicMock
from app.modules.autonomous_agent.service import AutonomousAgentService


@pytest.fixture
def mock_db_connection():
    conn = MagicMock()
    conn.id = "db_123"
    conn.dialect = "postgresql"
    return conn


@pytest.fixture
def mock_database():
    return MagicMock()


def test_get_session_results_dir(mock_db_connection, mock_database):
    """Should return session-scoped results directory."""
    service = AutonomousAgentService(
        db_connection=mock_db_connection,
        database=mock_database,
        base_results_dir="/tmp/results",
    )

    result_dir = service._get_session_results_dir("sess_abc123")

    assert result_dir == "/tmp/results/db_123/sess_abc123"
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/modules/autonomous_agent/test_service.py::test_get_session_results_dir -v`

Expected: FAIL with "unexpected keyword argument 'base_results_dir'" or "_get_session_results_dir"

**Step 3: Write minimal implementation**

Update `app/modules/autonomous_agent/service.py`:

1. Change `__init__` parameter from `results_dir` to `base_results_dir`:

```python
def __init__(
    self,
    db_connection: DatabaseConnection,
    database: SQLDatabase,
    base_results_dir: str = "./agent_results",  # renamed
    llm_config=None,
    checkpointer=None,
    storage: Storage = None,
):
    self.db_connection = db_connection
    self.database = database
    self.base_results_dir = base_results_dir  # renamed
    self.llm_config = llm_config
    self.checkpointer = checkpointer
    if storage is None:
        from app.server.config import Settings
        storage = Storage(Settings())
    self.storage = storage
```

2. Add helper method after `__init__`:

```python
def _get_session_results_dir(self, session_id: str) -> str:
    """Get results directory for a specific session.

    Args:
        session_id: The session ID

    Returns:
        Path to session-specific results directory
    """
    import os
    return os.path.join(
        self.base_results_dir,
        self.db_connection.id,
        session_id
    )
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/modules/autonomous_agent/test_service.py::test_get_session_results_dir -v`

Expected: PASS

**Step 5: Commit**

```bash
git add app/modules/autonomous_agent/service.py tests/modules/autonomous_agent/test_service.py
git commit -m "feat(agent): add session-scoped results directory helper"
```

---

### Task 5: Update execute() to Use Session ID

**Files:**
- Modify: `app/modules/autonomous_agent/service.py:174-249`
- Test: `tests/modules/autonomous_agent/test_service.py`

**Step 1: Write the failing test**

```python
@pytest.mark.asyncio
async def test_execute_uses_session_id_for_thread(mock_db_connection, mock_database):
    """Should use session_id as thread_id in LangGraph config."""
    from app.modules.autonomous_agent.models import AgentTask

    service = AutonomousAgentService(
        db_connection=mock_db_connection,
        database=mock_database,
        base_results_dir="/tmp/results",
    )

    # Mock the agent creation
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {
        "messages": [MagicMock(content="Analysis complete")]
    }
    service.create_agent = MagicMock(return_value=mock_agent)

    task = AgentTask(
        id="task_001",
        session_id="sess_abc123",
        prompt="Analyze revenue",
        db_connection_id="db_123",
    )

    await service.execute(task)

    # Verify invoke was called with session_id as thread_id
    call_args = mock_agent.invoke.call_args
    config = call_args[1]["config"]
    assert config["configurable"]["thread_id"] == "sess_abc123"
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/modules/autonomous_agent/test_service.py::test_execute_uses_session_id_for_thread -v`

Expected: FAIL (task.id used instead of task.session_id)

**Step 3: Write minimal implementation**

Update `execute()` method in `app/modules/autonomous_agent/service.py`:

1. Update config to use `task.session_id`:

```python
async def execute(self, task: AgentTask) -> AgentResult:
    """Execute task and return final result."""
    start_time = time.time()

    # Create session-specific results directory
    session_results_dir = self._get_session_results_dir(task.session_id)
    os.makedirs(session_results_dir, exist_ok=True)

    agent = self.create_agent(task.mode, results_dir=session_results_dir)

    config = {
        "configurable": {"thread_id": task.session_id},  # Changed from task.id
        "recursion_limit": 100,
    }
    # ... rest of method
```

2. Add `import os` at top of file if not present.

3. Update `create_agent()` to accept `results_dir` parameter:

```python
def create_agent(self, mode: str = "full_autonomy", results_dir: str | None = None):
    """Create autonomous deep agent.

    Args:
        mode: Agent mode (full_autonomy, analysis, query, script)
        results_dir: Override results directory (for session-scoped)

    Returns:
        Compiled LangGraph agent
    """
    effective_results_dir = results_dir or self.base_results_dir
    # Use effective_results_dir in _build_tools and _backend_factory
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/modules/autonomous_agent/test_service.py::test_execute_uses_session_id_for_thread -v`

Expected: PASS

**Step 5: Commit**

```bash
git add app/modules/autonomous_agent/service.py tests/modules/autonomous_agent/test_service.py
git commit -m "feat(agent): use session_id as thread_id for checkpointing"
```

---

### Task 6: Add Resume Detection Logic

**Files:**
- Modify: `app/modules/autonomous_agent/service.py`
- Test: `tests/modules/autonomous_agent/test_service.py`

**Step 1: Write the failing test**

```python
@pytest.mark.asyncio
async def test_execute_detects_resume(mock_db_connection, mock_database):
    """Should detect existing checkpoint and log resume."""
    from app.modules.autonomous_agent.models import AgentTask
    from unittest.mock import AsyncMock

    mock_checkpointer = MagicMock()
    mock_checkpointer.aget = AsyncMock(return_value={"some": "checkpoint"})

    service = AutonomousAgentService(
        db_connection=mock_db_connection,
        database=mock_database,
        base_results_dir="/tmp/results",
        checkpointer=mock_checkpointer,
    )

    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {
        "messages": [MagicMock(content="Resumed analysis")]
    }
    service.create_agent = MagicMock(return_value=mock_agent)

    task = AgentTask(
        id="task_002",
        session_id="sess_existing",
        prompt="Continue analysis",
        db_connection_id="db_123",
    )

    result = await service.execute(task)

    # Checkpointer should be queried
    mock_checkpointer.aget.assert_called_once()
    assert result.status == "completed"
```

**Step 2: Run test to verify behavior**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/modules/autonomous_agent/test_service.py::test_execute_detects_resume -v`

**Step 3: Implement resume detection**

Update `execute()` in `app/modules/autonomous_agent/service.py`:

```python
async def execute(self, task: AgentTask) -> AgentResult:
    """Execute task and return final result."""
    start_time = time.time()

    # Create session-specific results directory
    session_results_dir = self._get_session_results_dir(task.session_id)
    os.makedirs(session_results_dir, exist_ok=True)

    agent = self.create_agent(task.mode, results_dir=session_results_dir)

    config = {
        "configurable": {"thread_id": task.session_id},
        "recursion_limit": 100,
    }

    # Check for existing checkpoint (resume scenario)
    is_resume = False
    if self.checkpointer:
        existing_checkpoint = await self.checkpointer.aget(config)
        is_resume = existing_checkpoint is not None
        if is_resume:
            logger.info(f"Resuming session {task.session_id} from checkpoint")
        else:
            logger.info(f"Starting new session {task.session_id}")

    # ... rest of execute method
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/modules/autonomous_agent/test_service.py::test_execute_detects_resume -v`

Expected: PASS

**Step 5: Commit**

```bash
git add app/modules/autonomous_agent/service.py tests/modules/autonomous_agent/test_service.py
git commit -m "feat(agent): add resume detection from checkpoint"
```

---

## Phase 4: Learning Integration

### Task 7: Update Learning Context for Session Awareness

**Files:**
- Modify: `app/modules/autonomous_agent/learning.py`
- Test: `tests/modules/autonomous_agent/test_learning.py`

**Step 1: Write the failing test**

```python
# tests/modules/autonomous_agent/test_learning.py
import pytest
from app.modules.autonomous_agent.learning import get_agent_name


def test_get_agent_name_without_session():
    """Should generate agent name from db_connection_id only."""
    name = get_agent_name("db-123-abc")
    assert name == "kai_agent_db_123_abc"


def test_get_agent_name_with_session():
    """Should include session_id in agent name."""
    name = get_agent_name("db-123-abc", session_id="sess-xyz-789")
    assert name == "kai_agent_db_123_abc_sess_xyz"
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/modules/autonomous_agent/test_learning.py::test_get_agent_name_with_session -v`

Expected: FAIL (session_id parameter not accepted)

**Step 3: Write minimal implementation**

Update `get_agent_name()` in `app/modules/autonomous_agent/learning.py`:

```python
def get_agent_name(db_connection_id: str, session_id: str | None = None) -> str:
    """Generate Letta agent name from db_connection_id with optional session scope.

    Args:
        db_connection_id: The database connection identifier.
        session_id: Optional session ID for session-scoped agent.

    Returns:
        Sanitized agent name for Letta.
    """
    sanitized_db = db_connection_id.replace("-", "_").replace(" ", "_")
    if session_id:
        sanitized_session = session_id.replace("-", "_").replace(" ", "_")[:8]
        return f"kai_agent_{sanitized_db}_{sanitized_session}"
    return f"kai_agent_{sanitized_db}"
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/modules/autonomous_agent/test_learning.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add app/modules/autonomous_agent/learning.py tests/modules/autonomous_agent/test_learning.py
git commit -m "feat(learning): add session_id support to agent naming"
```

---

### Task 8: Update Learning Context Manager

**Files:**
- Modify: `app/modules/autonomous_agent/learning.py:74-119`
- Test: `tests/modules/autonomous_agent/test_learning.py`

**Step 1: Write the failing test**

```python
def test_learning_context_accepts_session_id():
    """Should accept session_id parameter."""
    from app.modules.autonomous_agent.learning import learning_context

    # Should not raise - just verify signature accepts session_id
    with learning_context("db_123", session_id="sess_456"):
        pass  # Falls through when learning not configured
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/modules/autonomous_agent/test_learning.py::test_learning_context_accepts_session_id -v`

Expected: FAIL (session_id parameter not accepted)

**Step 3: Write minimal implementation**

Update `learning_context()` in `app/modules/autonomous_agent/learning.py`:

```python
@contextmanager
def learning_context(db_connection_id: str, session_id: str | None = None):
    """Sync context manager for automatic learning.

    Wraps agent execution with memory injection and capture.
    Falls through silently if learning is not configured.

    Usage:
        with learning_context(db_connection.id, session_id=task.session_id):
            result = agent.invoke(input_state, config=config)

    Args:
        db_connection_id: The database connection identifier for agent scoping.
        session_id: Optional session ID for session-scoped memory.

    Yields:
        None - this is a context manager for wrapping execution.
    """
    client = get_learning_client()

    if client is None:
        yield
        return

    from app.server.config import Settings
    settings = Settings()

    try:
        from agentic_learning import learning

        agent_name = get_agent_name(db_connection_id, session_id)
        memory_blocks = get_memory_blocks()
        capture_only = settings.AUTO_LEARNING_CAPTURE_ONLY

        with learning(
            agent=agent_name,
            client=client,
            memory=memory_blocks,
            capture_only=capture_only,
        ):
            logger.debug(f"Learning context active: agent={agent_name}")
            yield

    except Exception as e:
        logger.warning(f"Learning context failed, continuing without: {e}")
        yield
```

Also update `async_learning_context()` similarly.

**Step 4: Run test to verify it passes**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/modules/autonomous_agent/test_learning.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add app/modules/autonomous_agent/learning.py tests/modules/autonomous_agent/test_learning.py
git commit -m "feat(learning): add session_id to learning context managers"
```

---

## Phase 5: Memory Backend Updates

### Task 9: Add Session Scope to Memory Backend Protocol

**Files:**
- Modify: `app/modules/memory/backends/base.py`

**Step 1: Update protocol signature**

Update `remember()` in `app/modules/memory/backends/base.py`:

```python
def remember(
    self,
    db_connection_id: str,
    namespace: str,
    key: str,
    value: dict[str, Any],
    importance: float = 0.5,
    session_id: str | None = None,  # NEW: optional session scope
) -> Memory:
    """Store a memory.

    Args:
        db_connection_id: Database connection to associate memory with.
        namespace: Category of memory (e.g., "user_preferences", "business_facts").
        key: Unique identifier within namespace.
        value: The memory content as a dictionary.
        importance: How important this memory is (0-1 scale).
        session_id: Optional session ID for session-scoped memories.

    Returns:
        The stored Memory object.
    """
    ...
```

Update `recall()` similarly:

```python
def recall(
    self,
    db_connection_id: str,
    query: str,
    namespace: str | None = None,
    limit: int = 5,
    session_id: str | None = None,  # NEW: optional session filter
) -> list[MemorySearchResult]:
```

**Step 2: Commit**

```bash
git add app/modules/memory/backends/base.py
git commit -m "feat(memory): add session_id to MemoryBackend protocol"
```

---

### Task 10: Implement Session Scope in TypeSense Backend

**Files:**
- Modify: `app/modules/memory/backends/typesense.py`
- Test: `tests/modules/memory/test_typesense_backend.py`

**Step 1: Write the failing test**

```python
# tests/modules/memory/test_typesense_backend.py
import pytest
from unittest.mock import MagicMock
from app.modules.memory.backends.typesense import TypeSenseMemoryBackend


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    storage.upsert.return_value = None
    return storage


@pytest.fixture
def backend(mock_storage):
    return TypeSenseMemoryBackend(storage=mock_storage)


def test_remember_with_session_id(backend, mock_storage):
    """Should include session_id in memory document."""
    backend.remember(
        db_connection_id="db_123",
        namespace="session_context",
        key="current_topic",
        value={"content": "Revenue analysis"},
        session_id="sess_456",
    )

    call_args = mock_storage.upsert.call_args[0]
    doc = call_args[1]
    assert doc["session_id"] == "sess_456"
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/modules/memory/test_typesense_backend.py::test_remember_with_session_id -v`

Expected: FAIL

**Step 3: Implement session_id in TypeSenseMemoryBackend**

Update `remember()` in `app/modules/memory/backends/typesense.py`:

```python
def remember(
    self,
    db_connection_id: str,
    namespace: str,
    key: str,
    value: dict[str, Any],
    importance: float = 0.5,
    session_id: str | None = None,
) -> Memory:
    # ... existing code ...

    doc = {
        "id": memory_id,
        "db_connection_id": db_connection_id,
        "namespace": namespace,
        "key": key,
        "value": json.dumps(value),
        "content_text": content_text,
        "importance": importance,
        "session_id": session_id,  # NEW
        "created_at": now,
        "updated_at": now,
    }

    # ... rest of method
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/modules/memory/test_typesense_backend.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add app/modules/memory/backends/typesense.py tests/modules/memory/test_typesense_backend.py
git commit -m "feat(memory): implement session_id in TypeSense backend"
```

---

## Phase 6: API Routes

### Task 11: Create Agent Session Routes

**Files:**
- Create: `app/server/routes/agent_sessions.py`
- Modify: `app/server/__init__.py` (to register routes)

**Step 1: Create route handlers**

```python
# app/server/routes/agent_sessions.py
"""API routes for agent session management."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Literal

from app.modules.autonomous_agent.repositories import AgentSessionRepository
from app.modules.autonomous_agent.models import AgentSession

router = APIRouter(prefix="/agent/sessions", tags=["agent-sessions"])


class CreateSessionRequest(BaseModel):
    db_connection_id: str
    mode: Literal["analysis", "query", "script", "full_autonomy"] = "full_autonomy"
    recursion_limit: int = 100
    title: str | None = None
    metadata: dict | None = None


class CreateSessionResponse(BaseModel):
    session_id: str


class SessionResponse(BaseModel):
    id: str
    db_connection_id: str
    status: str
    mode: str
    recursion_limit: int
    title: str | None
    created_at: str
    updated_at: str
    metadata: dict | None


@router.post("", response_model=CreateSessionResponse)
async def create_session(
    request: CreateSessionRequest,
    repository: AgentSessionRepository = Depends(get_session_repository),
):
    """Create a new agent session."""
    session_id = repository.create(
        db_connection_id=request.db_connection_id,
        mode=request.mode,
        recursion_limit=request.recursion_limit,
        title=request.title,
        metadata=request.metadata,
    )
    return CreateSessionResponse(session_id=session_id)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    repository: AgentSessionRepository = Depends(get_session_repository),
):
    """Get session by ID."""
    session = repository.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(
        id=session.id,
        db_connection_id=session.db_connection_id,
        status=session.status,
        mode=session.mode,
        recursion_limit=session.recursion_limit,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        metadata=session.metadata,
    )


@router.get("", response_model=list[SessionResponse])
async def list_sessions(
    db_connection_id: str | None = None,
    status: str | None = None,
    limit: int = 100,
    repository: AgentSessionRepository = Depends(get_session_repository),
):
    """List sessions with optional filters."""
    sessions = repository.list(
        db_connection_id=db_connection_id,
        status=status,
        limit=limit,
    )
    return [
        SessionResponse(
            id=s.id,
            db_connection_id=s.db_connection_id,
            status=s.status,
            mode=s.mode,
            recursion_limit=s.recursion_limit,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
            metadata=s.metadata,
        )
        for s in sessions
    ]


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    repository: AgentSessionRepository = Depends(get_session_repository),
):
    """Delete session and cleanup resources."""
    deleted = repository.delete(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    # TODO: Also cleanup checkpoint and results directory
    return {"status": "deleted"}


def get_session_repository():
    """Dependency to get session repository."""
    from app.server.dependencies import get_storage
    storage = get_storage()
    return AgentSessionRepository(storage=storage)
```

**Step 2: Register routes**

Add to `app/server/__init__.py`:

```python
from app.server.routes.agent_sessions import router as agent_sessions_router

# In create_app() or router registration:
app.include_router(agent_sessions_router)
```

**Step 3: Commit**

```bash
git add app/server/routes/agent_sessions.py app/server/__init__.py
git commit -m "feat(api): add agent session management endpoints"
```

---

## Phase 7: Integration & Final Testing

### Task 12: Integration Test for Session Lifecycle

**Files:**
- Create: `tests/integration/test_agent_sessions.py`

**Step 1: Write integration test**

```python
# tests/integration/test_agent_sessions.py
import pytest
from unittest.mock import MagicMock, AsyncMock

from app.modules.autonomous_agent.models import AgentTask, AgentSession
from app.modules.autonomous_agent.repositories import AgentSessionRepository
from app.modules.autonomous_agent.service import AutonomousAgentService


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    storage.upsert.return_value = None
    storage.find_by_id.return_value = None
    return storage


@pytest.fixture
def session_repository(mock_storage):
    return AgentSessionRepository(storage=mock_storage)


@pytest.mark.asyncio
async def test_full_session_lifecycle(mock_storage, session_repository):
    """Test create session -> execute -> resume flow."""
    # 1. Create session
    session_id = session_repository.create(
        db_connection_id="db_test",
        mode="full_autonomy",
        recursion_limit=50,
    )
    assert session_id.startswith("sess_")

    # 2. Mock storage to return session on get
    mock_storage.find_by_id.return_value = {
        "id": session_id,
        "db_connection_id": "db_test",
        "status": "active",
        "mode": "full_autonomy",
        "recursion_limit": 50,
        "created_at": "2024-12-04T10:00:00",
        "updated_at": "2024-12-04T10:00:00",
    }

    # 3. Verify session retrieval
    session = session_repository.get(session_id)
    assert session is not None
    assert session.recursion_limit == 50
```

**Step 2: Run integration tests**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && python -m pytest tests/integration/test_agent_sessions.py -v`

Expected: PASS

**Step 3: Commit**

```bash
git add tests/integration/test_agent_sessions.py
git commit -m "test(agent): add integration tests for session lifecycle"
```

---

### Task 13: Final Cleanup and Documentation

**Step 1: Run all tests**

```bash
cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI
python -m pytest tests/ -v --tb=short
```

**Step 2: Update README if needed**

Add session management section to README.md documenting new API endpoints.

**Step 3: Final commit**

```bash
git add .
git commit -m "docs: update documentation for session management feature"
```

---

## Summary

| Phase | Tasks | Status |
|-------|-------|--------|
| Phase 1: Data Models | Tasks 1-2 | Pending |
| Phase 2: Session Repository | Task 3 | Pending |
| Phase 3: Service Layer | Tasks 4-6 | Pending |
| Phase 4: Learning Integration | Tasks 7-8 | Pending |
| Phase 5: Memory Backend | Tasks 9-10 | Pending |
| Phase 6: API Routes | Task 11 | Pending |
| Phase 7: Integration | Tasks 12-13 | Pending |

**Total: 13 tasks across 7 phases**
