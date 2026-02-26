import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.modules.autonomous_agent.service import AutonomousAgentService
from app.modules.autonomous_agent.models import AgentTask


@pytest.fixture
def mock_db_connection():
    conn = Mock()
    conn.dialect = "postgresql"
    return conn


@pytest.fixture
def mock_database():
    db = Mock()
    db.run_sql.return_value = (
        "OK",
        {"result": [{"id": 1, "name": "Test"}]}
    )
    return db


@patch("app.modules.autonomous_agent.service.StateBackend")
def test_create_agent(mock_state_backend, mock_db_connection, mock_database):
    """Test agent creation."""
    service = AutonomousAgentService(mock_db_connection, mock_database)
    agent = service.create_agent("full_autonomy")
    assert agent is not None
    mock_state_backend.assert_called_once()


@pytest.mark.asyncio
@patch("app.modules.autonomous_agent.service.StateBackend")
async def test_execute_task(mock_state_backend, mock_db_connection, mock_database):
    """Test task execution."""
    service = AutonomousAgentService(mock_db_connection, mock_database)
    task = AgentTask(
        id="test_1",
        prompt="Show me all users",
        db_connection_id="test_db",
        mode="query",
    )
    # We can't easily run the full agent without credentials/LLM,
    # so we just verify the method exists and signature is correct.
    # To properly mock agent execution, we'd need to mock create_deep_agent return value.
    
    # Mocking create_agent to return a mock agent that returns a fixed result
    mock_agent = Mock()
    mock_agent.invoke.return_value = {"messages": [Mock(content="Test result")]}
    service.create_agent = Mock(return_value=mock_agent)

    result = await service.execute(task)
    assert result.task_id == "test_1"
    assert result.status == "completed"
    assert result.final_answer == "Test result"
