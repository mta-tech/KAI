from datetime import datetime

from pydantic import BaseModel, Field


class Instruction(BaseModel):
    id: str | None = None
    db_connection_id: str
    condition: str
    rules: str
    instruction_embedding: list[float] | None = None
    is_default: bool
    metadata: dict | None = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
