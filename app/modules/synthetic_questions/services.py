from langchain_community.callbacks import get_openai_callback
import random

from app.data.db.storage import Storage
from app.modules.synthetic_questions.models import (
    QuestionGenerationConfig,
    SyntheticQuestions,
)
from app.utils.question_generator.question_agent import QuestionGenerationAgent
from app.modules.table_description.models import TableDescription
from app.modules.table_description.models import (
    TableDescriptionStatus,
)

from app.utils.prompts.agent_prompts import DATABASE_DESCRIPTION_INTENTS_PROMPT
from app.modules.context_store.models import ContextStore
from app.modules.sql_generation.models import LLMConfig
from app.utils.model.chat_model import ChatModel


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
        llm_config: LLMConfig = None,
        instruction: str = None,
    ) -> SyntheticQuestions:
        """
        Generate synthetic questions based on database schema and optionally context stores.

        This method runs multiple question generation agents in parallel, one for each batch.
        Each agent will generate 'questions_per_batch' questions independently.

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
        table_descriptions_data = self.storage.find(
            collection="table_descriptions",
            filter={
                "db_connection_id": db_connection_id,
                "sync_status": TableDescriptionStatus.SCANNED.value,
            },
        )
        if not table_descriptions_data:
            raise ValueError(
                f"Table descriptions for database connection {db_connection_id} not found or not scanned"
            )

        # Convert raw data to TableDescription objects
        table_descriptions = [
            TableDescription(**row) for row in table_descriptions_data
        ]

        # Get context stores if enabled
        context_stores = []
        if peeking_context_stores:
            context_stores_data = self.storage.find(
                collection="context_stores",
                filter={"db_connection_id": db_connection_id},
            )
            context_stores = [ContextStore(**row) for row in context_stores_data]
            random_context_k = 5
            context_stores = random.sample(context_stores, min(random_context_k, len(context_stores)))

        # Create tasks to run agents in parallel
        tasks = []
        with get_openai_callback() as cb:
            db_description = db_connection.get("description")

            llm = ChatModel().get_model(
                database_connection=None,
                model_family=llm_config.model_family,
                model_name=llm_config.model_name,
                api_base=llm_config.api_base,
                temperature=0,
                max_retries=2,
            )

            db_intent = llm.invoke(
                DATABASE_DESCRIPTION_INTENTS_PROMPT.format(database_description=db_description)
            ).content

            # print(db_description)
            # print(db_intent)
            for batch_index in range(num_batches):
                # Create a question generation configuration for this batch
                # Each batch will have a single iteration (num_batches=1)
                question_generation_config = QuestionGenerationConfig(
                    db_connection_id=db_connection_id,
                    sql_dialect= db_connection.get("dialect"),
                    llm_config=llm_config,
                    questions_per_batch=questions_per_batch,
                    num_batches=1,  # Each agent handles just one batch
                    peeking_context_stores=peeking_context_stores,
                    evaluate=evaluate,
                    instruction=instruction,
                    db_intent=db_intent
                )

                # Create a new agent for each batch to ensure parallel processing
                agent = QuestionGenerationAgent()

                # Add the task to the list
                tasks.append(
                    agent.run(
                        question_generation_config=question_generation_config,
                        table_descriptions=table_descriptions,
                        context_stores=context_stores,
                    )
                )


            # Run all tasks in parallel and wait for all to complete
            import asyncio

            print(f"Starting {num_batches} question generation agents in parallel")
            results = await asyncio.gather(*tasks)


        # Combine all questions from all batches
        all_questions = []
        for question_sql_pairs in results:
            all_questions.extend(
                [pair.model_dump() for pair in question_sql_pairs]
            )

        print(f"Generated a total of {len(all_questions)} questions")
        
        synthetic_questions = SyntheticQuestions(
            questions=all_questions,
            input_tokens_used=cb.prompt_tokens,
            output_tokens_used=cb.completion_tokens,
        )

        return synthetic_questions