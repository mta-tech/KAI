# tests/modules/autonomous_agent/test_models.py
import pytest
from datetime import datetime
from app.modules.autonomous_agent.models import MissionRun, AgentTask, MissionState, MissionStage


def test_mission_run_creation():
    """Should create MissionRun with required fields."""
    run = MissionRun(
        id="run_123",
        question="Analyze sales by region",
        db_connection_id="db_456",
        state=MissionState.CREATED,
    )
    assert run.id == "run_123"
    assert run.db_connection_id == "db_456"
    assert run.state == MissionState.CREATED
    assert run.question == "Analyze sales by region"


def test_agent_task_with_mission_id():
    """Should create AgentTask with mission_id."""
    task = AgentTask(
        id="task_789",
        mission_id="run_123",
        prompt="Analyze revenue trends",
        db_connection_id="db_456",
    )
    assert task.id == "task_789"
    assert task.mission_id == "run_123"
    assert task.prompt == "Analyze revenue trends"
