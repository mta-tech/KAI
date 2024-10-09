import os
from datetime import datetime

from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    llm_name: str = os.getenv("LLM_NAME", "gpt-4-turbo-preview")
    api_base: str | None = None


class IntermediateStep(BaseModel):
    thought: str
    action: str
    action_input: str
    observation: str


class SQLGeneration(BaseModel):
    id: str | None = None
    prompt_id: str
    llm_config: LLMConfig | None
    evaluate: bool = False
    intermediate_steps: list[IntermediateStep] | None = None
    sql: str | None = None
    status: str = "INVALID"
    tokens_used: int | None = 0
    confidence_score: float | None = None
    completed_at: str | None = None
    error: str | None = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict | None = None