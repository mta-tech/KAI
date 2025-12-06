"""Agent Session API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional

from app.modules.autonomous_agent.api.requests import (
    CreateAgentSessionRequest,
    AgentTaskRequest,
    UpdateAgentSessionRequest,
)
from app.modules.autonomous_agent.api.responses import (
    AgentSessionResponse,
    AgentSessionListResponse,
    AgentTaskSubmittedResponse,
)
from app.modules.autonomous_agent.repositories import AgentSessionRepository
from app.modules.autonomous_agent.models import AgentSession, AgentTask
from app.data.db.storage import Storage

import uuid


# Dependency placeholder - will be configured during app startup
_storage: Storage | None = None


def set_agent_session_storage(storage: Storage) -> None:
    """Set the storage instance. Called during app startup."""
    global _storage
    _storage = storage


def get_agent_session_repository() -> AgentSessionRepository:
    """Dependency to get agent session repository."""
    if _storage is None:
        raise RuntimeError("Storage not configured. Call set_agent_session_storage() first.")
    return AgentSessionRepository(_storage)


router = APIRouter(prefix="/agent-sessions", tags=["agent-sessions"])


@router.post("", response_model=dict)
async def create_agent_session(
    body: CreateAgentSessionRequest,
    repo: AgentSessionRepository = Depends(get_agent_session_repository),
):
    """
    Create a new agent session for autonomous analysis.

    Returns the created session ID.
    """
    session_id = await repo.acreate(
        db_connection_id=body.db_connection_id,
        mode=body.mode,
        recursion_limit=body.recursion_limit,
        title=body.title,
        metadata=body.metadata,
    )
    return {"session_id": session_id}


@router.get("", response_model=AgentSessionListResponse)
async def list_agent_sessions(
    db_connection_id: Optional[str] = Query(None, description="Filter by database connection"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    repo: AgentSessionRepository = Depends(get_agent_session_repository),
):
    """
    List agent sessions with optional filters.
    """
    sessions = await repo.alist(
        db_connection_id=db_connection_id,
        status=status,
        limit=limit,
    )

    # Apply offset (repo.alist doesn't support offset natively)
    sessions = sessions[offset:]

    return AgentSessionListResponse(
        sessions=[AgentSessionResponse.from_session(s) for s in sessions],
        total=len(sessions),
        limit=limit,
        offset=offset,
    )


@router.get("/{session_id}", response_model=AgentSessionResponse)
async def get_agent_session(
    session_id: str,
    repo: AgentSessionRepository = Depends(get_agent_session_repository),
):
    """
    Get agent session details.
    """
    session = await repo.aget(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Agent session not found")

    return AgentSessionResponse.from_session(session)


@router.patch("/{session_id}", response_model=AgentSessionResponse)
async def update_agent_session(
    session_id: str,
    body: UpdateAgentSessionRequest,
    repo: AgentSessionRepository = Depends(get_agent_session_repository),
):
    """
    Update an agent session.
    """
    session = await repo.aget(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Agent session not found")

    # Apply updates
    if body.title is not None:
        session.title = body.title
    if body.status is not None:
        session.status = body.status
    if body.metadata is not None:
        session.metadata = body.metadata

    await repo.aupdate(session)
    return AgentSessionResponse.from_session(session)


@router.delete("/{session_id}")
async def delete_agent_session(
    session_id: str,
    repo: AgentSessionRepository = Depends(get_agent_session_repository),
):
    """
    Delete an agent session.
    """
    session = await repo.aget(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Agent session not found")

    await repo.adelete(session_id)
    return {"status": "deleted"}


@router.post("/{session_id}/pause")
async def pause_agent_session(
    session_id: str,
    repo: AgentSessionRepository = Depends(get_agent_session_repository),
):
    """
    Pause an active agent session.
    """
    session = await repo.aget(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Agent session not found")

    if session.status not in ("active", "running"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot pause session with status '{session.status}'",
        )

    session.status = "paused"
    await repo.aupdate(session)
    return {"status": "paused"}


@router.post("/{session_id}/resume")
async def resume_agent_session(
    session_id: str,
    repo: AgentSessionRepository = Depends(get_agent_session_repository),
):
    """
    Resume a paused agent session.
    """
    session = await repo.aget(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Agent session not found")

    if session.status != "paused":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot resume session with status '{session.status}'",
        )

    session.status = "active"
    await repo.aupdate(session)
    return {"status": "active"}


__all__ = ["router", "set_agent_session_storage", "get_agent_session_repository"]
