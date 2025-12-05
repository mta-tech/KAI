# Session Endpoint Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a session endpoint where users can ask multiple NL → SQL → Analysis queries with conversation memory, returning responses via SSE streaming.

**Architecture:** LangGraph-based session graph with Typesense checkpointing. Each session maintains state across multiple queries, summarizing older context while keeping recent messages in full. SSE streams status updates and chunked responses.

**Tech Stack:** FastAPI, LangGraph, Typesense, existing KAI SQL generation/analysis modules

---

## Task 1: Create Session Module Directory Structure

**Files:**
- Create: `app/modules/session/__init__.py`
- Create: `app/modules/session/models/__init__.py`
- Create: `app/modules/session/repositories/__init__.py`
- Create: `app/modules/session/services/__init__.py`
- Create: `app/modules/session/graph/__init__.py`
- Create: `app/modules/session/graph/state.py`
- Create: `app/modules/session/graph/nodes.py`
- Create: `app/modules/session/graph/checkpointer.py`
- Create: `app/modules/session/constants.py`

**Step 1: Create module directories and init files**

```bash
mkdir -p app/modules/session/models
mkdir -p app/modules/session/repositories
mkdir -p app/modules/session/services
mkdir -p app/modules/session/graph
```

**Step 2: Create empty __init__.py files**

Create `app/modules/session/__init__.py`:
```python
"""Session module for multi-query conversation management."""
```

Create `app/modules/session/models/__init__.py`:
```python
"""Session data models."""
```

Create `app/modules/session/repositories/__init__.py`:
```python
"""Session repository for Typesense storage."""
```

Create `app/modules/session/services/__init__.py`:
```python
"""Session service for orchestrating graph and streaming."""
```

Create `app/modules/session/graph/__init__.py`:
```python
"""LangGraph session graph components."""
```

**Step 3: Commit**

```bash
git add app/modules/session/
git commit -m "feat(session): create module directory structure"
```

---

## Task 2: Implement Session State and Message Models

**Files:**
- Create: `app/modules/session/graph/state.py`
- Create: `app/modules/session/models/__init__.py`
- Test: `tests/modules/session/test_models.py`

**Step 1: Write the failing test**

Create `tests/modules/session/__init__.py`:
```python
"""Session module tests."""
```

Create `tests/modules/session/test_models.py`:
```python
import pytest
from datetime import datetime
from app.modules.session.models import Session, Message, SessionStatus


def test_message_creation():
    msg = Message(
        id="msg_123",
        role="human",
        query="Show me top customers",
        sql=None,
        results_summary=None,
        analysis=None,
        timestamp=datetime.now()
    )
    assert msg.id == "msg_123"
    assert msg.role == "human"
    assert msg.query == "Show me top customers"


def test_session_creation():
    session = Session(
        id="sess_123",
        db_connection_id="db_456",
        messages=[],
        summary=None,
        status=SessionStatus.IDLE,
        metadata={},
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    assert session.id == "sess_123"
    assert session.status == SessionStatus.IDLE
    assert session.messages == []


def test_session_status_enum():
    assert SessionStatus.IDLE.value == "idle"
    assert SessionStatus.PROCESSING.value == "processing"
    assert SessionStatus.ERROR.value == "error"
    assert SessionStatus.CLOSED.value == "closed"
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && uv run pytest tests/modules/session/test_models.py -v`

Expected: FAIL with "ModuleNotFoundError" or "ImportError"

**Step 3: Write the implementation**

Update `app/modules/session/models/__init__.py`:
```python
"""Session data models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Literal


class SessionStatus(str, Enum):
    """Session lifecycle status."""
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    CLOSED = "closed"


@dataclass
class Message:
    """A single message in a session conversation."""
    id: str
    role: Literal["human", "assistant"]
    query: str
    sql: str | None = None
    results_summary: str | None = None
    analysis: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "role": self.role,
            "query": self.query,
            "sql": self.sql,
            "results_summary": self.results_summary,
            "analysis": self.analysis,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            role=data["role"],
            query=data["query"],
            sql=data.get("sql"),
            results_summary=data.get("results_summary"),
            analysis=data.get("analysis"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if isinstance(data.get("timestamp"), str) else data.get("timestamp", datetime.now())
        )


@dataclass
class Session:
    """A multi-query conversation session."""
    id: str
    db_connection_id: str
    messages: list[Message] = field(default_factory=list)
    summary: str | None = None
    status: SessionStatus = SessionStatus.IDLE
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "db_connection_id": self.db_connection_id,
            "messages": [m.to_dict() for m in self.messages],
            "summary": self.summary,
            "status": self.status.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            db_connection_id=data["db_connection_id"],
            messages=[Message.from_dict(m) for m in data.get("messages", [])],
            summary=data.get("summary"),
            status=SessionStatus(data.get("status", "idle")),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data.get("created_at"), str) else data.get("created_at", datetime.now()),
            updated_at=datetime.fromisoformat(data["updated_at"]) if isinstance(data.get("updated_at"), str) else data.get("updated_at", datetime.now())
        )
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && uv run pytest tests/modules/session/test_models.py -v`

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add app/modules/session/models/ tests/modules/session/
git commit -m "feat(session): implement Session and Message models"
```

---

## Task 3: Implement Session Graph State

**Files:**
- Create: `app/modules/session/graph/state.py`
- Test: `tests/modules/session/test_graph_state.py`

**Step 1: Write the failing test**

Create `tests/modules/session/test_graph_state.py`:
```python
import pytest
from app.modules.session.graph.state import SessionState, create_initial_state


def test_session_state_type():
    """SessionState should be a TypedDict with expected keys."""
    state = create_initial_state("sess_123", "db_456")

    assert state["session_id"] == "sess_123"
    assert state["db_connection_id"] == "db_456"
    assert state["messages"] == []
    assert state["summary"] is None
    assert state["current_query"] is None
    assert state["current_sql"] is None
    assert state["current_results"] is None
    assert state["current_analysis"] is None
    assert state["status"] == "idle"


def test_session_state_keys():
    """Verify all required keys exist."""
    state = create_initial_state("sess_123", "db_456")
    required_keys = [
        "session_id", "db_connection_id", "messages", "summary",
        "current_query", "current_sql", "current_results",
        "current_analysis", "status", "metadata", "error"
    ]
    for key in required_keys:
        assert key in state, f"Missing key: {key}"
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && uv run pytest tests/modules/session/test_graph_state.py -v`

Expected: FAIL with "ImportError"

**Step 3: Write the implementation**

Update `app/modules/session/graph/state.py`:
```python
"""Session graph state definition for LangGraph."""
from typing import TypedDict, Literal
from datetime import datetime


class MessageDict(TypedDict):
    """Message representation in state."""
    id: str
    role: Literal["human", "assistant"]
    query: str
    sql: str | None
    results_summary: str | None
    analysis: str | None
    timestamp: str


class SessionState(TypedDict):
    """
    LangGraph state for session management.

    This state flows through the session graph, accumulating
    results from each processing step.
    """
    # Session identification
    session_id: str
    db_connection_id: str

    # Conversation history
    messages: list[MessageDict]
    summary: str | None

    # Current query processing
    current_query: str | None
    current_sql: str | None
    current_results: list[dict] | None
    current_analysis: dict | None

    # Status tracking
    status: Literal["idle", "processing", "error", "closed"]
    error: str | None

    # Custom metadata
    metadata: dict


def create_initial_state(session_id: str, db_connection_id: str, metadata: dict | None = None) -> SessionState:
    """
    Create initial session state for a new session.

    Args:
        session_id: Unique session identifier
        db_connection_id: Database connection to use for queries
        metadata: Optional custom metadata

    Returns:
        Initial SessionState with default values
    """
    return SessionState(
        session_id=session_id,
        db_connection_id=db_connection_id,
        messages=[],
        summary=None,
        current_query=None,
        current_sql=None,
        current_results=None,
        current_analysis=None,
        status="idle",
        error=None,
        metadata=metadata or {}
    )
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && uv run pytest tests/modules/session/test_graph_state.py -v`

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add app/modules/session/graph/state.py tests/modules/session/test_graph_state.py
git commit -m "feat(session): implement SessionState TypedDict for LangGraph"
```

