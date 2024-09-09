from datetime import datetime

from pydantic import BaseModel, Field


class ContextStore(BaseModel):
    id: str | None = None
    db_connection_id: str
    prompt_text: str
    prompt_embedding: list[float] | None = None
    sql: str
    metadata: dict | None = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
