"""Session API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional

from app.modules.session.api.requests import CreateSessionRequest, SessionQueryRequest
from app.modules.session.api.responses import SessionResponse, SessionListResponse
from app.modules.session.services import SessionService
from app.modules.session.models import SessionStatus


# Dependency placeholder - will be configured during app startup
_session_service: SessionService | None = None


def set_session_service(service: SessionService) -> None:
    """Set the session service instance. Called during app startup."""
    global _session_service
    _session_service = service


def get_session_service() -> SessionService:
    """Dependency to get session service instance."""
    if _session_service is None:
        raise RuntimeError("Session service not configured. Call set_session_service() first.")
    return _session_service


router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=dict)
async def create_session(
    body: CreateSessionRequest,
    service: SessionService = Depends(get_session_service)
):
    """
    Create a new session.

    Returns the created session ID.
    """
    session_id = await service.create_session(
        db_connection_id=body.db_connection_id,
        metadata=body.metadata
    )
    return {"session_id": session_id}


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    db_connection_id: Optional[str] = Query(None, description="Filter by database connection"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    service: SessionService = Depends(get_session_service)
):
    """
    List sessions with optional filters.
    """
    status_enum = SessionStatus(status) if status else None

    sessions = await service.list_sessions(
        db_connection_id=db_connection_id,
        status=status_enum,
        limit=limit,
        offset=offset
    )

    return SessionListResponse(
        sessions=[SessionResponse.from_session(s) for s in sessions],
        total=len(sessions),
        limit=limit,
        offset=offset
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    """
    Get session details and conversation history.
    """
    session = await service.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse.from_session(session)


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    """
    Delete a session.
    """
    session = await service.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await service.delete_session(session_id)
    return {"status": "deleted"}


@router.post("/{session_id}/close")
async def close_session(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    """
    Close a session (mark as inactive).
    """
    session = await service.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await service.close_session(session_id)
    return {"status": "closed"}


@router.post("/{session_id}/query/stream")
async def query_session_stream(
    session_id: str,
    body: SessionQueryRequest,
    service: SessionService = Depends(get_session_service)
):
    """
    Send a query to the session and stream the response via SSE.

    Returns a stream of Server-Sent Events with:
    - status events: Processing step updates
    - chunk events: SQL, results, and analysis chunks
    - done event: Final completion signal
    - error event: Error information if failed
    """
    return StreamingResponse(
        service.stream_query(session_id, body.query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


__all__ = ["router", "get_session_service", "set_session_service"]
