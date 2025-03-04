from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.modules.sql_generation.models import LLMConfig


class QuestionSQLPair(BaseModel):
    """
    A pair of question and its corresponding SQL query.
    This can be used for both generating questions only and generating questions and SQL queries.
    """

    question: str
    sql: str | None = None
    metadata: dict | None = None


class QuestionGeneration(BaseModel):
    """
    Represents a question generation attempt, including configuration and results.
    """

    id: UUID = Field(default_factory=uuid4)
    db_connection_id: str
    llm_config: LLMConfig | None = None
    questions_per_batch: int = 5
    num_batches: int = 1
    peeking_context_stores: bool = False
    evaluate: bool = False
    question_sql_pairs: list[QuestionSQLPair] = []
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict | None = None


__all__ = ["QuestionGeneration", "QuestionSQLPair", "LLMConfig"]
