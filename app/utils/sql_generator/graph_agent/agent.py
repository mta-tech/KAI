import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from queue import Queue

from langchain_community.callbacks import get_openai_callback
from overrides import override

from app.modules.database_connection.models import DatabaseConnection
from app.modules.prompt.models import Prompt
from app.modules.sql_generation.models import SQLGeneration
from app.server.config import Settings
from app.utils.sql_database.sql_database import SQLDatabase
from app.utils.sql_generator.sql_generator import SQLGenerator
from app.utils.sql_tools import replace_unprocessable_characters
from app.utils.sql_generator.graph_agent.state import SQLAgentState
from app.utils.sql_generator.graph_agent.graph import build_sql_agent_graph

logger = logging.getLogger(__name__)


class LangGraphSQLAgent(SQLGenerator):
    """SQL agent implemented using LangGraph."""

    def __init__(self, llm_config):
        super().__init__(llm_config)
        self.settings = Settings()

    def _get_llm(self, database_connection: DatabaseConnection):
        """Get the LLM model configured for the specific database connection."""
        return self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            model_family=self.llm_config.model_family,
            model_name=self.llm_config.model_name,
            api_base=self.llm_config.api_base,
        )

    @override
    def generate_response(
        self,
        user_prompt: Prompt,
        database_connection: DatabaseConnection,
        context: List[dict] = None,
        metadata: dict = None,
    ) -> SQLGeneration:
        """Generate SQL response using LangGraph."""
        generation_start_time = datetime.now()

        # Initialize response object
        response = SQLGeneration(
            prompt_id=user_prompt.id,
            llm_config=self.llm_config,
            created_at=str(generation_start_time),
        )

        # Get LLM
        llm = self._get_llm(database_connection)

        # Build the graph
        graph = build_sql_agent_graph(llm)

        # Initialize the state
        initial_state = SQLAgentState(
            question=user_prompt.text,
            db_connection_id=str(database_connection.id),
            prompt_id=str(user_prompt.id),
            metadata=metadata or {},
        )

        repository_retrieval_end_time = datetime.now()
        # Execute the graph with token tracking
        with get_openai_callback() as cb:
            try:
                logger.info(f"Generating SQL response to question: {user_prompt.text}")
                final_state = graph.invoke(initial_state)

                # Update response with results from final state
                response.sql = replace_unprocessable_characters(
                    final_state.get('generated_sql') or ""
                )
                response.status = final_state.get('status')
                response.error = final_state.get('error')
                response.input_tokens_used = cb.prompt_tokens
                response.output_tokens_used = cb.completion_tokens
                response.completed_at = str(datetime.now())


                # This would be more precise in a real implementation
                agent_execution_end_time = datetime.now()

                time_taken = {
                    "agent_repository_setup_time": (
                        repository_retrieval_end_time - generation_start_time
                    ).total_seconds(),
                    "agent_execution_time": (
                        agent_execution_end_time - repository_retrieval_end_time
                    ).total_seconds(),
                }

                response.metadata = response.metadata or {}
                response.metadata["timing"] = time_taken

                logger.info(
                    f"cost: {str(cb.total_cost)} tokens: {str(cb.total_tokens)}"
                )

            except Exception as e:
                logger.error(f"Error in SQL generation: {str(e)}")
                return SQLGeneration(
                    prompt_id=user_prompt.id,
                    input_tokens_used=cb.prompt_tokens,
                    output_tokens_used=cb.completion_tokens,
                    completed_at=str(datetime.now()),
                    sql="",
                    status="INVALID",
                    error=str(e),
                )

        # Validate the query if needed (this could also be part of the graph)
        if response.sql and response.status != "INVALID":
            self.database = SQLDatabase.get_sql_engine(database_connection)
            response = self.create_sql_query_status(
                self.database,
                response.sql,
                response,
            )

        return response

    @override
    def stream_response(
        self,
        user_prompt: Prompt,
        database_connection: DatabaseConnection,
        response: SQLGeneration,
        queue: Queue,
        metadata: dict = None,
    ):
        """Stream SQL response using LangGraph."""
        # This is a placeholder for streaming implementation
        # LangGraph supports streaming, but it requires more complex setup
        # For now, we'll just generate the full response and put it in the queue

        result = self.generate_response(
            user_prompt=user_prompt,
            database_connection=database_connection,
            metadata=metadata,
        )

        # Put the result in the queue
        queue.put(result)
