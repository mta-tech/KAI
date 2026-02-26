"""Agent Session API endpoints."""
import json
import uuid
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

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
from app.modules.autonomous_agent.service import AutonomousAgentService
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.utils.sql_database.sql_database import SQLDatabase
from app.data.db.storage import Storage
from langgraph.checkpoint.memory import MemorySaver


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


# ============================================================================
# Streaming endpoint for autonomous agent execution
# ============================================================================

# Session-scoped checkpointers for multi-turn conversations
_session_checkpointers: dict[str, MemorySaver] = {}


def _get_or_create_checkpointer(session_id: str) -> MemorySaver:
    """Get or create a MemorySaver checkpointer for a session."""
    if session_id not in _session_checkpointers:
        _session_checkpointers[session_id] = MemorySaver()
    return _session_checkpointers[session_id]


def _create_autonomous_service(
    session: AgentSession,
    storage: Storage,
) -> AutonomousAgentService:
    """Create AutonomousAgentService instance for a session.

    Args:
        session: The agent session
        storage: Storage instance for database operations

    Returns:
        Configured AutonomousAgentService
    """
    # Get database connection from storage
    db_repo = DatabaseConnectionRepository(storage)
    db_connection = db_repo.find_by_id(session.db_connection_id)

    if not db_connection:
        raise HTTPException(
            status_code=404,
            detail=f"Database connection '{session.db_connection_id}' not found",
        )

    # Create SQLDatabase instance
    database = SQLDatabase.get_sql_engine(db_connection, False)

    # Get or create checkpointer for this session
    checkpointer = _get_or_create_checkpointer(session.id)

    # Create the service
    return AutonomousAgentService(
        db_connection=db_connection,
        database=database,
        checkpointer=checkpointer,
        storage=storage,
    )


async def _stream_generator(
    service: AutonomousAgentService,
    task: AgentTask,
) -> AsyncGenerator[str, None]:
    """Convert stream_execute events to SSE format.

    Args:
        service: AutonomousAgentService instance
        task: AgentTask to execute

    Yields:
        SSE formatted event strings
    """
    async for event in service.stream_execute(task):
        event_type = event.get("type", "chunk")
        yield f"event: {event_type}\ndata: {json.dumps(event)}\n\n"


@router.post("/{session_id}/stream")
async def stream_agent_task(
    session_id: str,
    body: AgentTaskRequest,
    repo: AgentSessionRepository = Depends(get_agent_session_repository),
):
    """
    Stream autonomous agent execution via Server-Sent Events (SSE).

    Executes the agent task and streams events in real-time including:
    - memory_loaded: When memories from previous sessions are loaded
    - skill_loaded: When relevant skills are loaded
    - session_resumed: When resuming from a checkpoint
    - token: LLM token streaming
    - tool_start: When a tool starts executing
    - tool_end: When a tool finishes executing
    - todo_update: When the agent's todo list changes
    - done: When execution completes
    - error: When an error occurs

    Returns a streaming response with media type text/event-stream.
    """
    # Validate session exists
    session = await repo.aget(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Agent session not found")

    # Check session status
    if session.status == "closed":
        raise HTTPException(
            status_code=400,
            detail="Cannot execute task on closed session",
        )

    # Ensure storage is available
    if _storage is None:
        raise RuntimeError("Storage not configured. Call set_agent_session_storage() first.")

    # Create the service
    service = _create_autonomous_service(session, _storage)

    # Create task
    task = AgentTask(
        id=f"task_{uuid.uuid4().hex[:8]}",
        session_id=session_id,
        prompt=body.prompt,
        db_connection_id=session.db_connection_id,
        mode=session.mode,
        context=body.context,
        metadata=body.metadata,
    )

    # Update session status
    session.status = "running"
    await repo.aupdate(session)

    # Return streaming response
    async def stream_with_status_update():
        """Stream and update session status on completion."""
        try:
            async for chunk in _stream_generator(service, task):
                yield chunk
        finally:
            # Update session status after streaming completes
            session.status = "active"
            await repo.aupdate(session)

    return StreamingResponse(
        stream_with_status_update(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


__all__ = ["router", "set_agent_session_storage", "get_agent_session_repository"]
