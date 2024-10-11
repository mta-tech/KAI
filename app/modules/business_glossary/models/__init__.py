from datetime import datetime

from pydantic import BaseModel, Field


class BusinessGlossary(BaseModel):
    id: str | None = None
    db_connection_id: str
    metric: str
    alias: list[str] | None = None
    sql: str
    metadata: dict | None = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
