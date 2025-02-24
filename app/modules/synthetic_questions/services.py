from typing import List
from app.data.db.storage import Storage
from app.modules.synthetic_questions.models import QuestionGeneration, QuestionSQLPair
from app.utils.question_generator.question_agent import QuestionGenerationAgent
from app.modules.table_description.models import TableDescription
from app.modules.table_description.models import (
    TableDescriptionStatus,
)
from app.modules.context_store.models import ContextStore


class SyntheticQuestionService:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.agent = QuestionGenerationAgent()

    async def generate_questions(
        self,
        db_connection_id: str,
        questions_per_batch: int = 5,
        num_batches: int = 1,
        peeking_context_stores: bool = False,
        evaluate: bool = False,
        llm_config=None,
    ) -> List[str]:
        """
        Generate synthetic questions based on database schema and optionally context stores.

        Args:
            db_connection_id (str): ID of the database connection to use for context
            questions_per_batch (int): Number of questions to generate per batch
            num_batches (int): Number of batches to generate
            peeking_context_stores (bool): Whether to use context stores for additional context
            evaluate (bool): Whether to evaluate generated questions
            llm_config: Optional LLM configuration

        Returns:
            List[str]: List of generated questions
        """
        # Check if database connection exists
        db_connection = self.storage.find_by_id(
            collection="database_connections", id=db_connection_id
        )
        if not db_connection:
            raise ValueError(f"Database connection {db_connection_id} not found")

        # Get table descriptions for context
        table_descriptions = self.storage.find(
            collection="table_descriptions",
            filter={
                "db_connection_id": db_connection_id,
                "sync_status": TableDescriptionStatus.SCANNED.value,
            },
        )
        if not table_descriptions:
            raise ValueError(
                f"Table descriptions for database connection {db_connection_id} not found or not scanned"
            )

        table_descriptions = [TableDescription(**row) for row in table_descriptions]

        # Get context stores if enabled
        context_stores = []
        if peeking_context_stores:
            context_stores = self.storage.find(
                collection="context_stores",
                filter={"db_connection_id": db_connection_id},
            )
        context_stores = [ContextStore(**row) for row in context_stores]

        # Create question generation configuration
        question_generation = QuestionGeneration(
            db_connection_id=db_connection_id,
            llm_config=llm_config,
            questions_per_batch=questions_per_batch,
            num_batches=num_batches,
            peeking_context_stores=peeking_context_stores,
            evaluate=evaluate,
        )

        # Run the question generation agent
        result = await self.agent.run(
            question_generation=question_generation,
            table_descriptions=table_descriptions,
            context_stores=context_stores,
        )

        # Extract just the questions from the question-SQL pairs
        return [pair.question for pair in result.question_sql_pairs]