---

## Task 4: Implement Session Constants

**Files:**
- Create: `app/modules/session/constants.py`

**Step 1: Write the implementation**

Create `app/modules/session/constants.py`:
```python
"""Session module constants."""

# Status messages for SSE streaming
STATUS_MESSAGES = {
    "build_context": "Loading conversation history...",
    "generate_sql": "Analyzing your question...",
    "execute_sql": "Running query...",
    "generate_analysis": "Generating insights...",
    "summarize": "Updating conversation memory...",
    "save_checkpoint": "Saving session state...",
}

# Summarization thresholds
MAX_FULL_MESSAGES = 3  # Keep last N messages in full
SUMMARIZE_THRESHOLD_MESSAGES = 5  # Trigger summarization when messages exceed this
SUMMARIZE_THRESHOLD_TOKENS = 2000  # Or when token count exceeds this
MAX_SUMMARY_TOKENS = 500  # Maximum tokens for summary

# Session configuration
SESSION_COLLECTION_NAME = "sessions"
DEFAULT_SESSION_TTL_HOURS = 24

# Summarization prompt
SUMMARIZATION_PROMPT = """Given the conversation history below, create a concise summary that captures:
1. Key questions asked and their intent
2. Important findings/insights discovered
3. Any constraints or filters the user specified
4. SQL patterns that worked well

Keep the summary under {max_tokens} tokens.

Conversation history:
{history}

Summary:"""
```

**Step 2: Commit**

```bash
git add app/modules/session/constants.py
git commit -m "feat(session): add session constants and configuration"
```

---

## Task 5: Implement Typesense Checkpointer

**Files:**
- Create: `app/modules/session/graph/checkpointer.py`
- Test: `tests/modules/session/test_checkpointer.py`

**Step 1: Write the failing test**

Create `tests/modules/session/test_checkpointer.py`:
```python
import pytest
from unittest.mock import AsyncMock, MagicMock
import json

from app.modules.session.graph.checkpointer import TypesenseCheckpointer


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    storage.find_by_id = AsyncMock(return_value=None)
    storage.update_or_create = AsyncMock()
    return storage


@pytest.fixture
def checkpointer(mock_storage):
    return TypesenseCheckpointer(storage=mock_storage)


@pytest.mark.asyncio
async def test_aget_returns_none_when_no_session(checkpointer, mock_storage):
    """Should return None when session doesn't exist."""
    mock_storage.find_by_id.return_value = None

    config = {"configurable": {"thread_id": "sess_123"}}
    result = await checkpointer.aget(config)

    assert result is None
    mock_storage.find_by_id.assert_called_once()


@pytest.mark.asyncio
async def test_aget_returns_checkpoint_when_exists(checkpointer, mock_storage):
    """Should return deserialized checkpoint when session exists."""
    checkpoint_data = {
        "v": 1,
        "ts": "2024-01-01T00:00:00",
        "channel_values": {"messages": []},
        "channel_versions": {},
        "versions_seen": {}
    }
    mock_storage.find_by_id.return_value = {
        "id": "sess_123",
        "checkpoint": json.dumps(checkpoint_data)
    }

    config = {"configurable": {"thread_id": "sess_123"}}
    result = await checkpointer.aget(config)

    assert result is not None


@pytest.mark.asyncio
async def test_aput_saves_checkpoint(checkpointer, mock_storage):
    """Should serialize and save checkpoint."""
    config = {"configurable": {"thread_id": "sess_123"}}
    checkpoint = {
        "v": 1,
        "ts": "2024-01-01T00:00:00",
        "id": "checkpoint_1",
        "channel_values": {},
        "channel_versions": {},
        "versions_seen": {}
    }
    metadata = {}

    await checkpointer.aput(config, checkpoint, metadata, {})

    mock_storage.update_or_create.assert_called_once()
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && uv run pytest tests/modules/session/test_checkpointer.py -v`

Expected: FAIL with "ImportError"

**Step 3: Write the implementation**

Update `app/modules/session/graph/checkpointer.py`:
```python
"""Typesense-backed checkpointer for LangGraph session persistence."""
import json
import time
from typing import Any, AsyncIterator, Optional, Sequence, Tuple

from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
)
from langchain_core.runnables import RunnableConfig

from app.data.db.storage import Storage
from app.modules.session.constants import SESSION_COLLECTION_NAME


class TypesenseCheckpointer(BaseCheckpointSaver):
    """
    Custom LangGraph checkpointer that persists to Typesense.

    This enables session state to be saved and restored across
    multiple queries, allowing for resumable conversations.
    """

    def __init__(self, storage: Storage):
        """
        Initialize checkpointer with Typesense storage.

        Args:
            storage: Typesense storage instance
        """
        super().__init__()
        self.storage = storage
        self.collection = SESSION_COLLECTION_NAME

    def _get_thread_id(self, config: RunnableConfig) -> str:
        """Extract thread_id (session_id) from config."""
        return config["configurable"]["thread_id"]

    def _serialize(self, checkpoint: Checkpoint) -> str:
        """Serialize checkpoint to JSON string."""
        return json.dumps(checkpoint, default=str)

    def _deserialize(self, data: str) -> Checkpoint:
        """Deserialize checkpoint from JSON string."""
        return json.loads(data)

    async def aget(self, config: RunnableConfig) -> Optional[Checkpoint]:
        """
        Get the latest checkpoint for a session.

        Args:
            config: Runnable config containing thread_id

        Returns:
            Checkpoint if exists, None otherwise
        """
        thread_id = self._get_thread_id(config)
        doc = await self.storage.find_by_id(self.collection, thread_id)

        if doc and doc.get("checkpoint"):
            return self._deserialize(doc["checkpoint"])
        return None

    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """
        Get checkpoint tuple with metadata.

        Args:
            config: Runnable config containing thread_id

        Returns:
            CheckpointTuple if exists, None otherwise
        """
        thread_id = self._get_thread_id(config)
        doc = await self.storage.find_by_id(self.collection, thread_id)

        if doc and doc.get("checkpoint"):
            checkpoint = self._deserialize(doc["checkpoint"])
            metadata = doc.get("checkpoint_metadata", {})
            if isinstance(metadata, str):
                metadata = json.loads(metadata)

            return CheckpointTuple(
                config=config,
                checkpoint=checkpoint,
                metadata=metadata,
                parent_config=None
            )
        return None

    async def alist(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> AsyncIterator[CheckpointTuple]:
        """
        List checkpoints (single checkpoint per session in this implementation).

        Args:
            config: Runnable config containing thread_id
            filter: Optional filter criteria
            before: Optional config to get checkpoints before
            limit: Maximum number of checkpoints to return

        Yields:
            CheckpointTuple for each matching checkpoint
        """
        if config:
            tuple_result = await self.aget_tuple(config)
            if tuple_result:
                yield tuple_result

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict[str, Any]
    ) -> RunnableConfig:
        """
        Save checkpoint to Typesense.

        Args:
            config: Runnable config containing thread_id
            checkpoint: Checkpoint data to save
            metadata: Checkpoint metadata
            new_versions: New channel versions

        Returns:
            Updated config with checkpoint ID
        """
        thread_id = self._get_thread_id(config)

        await self.storage.update_or_create(
            self.collection,
            thread_id,
            {
                "checkpoint": self._serialize(checkpoint),
                "checkpoint_metadata": json.dumps(metadata) if metadata else "{}",
                "updated_at": int(time.time())
            }
        )

        return {
            **config,
            "configurable": {
                **config.get("configurable", {}),
                "checkpoint_id": checkpoint.get("id", thread_id)
            }
        }

    async def aput_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str
    ) -> None:
        """
        Save intermediate writes (not implemented for Typesense).

        For simplicity, this implementation only saves full checkpoints.
        """
        pass

    # Sync methods (delegate to async)
    def get(self, config: RunnableConfig) -> Optional[Checkpoint]:
        """Sync version of aget - not recommended for production."""
        import asyncio
        return asyncio.get_event_loop().run_until_complete(self.aget(config))

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Sync version of aget_tuple - not recommended for production."""
        import asyncio
        return asyncio.get_event_loop().run_until_complete(self.aget_tuple(config))

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict[str, Any]
    ) -> RunnableConfig:
        """Sync version of aput - not recommended for production."""
        import asyncio
        return asyncio.get_event_loop().run_until_complete(
            self.aput(config, checkpoint, metadata, new_versions)
        )

    def put_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str
    ) -> None:
        """Sync version of aput_writes."""
        pass
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && uv run pytest tests/modules/session/test_checkpointer.py -v`

Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add app/modules/session/graph/checkpointer.py tests/modules/session/test_checkpointer.py
git commit -m "feat(session): implement TypesenseCheckpointer for LangGraph persistence"
```

---

## Task 6: Implement Session Graph Nodes

**Files:**
- Update: `app/modules/session/graph/nodes.py`
- Test: `tests/modules/session/test_graph_nodes.py`

**Step 1: Write the failing test**

Create `tests/modules/session/test_graph_nodes.py`:
```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.modules.session.graph.state import SessionState, create_initial_state
from app.modules.session.graph.nodes import (
    build_context_node,
    should_summarize,
    format_context_for_llm,
)


