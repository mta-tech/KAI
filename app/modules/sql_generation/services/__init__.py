import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime
from langchain_community.callbacks import get_openai_callback
from fastapi import HTTPException
from dotenv import load_dotenv
import logging

from app.api.requests import (
    PromptSQLGenerationRequest,
    SQLGenerationRequest,
    UpdateMetadataRequest,
)
from app.modules.context_store.services import ContextStoreService
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.prompt.repositories import PromptRepository
from app.modules.prompt.services import PromptService
from app.modules.sql_generation.models import LLMConfig, SQLGeneration
from app.modules.sql_generation.repositories import SQLGenerationRepository
from app.server.config import Settings
from app.utils.sql_database.sql_database import SQLDatabase
from app.utils.sql_evaluator.simple_evaluator import SimpleEvaluator
from app.utils.sql_generator.sql_agent import SQLAgent
from app.utils.sql_generator.sql_agent_dev import FullContextSQLAgent
from app.utils.sql_generator.sql_query_status import create_sql_query_status
from app.utils.model.chat_model import ChatModel
from app.utils.prompts_ner.prompts_ner import (
    get_ner_labels,
    # request_ner_service,
    request_ner_llm,
    # get_prompt_text_ner,
    replace_entities_with_labels,
    get_labels_entities,
    generate_ner_llm,
)

load_dotenv()
logger = logging.getLogger(__name__)


