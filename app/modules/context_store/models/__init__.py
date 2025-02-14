from datetime import datetime

from pydantic import BaseModel, Field


class ContextStore(BaseModel):
    id: str | None = None
    db_connection_id: str
    prompt_text: str
    prompt_text_ner: str
    entities: list[str] | None
    labels: list[str] | None
    prompt_embedding: list[float]
    sql: str
    metadata: dict | None = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