def test_should_summarize_when_messages_exceed_threshold():
    """Should return True when messages exceed threshold."""
    state = create_initial_state("sess_123", "db_456")
    state["messages"] = [{"id": f"msg_{i}", "role": "human", "query": f"Query {i}"} for i in range(6)]

    assert should_summarize(state) is True


def test_should_not_summarize_when_few_messages():
    """Should return False when messages are under threshold."""
    state = create_initial_state("sess_123", "db_456")
    state["messages"] = [{"id": "msg_1", "role": "human", "query": "Query 1"}]

    assert should_summarize(state) is False


def test_format_context_for_llm_with_summary():
    """Should include summary and recent messages."""
    state = create_initial_state("sess_123", "db_456")
    state["summary"] = "Previous discussion about sales data."
    state["messages"] = [
        {"id": "msg_1", "role": "human", "query": "Show revenue", "sql": "SELECT SUM(revenue)...", "results_summary": "Total: $1M"},
        {"id": "msg_2", "role": "human", "query": "By region", "sql": "SELECT region, SUM(revenue)...", "results_summary": "Top: West"},
    ]

    context = format_context_for_llm(state)

    assert "Previous discussion about sales data" in context
    assert "Show revenue" in context
    assert "By region" in context


def test_format_context_for_llm_without_summary():
    """Should only include recent messages when no summary."""
    state = create_initial_state("sess_123", "db_456")
    state["messages"] = [
        {"id": "msg_1", "role": "human", "query": "Show customers", "sql": "SELECT * FROM customers", "results_summary": "10 rows"},
    ]

    context = format_context_for_llm(state)

    assert "Show customers" in context
    assert "Previous context" not in context
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && uv run pytest tests/modules/session/test_graph_nodes.py -v`

Expected: FAIL with "ImportError"

**Step 3: Write the implementation**

Update `app/modules/session/graph/nodes.py`:
```python
"""Session graph nodes for LangGraph."""
import uuid
from datetime import datetime
from typing import Any

from app.modules.session.graph.state import SessionState, MessageDict
from app.modules.session.constants import (
    MAX_FULL_MESSAGES,
    SUMMARIZE_THRESHOLD_MESSAGES,
    SUMMARIZE_THRESHOLD_TOKENS,
    MAX_SUMMARY_TOKENS,
    SUMMARIZATION_PROMPT,
)


def should_summarize(state: SessionState) -> bool:
    """
    Determine if conversation history should be summarized.

    Args:
        state: Current session state

    Returns:
        True if summarization is needed
    """
    message_count = len(state.get("messages", []))
    return message_count > SUMMARIZE_THRESHOLD_MESSAGES


def format_context_for_llm(state: SessionState) -> str:
    """
    Format conversation context for LLM consumption.

    Combines summary (if exists) with recent full messages.

    Args:
        state: Current session state

    Returns:
        Formatted context string
    """
    context_parts = []

    # Add summary if exists
    if state.get("summary"):
        context_parts.append(f"Previous context:\n{state['summary']}")

    # Add recent messages in full
    messages = state.get("messages", [])
    recent_messages = messages[-MAX_FULL_MESSAGES:] if messages else []

    for msg in recent_messages:
        parts = [f"Q: {msg.get('query', '')}"]
        if msg.get("sql"):
            parts.append(f"SQL: {msg['sql']}")
        if msg.get("results_summary"):
            parts.append(f"Result: {msg['results_summary']}")
        context_parts.append("\n".join(parts))

    return "\n\n".join(context_parts)


def format_history_for_summarization(messages: list[MessageDict]) -> str:
    """
    Format message history for summarization prompt.

    Args:
        messages: List of messages to summarize

    Returns:
        Formatted history string
    """
    history_parts = []
    for msg in messages:
        entry = f"Q: {msg.get('query', '')}"
        if msg.get("sql"):
            entry += f"\nSQL: {msg['sql']}"
        if msg.get("results_summary"):
            entry += f"\nResult: {msg['results_summary']}"
        if msg.get("analysis"):
            entry += f"\nAnalysis: {msg['analysis'][:200]}..."  # Truncate long analysis
        history_parts.append(entry)
    return "\n---\n".join(history_parts)


async def build_context_node(state: SessionState) -> dict[str, Any]:
    """
    Build context from conversation history.

    This node prepares the context for SQL generation by
    combining summary and recent messages.

    Args:
        state: Current session state

    Returns:
        State update with built context (stored in metadata)
    """
    context = format_context_for_llm(state)

    return {
        "metadata": {
            **state.get("metadata", {}),
            "built_context": context
        },
        "status": "processing"
    }


async def receive_query_node(state: SessionState, query: str) -> dict[str, Any]:
    """
    Receive and store new query.

    Args:
        state: Current session state
        query: New natural language query

    Returns:
        State update with current query set
    """
    return {
        "current_query": query,
        "current_sql": None,
        "current_results": None,
        "current_analysis": None,
        "error": None,
        "status": "processing"
    }


