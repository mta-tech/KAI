import datetime
import logging
import os
from queue import Queue
from threading import Thread
from typing import Any, Dict, List

from langchain.agents.agent import AgentExecutor
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains.llm import LLMChain
from langchain_community.callbacks import get_openai_callback
from langchain_openai import OpenAIEmbeddings
from overrides import override

from app.data.db.storage import Storage
from app.modules.context_store.services import ContextStoreService
from app.modules.database_connection.models import DatabaseConnection
from app.modules.instruction.services import InstructionService
from app.modules.prompt.models import Prompt
from app.modules.sql_generation.models import SQLGeneration
from app.modules.sql_generation.repositories import SQLGenerationRepository
from app.modules.table_description.models import (
    TableDescriptionStatus,
)
from app.modules.table_description.repositories import TableDescriptionRepository
from app.server.config import Settings
from app.utils.prompts.agent_prompts import (
    AGENT_PREFIX,
    ERROR_PARSING_MESSAGE,
    FORMAT_INSTRUCTIONS,
    PLAN_BASE,
    PLAN_WITH_FEWSHOT_EXAMPLES,
    PLAN_WITH_FEWSHOT_EXAMPLES_AND_INSTRUCTIONS,
    PLAN_WITH_INSTRUCTIONS,
    SUFFIX_WITH_FEW_SHOT_SAMPLES,
    SUFFIX_WITHOUT_FEW_SHOT_SAMPLES,
)
from app.utils.sql_database.sql_database import SQLDatabase
from app.utils.sql_generator.sql_database_toolkit import SQLDatabaseToolkit
from app.utils.sql_generator.sql_generator import SQLGenerator
from app.utils.sql_tools import replace_unprocessable_characters

logger = logging.getLogger(__name__)


EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-large")


