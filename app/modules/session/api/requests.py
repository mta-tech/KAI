"""Session API request models."""
from pydantic import BaseModel, Field
from typing import Optional


class CreateSessionRequest(BaseModel):
    """Request to create a new session."""
    db_connection_id: str = Field(..., description="Database connection ID for this session")
    metadata: Optional[dict] = Field(default=None, description="Optional custom metadata")


class SessionQueryRequest(BaseModel):
    """Request to query within a session."""
    query: str = Field(..., description="Natural language query", min_length=1)
