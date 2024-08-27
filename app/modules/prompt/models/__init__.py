from datetime import datetime

from pydantic import BaseModel, Field


class Prompt(BaseModel):
    id: str | None = None
    text: str
    db_connection_id: str
    schemas: list[str] | None = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict | None = None
