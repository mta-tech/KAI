"""Response models for Agent Session API."""
from pydantic import BaseModel, Field
from typing import Literal

from app.modules.autonomous_agent.models import AgentSession


class AgentSessionResponse(BaseModel):
    """Response model for an agent session."""

    id: str
    db_connection_id: str
    status: Literal["active", "paused", "running", "completed", "failed"]
    mode: Literal["analysis", "query", "script", "full_autonomy"]
    recursion_limit: int
    title: str | None
    created_at: str
    updated_at: str
    metadata: dict | None

    @classmethod
    def from_session(cls, session: AgentSession) -> "AgentSessionResponse":
        """Create response from AgentSession model."""
        return cls(
            id=session.id,
            db_connection_id=session.db_connection_id,
            status=session.status,
            mode=session.mode,
            recursion_limit=session.recursion_limit,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
            metadata=session.metadata,
        )


class AgentSessionListResponse(BaseModel):
    """Response model for listing agent sessions."""

    sessions: list[AgentSessionResponse]
    total: int
    limit: int
    offset: int


class AgentTaskSubmittedResponse(BaseModel):
    """Response after submitting a task to an agent session."""

    task_id: str
    session_id: str
    status: str = "submitted"


class AgentResultResponse(BaseModel):
    """Response model for agent execution result."""

    task_id: str
    status: Literal["completed", "failed", "partial"]
    final_answer: str
    sql_queries: list[str] = Field(default_factory=list)
    charts: list[dict] = Field(default_factory=list)
    insights: list[dict] = Field(default_factory=list)
    suggested_questions: list[dict] = Field(default_factory=list)
    execution_time_ms: int = 0
    error: str | None = None
