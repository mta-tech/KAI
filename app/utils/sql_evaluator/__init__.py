import os
from abc import ABC, abstractmethod
from typing import Annotated

from pydantic import BaseModel, Field, confloat

from app.modules.database_connection.models import DatabaseConnection
from app.modules.prompt.models import Prompt
from app.modules.sql_generation.models import LLMConfig, SQLGeneration
from app.utils.model.chat_model import ChatModel
from app.utils.sql_database.sql_database import SQLDatabase

# Feature flag for gradual rollout of LangGraph evaluators
USE_LANGGRAPH_EVALUATORS = os.getenv("USE_LANGGRAPH_EVALUATORS", "false").lower() == "true"


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


# Lazy imports for evaluator implementations
def get_evaluation_agent(llm_config: LLMConfig) -> Evaluator:
    """Factory function to get the appropriate evaluation agent based on feature flag."""
    if USE_LANGGRAPH_EVALUATORS:
        from app.utils.sql_evaluator.eval_agent_graph import LangGraphEvaluationAgent
        evaluator = LangGraphEvaluationAgent()
        evaluator.llm_config = llm_config
        return evaluator
    else:
        from app.utils.sql_evaluator.eval_agent import EvaluationAgent
        evaluator = EvaluationAgent()
        evaluator.llm_config = llm_config
        return evaluator


def get_simple_evaluator(llm_config: LLMConfig) -> Evaluator:
    """Factory function to get the appropriate simple evaluator based on feature flag."""
    if USE_LANGGRAPH_EVALUATORS:
        from app.utils.sql_evaluator.simple_evaluator_lcel import SimpleEvaluatorLCEL
        evaluator = SimpleEvaluatorLCEL()
        evaluator.llm_config = llm_config
        return evaluator
    else:
        from app.utils.sql_evaluator.simple_evaluator import SimpleEvaluator
        evaluator = SimpleEvaluator()
        evaluator.llm_config = llm_config
        return evaluator
