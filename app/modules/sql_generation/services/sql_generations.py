import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime
from queue import Queue

# import pandas as pd

from app.api.requests import SQLGenerationRequest
from app.data.db.storage import Storage
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.prompt.repositories import PromptRepository
from app.modules.sql_generation.models import LLMConfig, SQLGeneration
from app.modules.sql_generation.repositories import SQLGenerationRepository
from app.modules.sql_generation.services.sql_agent import SQLAgent


class SQLGenerationService:
    def __init__(self, system: System, storage: Storage):
        self.system = system
        self.storage = storage
        self.sql_generation_repository = SQLGenerationRepository(self.storage)

    def update_error(self, sql_generation: SQLGeneration, error: str) -> SQLGeneration:
        sql_generation.error = error
        return self.sql_generation_repository.update(sql_generation)

    def generate_response_with_timeout(
        self, sql_generator, user_prompt, db_connection, metadata=None
    ):
        return sql_generator.generate_response(
            user_prompt=user_prompt,
            database_connection=db_connection,
            metadata=metadata,
        )

    def update_the_initial_sql_generation(
        self, initial_sql_generation: SQLGeneration, sql_generation: SQLGeneration
    ):
        initial_sql_generation.sql = sql_generation.sql
        initial_sql_generation.tokens_used = sql_generation.tokens_used
        initial_sql_generation.completed_at = datetime.now()
        initial_sql_generation.status = sql_generation.status
        initial_sql_generation.error = sql_generation.error
        initial_sql_generation.intermediate_steps = sql_generation.intermediate_steps
        return self.sql_generation_repository.update(initial_sql_generation)

    def create(  # noqa: PLR0912
        self, prompt_id: str, sql_generation_request: SQLGenerationRequest
    ) -> SQLGeneration:  # noqa: PLR0912
        initial_sql_generation = SQLGeneration(
            prompt_id=prompt_id,
            created_at=datetime.now(),
            llm_config=(
                sql_generation_request.llm_config
                if sql_generation_request.llm_config
                else LLMConfig()
            ),
            metadata=sql_generation_request.metadata,
        )
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
            raise Exception(f"Prompt {prompt_id} not found", initial_sql_generation.id)

        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(prompt.db_connection_id)

        database = SQLDatabase.get_sql_engine(db_connection, True)
        
        if sql_generation_request.sql is not None:
            sql_generation = SQLGeneration(
                prompt_id=prompt_id,
                sql=sql_generation_request.sql,
                tokens_used=0,
            )
            try:
                sql_generation = create_sql_query_status(
                    db=database, query=sql_generation.sql, sql_generation=sql_generation
                )
            except Exception as e:
                self.update_error(initial_sql_generation, str(e))
                raise Exception(str(e), initial_sql_generation.id) from e
        else:
            sql_generator = SQLAgent(
                self.system,
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
                        raise Exception(
                            "SQL generation request timed out",
                            initial_sql_generation.id,
                        ) from e
            except Exception as e:
                self.update_error(initial_sql_generation, str(e))
                raise Exception(str(e), initial_sql_generation.id) from e
        if sql_generation_request.evaluate:
            evaluator = self.system.instance(Evaluator)
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
        return self.update_the_initial_sql_generation(
            initial_sql_generation, sql_generation
        )

    def start_streaming(
        self, prompt_id: str, sql_generation_request: SQLGenerationRequest, queue: Queue
    ):
        initial_sql_generation = SQLGeneration(
            prompt_id=prompt_id,
            created_at=datetime.now(),
            llm_config=(
                sql_generation_request.llm_config
                if sql_generation_request.llm_config
                else LLMConfig()
            ),
            metadata=sql_generation_request.metadata,
        )
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
            raise Exception(f"Prompt {prompt_id} not found", initial_sql_generation.id)
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(prompt.db_connection_id)

        sql_generator = SQLAgent(
            self.system,
            (
                sql_generation_request.llm_config
                if sql_generation_request.llm_config
                else LLMConfig()
            ),
        )
        try:
            sql_generator.stream_response(
                user_prompt=prompt,
                database_connection=db_connection,
                response=initial_sql_generation,
                queue=queue,
                metadata=langsmith_metadata,
            )
        except Exception as e:
            self.update_error(initial_sql_generation, str(e))
            raise Exception(str(e), initial_sql_generation.id) from e

    def get(self, query) -> list[SQLGeneration]:
        return self.sql_generation_repository.find_by(query)

    def execute(self, sql_generation_id: str, max_rows: int = 100) -> tuple[str, dict]:
        sql_generation = self.sql_generation_repository.find_by_id(sql_generation_id)
        if not sql_generation:
            raise Exception(f"SQL Generation {sql_generation_id} not found")
        prompt_repository = PromptRepository(self.storage)
        prompt = prompt_repository.find_by_id(sql_generation.prompt_id)
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(prompt.db_connection_id)
        database = SQLDatabase.get_sql_engine(db_connection, True)
        return database.run_sql(sql_generation.sql, max_rows)

    def update_metadata(self, sql_generation_id, metadata_request) -> SQLGeneration:
        sql_generation = self.sql_generation_repository.find_by_id(sql_generation_id)
        if not sql_generation:
            raise Exception(f"Sql generation {sql_generation_id} not found")
        sql_generation.metadata = metadata_request.metadata
        return self.sql_generation_repository.update(sql_generation)

    # def create_dataframe(self, sql_generation_id):
    #     sql_generation = self.sql_generation_repository.find_by_id(sql_generation_id)
    #     if not sql_generation:
    #         raise Exception(f"Sql generation {sql_generation_id} not found")
    #     prompt_repository = PromptRepository(self.storage)
    #     prompt = prompt_repository.find_by_id(sql_generation.prompt_id)
    #     db_connection_repository = DatabaseConnectionRepository(self.storage)
    #     db_connection = db_connection_repository.find_by_id(prompt.db_connection_id)
    #     database = SQLDatabase.get_sql_engine(db_connection)
    #     results = database.run_sql(sql_generation.sql)
    #     if results is None:
    #         raise Exception(f"Sql generation {sql_generation_id} is empty")
    #     data = results[1]["result"]
    #     return pd.DataFrame(data)
