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
