from datetime import datetime

from pydantic import BaseModel, Field


class Alias(BaseModel):
    id: str | None = None
    db_connection_id: str
    name: str
    target_name: str
    target_type: str  # e.g., "table", "column", "query", etc.
    description: str | None = None
    metadata: dict | None = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
