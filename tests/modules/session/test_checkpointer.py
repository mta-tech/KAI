"""Tests for Typesense checkpointer."""
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
        "id": "checkpoint_1",
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
    assert result["id"] == "checkpoint_1"


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
    call_args = mock_storage.update_or_create.call_args
    assert call_args[0][1] == "sess_123"  # session_id


def test_serialize_deserialize_roundtrip(checkpointer):
    """Checkpoint should survive serialization roundtrip."""
    checkpoint = {
        "v": 1,
        "ts": "2024-01-01T00:00:00",
        "id": "test_checkpoint",
        "channel_values": {"key": "value"},
        "channel_versions": {"ch1": 1},
        "versions_seen": {"node1": {"ch1": 1}}
    }

    serialized = checkpointer._serialize(checkpoint)
    deserialized = checkpointer._deserialize(serialized)

    assert deserialized == checkpoint
