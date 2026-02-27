# tests/modules/autonomous_agent/test_models_fix.py
"""Unit tests for AgentTask session_id and AgentResult mission_id fixes."""
import pytest
from app.modules.autonomous_agent.models import AgentTask, AgentResult


class TestAgentTaskSessionId:
    """Tests for AgentTask.session_id auto-fill behavior."""

    def test_session_id_auto_fills_from_id_when_omitted(self):
        """AgentTask without session_id should auto-fill session_id from id."""
        task = AgentTask(id="task-abc", prompt="q", db_connection_id="conn-1")
        assert task.session_id == "task-abc"

    def test_explicit_session_id_is_preserved(self):
        """AgentTask with explicit session_id should keep that value."""
        task = AgentTask(
            id="task-abc",
            prompt="q",
            db_connection_id="conn-1",
            session_id="session-xyz",
        )
        assert task.session_id == "session-xyz"

    def test_empty_string_session_id_falls_back_to_id(self):
        """AgentTask with session_id='' should still auto-fill from id."""
        task = AgentTask(
            id="task-abc",
            prompt="q",
            db_connection_id="conn-1",
            session_id="",
        )
        assert task.session_id == "task-abc"

    def test_required_fields_still_positional(self):
        """id, prompt, db_connection_id are still required positional fields."""
        with pytest.raises(TypeError):
            AgentTask()  # type: ignore[call-arg]

    def test_keyword_construction(self):
        """Keyword construction with all required fields should work."""
        task = AgentTask(id="t1", prompt="analyze", db_connection_id="c1")
        assert task.id == "t1"
        assert task.prompt == "analyze"
        assert task.db_connection_id == "c1"

    def test_mode_default_is_full_autonomy(self):
        """Default mode should remain 'full_autonomy' after adding session_id."""
        task = AgentTask(id="t1", prompt="q", db_connection_id="c1")
        assert task.mode == "full_autonomy"

    def test_session_id_field_ordering_no_positional_conflict(self):
        """session_id as 4th positional arg should work without conflict."""
        task = AgentTask("t1", "prompt", "conn", "sess-override")
        assert task.session_id == "sess-override"


class TestAgentResultMissionId:
    """Tests for AgentResult.mission_id optional default behavior."""

    def test_agent_result_without_mission_id_defaults_to_empty_string(self):
        """AgentResult constructed without mission_id should default to ''."""
        result = AgentResult(task_id="t1", status="completed", final_answer="ans")
        assert result.mission_id == ""

    def test_agent_result_with_explicit_mission_id_preserved(self):
        """AgentResult with explicit mission_id should keep that value."""
        result = AgentResult(task_id="t1", mission_id="m1")
        assert result.mission_id == "m1"

    def test_agent_result_only_task_id_required(self):
        """Only task_id should be required; status and final_answer have defaults."""
        result = AgentResult(task_id="t1")
        assert result.task_id == "t1"
        assert result.mission_id == ""
        assert result.status == "completed"
        assert result.final_answer == ""

    def test_agent_result_no_positional_args_required_beyond_task_id(self):
        """AgentResult(task_id=...) alone should not raise TypeError."""
        try:
            AgentResult(task_id="t1")
        except TypeError as e:
            pytest.fail(f"AgentResult(task_id='t1') raised TypeError: {e}")

    def test_agent_result_keyword_all_fields(self):
        """All fields can be set via keyword args."""
        result = AgentResult(
            task_id="t1",
            mission_id="m1",
            status="failed",
            final_answer="error occurred",
        )
        assert result.task_id == "t1"
        assert result.mission_id == "m1"
        assert result.status == "failed"
        assert result.final_answer == "error occurred"
