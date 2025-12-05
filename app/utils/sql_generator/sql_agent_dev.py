# import datetime
import logging
import os
from queue import Queue
from typing import Any, Dict, List
from datetime import datetime
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_community.callbacks import get_openai_callback
from overrides import override
from concurrent.futures import ThreadPoolExecutor

from app.data.db.storage import Storage
from app.modules.business_glossary.services import BusinessGlossaryService
from app.modules.context_store.services import ContextStoreService
from app.modules.database_connection.models import DatabaseConnection
from app.modules.instruction.services import InstructionService
from app.modules.prompt.models import Prompt
from app.modules.sql_generation.models import SQLGeneration
from app.modules.table_description.models import (
    TableDescriptionStatus,
)
from app.modules.table_description.repositories import TableDescriptionRepository

# from app.server.config import Settings
from app.utils.prompts.agent_prompts import (
    ERROR_PARSING_MESSAGE,
    FORMAT_INSTRUCTIONS,
)
from app.utils.prompts.agent_prompts_dev import (
    AGENT_PREFIX_DEV,
    PLAN_WITH_ALL_CONTEXT,
    SUFFIX_WITH_CONTEXT,
    SUFFIX_WITHOUT_CONTEXT,
    FEWSHOT_PROMPT,
    INSTRUCTION_PROMPT,
    ADDITIONAL_PROMPT,
)
from app.utils.sql_database.sql_database import SQLDatabase

# from app.utils.sql_generator.sql_database_toolkit import SQLDatabaseToolkit
from app.utils.sql_generator.sql_database_toolkit_dev import SQLDatabaseToolkitDev
from app.utils.sql_generator.sql_generator import SQLGenerator
from app.utils.sql_generator.sql_history import SQLHistory
from app.utils.sql_tools import replace_unprocessable_characters
from app.utils.model.embedding_model import EmbeddingModel

logger = logging.getLogger(__name__)


