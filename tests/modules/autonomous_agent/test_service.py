import pytest
from unittest.mock import Mock, MagicMock, patch
from app.modules.autonomous_agent.models import AgentTask, AgentResult


def test_agent_task_creation():
    """Test AgentTask model can be created with required fields."""
    task = AgentTask(
        id="test_1",
        prompt="Show me all users",
        db_connection_id="test_db",
        session_id="sess_test123",
        mode="query",
    )
    assert task.id == "test_1"
    assert task.prompt == "Show me all users"
    assert task.db_connection_id == "test_db"
    assert task.session_id == "sess_test123"
    assert task.mode == "query"


def test_agent_result_creation():
    """Test AgentResult model can be created with required fields."""
    result = AgentResult(
        task_id="test_1",
        status="completed",
        final_answer="The result is 42",
    )
    assert result.task_id == "test_1"
    assert result.status == "completed"
    assert result.final_answer == "The result is 42"


def test_agent_result_with_artifacts():
    """Test AgentResult can store artifacts."""
    result = AgentResult(
        task_id="test_1",
        status="completed",
        final_answer="Data analysis complete",
        artifacts={"sql_query": "SELECT * FROM users", "row_count": 100}
    )
    assert result.artifacts["sql_query"] == "SELECT * FROM users"
    assert result.artifacts["row_count"] == 100


def test_service_import():
    """Test that AutonomousAgentService can be imported.

    Full instantiation requires TypeSense and settings,
    which are integration test concerns.
    """
    from app.modules.autonomous_agent.service import AutonomousAgentService
    assert AutonomousAgentService is not None
    # Verify the service has expected methods
    assert hasattr(AutonomousAgentService, 'create_agent')
    assert hasattr(AutonomousAgentService, 'execute')
    assert hasattr(AutonomousAgentService, 'stream_execute')
