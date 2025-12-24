"""Tests for session repository."""
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
    assert session_id.startswith("sess_")
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
        "messages": "[]",
        "status": "idle",
        "metadata": {},
        "created_at": int(datetime.now().timestamp()),
        "updated_at": int(datetime.now().timestamp())
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
            "messages": "[]",
            "status": "idle",
            "metadata": {},
            "created_at": int(datetime.now().timestamp()),
            "updated_at": int(datetime.now().timestamp())
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