class FullContextSQLAgent(SQLGenerator):
    """SQL agent with all tools registered as Full Context Prompts"""

    from app.server.config import Settings

    max_number_of_examples: int = 5  # maximum number of question/SQL pairs
    llm: Any = None
    settings: Settings = Settings()

    def remove_duplicate_examples(self, fewshot_examples: List[dict]) -> List[dict]:
        returned_result = []
        seen_list = set()
        for example in fewshot_examples:
            prompt_text = example["prompt_text"]
            if prompt_text not in seen_list:
                seen_list.add(prompt_text)
                returned_result.append(example)
        return returned_result

    def create_sql_agent(
        self,
        toolkit: SQLDatabaseToolkitDev,
        sql_history: str | None = None,
        prefix: str = AGENT_PREFIX_DEV,
        suffix: str | None = None,
        format_instructions: str = FORMAT_INSTRUCTIONS,
        max_examples: int = 3,
        instructions: List[dict] | None = None,
        fewshot_examples: List[dict] | None = None,
        aliases: List[dict] | None = None,
        max_iterations: int | None = int(os.getenv("AGENT_MAX_ITERATIONS", "15")),  # noqa: B008
        max_execution_time: float | None = None,
        verbose: bool = False,
        agent_executor_kwargs: Dict[str, Any] | None = None,
        **kwargs: Dict[str, Any],
    ) -> AgentExecutor:
        """Construct an SQL agent from an LLM and tools."""
        tools = toolkit.get_tools()

        fewshot_prompt = ""
        instruction_prompt = ""
        additional_prompt = ""
        alias_prompt = ""

        suffix = SUFFIX_WITHOUT_CONTEXT
        if fewshot_examples:
            fewshot_string = ""
            for example in fewshot_examples[:max_examples]:
                fewshot_string += f"Question: {example['prompt_text']} \n"
                fewshot_string += f"```sql\n{example['sql']}\n```\n"
            fewshot_prompt = FEWSHOT_PROMPT.format(fewshot_examples=fewshot_string)
            additional_prompt = ADDITIONAL_PROMPT
            suffix = SUFFIX_WITH_CONTEXT
        if instructions:
            instruction_string = ""
            for index, instruction in enumerate(instructions):
                instruction_string += f"{index + 1}) {instruction['instruction']}\n"
            instruction_prompt = INSTRUCTION_PROMPT.format(
                admin_instructions=instruction_string
            )

        # Format alias information if provided
        if aliases and len(aliases) > 0:
            alias_prompt = "**) The user's query contains aliases. Here are the mappings between alias names and their actual database objects:\n"
            for alias in aliases:
                alias_prompt += f"- Alias: '{alias['name']}' refers to {alias['target_type']} '{alias['target_name']}'\n"
            alias_prompt += "When generating SQL, use the actual database object names (target_name), not the alias names."

        agent_plan = PLAN_WITH_ALL_CONTEXT.format(
            fewshot_prompt=fewshot_prompt,
            instruction_prompt=instruction_prompt,
            additional_prompt=additional_prompt,
            alias_prompt=alias_prompt,
            dialect=toolkit.dialect,
        )

        prefix = AGENT_PREFIX_DEV.format(
            dialect=toolkit.dialect, agent_plan=agent_plan, sql_history=sql_history
        )

        # Create ReAct-style prompt template
        react_template = f"""{prefix}

You have access to the following tools:

{{tools}}

{format_instructions}

{suffix}

Question: {{input}}
Thought:{{agent_scratchpad}}"""

        prompt = PromptTemplate.from_template(react_template)

        # Use create_react_agent instead of deprecated ZeroShotAgent
        agent = create_react_agent(self.llm, tools, prompt)

        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=verbose,
            max_iterations=max_iterations,
            max_execution_time=max_execution_time,
            handle_parsing_errors=ERROR_PARSING_MESSAGE,
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
        generation_start_time = datetime.now()
        storage = Storage(self.settings)
        context_store_service = ContextStoreService(storage)
        instruction_service = InstructionService(storage)
        business_metrics_service = BusinessGlossaryService(storage)
        response = SQLGeneration(
            prompt_id=user_prompt.id,
            llm_config=self.llm_config,
            created_at=str(generation_start_time),
        )
        self.llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0.1,
            model_family=self.llm_config.model_family,
            model_name=self.llm_config.model_name,
            api_base=self.llm_config.api_base,
        )
        repository = TableDescriptionRepository(storage)

        # Use ThreadPoolExecutor to fetch context in parallel
        with ThreadPoolExecutor() as executor:
            # Get table descriptions (db_scan)
            future_db_scan = executor.submit(
                repository.get_all_tables_by_db,
                {
                    "db_connection_id": str(database_connection.id),
                    "sync_status": TableDescriptionStatus.SCANNED.value,
                },
            )
            # Get few-shot examples
            future_few_shots_examples = executor.submit(
                context_store_service.retrieve_context_for_question, user_prompt
            )
            # Get instructions
            future_instructions = executor.submit(
                instruction_service.retrieve_instruction_for_question, user_prompt
            )
            # Get business metrics
            future_metrics = executor.submit(
                business_metrics_service.retrieve_business_metrics_for_question,
                user_prompt,
            )

            db_scan = future_db_scan.result()
            few_shot_examples = future_few_shots_examples.result()
            instructions = future_instructions.result()
            business_metrics = future_metrics.result()

        if not db_scan:
            raise ValueError("No scanned tables found for database")
        db_scan = SQLGenerator.filter_tables_by_schema(
            db_scan=db_scan, prompt=user_prompt
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

        toolkit = SQLDatabaseToolkitDev(
            db=self.database,
            context=context,
            few_shot_examples=new_fewshot_examples,
            business_metrics=business_metrics,
            instructions=instructions,
            is_multiple_schema=len(user_prompt.schemas) > 1 if user_prompt.schemas else False,
            db_scan=db_scan,
            embedding=EmbeddingModel().get_model(),
        )

        repository_retrieval_end_time = datetime.now()

        agent_executor = self.create_sql_agent(
            toolkit=toolkit,
            verbose=True,
            sql_history=SQLHistory.get_sql_history(user_prompt),
            instructions=instructions,
            fewshot_examples=new_fewshot_examples,
            aliases=metadata.get("aliases")
            if metadata and "aliases" in metadata
            else None,
            max_execution_time=int(os.environ.get("DH_ENGINE_TIMEOUT", 150)),
        )
        agent_executor.return_intermediate_steps = True
        with get_openai_callback() as cb:
            try:
                result = agent_executor.invoke(
                    {"input": user_prompt.text}, {"metadata": metadata}
                )
                result = self.check_for_time_out_or_tool_limit(result)
            except Exception as e:
                return SQLGeneration(
                    prompt_id=user_prompt.id,
                    input_tokens_used=cb.prompt_tokens,
                    output_tokens_used=cb.completion_tokens,
                    completed_at=str(datetime.now()),
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
        agent_execution_end_time = datetime.now()
        logger.info(f"cost: {str(cb.total_cost)} tokens: {str(cb.total_tokens)}")
        response.sql = replace_unprocessable_characters(sql_query)
        response.input_tokens_used = cb.prompt_tokens
        response.output_tokens_used = cb.completion_tokens
        response.completed_at = str(datetime.now())
        if number_of_samples > 0:
            suffix = SUFFIX_WITH_CONTEXT
        else:
            suffix = SUFFIX_WITHOUT_CONTEXT
        response.intermediate_steps = self.construct_intermediate_steps(
            result["intermediate_steps"], suffix=suffix
        )

        result = self.create_sql_query_status(
            self.database,
            response.sql,
            response,
        )

        time_taken = {
            "agent_repository_setup_time": (
                repository_retrieval_end_time - generation_start_time
            ).total_seconds(),
            "agent_execution_time": (
                agent_execution_end_time - repository_retrieval_end_time
            ).total_seconds(),
        }
        result.metadata = result.metadata or {}
        result.metadata["timing"] = time_taken
        return result

    @override
    def stream_response(
        self,
        user_prompt: Prompt,
        database_connection: DatabaseConnection,
        response: SQLGeneration,
        queue: Queue,
        metadata: dict = None,
    ):
        pass
