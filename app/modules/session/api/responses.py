"""Session API response models."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MessageResponse(BaseModel):
    """Response model for a message in conversation history."""
    id: str
    role: str
    query: str
    sql: Optional[str] = None
    results_summary: Optional[str] = None
    analysis: Optional[str] = None
    timestamp: datetime


class SessionResponse(BaseModel):
    """Response model for session details."""
    id: str
    db_connection_id: str
    status: str
    messages: List[MessageResponse] = Field(default_factory=list)
    summary: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_session(cls, session) -> "SessionResponse":
        """Create from Session model."""
        return cls(
            id=session.id,
            db_connection_id=session.db_connection_id,
            status=session.status.value,
            messages=[
                MessageResponse(
                    id=m.id,
                    role=m.role,
                    query=m.query,
                    sql=m.sql,
                    results_summary=m.results_summary,
                    analysis=m.analysis,
                    timestamp=m.timestamp
                )
                for m in session.messages
            ],
            summary=session.summary,
            metadata=session.metadata,
            created_at=session.created_at,
            updated_at=session.updated_at
        )


class SessionListResponse(BaseModel):
    """Response model for listing sessions."""
    sessions: List[SessionResponse]
    total: int
    limit: int
    offset: int
