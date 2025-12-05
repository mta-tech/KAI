"""Tests for session graph state."""
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


def test_session_state_with_metadata():
    """Should accept custom metadata."""
    state = create_initial_state("sess_123", "db_456", metadata={"user": "test"})
    assert state["metadata"] == {"user": "test"}


def test_session_state_default_metadata():
    """Should have empty dict as default metadata."""
    state = create_initial_state("sess_123", "db_456")
    assert state["metadata"] == {}
