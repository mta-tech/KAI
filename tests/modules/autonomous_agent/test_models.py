# tests/modules/autonomous_agent/test_models.py
import pytest
from datetime import datetime
from app.modules.autonomous_agent.models import AgentSession, AgentTask


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
