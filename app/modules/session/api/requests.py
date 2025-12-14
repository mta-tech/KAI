"""Session API request models."""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class CreateSessionRequest(BaseModel):
    """Request to create a new session."""
    db_connection_id: str = Field(..., description="Database connection ID for this session")
    language: Literal["id", "en"] = Field(
        default="id",
        description="Response language: 'id' for Bahasa Indonesia, 'en' for English"
    )
    metadata: Optional[dict] = Field(default=None, description="Optional custom metadata")


class SessionQueryRequest(BaseModel):
    """Request to query within a session."""
    query: str = Field(..., description="Natural language query", min_length=1)
