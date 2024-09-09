from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.sql_generation.models import LLMConfig


class NLGeneration(BaseModel):
    id: str | None = None
    sql_generation_id: str
    llm_config: LLMConfig | None
    text: str | None = None
    metadata: dict | None = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
