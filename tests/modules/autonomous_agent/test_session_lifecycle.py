"""Integration tests for agent session lifecycle."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

from app.modules.autonomous_agent.models import AgentSession, AgentTask
from app.modules.autonomous_agent.repositories import AgentSessionRepository


@pytest.fixture
def mock_storage():
    """Create a mock storage with in-memory session storage."""
    storage = MagicMock()
    sessions = {}

    def mock_upsert(collection, doc):
        sessions[doc["id"]] = doc

    def mock_find_by_id(collection, id):
        return sessions.get(id)

    def mock_search(collection, query, filter_by, limit, sort_by):
        results = list(sessions.values())
        # Apply filters
        if filter_by:
            if "db_connection_id" in filter_by:
                results = [s for s in results if s.get("db_connection_id") == filter_by["db_connection_id"]]
            if "status" in filter_by:
                results = [s for s in results if s.get("status") == filter_by["status"]]
        return results[:limit]

    def mock_delete(collection, id):
        if id in sessions:
            del sessions[id]
            return True
        return False

    storage.upsert = mock_upsert
    storage.find_by_id = mock_find_by_id
    storage.search = mock_search
    storage.delete = mock_delete

    return storage


@pytest.fixture
def repository(mock_storage):
    """Create repository with mock storage."""
    return AgentSessionRepository(storage=mock_storage)


class TestSessionLifecycle:
    """Test the complete session lifecycle."""

    def test_create_session(self, repository):
        """Test session creation."""
        session_id = repository.create(
            db_connection_id="db_123",
            mode="full_autonomy",
            recursion_limit=100,
            title="Test Session",
            metadata={"purpose": "testing"},
        )

        assert session_id is not None
        assert session_id.startswith("sess_")

    def test_get_session(self, repository):
        """Test getting a session by ID."""
        # Create session
        session_id = repository.create(
            db_connection_id="db_456",
            mode="query",
        )

        # Retrieve session
        session = repository.get(session_id)

        assert session is not None
        assert session.id == session_id
        assert session.db_connection_id == "db_456"
        assert session.mode == "query"
        assert session.status == "active"

    def test_get_nonexistent_session(self, repository):
        """Test getting a session that doesn't exist."""
        session = repository.get("nonexistent_123")
        assert session is None

    def test_list_sessions(self, repository):
        """Test listing sessions with filters."""
        # Create multiple sessions
        repository.create(db_connection_id="db_A", mode="query")
        repository.create(db_connection_id="db_A", mode="analysis")
        repository.create(db_connection_id="db_B", mode="full_autonomy")

        # List all
        all_sessions = repository.list()
        assert len(all_sessions) == 3

        # Filter by db_connection_id
        db_a_sessions = repository.list(db_connection_id="db_A")
        assert len(db_a_sessions) == 2

    def test_update_session(self, repository):
        """Test updating a session."""
        # Create session
        session_id = repository.create(
            db_connection_id="db_update",
            mode="query",
            title="Original Title",
        )

        # Get and update
        session = repository.get(session_id)
        session.title = "Updated Title"
        session.status = "paused"
        repository.update(session)

        # Verify update
        updated = repository.get(session_id)
        assert updated.title == "Updated Title"
        assert updated.status == "paused"

    def test_delete_session(self, repository):
        """Test deleting a session."""
        # Create session
        session_id = repository.create(db_connection_id="db_delete")

        # Verify exists
        assert repository.get(session_id) is not None

        # Delete
        result = repository.delete(session_id)
        assert result is True

        # Verify deleted
        assert repository.get(session_id) is None

    def test_session_pause_resume(self, repository):
        """Test pausing and resuming a session."""
        session_id = repository.create(db_connection_id="db_pause")

        # Initially active
        session = repository.get(session_id)
        assert session.status == "active"

        # Pause
        session.status = "paused"
        repository.update(session)
        paused = repository.get(session_id)
        assert paused.status == "paused"

        # Resume
        session = repository.get(session_id)
        session.status = "active"
        repository.update(session)
        resumed = repository.get(session_id)
        assert resumed.status == "active"


class TestAgentTaskWithSession:
    """Test AgentTask model with session_id."""

    def test_task_has_session_id(self):
        """Test that AgentTask includes session_id."""
        task = AgentTask(
            id="task_123",
            session_id="sess_abc123",
            prompt="Analyze revenue trends",
            db_connection_id="db_789",
            mode="analysis",
        )

        assert task.session_id == "sess_abc123"
        assert task.prompt == "Analyze revenue trends"

    def test_task_with_context_and_metadata(self):
        """Test AgentTask with context and metadata."""
        task = AgentTask(
            id="task_456",
            session_id="sess_def456",
            prompt="Run complex analysis",
            db_connection_id="db_complex",
            mode="full_autonomy",
            context={"previous_results": ["result1", "result2"]},
            metadata={"priority": "high", "requester": "system"},
        )

        assert task.context["previous_results"] == ["result1", "result2"]
        assert task.metadata["priority"] == "high"


class TestSessionMemoryIntegration:
    """Test session-scoped memory functionality."""

    def test_session_id_in_memory_model(self):
        """Test that Memory model supports session_id."""
        from app.modules.memory.models import Memory

        # Session-scoped memory
        session_memory = Memory(
            db_connection_id="db_mem",
            session_id="sess_mem123",
            namespace="analysis",
            key="revenue_pattern",
            value={"pattern": "increasing"},
            content_text="Revenue shows an increasing pattern",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        assert session_memory.session_id == "sess_mem123"

        # Shared memory (database-level)
        shared_memory = Memory(
            db_connection_id="db_mem",
            session_id=None,  # Shared
            namespace="facts",
            key="table_info",
            value={"tables": ["users", "orders"]},
            content_text="Database has users and orders tables",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        assert shared_memory.session_id is None
