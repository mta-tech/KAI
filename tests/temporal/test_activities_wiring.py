# tests/temporal/test_activities_wiring.py
"""Tests for Temporal KaiActivities wiring to AutonomousAgentService."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.modules.autonomous_agent.models import AgentResult, AgentTask


def _make_activities():
    """Create a KaiActivities instance with mocked settings."""
    with patch("app.temporal.activities.Settings") as MockSettings:
        mock_settings = MagicMock()
        mock_settings.CHAT_FAMILY = "google"
        mock_settings.CHAT_MODEL = "gemini-2.0-flash"
        MockSettings.return_value = mock_settings
        from app.temporal.activities import KaiActivities
        activities = KaiActivities()
        activities.settings = mock_settings
        return activities


def _make_db_connection(connection_id: str = "conn-1"):
    conn = MagicMock()
    conn.id = connection_id
    conn.alias = "test-db"
    conn.dialect = "postgresql"
    return conn


def _make_agent_result(task_id: str = "task-1") -> AgentResult:
    return AgentResult(
        task_id=task_id,
        mission_id="mission-abc",
        status="completed",
        final_answer="Revenue was $1M",
        sql_queries=["SELECT sum(revenue) FROM sales"],
        execution_time_ms=420,
        error=None,
        stages_completed=["plan", "execute", "synthesize"],
    )


class TestChatActivity:
    """Tests for KaiActivities.chat()."""

    @pytest.mark.asyncio
    async def test_chat_constructs_agent_task_with_session_id_from_conversation_id(self):
        """chat() should pass conversation_id as session_id to AgentTask."""
        activities = _make_activities()
        db_connection = _make_db_connection()
        agent_result = _make_agent_result()

        with (
            patch("app.temporal.activities.DatabaseConnectionRepository") as MockRepo,
            patch("app.temporal.activities.SQLDatabase") as MockSQLDB,
            patch("app.temporal.activities.AutonomousAgentService") as MockService,
        ):
            MockRepo.return_value.find_by_id.return_value = db_connection
            MockSQLDB.get_sql_engine.return_value = MagicMock()
            mock_service_instance = MagicMock()
            mock_service_instance.execute = AsyncMock(return_value=agent_result)
            MockService.return_value = mock_service_instance

            await activities.chat(
                prompt_text="Analyze revenue",
                connection_id="conn-1",
                conversation_id="conv-session-42",
            )

            call_args = mock_service_instance.execute.call_args[0][0]
            assert isinstance(call_args, AgentTask)
            assert call_args.session_id == "conv-session-42"
            assert call_args.prompt == "Analyze revenue"
            assert call_args.db_connection_id == "conn-1"
            assert call_args.mode == "full_autonomy"

    @pytest.mark.asyncio
    async def test_chat_generates_session_id_when_conversation_id_is_none(self):
        """chat() with no conversation_id should generate a temporal_ session_id."""
        activities = _make_activities()
        db_connection = _make_db_connection()
        agent_result = _make_agent_result()

        with (
            patch("app.temporal.activities.DatabaseConnectionRepository") as MockRepo,
            patch("app.temporal.activities.SQLDatabase") as MockSQLDB,
            patch("app.temporal.activities.AutonomousAgentService") as MockService,
        ):
            MockRepo.return_value.find_by_id.return_value = db_connection
            MockSQLDB.get_sql_engine.return_value = MagicMock()
            mock_service_instance = MagicMock()
            mock_service_instance.execute = AsyncMock(return_value=agent_result)
            MockService.return_value = mock_service_instance

            await activities.chat(
                prompt_text="Analyze revenue",
                connection_id="conn-1",
                conversation_id=None,
            )

            call_args = mock_service_instance.execute.call_args[0][0]
            assert call_args.session_id.startswith("temporal_")

    @pytest.mark.asyncio
    async def test_chat_serializes_agent_result_to_dict(self):
        """chat() should return a dict with all expected keys from AgentResult."""
        activities = _make_activities()
        db_connection = _make_db_connection()
        agent_result = _make_agent_result(task_id="task-xyz")

        with (
            patch("app.temporal.activities.DatabaseConnectionRepository") as MockRepo,
            patch("app.temporal.activities.SQLDatabase") as MockSQLDB,
            patch("app.temporal.activities.AutonomousAgentService") as MockService,
        ):
            MockRepo.return_value.find_by_id.return_value = db_connection
            MockSQLDB.get_sql_engine.return_value = MagicMock()
            mock_service_instance = MagicMock()
            mock_service_instance.execute = AsyncMock(return_value=agent_result)
            MockService.return_value = mock_service_instance

            result = await activities.chat(
                prompt_text="Q",
                connection_id="conn-1",
                conversation_id="conv-1",
            )

        assert result["task_id"] == "task-xyz"
        assert result["status"] == "completed"
        assert result["final_answer"] == "Revenue was $1M"
        assert result["sql_queries"] == ["SELECT sum(revenue) FROM sales"]
        assert result["execution_time_ms"] == 420
        assert result["error"] is None
        assert result["mission_id"] == "mission-abc"
        assert result["stages_completed"] == ["plan", "execute", "synthesize"]

    @pytest.mark.asyncio
    async def test_chat_raises_value_error_when_connection_not_found(self):
        """chat() should raise ValueError when connection_id is not found."""
        activities = _make_activities()

        with patch("app.temporal.activities.DatabaseConnectionRepository") as MockRepo:
            MockRepo.return_value.find_by_id.return_value = None

            with pytest.raises(ValueError, match="conn-missing not found"):
                await activities.chat(
                    prompt_text="Q",
                    connection_id="conn-missing",
                    conversation_id=None,
                )


class TestAutonomousChatActivity:
    """Tests for KaiActivities.autonomous_chat() — identical behavior to chat()."""

    @pytest.mark.asyncio
    async def test_autonomous_chat_constructs_agent_task_with_session_id(self):
        """autonomous_chat() should pass conversation_id as session_id."""
        activities = _make_activities()
        db_connection = _make_db_connection()
        agent_result = _make_agent_result()

        with (
            patch("app.temporal.activities.DatabaseConnectionRepository") as MockRepo,
            patch("app.temporal.activities.SQLDatabase") as MockSQLDB,
            patch("app.temporal.activities.AutonomousAgentService") as MockService,
        ):
            MockRepo.return_value.find_by_id.return_value = db_connection
            MockSQLDB.get_sql_engine.return_value = MagicMock()
            mock_service_instance = MagicMock()
            mock_service_instance.execute = AsyncMock(return_value=agent_result)
            MockService.return_value = mock_service_instance

            await activities.autonomous_chat(
                prompt_text="Analyze revenue",
                connection_id="conn-1",
                conversation_id="conv-session-99",
            )

            call_args = mock_service_instance.execute.call_args[0][0]
            assert call_args.session_id == "conv-session-99"
            assert call_args.mode == "full_autonomy"
            assert call_args.metadata == {"source": "temporal_worker"}

    @pytest.mark.asyncio
    async def test_autonomous_chat_serializes_result_identically_to_chat(self):
        """autonomous_chat() should return same dict structure as chat()."""
        activities = _make_activities()
        db_connection = _make_db_connection()
        agent_result = _make_agent_result(task_id="task-auto")

        with (
            patch("app.temporal.activities.DatabaseConnectionRepository") as MockRepo,
            patch("app.temporal.activities.SQLDatabase") as MockSQLDB,
            patch("app.temporal.activities.AutonomousAgentService") as MockService,
        ):
            MockRepo.return_value.find_by_id.return_value = db_connection
            MockSQLDB.get_sql_engine.return_value = MagicMock()
            mock_service_instance = MagicMock()
            mock_service_instance.execute = AsyncMock(return_value=agent_result)
            MockService.return_value = mock_service_instance

            result = await activities.autonomous_chat(
                prompt_text="Q",
                connection_id="conn-1",
                conversation_id="conv-1",
            )

        assert result["task_id"] == "task-auto"
        assert result["status"] == "completed"
        assert result["mission_id"] == "mission-abc"
        assert set(result.keys()) == {
            "task_id", "status", "final_answer", "sql_queries",
            "execution_time_ms", "error", "mission_id", "stages_completed",
        }

    @pytest.mark.asyncio
    async def test_autonomous_chat_raises_value_error_when_connection_not_found(self):
        """autonomous_chat() should raise ValueError when connection not found."""
        activities = _make_activities()

        with patch("app.temporal.activities.DatabaseConnectionRepository") as MockRepo:
            MockRepo.return_value.find_by_id.return_value = None

            with pytest.raises(ValueError, match="conn-gone not found"):
                await activities.autonomous_chat(
                    prompt_text="Q",
                    connection_id="conn-gone",
                    conversation_id=None,
                )
