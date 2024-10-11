from abc import ABC, abstractmethod
from typing import Annotated

from pydantic import BaseModel, Field, confloat

from app.modules.database_connection.models import DatabaseConnection
from app.modules.prompt.models import Prompt
from app.modules.sql_generation.models import LLMConfig, SQLGeneration
from app.utils.model.chat_model import ChatModel
from app.utils.sql_database.sql_database import SQLDatabase


class Evaluation(BaseModel):
    id: str | None = None
    question_id: str | None = None
    answer_id: str | None = None
    score: Annotated[float, Field(ge=0, le=1)] = 0.5


class Evaluator(ABC):
    database: SQLDatabase
    acceptance_threshold: Annotated[float, Field(ge=0, le=1)] = 0.6
    llm_config: LLMConfig
    llm: ChatModel | None = None

    def __init__(self):
        self.model = ChatModel()

    def get_confidence_score(
        self,
        user_prompt: Prompt,
        sql_generation: SQLGeneration,
        database_connection: DatabaseConnection,
    ) -> confloat:
        """Determines if a generated response from the engine is acceptable considering the ACCEPTANCE_THRESHOLD"""
        evaluation = self.evaluate(
            user_prompt=user_prompt,
            sql_generation=sql_generation,
            database_connection=database_connection,
        )
        return evaluation.score

    @abstractmethod
    def evaluate(
        self,
        user_prompt: Prompt,
        sql_generation: SQLGeneration,
        database_connection: DatabaseConnection,
    ) -> Evaluation:
        """Evaluates a question with an SQL pair."""
