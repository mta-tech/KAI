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
    finetuning_id: str | None
    low_latency_mode: bool = False
    llm_config: LLMConfig | None
    evaluate: bool = False
    intermediate_steps: list[IntermediateStep] | None
    sql: str | None
    status: str = "INVALID"
    completed_at: datetime | None
    tokens_used: int | None
    confidence_score: float | None
    error: str | None
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: dict | None