class SQLGenerationService:
    def __init__(self, storage):
        self.settings = Settings()
        self.storage = storage
        self.sql_generation_repository = SQLGenerationRepository(storage)

    def create_sql_generation(
        self, prompt_id: str, sql_generation_request: SQLGenerationRequest
    ) -> SQLGeneration:
        start_time = datetime.now()
        initial_sql_generation = SQLGeneration(
            prompt_id=prompt_id,
            llm_config=(
                sql_generation_request.llm_config
                if sql_generation_request.llm_config
                else LLMConfig()
            )
        )
        if not initial_sql_generation.metadata:
            initial_sql_generation.metadata = {}

        # TODO: explore why using this
        langsmith_metadata = (
            sql_generation_request.metadata.get("lang_smith", {})
            if sql_generation_request.metadata
            else {}
        )

        self.sql_generation_repository.insert(initial_sql_generation)

        prompt_repository = PromptRepository(self.storage)
        prompt = prompt_repository.find_by_id(prompt_id)

        if not prompt:
            self.update_error(initial_sql_generation, f"Prompt {prompt_id} not found")
            raise HTTPException(
                f"Prompt {prompt_id} not found", initial_sql_generation.id
            )

        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(prompt.db_connection_id)

        database = SQLDatabase.get_sql_engine(db_connection, True)

        # Perform Smart Cache
        context_store = ContextStoreService(self.storage).retrieve_exact_prompt(
            prompt.db_connection_id, prompt.text
        )

        sql_generation_setup_end_time = datetime.now()
        # Assing context store SQL
        if context_store:
            sql_generation_request.sql = context_store.sql
            sql_generation_request.evaluate = False
            input_tokens = 0
            output_tokens = 0
            print("Exact context cache HIT!")
        
        else:
            llm_model = ChatModel().get_model(
                    database_connection=None,
                    model_family=sql_generation_request.llm_config.llm_family,
                    model_name=sql_generation_request.llm_config.llm_name,
                    api_base=sql_generation_request.llm_config.api_base,
                    temperature=0,
                    max_retries=2
                )

            with get_openai_callback() as cb:
                try:                
                    similar_prompts = self.get_similar_prompts(prompt=prompt, llm_model=llm_model)
                    if similar_prompts:
                        print("Similar prompt context HIT!")
                        similar_prompt = similar_prompts[0]
                        sql_generation_request.sql = generate_ner_llm(llm_model, similar_prompt['prompt_text'], similar_prompt['sql'], prompt.text)
                except Exception as e:
                    print(e)
                    
            input_tokens = cb.prompt_tokens
            output_tokens = cb.completion_tokens

        # SQL is given in request
        if sql_generation_request.sql:
            sql_generation = SQLGeneration(
                prompt_id=prompt_id,
                llm_config=sql_generation_request.llm_config,
                sql=sql_generation_request.sql,
                input_tokens_used=input_tokens,
                output_tokens_used=output_tokens,
            )
            try:
                sql_generation = create_sql_query_status(
                    db=database, query=sql_generation.sql, sql_generation=sql_generation
                )
            except Exception as e:
                self.update_error(initial_sql_generation, str(e))
                raise HTTPException(str(e), initial_sql_generation.id) from e
        else:
            option = sql_generation_request.metadata.get("option", "")
            if option == "dev":
                sql_generator = FullContextSQLAgent(
                    (
                        sql_generation_request.llm_config
                        if sql_generation_request.llm_config
                        else LLMConfig()
                    ),
                )
            else:
                sql_generator = SQLAgent(
                    (
                        sql_generation_request.llm_config
                        if sql_generation_request.llm_config
                        else LLMConfig()
                    ),
                )

            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        self.generate_response_with_timeout,
                        sql_generator,
                        prompt,
                        db_connection,
                        metadata=langsmith_metadata,
                    )
                    try:
                        sql_generation = future.result(
                            timeout=int(os.environ.get("DH_ENGINE_TIMEOUT", 150))
                        )
                    except TimeoutError as e:
                        self.update_error(
                            initial_sql_generation, "SQL generation request timed out"
                        )
                        raise HTTPException(
                            "SQL generation request timed out",
                            initial_sql_generation.id,
                        ) from e
            except Exception as e:
                self.update_error(initial_sql_generation, str(e))
                raise HTTPException(str(e), initial_sql_generation.id) from e
        thread_pool_end_time = datetime.now()
        if sql_generation_request.evaluate:
            evaluator = SimpleEvaluator()
            evaluator.llm_config = (
                sql_generation_request.llm_config
                if sql_generation_request.llm_config
                else LLMConfig()
            )
            confidence_score = evaluator.get_confidence_score(
                user_prompt=prompt,
                sql_generation=sql_generation,
                database_connection=db_connection,
            )
            initial_sql_generation.evaluate = sql_generation_request.evaluate
            initial_sql_generation.confidence_score = confidence_score
        sql_generation.input_tokens_used += input_tokens
        sql_generation.output_tokens_used += output_tokens

        time_taken = {
            "sql_generation_setup_time": (
                sql_generation_setup_end_time - start_time
            ).total_seconds(),
            # "sql_generation_total_agent_time": (
            #     thread_pool_end_time - sql_generation_setup_end_time
            # ).total_seconds(),
        }

        initial_sql_generation = self.update_the_initial_sql_generation(
            initial_sql_generation, sql_generation
        )
        initial_sql_generation.metadata.setdefault("timing", {}).update(time_taken)
        return initial_sql_generation

    def create_prompt_and_sql_generation(
        self, prompt_sql_generation_request: PromptSQLGenerationRequest
    ) -> SQLGeneration:
        start_time = datetime.now()
        prompt_service = PromptService(self.storage)
        prompt = prompt_service.create_prompt(prompt_sql_generation_request.prompt)
        prompt_end_time = datetime.now()

        sql_generation = self.create_sql_generation(
            prompt.id, prompt_sql_generation_request
        )

        time_taken = {
            "prompt_creation_time": (prompt_end_time - start_time).total_seconds(),
        }

        sql_generation.metadata = sql_generation.metadata or {}
        sql_generation.metadata.setdefault("timing", {}).update(time_taken)

        return SQLGeneration(**sql_generation.model_dump())

    def get_sql_generations(self, prompt_id: str) -> list[SQLGeneration]:
        prompt_repository = PromptRepository(self.storage)
        prompt = prompt_repository.find_by_id(prompt_id)
        if not prompt:
            raise HTTPException(f"Prompt {prompt_id} not found")

        sql_generations = self.sql_generation_repository.find_by(
            {"prompt_id": prompt_id}
        )
        return sql_generations

    def get_sql_generation(self, sql_generation_id: str) -> SQLGeneration:
        sql_generation = self.sql_generation_repository.find_by_id(sql_generation_id)
        if sql_generation is None:
            raise HTTPException(
                status_code=404, detail=f"SQL Generation {sql_generation_id} not found"
            )

        return sql_generation

    def update_sql_generation(
        self, sql_generation_id: str, metadata_request: UpdateMetadataRequest
    ) -> SQLGeneration:
        sql_generation = self.sql_generation_repository.find_by_id(sql_generation_id)
        if sql_generation is None:
            raise HTTPException(
                status_code=404, detail=f"SQL Generation {sql_generation_id} not found"
            )
        sql_generation.metadata = metadata_request.metadata
        return self.sql_generation_repository.update(sql_generation)

    def execute_sql_query(
        self, sql_generation_id: str, max_rows: int = 100
    ) -> tuple[str, dict]:
        sql_generation = self.sql_generation_repository.find_by_id(sql_generation_id)
        if not sql_generation:
            raise HTTPException(f"SQL Generation {sql_generation_id} not found")
        prompt_repository = PromptRepository(self.storage)
        prompt = prompt_repository.find_by_id(sql_generation.prompt_id)
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(prompt.db_connection_id)
        database = SQLDatabase.get_sql_engine(db_connection, True)
        return database.run_sql(sql_generation.sql, max_rows)

    # ================= HELPERS ================= #

    def generate_response_with_timeout(
        self, sql_generator: SQLAgent, user_prompt, db_connection, metadata=None
    ):
        return sql_generator.generate_response(
            user_prompt=user_prompt,
            database_connection=db_connection,
            metadata=metadata,
        )

    def update_error(self, sql_generation: SQLGeneration, error: str) -> SQLGeneration:
        sql_generation.error = error
        return self.sql_generation_repository.update(sql_generation)

    def update_the_initial_sql_generation(
        self, initial_sql_generation: SQLGeneration, sql_generation: SQLGeneration
    ):
        if not sql_generation.metadata:
            sql_generation.metadata = {}
        initial_sql_generation.sql = sql_generation.sql
        initial_sql_generation.input_tokens_used = sql_generation.input_tokens_used
        initial_sql_generation.output_tokens_used = sql_generation.output_tokens_used
        initial_sql_generation.completed_at = str(datetime.now())
        initial_sql_generation.status = sql_generation.status
        initial_sql_generation.error = sql_generation.error
        initial_sql_generation.intermediate_steps = sql_generation.intermediate_steps
        initial_sql_generation.metadata.update(sql_generation.metadata)
        return self.sql_generation_repository.update(initial_sql_generation)

    def get_similar_prompts(
            self,
            prompt: PromptRepository,
            llm_model: ChatModel
        ) -> list[dict] | None:
        labels = get_ner_labels(prompt.text)
        prompt_text_ner = prompt.text
    
        # labels_entities_ner = request_ner_service(prompt.text, labels)
        labels_entities_ner = request_ner_llm(llm_model, prompt.text, labels)
        if labels_entities_ner[0]:
            # prompt_text_ner = get_prompt_text_ner(prompt.text, labels_entities_ner)
            prompt_text_ner = replace_entities_with_labels(prompt.text, labels_entities_ner)
        
        filter_by = get_labels_entities(labels_entities_ner)
        filter_by = {"labels": filter_by.get("labels")}

        
        similar_prompts = ContextStoreService(self.storage).retrieve_exact_prompt_ner(
            prompt.db_connection_id,
            prompt_text_ner,
            filter_by
        )

        return similar_prompts