"""Memory models for KAI long-term memory system."""

from pydantic import BaseModel, Field
from typing import Any


class Memory(BaseModel):
    """A single memory entry stored in long-term memory.

    Memories persist across conversations and can be semantically searched.
    They are organized by namespace and identified by a unique key within
    that namespace.

    Memories can be either:
    - Session-scoped: Associated with a specific session_id
    - Shared: No session_id, visible to all sessions for this db_connection
    """

    id: str | None = None
    db_connection_id: str
    session_id: str | None = None  # None = shared (database-level) memory
    namespace: str  # e.g., "user_preferences", "facts", "insights"
    key: str  # Unique identifier within namespace
    value: dict[str, Any]  # The actual memory content
    content_text: str  # Searchable text representation
    memory_embedding: list[float] | None = None
    importance: float = Field(default=0.5, ge=0.0, le=1.0)  # 0-1 scale
    access_count: int = 0
    last_accessed_at: str | None = None
    created_at: str
    updated_at: str


class MemoryMetadata(BaseModel):
    """Metadata about a memory for quick retrieval."""

    namespace: str
    key: str
    importance: float
    created_at: str


class MemorySearchResult(BaseModel):
    """Result from semantic memory search."""

    memory: Memory
    score: float
    match_type: str = "hybrid"  # "semantic", "exact", "hybrid"
