"""Tests for session service."""
import pytest
from unittest.mock import AsyncMock, MagicMock
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


def test_format_sse(service):
    """Should format SSE correctly."""
    sse = service._format_sse("status", {"step": "test", "message": "Testing"})

    assert sse.startswith("event: status\n")
    assert "data: " in sse
    assert sse.endswith("\n\n")

    # Verify JSON is valid
    lines = sse.strip().split("\n")
    data_line = [l for l in lines if l.startswith("data: ")][0]
    data = json.loads(data_line[6:])
    assert data["step"] == "test"