async def generate_sql_node(
    state: SessionState,
    sql_generation_service: Any
) -> dict[str, Any]:
    """
    Generate SQL from natural language query.

    Uses existing SQL generation service with conversation context.

    Args:
        state: Current session state
        sql_generation_service: SQL generation service instance

    Returns:
        State update with generated SQL
    """
    context = state.get("metadata", {}).get("built_context", "")
    query = state["current_query"]
    db_connection_id = state["db_connection_id"]

    # Build prompt with context
    contextualized_query = query
    if context:
        contextualized_query = f"Context from previous conversation:\n{context}\n\nCurrent question: {query}"

    try:
        # Call existing SQL generation service
        result = await sql_generation_service.generate_sql(
            db_connection_id=db_connection_id,
            prompt=contextualized_query
        )

        return {
            "current_sql": result.sql if hasattr(result, 'sql') else str(result),
            "status": "processing"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


async def execute_sql_node(
    state: SessionState,
    sql_generation_service: Any
) -> dict[str, Any]:
    """
    Execute generated SQL query.

    Args:
        state: Current session state
        sql_generation_service: SQL generation service for execution

    Returns:
        State update with execution results
    """
    if state.get("error"):
        return {}  # Skip if already errored

    sql = state["current_sql"]
    if not sql:
        return {"error": "No SQL to execute", "status": "error"}

    try:
        # Execute SQL using existing service
        results = await sql_generation_service.execute_sql(sql)

        # Create summary of results for context
        row_count = len(results) if results else 0
        results_summary = f"{row_count} rows returned"
        if results and row_count > 0:
            # Add first row preview
            first_row = results[0]
            preview = ", ".join(f"{k}={v}" for k, v in list(first_row.items())[:3])
            results_summary += f" (e.g., {preview})"

        return {
            "current_results": results,
            "metadata": {
                **state.get("metadata", {}),
                "results_summary": results_summary
            },
            "status": "processing"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


async def generate_analysis_node(
    state: SessionState,
    analysis_service: Any
) -> dict[str, Any]:
    """
    Generate analysis from SQL results.

    Args:
        state: Current session state
        analysis_service: Analysis service instance

    Returns:
        State update with analysis
    """
    if state.get("error"):
        return {}  # Skip if already errored

    results = state["current_results"]
    query = state["current_query"]
    sql = state["current_sql"]

    if not results:
        return {
            "current_analysis": {"summary": "No results to analyze."},
            "status": "processing"
        }

    try:
        analysis = await analysis_service.generate_analysis(
            query=query,
            sql=sql,
            results=results
        )

        return {
            "current_analysis": analysis.to_dict() if hasattr(analysis, 'to_dict') else analysis,
            "status": "processing"
        }
    except Exception as e:
        # Analysis failure is non-fatal
        return {
            "current_analysis": {"summary": f"Analysis unavailable: {str(e)}"},
            "status": "processing"
        }


async def summarize_node(
    state: SessionState,
    llm: Any
) -> dict[str, Any]:
    """
    Summarize older conversation history.

    Called when message count exceeds threshold.

    Args:
        state: Current session state
        llm: Language model for summarization

    Returns:
        State update with new summary and trimmed messages
    """
    if not should_summarize(state):
        return {}

    messages = state.get("messages", [])

    # Messages to summarize (older ones)
    messages_to_summarize = messages[:-MAX_FULL_MESSAGES]

    # Combine existing summary with messages to summarize
    existing_summary = state.get("summary", "")
    history = format_history_for_summarization(messages_to_summarize)

    if existing_summary:
        history = f"Previous summary:\n{existing_summary}\n\nNew messages:\n{history}"

    prompt = SUMMARIZATION_PROMPT.format(
        max_tokens=MAX_SUMMARY_TOKENS,
        history=history
    )

    try:
        response = await llm.ainvoke(prompt)
        new_summary = response.content if hasattr(response, 'content') else str(response)

        # Keep only recent messages
        recent_messages = messages[-MAX_FULL_MESSAGES:]

        return {
            "summary": new_summary,
            "messages": recent_messages
        }
    except Exception as e:
        # Summarization failure is non-fatal, keep messages
        return {}


async def save_message_node(state: SessionState) -> dict[str, Any]:
    """
    Save current query/response as a message.

    Args:
        state: Current session state

    Returns:
        State update with new message added
    """
    if state.get("error"):
        # Still save errored queries for context
        pass

    new_message: MessageDict = {
        "id": f"msg_{uuid.uuid4().hex[:8]}",
        "role": "assistant",
        "query": state["current_query"] or "",
        "sql": state["current_sql"],
        "results_summary": state.get("metadata", {}).get("results_summary"),
        "analysis": state["current_analysis"].get("summary") if state.get("current_analysis") else None,
        "timestamp": datetime.now().isoformat()
    }

    messages = state.get("messages", []).copy()
    messages.append(new_message)

    return {
        "messages": messages,
        "status": "idle" if not state.get("error") else "error"
    }
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && uv run pytest tests/modules/session/test_graph_nodes.py -v`

Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add app/modules/session/graph/nodes.py tests/modules/session/test_graph_nodes.py
git commit -m "feat(session): implement session graph nodes"
```

---

## Task 7: Implement Session Graph Builder

**Files:**
- Update: `app/modules/session/graph/__init__.py`
- Test: `tests/modules/session/test_graph.py`

**Step 1: Write the failing test**

Create `tests/modules/session/test_graph.py`:
```python
import pytest
from unittest.mock import MagicMock, AsyncMock

from app.modules.session.graph import build_session_graph


def test_build_session_graph_returns_compiled_graph():
    """Should return a compiled LangGraph."""
    mock_sql_service = MagicMock()
    mock_analysis_service = MagicMock()
    mock_llm = MagicMock()
    mock_checkpointer = MagicMock()

    graph = build_session_graph(
        sql_generation_service=mock_sql_service,
        analysis_service=mock_analysis_service,
        llm=mock_llm,
        checkpointer=mock_checkpointer
    )

    assert graph is not None
    # LangGraph compiled graphs have these attributes
    assert hasattr(graph, 'invoke') or hasattr(graph, 'ainvoke')


def test_build_session_graph_has_expected_nodes():
    """Graph should have expected node names."""
    mock_sql_service = MagicMock()
    mock_analysis_service = MagicMock()
    mock_llm = MagicMock()
    mock_checkpointer = MagicMock()

    graph = build_session_graph(
        sql_generation_service=mock_sql_service,
        analysis_service=mock_analysis_service,
        llm=mock_llm,
        checkpointer=mock_checkpointer
    )

    # The graph should be built successfully
    assert graph is not None
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && uv run pytest tests/modules/session/test_graph.py -v`

Expected: FAIL with "ImportError"

**Step 3: Write the implementation**

Update `app/modules/session/graph/__init__.py`:
```python
"""LangGraph session graph components."""
from typing import Any, Literal
from functools import partial

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver

from app.modules.session.graph.state import SessionState
from app.modules.session.graph.nodes import (
    build_context_node,
    generate_sql_node,
    execute_sql_node,
    generate_analysis_node,
    summarize_node,
    save_message_node,
    should_summarize,
)


def build_session_graph(
    sql_generation_service: Any,
    analysis_service: Any,
    llm: Any,
    checkpointer: BaseCheckpointSaver | None = None
):
    """
    Build the session LangGraph.

    Graph flow:
    START -> build_context -> generate_sql -> execute_sql ->
    generate_analysis -> check_summarize -> [summarize?] -> save_message -> END

    Args:
        sql_generation_service: SQL generation service instance
        analysis_service: Analysis service instance
        llm: Language model for summarization
        checkpointer: Optional checkpointer for persistence

    Returns:
        Compiled LangGraph
    """
    # Create graph with SessionState
    graph = StateGraph(SessionState)

    # Add nodes with bound services
    graph.add_node("build_context", build_context_node)

    graph.add_node(
        "generate_sql",
        partial(generate_sql_node, sql_generation_service=sql_generation_service)
    )

    graph.add_node(
        "execute_sql",
        partial(execute_sql_node, sql_generation_service=sql_generation_service)
    )

    graph.add_node(
        "generate_analysis",
        partial(generate_analysis_node, analysis_service=analysis_service)
    )

    graph.add_node(
        "summarize",
        partial(summarize_node, llm=llm)
    )

    graph.add_node("save_message", save_message_node)

    # Define edges
    graph.set_entry_point("build_context")

    graph.add_edge("build_context", "generate_sql")
    graph.add_edge("generate_sql", "execute_sql")
    graph.add_edge("execute_sql", "generate_analysis")

    # Conditional edge for summarization
    def check_summarize(state: SessionState) -> Literal["summarize", "save_message"]:
        if should_summarize(state):
            return "summarize"
        return "save_message"

    graph.add_conditional_edges(
        "generate_analysis",
        check_summarize,
        {
            "summarize": "summarize",
            "save_message": "save_message"
        }
    )

    graph.add_edge("summarize", "save_message")
    graph.add_edge("save_message", END)

    # Compile with checkpointer
    return graph.compile(checkpointer=checkpointer)


__all__ = [
    "build_session_graph",
    "SessionState",
]
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && uv run pytest tests/modules/session/test_graph.py -v`

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add app/modules/session/graph/__init__.py tests/modules/session/test_graph.py
git commit -m "feat(session): implement session graph builder"
```

---

## Task 8: Implement Session Repository

**Files:**
- Update: `app/modules/session/repositories/__init__.py`
- Test: `tests/modules/session/test_repository.py`

**Step 1: Write the failing test**

Create `tests/modules/session/test_repository.py`:
```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.modules.session.repositories import SessionRepository
from app.modules.session.models import Session, SessionStatus


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    storage.insert_one = AsyncMock(return_value="sess_123")
    storage.find_by_id = AsyncMock(return_value=None)
    storage.find = AsyncMock(return_value=[])
    storage.update_or_create = AsyncMock()
    storage.delete = AsyncMock()
    return storage


@pytest.fixture
def repository(mock_storage):
    return SessionRepository(storage=mock_storage)


@pytest.mark.asyncio
async def test_create_session(repository, mock_storage):
    """Should create session and return ID."""
    session_id = await repository.create(
        db_connection_id="db_456",
        metadata={"user": "test"}
    )

    assert session_id is not None
    mock_storage.insert_one.assert_called_once()


@pytest.mark.asyncio
async def test_get_session_returns_none_when_not_found(repository, mock_storage):
    """Should return None when session doesn't exist."""
    mock_storage.find_by_id.return_value = None

    session = await repository.get("nonexistent")

    assert session is None


@pytest.mark.asyncio
async def test_get_session_returns_session_when_found(repository, mock_storage):
    """Should return Session when found."""
    mock_storage.find_by_id.return_value = {
        "id": "sess_123",
        "db_connection_id": "db_456",
        "messages": [],
        "status": "idle",
        "metadata": {},
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    session = await repository.get("sess_123")

    assert session is not None
    assert session.id == "sess_123"


@pytest.mark.asyncio
async def test_list_sessions_by_db_connection(repository, mock_storage):
    """Should list sessions filtered by db_connection_id."""
    mock_storage.find.return_value = [
        {
            "id": "sess_1",
            "db_connection_id": "db_456",
            "messages": [],
            "status": "idle",
            "metadata": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]

    sessions = await repository.list(db_connection_id="db_456")

    assert len(sessions) == 1
    assert sessions[0].db_connection_id == "db_456"


@pytest.mark.asyncio
async def test_delete_session(repository, mock_storage):
    """Should delete session."""
    await repository.delete("sess_123")

    mock_storage.delete.assert_called_once()
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && uv run pytest tests/modules/session/test_repository.py -v`

Expected: FAIL with "ImportError"

**Step 3: Write the implementation**

Update `app/modules/session/repositories/__init__.py`:
```python
"""Session repository for Typesense storage."""
import uuid
from datetime import datetime
from typing import Optional

from app.data.db.storage import Storage
from app.modules.session.models import Session, SessionStatus
from app.modules.session.constants import SESSION_COLLECTION_NAME


class SessionRepository:
    """
    Repository for session CRUD operations.

    Uses Typesense as the storage backend.
    """

    def __init__(self, storage: Storage):
        """
        Initialize repository with storage.

        Args:
            storage: Typesense storage instance
        """
        self.storage = storage
        self.collection = SESSION_COLLECTION_NAME

    async def create(
        self,
        db_connection_id: str,
        metadata: dict | None = None
    ) -> str:
        """
        Create a new session.

        Args:
            db_connection_id: Database connection for this session
            metadata: Optional custom metadata

        Returns:
            Created session ID
        """
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        now = datetime.now()

        session_data = {
            "id": session_id,
            "db_connection_id": db_connection_id,
            "messages": "[]",  # JSON string for Typesense
            "summary": None,
            "status": SessionStatus.IDLE.value,
            "metadata": metadata or {},
            "checkpoint": None,
            "checkpoint_metadata": "{}",
            "created_at": int(now.timestamp()),
            "updated_at": int(now.timestamp())
        }

        await self.storage.insert_one(self.collection, session_data)
        return session_id

    async def get(self, session_id: str) -> Optional[Session]:
        """
        Get session by ID.

        Args:
            session_id: Session ID to retrieve

        Returns:
            Session if found, None otherwise
        """
        doc = await self.storage.find_by_id(self.collection, session_id)

        if not doc:
            return None

        return self._doc_to_session(doc)

    async def list(
        self,
        db_connection_id: str | None = None,
        status: SessionStatus | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Session]:
        """
        List sessions with optional filters.

        Args:
            db_connection_id: Filter by database connection
            status: Filter by status
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of matching sessions
        """
        filters = {}
        if db_connection_id:
            filters["db_connection_id"] = db_connection_id
        if status:
            filters["status"] = status.value

        docs = await self.storage.find(
            self.collection,
            filters=filters,
            limit=limit,
            offset=offset,
            sort_by="updated_at",
            sort_order="desc"
        )

        return [self._doc_to_session(doc) for doc in docs]

    async def update(self, session: Session) -> None:
        """
        Update an existing session.

        Args:
            session: Session with updated data
        """
        import json

        session_data = {
            "messages": json.dumps([m.to_dict() for m in session.messages]),
            "summary": session.summary,
            "status": session.status.value,
            "metadata": session.metadata,
            "updated_at": int(datetime.now().timestamp())
        }

        await self.storage.update_or_create(
            self.collection,
            session.id,
            session_data
        )

    async def delete(self, session_id: str) -> None:
        """
        Delete a session.

        Args:
            session_id: Session ID to delete
        """
        await self.storage.delete(self.collection, session_id)

    async def close(self, session_id: str) -> None:
        """
        Close a session (soft delete / status change).

        Args:
            session_id: Session ID to close
        """
        await self.storage.update_or_create(
            self.collection,
            session_id,
            {
                "status": SessionStatus.CLOSED.value,
                "updated_at": int(datetime.now().timestamp())
            }
        )

    def _doc_to_session(self, doc: dict) -> Session:
        """
        Convert Typesense document to Session model.

        Args:
            doc: Raw document from Typesense

        Returns:
            Session instance
        """
        import json
        from app.modules.session.models import Message

        # Parse messages from JSON string
        messages_raw = doc.get("messages", "[]")
        if isinstance(messages_raw, str):
            messages_data = json.loads(messages_raw)
        else:
            messages_data = messages_raw

        messages = [Message.from_dict(m) for m in messages_data]

        # Parse timestamps
        created_at = doc.get("created_at")
        updated_at = doc.get("updated_at")

        if isinstance(created_at, int):
            created_at = datetime.fromtimestamp(created_at)
        elif isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = datetime.now()

        if isinstance(updated_at, int):
            updated_at = datetime.fromtimestamp(updated_at)
        elif isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        else:
            updated_at = datetime.now()

        return Session(
            id=doc["id"],
            db_connection_id=doc["db_connection_id"],
            messages=messages,
            summary=doc.get("summary"),
            status=SessionStatus(doc.get("status", "idle")),
            metadata=doc.get("metadata", {}),
            created_at=created_at,
            updated_at=updated_at
        )


__all__ = ["SessionRepository"]
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && uv run pytest tests/modules/session/test_repository.py -v`

Expected: PASS (5 tests)

**Step 5: Commit**

```bash
git add app/modules/session/repositories/__init__.py tests/modules/session/test_repository.py
git commit -m "feat(session): implement SessionRepository for Typesense storage"
```

---

## Task 9: Implement Session Service with Streaming

**Files:**
- Update: `app/modules/session/services/__init__.py`
- Test: `tests/modules/session/test_service.py`

**Step 1: Write the failing test**

Create `tests/modules/session/test_service.py`:
```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from app.modules.session.services import SessionService
from app.modules.session.models import Session, SessionStatus


@pytest.fixture
def mock_repository():
    repo = MagicMock()
    repo.create = AsyncMock(return_value="sess_123")
    repo.get = AsyncMock(return_value=None)
    repo.list = AsyncMock(return_value=[])
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.close = AsyncMock()
    return repo


@pytest.fixture
def mock_graph():
    graph = MagicMock()
    graph.astream_events = MagicMock()
    return graph


@pytest.fixture
def mock_checkpointer():
    return MagicMock()


@pytest.fixture
def service(mock_repository, mock_graph, mock_checkpointer):
    return SessionService(
        repository=mock_repository,
        graph=mock_graph,
        checkpointer=mock_checkpointer
    )


@pytest.mark.asyncio
async def test_create_session(service, mock_repository):
    """Should create session and return ID."""
    session_id = await service.create_session(
        db_connection_id="db_456",
        metadata={"user": "test"}
    )

    assert session_id == "sess_123"
    mock_repository.create.assert_called_once_with(
        db_connection_id="db_456",
        metadata={"user": "test"}
    )


@pytest.mark.asyncio
async def test_get_session(service, mock_repository):
    """Should get session by ID."""
    from datetime import datetime
    mock_repository.get.return_value = Session(
        id="sess_123",
        db_connection_id="db_456",
        messages=[],
        status=SessionStatus.IDLE,
        metadata={},
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    session = await service.get_session("sess_123")

    assert session is not None
    assert session.id == "sess_123"


@pytest.mark.asyncio
async def test_list_sessions(service, mock_repository):
    """Should list sessions."""
    sessions = await service.list_sessions(db_connection_id="db_456")

    mock_repository.list.assert_called_once()


@pytest.mark.asyncio
async def test_delete_session(service, mock_repository):
    """Should delete session."""
    await service.delete_session("sess_123")

    mock_repository.delete.assert_called_once_with("sess_123")
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && uv run pytest tests/modules/session/test_service.py -v`

Expected: FAIL with "ImportError"

**Step 3: Write the implementation**

Update `app/modules/session/services/__init__.py`:
```python
"""Session service for orchestrating graph and streaming."""
import json
from typing import AsyncGenerator, Any, Optional

from app.modules.session.repositories import SessionRepository
from app.modules.session.models import Session, SessionStatus
from app.modules.session.graph.state import create_initial_state
from app.modules.session.constants import STATUS_MESSAGES


class SessionService:
    """
    Service for session management and query streaming.

    Orchestrates the session graph and handles SSE streaming.
    """

    def __init__(
        self,
        repository: SessionRepository,
        graph: Any,  # CompiledGraph
        checkpointer: Any  # TypesenseCheckpointer
    ):
        """
        Initialize session service.

        Args:
            repository: Session repository
            graph: Compiled LangGraph
            checkpointer: Checkpointer for persistence
        """
        self.repository = repository
        self.graph = graph
        self.checkpointer = checkpointer

    async def create_session(
        self,
        db_connection_id: str,
        metadata: dict | None = None
    ) -> str:
        """
        Create a new session.

        Args:
            db_connection_id: Database connection for this session
            metadata: Optional custom metadata

        Returns:
            Created session ID
        """
        return await self.repository.create(
            db_connection_id=db_connection_id,
            metadata=metadata
        )

    async def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get session by ID.

        Args:
            session_id: Session ID to retrieve

        Returns:
            Session if found, None otherwise
        """
        return await self.repository.get(session_id)

    async def list_sessions(
        self,
        db_connection_id: str | None = None,
        status: SessionStatus | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Session]:
        """
        List sessions with optional filters.

        Args:
            db_connection_id: Filter by database connection
            status: Filter by status
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of matching sessions
        """
        return await self.repository.list(
            db_connection_id=db_connection_id,
            status=status,
            limit=limit,
            offset=offset
        )

    async def delete_session(self, session_id: str) -> None:
        """
        Delete a session.

        Args:
            session_id: Session ID to delete
        """
        await self.repository.delete(session_id)

    async def close_session(self, session_id: str) -> None:
        """
        Close a session (mark as closed).

        Args:
            session_id: Session ID to close
        """
        await self.repository.close(session_id)

    async def stream_query(
        self,
        session_id: str,
        query: str
    ) -> AsyncGenerator[str, None]:
        """
        Stream query processing via SSE.

        Executes the session graph and yields SSE events.

        Args:
            session_id: Session ID
            query: Natural language query

        Yields:
            SSE formatted event strings
        """
        # Get session to validate it exists
        session = await self.repository.get(session_id)
        if not session:
            yield self._format_sse("error", {"message": "Session not found"})
            return

        if session.status == SessionStatus.CLOSED:
            yield self._format_sse("error", {"message": "Session is closed"})
            return

        # Prepare config for LangGraph
        config = {
            "configurable": {
                "thread_id": session_id
            }
        }

        # Prepare initial state update with query
        input_state = {
            "current_query": query,
            "db_connection_id": session.db_connection_id
        }

        try:
            # Stream events from LangGraph
            async for event in self.graph.astream_events(
                input_state,
                config=config,
                version="v2"
            ):
                sse_event = self._process_graph_event(event)
                if sse_event:
                    yield sse_event

            # Final done event
            yield self._format_sse("done", {
                "session_id": session_id,
                "status": "complete"
            })

        except Exception as e:
            yield self._format_sse("error", {"message": str(e)})

    def _process_graph_event(self, event: dict) -> Optional[str]:
        """
        Process LangGraph event and convert to SSE.

        Args:
            event: LangGraph event

        Returns:
            SSE formatted string or None
        """
        event_type = event.get("event")

        if event_type == "on_chain_start":
            node = event.get("name", "")
            if node in STATUS_MESSAGES:
                return self._format_sse("status", {
                    "step": node,
                    "message": STATUS_MESSAGES[node]
                })

        elif event_type == "on_chat_model_stream":
            chunk = event.get("data", {}).get("chunk")
            if chunk:
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if content:
                    return self._format_sse("chunk", {
                        "type": "text",
                        "content": content
                    })

        elif event_type == "on_chain_end":
            node = event.get("name", "")
            output = event.get("data", {}).get("output", {})

            if node == "generate_sql" and output.get("current_sql"):
                return self._format_sse("chunk", {
                    "type": "sql",
                    "content": output["current_sql"]
                })

            elif node == "execute_sql" and output.get("current_results"):
                return self._format_sse("chunk", {
                    "type": "results",
                    "content": output["current_results"]
                })

            elif node == "generate_analysis" and output.get("current_analysis"):
                return self._format_sse("chunk", {
                    "type": "analysis",
                    "content": output["current_analysis"]
                })

        return None

    def _format_sse(self, event_type: str, data: dict) -> str:
        """
        Format data as SSE event.

        Args:
            event_type: Event type (status, chunk, done, error)
            data: Event data

        Returns:
            SSE formatted string
        """
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


__all__ = ["SessionService"]
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && uv run pytest tests/modules/session/test_service.py -v`

Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add app/modules/session/services/__init__.py tests/modules/session/test_service.py
git commit -m "feat(session): implement SessionService with SSE streaming"
```

---

## Task 10: Implement API Request/Response Models

**Files:**
- Create: `app/modules/session/api/__init__.py`
- Create: `app/modules/session/api/requests.py`
- Create: `app/modules/session/api/responses.py`

**Step 1: Create API models directory**

```bash
mkdir -p app/modules/session/api
```

**Step 2: Write request models**

Create `app/modules/session/api/__init__.py`:
```python
"""Session API models."""
from app.modules.session.api.requests import (
    CreateSessionRequest,
    SessionQueryRequest,
)
from app.modules.session.api.responses import (
    SessionResponse,
    SessionListResponse,
    MessageResponse,
)

__all__ = [
    "CreateSessionRequest",
    "SessionQueryRequest",
    "SessionResponse",
    "SessionListResponse",
    "MessageResponse",
]
```

Create `app/modules/session/api/requests.py`:
```python
"""Session API request models."""
from pydantic import BaseModel, Field
from typing import Optional


class CreateSessionRequest(BaseModel):
    """Request to create a new session."""
    db_connection_id: str = Field(..., description="Database connection ID for this session")
    metadata: Optional[dict] = Field(default=None, description="Optional custom metadata")


class SessionQueryRequest(BaseModel):
    """Request to query within a session."""
    query: str = Field(..., description="Natural language query", min_length=1)
```

Create `app/modules/session/api/responses.py`:
```python
"""Session API response models."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MessageResponse(BaseModel):
    """Response model for a message in conversation history."""
    id: str
    role: str
    query: str
    sql: Optional[str] = None
    results_summary: Optional[str] = None
    analysis: Optional[str] = None
    timestamp: datetime


class SessionResponse(BaseModel):
    """Response model for session details."""
    id: str
    db_connection_id: str
    status: str
    messages: List[MessageResponse] = Field(default_factory=list)
    summary: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_session(cls, session) -> "SessionResponse":
        """Create from Session model."""
        return cls(
            id=session.id,
            db_connection_id=session.db_connection_id,
            status=session.status.value,
            messages=[
                MessageResponse(
                    id=m.id,
                    role=m.role,
                    query=m.query,
                    sql=m.sql,
                    results_summary=m.results_summary,
                    analysis=m.analysis,
                    timestamp=m.timestamp
                )
                for m in session.messages
            ],
            summary=session.summary,
            metadata=session.metadata,
            created_at=session.created_at,
            updated_at=session.updated_at
        )


class SessionListResponse(BaseModel):
    """Response model for listing sessions."""
    sessions: List[SessionResponse]
    total: int
    limit: int
    offset: int
```

**Step 3: Commit**

```bash
git add app/modules/session/api/
git commit -m "feat(session): add API request/response models"
```

---

## Task 11: Implement API Endpoints

**Files:**
- Create: `app/modules/session/api/endpoints.py`
- Modify: `app/api/__init__.py`

**Step 1: Write endpoint implementation**

Create `app/modules/session/api/endpoints.py`:
```python
"""Session API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional

from app.modules.session.api.requests import CreateSessionRequest, SessionQueryRequest
from app.modules.session.api.responses import SessionResponse, SessionListResponse
from app.modules.session.services import SessionService
from app.modules.session.models import SessionStatus

# This will be injected via dependency
def get_session_service() -> SessionService:
    """Dependency to get session service instance."""
    # Will be implemented in dependency injection setup
    raise NotImplementedError("Session service dependency not configured")


router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=dict)
async def create_session(
    body: CreateSessionRequest,
    service: SessionService = Depends(get_session_service)
):
    """
    Create a new session.

    Returns the created session ID.
    """
    session_id = await service.create_session(
        db_connection_id=body.db_connection_id,
        metadata=body.metadata
    )
    return {"session_id": session_id}


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    db_connection_id: Optional[str] = Query(None, description="Filter by database connection"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    service: SessionService = Depends(get_session_service)
):
    """
    List sessions with optional filters.
    """
    status_enum = SessionStatus(status) if status else None

    sessions = await service.list_sessions(
        db_connection_id=db_connection_id,
        status=status_enum,
        limit=limit,
        offset=offset
    )

    return SessionListResponse(
        sessions=[SessionResponse.from_session(s) for s in sessions],
        total=len(sessions),  # TODO: Add proper count query
        limit=limit,
        offset=offset
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    """
    Get session details and conversation history.
    """
    session = await service.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse.from_session(session)


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    """
    Delete a session.
    """
    session = await service.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await service.delete_session(session_id)
    return {"status": "deleted"}


@router.post("/{session_id}/close")
async def close_session(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    """
    Close a session (mark as inactive).
    """
    session = await service.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await service.close_session(session_id)
    return {"status": "closed"}


@router.post("/{session_id}/query/stream")
async def query_session_stream(
    session_id: str,
    body: SessionQueryRequest,
    service: SessionService = Depends(get_session_service)
):
    """
    Send a query to the session and stream the response via SSE.

    Returns a stream of Server-Sent Events with:
    - status events: Processing step updates
    - chunk events: SQL, results, and analysis chunks
    - done event: Final completion signal
    - error event: Error information if failed
    """
    return StreamingResponse(
        service.stream_query(session_id, body.query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


__all__ = ["router", "get_session_service"]
```

**Step 2: Commit**

```bash
git add app/modules/session/api/endpoints.py
git commit -m "feat(session): implement API endpoints with SSE streaming"
```

---

## Task 12: Wire Up Dependencies and Register Routes

**Files:**
- Create: `app/modules/session/dependencies.py`
- Modify: `app/api/__init__.py`

**Step 1: Create dependencies module**

Create `app/modules/session/dependencies.py`:
```python
"""Session module dependency injection."""
from functools import lru_cache
from typing import Any

from app.data.db.storage import Storage
from app.modules.session.repositories import SessionRepository
from app.modules.session.services import SessionService
from app.modules.session.graph import build_session_graph
from app.modules.session.graph.checkpointer import TypesenseCheckpointer


class SessionDependencies:
    """
    Container for session module dependencies.

    Lazily initializes and caches service instances.
    """

    _instance: "SessionDependencies | None" = None
    _service: SessionService | None = None

    def __init__(
        self,
        storage: Storage,
        sql_generation_service: Any,
        analysis_service: Any,
        llm: Any
    ):
        """
        Initialize dependencies.

        Args:
            storage: Typesense storage
            sql_generation_service: SQL generation service
            analysis_service: Analysis service
            llm: Language model for summarization
        """
        self.storage = storage
        self.sql_generation_service = sql_generation_service
        self.analysis_service = analysis_service
        self.llm = llm

    @classmethod
    def configure(
        cls,
        storage: Storage,
        sql_generation_service: Any,
        analysis_service: Any,
        llm: Any
    ) -> None:
        """
        Configure session dependencies.

        Call this during application startup.
        """
        cls._instance = cls(
            storage=storage,
            sql_generation_service=sql_generation_service,
            analysis_service=analysis_service,
            llm=llm
        )

    @classmethod
    def get_service(cls) -> SessionService:
        """
        Get configured session service.

        Returns:
            SessionService instance

        Raises:
            RuntimeError: If dependencies not configured
        """
        if cls._instance is None:
            raise RuntimeError("Session dependencies not configured. Call configure() first.")

        if cls._service is None:
            # Build components
            repository = SessionRepository(cls._instance.storage)
            checkpointer = TypesenseCheckpointer(cls._instance.storage)

            graph = build_session_graph(
                sql_generation_service=cls._instance.sql_generation_service,
                analysis_service=cls._instance.analysis_service,
                llm=cls._instance.llm,
                checkpointer=checkpointer
            )

            cls._service = SessionService(
                repository=repository,
                graph=graph,
                checkpointer=checkpointer
            )

        return cls._service


def get_session_service() -> SessionService:
    """
    FastAPI dependency for session service.

    Returns:
        Configured SessionService instance
    """
    return SessionDependencies.get_service()


__all__ = ["SessionDependencies", "get_session_service"]
```

**Step 2: Read current API init file**

Run: `cat app/api/__init__.py` to see current structure

**Step 3: Update API routes**

Modify `app/api/__init__.py` to add:
```python
# Add to imports
from app.modules.session.api.endpoints import router as session_router

# Add to router includes (after existing routers)
router.include_router(session_router)
```

**Step 4: Commit**

```bash
git add app/modules/session/dependencies.py app/api/__init__.py
git commit -m "feat(session): wire up dependencies and register routes"
```

---

## Task 13: Create Typesense Collection Schema

**Files:**
- Create: `app/modules/session/schema.py`

**Step 1: Write schema definition**

Create `app/modules/session/schema.py`:
```python
"""Typesense collection schema for sessions."""

SESSIONS_SCHEMA = {
    "name": "sessions",
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "db_connection_id", "type": "string", "facet": True},
        {"name": "status", "type": "string", "facet": True},
        {"name": "summary", "type": "string", "optional": True},
        {"name": "messages", "type": "string"},  # JSON stringified array
        {"name": "checkpoint", "type": "string", "optional": True},  # LangGraph checkpoint
        {"name": "checkpoint_metadata", "type": "string", "optional": True},
        {"name": "metadata", "type": "object", "optional": True},
        {"name": "created_at", "type": "int64"},
        {"name": "updated_at", "type": "int64"},
    ],
    "default_sorting_field": "updated_at"
}


async def ensure_sessions_collection(storage) -> None:
    """
    Ensure sessions collection exists in Typesense.

    Creates the collection if it doesn't exist.

    Args:
        storage: Typesense storage instance
    """
    try:
        await storage.create_collection(SESSIONS_SCHEMA)
    except Exception as e:
        # Collection may already exist
        if "already exists" not in str(e).lower():
            raise


__all__ = ["SESSIONS_SCHEMA", "ensure_sessions_collection"]
```

**Step 2: Commit**

```bash
git add app/modules/session/schema.py
git commit -m "feat(session): add Typesense collection schema"
```

---

## Task 14: Integration Tests

**Files:**
- Create: `tests/modules/session/test_integration.py`

**Step 1: Write integration test**

Create `tests/modules/session/test_integration.py`:
```python
"""Integration tests for session module."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from app.modules.session.services import SessionService
from app.modules.session.repositories import SessionRepository
from app.modules.session.graph import build_session_graph
from app.modules.session.graph.checkpointer import TypesenseCheckpointer
from app.modules.session.models import Session, SessionStatus


@pytest.fixture
def mock_storage():
    """Create mock storage with async methods."""
    storage = MagicMock()
    storage.insert_one = AsyncMock(return_value="sess_123")
    storage.find_by_id = AsyncMock(return_value=None)
    storage.find = AsyncMock(return_value=[])
    storage.update_or_create = AsyncMock()
    storage.delete = AsyncMock()
    return storage


@pytest.fixture
def mock_sql_service():
    """Create mock SQL generation service."""
    service = MagicMock()
    service.generate_sql = AsyncMock(return_value=MagicMock(sql="SELECT * FROM users"))
    service.execute_sql = AsyncMock(return_value=[{"id": 1, "name": "Test"}])
    return service


@pytest.fixture
def mock_analysis_service():
    """Create mock analysis service."""
    service = MagicMock()
    service.generate_analysis = AsyncMock(return_value=MagicMock(
        to_dict=lambda: {"summary": "Test analysis"}
    ))
    return service


@pytest.fixture
def mock_llm():
    """Create mock LLM."""
    llm = MagicMock()
    llm.ainvoke = AsyncMock(return_value=MagicMock(content="Summary of conversation"))
    return llm


@pytest.mark.asyncio
async def test_full_session_flow(mock_storage, mock_sql_service, mock_analysis_service, mock_llm):
    """Test creating session and streaming a query."""
    # Setup
    repository = SessionRepository(storage=mock_storage)
    checkpointer = TypesenseCheckpointer(storage=mock_storage)

    # Create session
    session_id = await repository.create(
        db_connection_id="db_456",
        metadata={"test": True}
    )

    assert session_id == "sess_123"
    mock_storage.insert_one.assert_called_once()


@pytest.mark.asyncio
async def test_session_crud_operations(mock_storage):
    """Test all CRUD operations work correctly."""
    repository = SessionRepository(storage=mock_storage)

    # Create
    session_id = await repository.create(db_connection_id="db_456")
    assert session_id is not None

    # Get (not found)
    session = await repository.get("nonexistent")
    assert session is None

    # List
    sessions = await repository.list(db_connection_id="db_456")
    assert isinstance(sessions, list)

    # Delete
    await repository.delete(session_id)
    mock_storage.delete.assert_called()


@pytest.mark.asyncio
async def test_sse_event_format():
    """Test SSE events are properly formatted."""
    from app.modules.session.services import SessionService

    # Create minimal mock service
    mock_repo = MagicMock()
    mock_graph = MagicMock()
    mock_checkpointer = MagicMock()

    service = SessionService(
        repository=mock_repo,
        graph=mock_graph,
        checkpointer=mock_checkpointer
    )

    # Test SSE formatting
    sse = service._format_sse("status", {"step": "test", "message": "Testing"})

    assert sse.startswith("event: status\n")
    assert "data: " in sse
    assert sse.endswith("\n\n")

    # Parse the data
    lines = sse.strip().split("\n")
    data_line = [l for l in lines if l.startswith("data: ")][0]
    data = json.loads(data_line[6:])

    assert data["step"] == "test"
    assert data["message"] == "Testing"
```

**Step 2: Run integration tests**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && uv run pytest tests/modules/session/test_integration.py -v`

Expected: PASS (3 tests)

**Step 3: Commit**

```bash
git add tests/modules/session/test_integration.py
git commit -m "test(session): add integration tests"
```

---

## Task 15: Update Module Exports

**Files:**
- Update: `app/modules/session/__init__.py`

**Step 1: Update module init**

Update `app/modules/session/__init__.py`:
```python
"""
Session module for multi-query conversation management.

This module provides:
- Session CRUD operations (create, get, list, delete)
- Multi-query conversation with memory
- SSE streaming for real-time responses
- LangGraph-based state management
- Typesense persistence with checkpointing

Usage:
    from app.modules.session import SessionService, SessionDependencies

    # Configure during startup
    SessionDependencies.configure(
        storage=storage,
        sql_generation_service=sql_service,
        analysis_service=analysis_service,
        llm=llm
    )

    # Use in endpoints
    service = SessionDependencies.get_service()
    session_id = await service.create_session(db_connection_id="...")
"""

from app.modules.session.models import Session, Message, SessionStatus
from app.modules.session.repositories import SessionRepository
from app.modules.session.services import SessionService
from app.modules.session.dependencies import SessionDependencies, get_session_service
from app.modules.session.graph import build_session_graph
from app.modules.session.graph.state import SessionState, create_initial_state
from app.modules.session.graph.checkpointer import TypesenseCheckpointer
from app.modules.session.schema import SESSIONS_SCHEMA, ensure_sessions_collection

__all__ = [
    # Models
    "Session",
    "Message",
    "SessionStatus",
    "SessionState",
    "create_initial_state",
    # Repository & Service
    "SessionRepository",
    "SessionService",
    # Dependencies
    "SessionDependencies",
    "get_session_service",
    # Graph
    "build_session_graph",
    "TypesenseCheckpointer",
    # Schema
    "SESSIONS_SCHEMA",
    "ensure_sessions_collection",
]
```

**Step 2: Commit**

```bash
git add app/modules/session/__init__.py
git commit -m "feat(session): update module exports"
```

---

## Task 16: Run All Tests

**Step 1: Run full test suite for session module**

Run: `cd /Users/fitrakacamarga/project/self/bmad-new/keycenter-new/services/KAI && uv run pytest tests/modules/session/ -v`

Expected: All tests PASS

**Step 2: Final commit**

```bash
git add -A
git commit -m "feat(session): complete session endpoint implementation"
```

---

## Summary

The implementation plan covers:

1. **Tasks 1-4**: Module structure, models, state, constants
2. **Tasks 5-7**: LangGraph checkpointer, nodes, graph builder
3. **Tasks 8-9**: Repository and service with streaming
4. **Tasks 10-12**: API models, endpoints, dependency injection
5. **Tasks 13-16**: Schema, integration tests, final wiring

**Total: 16 tasks with TDD approach**

Each task follows RED-GREEN-REFACTOR:
- Write failing test
- Implement minimal code
- Verify tests pass
- Commit