class SQLAgent(SQLGenerator):
    """SQL agent"""

    max_number_of_examples: int = 5  # maximum number of question/SQL pairs
    llm: Any = None
    settings = Settings()

    def remove_duplicate_examples(self, fewshot_exmaples: List[dict]) -> List[dict]:
        returned_result = []
        seen_list = []
        for example in fewshot_exmaples:
            if example["prompt_text"] not in seen_list:
                seen_list.append(example["prompt_text"])
                returned_result.append(example)
        return returned_result

    def create_sql_agent(
        self,
        toolkit: SQLDatabaseToolkit,
        callback_manager: BaseCallbackManager | None = None,
        prefix: str = AGENT_PREFIX,
        suffix: str | None = None,
        format_instructions: str = FORMAT_INSTRUCTIONS,
        input_variables: List[str] | None = None,
        max_examples: int = 20,
        number_of_instructions: int = 1,
        max_iterations: int | None = int(os.getenv("AGENT_MAX_ITERATIONS", "15")),  # noqa: B008
        max_execution_time: float | None = None,
        early_stopping_method: str = "generate",
        verbose: bool = False,
        agent_executor_kwargs: Dict[str, Any] | None = None,
        **kwargs: Dict[str, Any],
    ) -> AgentExecutor:
        """Construct an SQL agent from an LLM and tools."""
        tools = toolkit.get_tools()
        if max_examples > 0 and number_of_instructions > 0:
            plan = PLAN_WITH_FEWSHOT_EXAMPLES_AND_INSTRUCTIONS
            suffix = SUFFIX_WITH_FEW_SHOT_SAMPLES
        elif max_examples > 0:
            plan = PLAN_WITH_FEWSHOT_EXAMPLES
            suffix = SUFFIX_WITH_FEW_SHOT_SAMPLES
        elif number_of_instructions > 0:
            plan = PLAN_WITH_INSTRUCTIONS
            suffix = SUFFIX_WITHOUT_FEW_SHOT_SAMPLES
        else:
            plan = PLAN_BASE
            suffix = SUFFIX_WITHOUT_FEW_SHOT_SAMPLES
        plan = plan.format(
            dialect=toolkit.dialect,
            max_examples=max_examples,
        )
        prefix = prefix.format(
            dialect=toolkit.dialect, max_examples=max_examples, agent_plan=plan
        )
        prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            format_instructions=format_instructions,
            input_variables=input_variables,
        )
        llm_chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            callback_manager=callback_manager,
            verbose=True,
        )
        tool_names = [tool.name for tool in tools]
        agent = ZeroShotAgent(llm_chain=llm_chain, allowed_tools=tool_names, **kwargs)
        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            callback_manager=callback_manager,
            verbose=verbose,
            max_iterations=max_iterations,
            max_execution_time=max_execution_time,
            early_stopping_method=early_stopping_method,
            **(agent_executor_kwargs or {}),
        )

    @override
    def generate_response(  # noqa: PLR0912
        self,
        user_prompt: Prompt,
        database_connection: DatabaseConnection,
        context: List[dict] = None,
        metadata: dict = None,
    ) -> SQLGeneration:  # noqa: PLR0912
        storage = Storage(Settings())
        context_store_service = ContextStoreService(storage)
        instruction_service = InstructionService(storage)
        response = SQLGeneration(
            prompt_id=user_prompt.id,
            llm_config=self.llm_config,
            created_at=str(datetime.datetime.now()),
        )
        self.llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            model_name=self.llm_config.llm_name,
            api_base=self.llm_config.api_base,
        )
        repository = TableDescriptionRepository(storage)
        db_scan = repository.get_all_tables_by_db(
            {
                "db_connection_id": str(database_connection.id),
                "sync_status": TableDescriptionStatus.SCANNED.value,
            }
        )
        if not db_scan:
            raise ValueError("No scanned tables found for database")
        db_scan = SQLGenerator.filter_tables_by_schema(
            db_scan=db_scan, prompt=user_prompt
        )
        few_shot_examples = context_store_service.retrieve_context_for_question(
            user_prompt
        )

        instructions = instruction_service.retrieve_instruction_for_question(
            user_prompt
        )

        if few_shot_examples is not None:
            new_fewshot_examples = self.remove_duplicate_examples(few_shot_examples)
            number_of_samples = len(new_fewshot_examples)
        else:
            new_fewshot_examples = None
            number_of_samples = 0
        logger.info(
            f"Generating SQL response to question: {str(user_prompt.model_dump())}"
        )
        self.database = SQLDatabase.get_sql_engine(database_connection)

        toolkit = SQLDatabaseToolkit(
            db=self.database,
            context=context,
            few_shot_examples=new_fewshot_examples,
            instructions=instructions,
            is_multiple_schema=True if user_prompt.schemas else False,
            db_scan=db_scan,
            embedding=OpenAIEmbeddings(
                openai_api_key=self.settings.require("OPENAI_API_KEY"),
                model=EMBEDDING_MODEL,
            ),
        )
        agent_executor = self.create_sql_agent(
            toolkit=toolkit,
            verbose=True,
            max_examples=number_of_samples,
            number_of_instructions=len(instructions) if instructions is not None else 0,
            max_execution_time=int(os.environ.get("DH_ENGINE_TIMEOUT", 150)),
        )
        agent_executor.return_intermediate_steps = True
        agent_executor.handle_parsing_errors = ERROR_PARSING_MESSAGE
        with get_openai_callback() as cb:
            try:
                result = agent_executor.invoke(
                    {"input": user_prompt.text}, {"metadata": metadata}
                )
                result = self.check_for_time_out_or_tool_limit(result)
            except Exception as e:
                return SQLGeneration(
                    prompt_id=user_prompt.id,
                    tokens_used=cb.total_tokens,
                    completed_at=str(datetime.datetime.now()),
                    sql="",
                    status="INVALID",
                    error=str(e),
                )
        sql_query = ""
        if "```sql" in result["output"]:
            sql_query = self.remove_markdown(result["output"])
        else:
            sql_query = self.extract_query_from_intermediate_steps(
                result["intermediate_steps"]
            )
        logger.info(f"cost: {str(cb.total_cost)} tokens: {str(cb.total_tokens)}")
        response.sql = replace_unprocessable_characters(sql_query)
        response.tokens_used = cb.total_tokens
        response.completed_at = str(datetime.datetime.now())
        if number_of_samples > 0:
            suffix = SUFFIX_WITH_FEW_SHOT_SAMPLES
        else:
            suffix = SUFFIX_WITHOUT_FEW_SHOT_SAMPLES
        response.intermediate_steps = self.construct_intermediate_steps(
            result["intermediate_steps"], suffix=suffix
        )
        return self.create_sql_query_status(
            self.database,
            response.sql,
            response,
        )

    @override
    def stream_response(
        self,
        user_prompt: Prompt,
        database_connection: DatabaseConnection,
        response: SQLGeneration,
        queue: Queue,
        metadata: dict = None,
    ):
        storage = Storage()
        context_store_service = ContextStoreService(storage)
        instruction_service = InstructionService(storage)
        sql_generation_repository = SQLGenerationRepository(storage)
        self.llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            model_name=self.llm_config.llm_name,
            api_base=self.llm_config.api_base,
            streaming=True,
        )
        repository = TableDescriptionRepository(storage)
        db_scan = repository.get_all_tables_by_db(
            {
                "db_connection_id": str(database_connection.id),
                "sync_status": TableDescriptionStatus.SCANNED.value,
            }
        )
        if not db_scan:
            raise ValueError("No scanned tables found for database")
        db_scan = SQLGenerator.filter_tables_by_schema(
            db_scan=db_scan, prompt=user_prompt
        )
        few_shot_examples = context_store_service.retrieve_context_for_question(
            user_prompt
        )

        instructions = instruction_service.retrieve_instruction_for_question(
            user_prompt.db_connection_id
        )
        if few_shot_examples is not None:
            new_fewshot_examples = self.remove_duplicate_examples(few_shot_examples)
            number_of_samples = len(new_fewshot_examples)
        else:
            new_fewshot_examples = None
            number_of_samples = 0
        self.database = SQLDatabase.get_sql_engine(database_connection)

        embedding = OpenAIEmbeddings(
            openai_api_key=self.settings.require("OPENAI_API_KEY"),
            model=EMBEDDING_MODEL,
        )
        toolkit = SQLDatabaseToolkit(
            queuer=queue,
            db=self.database,
            context=[{}],
            few_shot_examples=new_fewshot_examples,
            instructions=instructions,
            is_multiple_schema=True if user_prompt.schemas else False,
            db_scan=db_scan,
            embedding=embedding,
        )
        
        agent_executor = self.create_sql_agent(
            toolkit=toolkit,
            verbose=True,
            max_examples=number_of_samples,
            number_of_instructions=len(instructions) if instructions is not None else 0,
            max_execution_time=int(os.environ.get("DH_ENGINE_TIMEOUT", 150)),
        )
        agent_executor.return_intermediate_steps = True
        agent_executor.handle_parsing_errors = ERROR_PARSING_MESSAGE
        thread = Thread(
            target=self.stream_agent_steps,
            args=(
                user_prompt.text,
                agent_executor,
                response,
                sql_generation_repository,
                queue,
                metadata,
            ),
        )
        thread.start()
