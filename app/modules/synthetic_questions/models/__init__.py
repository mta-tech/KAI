from datetime import datetime
from typing import Optional, List, Dict
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

class SyntheticQuestions(BaseModel):
    questions: List
    input_tokens_used: Optional[int] = None
    output_tokens_used: Optional[int] = None
    metadata: Optional[Dict] = None


class QuestionGenerationConfig(BaseModel):
    """
    Represents a question generation configuration and results.
    This class contains both the configuration parameters for question generation
    and stores the generated question-SQL pairs.
    """

    id: UUID = Field(default_factory=uuid4)
    db_connection_id: str
    llm_config: LLMConfig | None = None
    questions_per_batch: int = 5
    num_batches: int = 1
    peeking_context_stores: bool = False
    evaluate: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict | None = None


__all__ = ["QuestionGenerationConfig", "QuestionSQLPair", "LLMConfig", "SyntheticQuestions"]
