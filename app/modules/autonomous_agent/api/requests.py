"""Request models for Agent Session API."""
from pydantic import BaseModel, Field
from typing import Literal


class CreateAgentSessionRequest(BaseModel):
    """Request to create a new agent session."""

    db_connection_id: str = Field(..., description="Database connection ID")
    mode: Literal["analysis", "query", "script", "full_autonomy"] = Field(
        default="full_autonomy", description="Agent mode"
    )
    recursion_limit: int = Field(default=100, ge=1, le=500, description="Max recursion for LangGraph")
    title: str | None = Field(default=None, description="Optional session title")
    metadata: dict | None = Field(default=None, description="Optional session metadata")


class AgentTaskRequest(BaseModel):
    """Request to submit a task to an agent session."""

    prompt: str = Field(..., min_length=1, description="The task prompt")
    context: dict | None = Field(default=None, description="Optional context for the task")
    metadata: dict | None = Field(default=None, description="Optional task metadata")


class UpdateAgentSessionRequest(BaseModel):
    """Request to update an agent session."""

    title: str | None = Field(default=None, description="Update session title")
    status: Literal["active", "paused"] | None = Field(default=None, description="Update session status")
    metadata: dict | None = Field(default=None, description="Update session metadata")
