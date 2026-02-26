"""LangGraph ReAct SQL Agent - replacement for deprecated ZeroShotAgent pattern."""

import logging
import os
from datetime import datetime
from queue import Queue
from typing import Annotated, Any, Dict, List, Tuple

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_community.callbacks import get_openai_callback
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from overrides import override
from typing_extensions import TypedDict

from app.data.db.storage import Storage
from app.modules.business_glossary.services import BusinessGlossaryService
from app.modules.context_store.services import ContextStoreService
from app.modules.database_connection.models import DatabaseConnection
from app.modules.instruction.services import InstructionService
from app.modules.prompt.models import Prompt
from app.modules.sql_generation.models import IntermediateStep, SQLGeneration
from app.modules.table_description.models import TableDescriptionStatus
from app.modules.table_description.repositories import TableDescriptionRepository
from app.utils.model.embedding_model import EmbeddingModel
from app.utils.prompts.agent_prompts import (
    AGENT_PREFIX,
    PLAN_BASE,
    PLAN_WITH_FEWSHOT_EXAMPLES,
    PLAN_WITH_FEWSHOT_EXAMPLES_AND_INSTRUCTIONS,
    PLAN_WITH_INSTRUCTIONS,
)
from app.utils.sql_database.sql_database import SQLDatabase
from app.utils.sql_generator.sql_database_toolkit import SQLDatabaseToolkit
from app.utils.sql_generator.sql_generator import SQLGenerator
from app.utils.sql_generator.sql_history import SQLHistory
from app.utils.sql_tools import replace_unprocessable_characters

logger = logging.getLogger(__name__)


class ReActSQLAgentState(TypedDict):
    """State schema for the LangGraph ReAct SQL Agent."""

    messages: Annotated[list[BaseMessage], add_messages]
    question: str
    dialect: str
    tools: List[Any]
    iteration_count: int
    max_iterations: int
    intermediate_steps: List[Tuple[Any, str]]


def build_system_prompt(
    dialect: str,
    sql_history: str | None,
    max_examples: int,
    number_of_instructions: int,
    tool_names: List[str],
) -> str:
    """Build the system prompt for the ReAct SQL agent."""
    if max_examples > 0 and number_of_instructions > 0:
        plan = PLAN_WITH_FEWSHOT_EXAMPLES_AND_INSTRUCTIONS
    elif max_examples > 0:
        plan = PLAN_WITH_FEWSHOT_EXAMPLES
    elif number_of_instructions > 0:
        plan = PLAN_WITH_INSTRUCTIONS
    else:
        plan = PLAN_BASE

    plan = plan.format(dialect=dialect, max_examples=max_examples)

    prefix = AGENT_PREFIX.format(
        dialect=dialect,
        sql_history=sql_history or "",
        max_examples=max_examples,
        agent_plan=plan,
    )

    system_prompt = f"""{prefix}

You have access to the following tools: {', '.join(tool_names)}

When you need to use a tool, you MUST use the tool calling format.
After gathering enough information, provide your final answer with the SQL query in ```sql and ``` format.

Important:
- Use tools to explore the database schema and validate your queries
- Always test your SQL query using the SqlDbQuery tool before providing the final answer
- If a query fails, analyze the error and try again
"""
    return system_prompt


def create_agent_node(llm_with_tools, system_prompt: str):
    """Create the agent node that invokes the LLM with bound tools."""

    def agent_node(state: ReActSQLAgentState) -> Dict[str, Any]:
        """Agent node that processes messages and decides on tool calls or final answer."""
        messages = state["messages"]

        # Ensure system prompt is first
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_prompt)] + list(messages)
        elif messages and isinstance(messages[0], SystemMessage):
            # Update system message if it exists
            messages = [SystemMessage(content=system_prompt)] + list(messages[1:])

        # Invoke LLM
        response = llm_with_tools.invoke(messages)

        # Update iteration count
        new_iteration_count = state.get("iteration_count", 0) + 1

        return {
            "messages": [response],
            "iteration_count": new_iteration_count,
        }

    return agent_node


def should_continue(state: ReActSQLAgentState) -> str:
    """Determine if the agent should continue with tool calls or finish."""
    messages = state["messages"]
    iteration_count = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 15)

    if not messages:
        return END

    last_message = messages[-1]

    # Check iteration limit
    if iteration_count >= max_iterations:
        logger.warning(f"Max iterations ({max_iterations}) reached")
        return END

    # Check if LLM wants to use tools
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    return END


def extract_intermediate_steps(
    messages: List[BaseMessage],
) -> List[Tuple[Any, str]]:
    """Extract intermediate steps from message history for backward compatibility."""
    from langchain_core.agents import AgentAction

    intermediate_steps = []

    i = 0
    while i < len(messages):
        msg = messages[i]

        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tool_call in msg.tool_calls:
                # Find the corresponding tool response
                tool_response = ""
                for j in range(i + 1, len(messages)):
                    if isinstance(messages[j], ToolMessage):
                        if messages[j].tool_call_id == tool_call["id"]:
                            tool_response = messages[j].content
                            break

                # Create AgentAction for backward compatibility
                thought = msg.content or ""
                action = AgentAction(
                    tool=tool_call["name"],
                    tool_input=tool_call["args"]
                    if isinstance(tool_call["args"], str)
                    else str(tool_call["args"]),
                    log=f"Thought: {thought}\nAction: {tool_call['name']}\nAction Input: {tool_call['args']}",
                )
                intermediate_steps.append((action, tool_response))

        i += 1

    return intermediate_steps


def build_react_sql_agent_graph(
    llm,
    toolkit: SQLDatabaseToolkit,
    sql_history: str | None = None,
    max_examples: int = 3,
    number_of_instructions: int = 0,
    max_iterations: int = 15,
):
    """Build and compile the LangGraph ReAct SQL agent."""
    tools = toolkit.get_tools()
    tool_names = [tool.name for tool in tools]

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)

    # Build system prompt
    system_prompt = build_system_prompt(
        dialect=toolkit.dialect,
        sql_history=sql_history,
        max_examples=max_examples,
        number_of_instructions=number_of_instructions,
        tool_names=tool_names,
    )

    # Create graph
    graph = StateGraph(ReActSQLAgentState)

    # Add nodes
    agent_node = create_agent_node(llm_with_tools, system_prompt)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))

    # Add edges
    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )
    graph.add_edge("tools", "agent")

    return graph.compile()


class LangGraphReActSQLAgent(SQLGenerator):
    """LangGraph ReAct SQL Agent - implements SQLGenerator interface."""

    from app.server.config import Settings

    max_number_of_examples: int = 5
    llm: Any = None
    settings: Settings = Settings()

    def remove_duplicate_examples(self, fewshot_examples: List[dict]) -> List[dict]:
        """Remove duplicate examples based on prompt_text."""
        returned_result = []
        seen_list = set()
        for example in fewshot_examples:
            prompt_text = example["prompt_text"]
            if prompt_text not in seen_list:
                seen_list.add(prompt_text)
                returned_result.append(example)
        return returned_result

    @override
    def generate_response(
        self,
        user_prompt: Prompt,
        database_connection: DatabaseConnection,
        context: List[dict] = None,
        metadata: dict = None,
    ) -> SQLGeneration:
        """Generate SQL response using LangGraph ReAct agent."""
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
            temperature=0,
            model_family=self.llm_config.model_family,
            model_name=self.llm_config.model_name,
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

        db_scan = SQLGenerator.filter_tables_by_schema(db_scan=db_scan, prompt=user_prompt)

        few_shot_examples = context_store_service.retrieve_context_for_question(user_prompt)
        instructions = instruction_service.retrieve_instruction_for_question(user_prompt)
        business_metrics = business_metrics_service.retrieve_business_metrics_for_question(
            user_prompt
        )

        if few_shot_examples is not None:
            new_fewshot_examples = self.remove_duplicate_examples(few_shot_examples)
            number_of_samples = len(new_fewshot_examples)
        else:
            new_fewshot_examples = None
            number_of_samples = 0

        number_of_metrics = len(business_metrics) if business_metrics else 0
        number_of_context = number_of_samples + number_of_metrics

        logger.info(f"Generating SQL response to question: {str(user_prompt.model_dump())}")

        self.database = SQLDatabase.get_sql_engine(database_connection)

        toolkit = SQLDatabaseToolkit(
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

        # Build and run the LangGraph agent
        max_iterations = int(os.getenv("AGENT_MAX_ITERATIONS", "15"))
        graph = build_react_sql_agent_graph(
            llm=self.llm,
            toolkit=toolkit,
            sql_history=SQLHistory.get_sql_history(user_prompt),
            max_examples=number_of_context,
            number_of_instructions=len(instructions) if instructions else 0,
            max_iterations=max_iterations,
        )

        initial_state: ReActSQLAgentState = {
            "messages": [HumanMessage(content=user_prompt.text)],
            "question": user_prompt.text,
            "dialect": toolkit.dialect,
            "tools": toolkit.get_tools(),
            "iteration_count": 0,
            "max_iterations": max_iterations,
            "intermediate_steps": [],
        }

        with get_openai_callback() as cb:
            try:
                result = graph.invoke(initial_state, {"metadata": metadata})
            except Exception as e:
                logger.exception("LangGraph agent execution failed")
                return SQLGeneration(
                    prompt_id=user_prompt.id,
                    input_tokens_used=cb.prompt_tokens,
                    output_tokens_used=cb.completion_tokens,
                    completed_at=str(datetime.now()),
                    sql="",
                    status="INVALID",
                    error=str(e),
                )

        # Extract SQL from final message
        messages = result.get("messages", [])
        sql_query = ""

        if messages:
            final_message = messages[-1]
            if isinstance(final_message, AIMessage):
                content = final_message.content or ""
                if "```sql" in content:
                    sql_query = self.remove_markdown(content)
                else:
                    # Try to extract from intermediate steps
                    intermediate_steps = extract_intermediate_steps(messages)
                    sql_query = self.extract_query_from_intermediate_steps(intermediate_steps)

        agent_execution_end_time = datetime.now()
        logger.info(f"cost: {str(cb.total_cost)} tokens: {str(cb.total_tokens)}")

        response.sql = replace_unprocessable_characters(sql_query)
        response.input_tokens_used = cb.prompt_tokens
        response.output_tokens_used = cb.completion_tokens
        response.completed_at = str(datetime.now())

        # Build intermediate steps for backward compatibility
        intermediate_steps = extract_intermediate_steps(messages)
        response.intermediate_steps = self._build_intermediate_steps(intermediate_steps)

        result_response = self.create_sql_query_status(
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
        result_response.metadata = result_response.metadata or {}
        result_response.metadata["timing"] = time_taken
        result_response.metadata["runtime"] = "langgraph_react"

        return result_response

    def _build_intermediate_steps(
        self, intermediate_steps: List[Tuple[Any, str]]
    ) -> List[IntermediateStep]:
        """Build IntermediateStep objects from raw intermediate steps."""
        formatted_steps = []
        for step in intermediate_steps:
            action, observation = step
            if action.tool == "SqlDbQuery":
                formatted_steps.append(
                    IntermediateStep(
                        thought=str(action.log).split("Action:")[0] if "Action:" in str(action.log) else str(action.log),
                        action=action.tool,
                        action_input=str(action.tool_input),
                        observation="QUERY RESULTS ARE NOT STORED FOR PRIVACY REASONS.",
                    )
                )
            else:
                formatted_steps.append(
                    IntermediateStep(
                        thought=str(action.log).split("Action:")[0] if "Action:" in str(action.log) else str(action.log),
                        action=action.tool,
                        action_input=str(action.tool_input),
                        observation=self.truncate_observations(str(observation)),
                    )
                )
        return formatted_steps

    @override
    def stream_response(
        self,
        user_prompt: Prompt,
        database_connection: DatabaseConnection,
        response: SQLGeneration,
        queue: Queue,
        metadata: dict = None,
    ):
        """Stream SQL response using LangGraph ReAct agent."""
        storage = Storage(self.settings)
        context_store_service = ContextStoreService(storage)
        instruction_service = InstructionService(storage)
        business_metrics_service = BusinessGlossaryService(storage)

        self.llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            model_family=self.llm_config.model_family,
            model_name=self.llm_config.model_name,
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
            queue.put("Error: No scanned tables found for database\n")
            queue.put(None)
            return

        db_scan = SQLGenerator.filter_tables_by_schema(db_scan=db_scan, prompt=user_prompt)

        few_shot_examples = context_store_service.retrieve_context_for_question(user_prompt)
        instructions = instruction_service.retrieve_instruction_for_question(user_prompt)
        business_metrics = business_metrics_service.retrieve_business_metrics_for_question(
            user_prompt
        )

        if few_shot_examples is not None:
            new_fewshot_examples = self.remove_duplicate_examples(few_shot_examples)
            number_of_samples = len(new_fewshot_examples)
        else:
            new_fewshot_examples = None
            number_of_samples = 0

        number_of_metrics = len(business_metrics) if business_metrics else 0
        number_of_context = number_of_samples + number_of_metrics

        self.database = SQLDatabase.get_sql_engine(database_connection)

        toolkit = SQLDatabaseToolkit(
            db=self.database,
            context=None,
            few_shot_examples=new_fewshot_examples,
            business_metrics=business_metrics,
            instructions=instructions,
            is_multiple_schema=len(user_prompt.schemas) > 1 if user_prompt.schemas else False,
            db_scan=db_scan,
            embedding=EmbeddingModel().get_model(),
        )

        max_iterations = int(os.getenv("AGENT_MAX_ITERATIONS", "15"))
        graph = build_react_sql_agent_graph(
            llm=self.llm,
            toolkit=toolkit,
            sql_history=SQLHistory.get_sql_history(user_prompt),
            max_examples=number_of_context,
            number_of_instructions=len(instructions) if instructions else 0,
            max_iterations=max_iterations,
        )

        initial_state: ReActSQLAgentState = {
            "messages": [HumanMessage(content=user_prompt.text)],
            "question": user_prompt.text,
            "dialect": toolkit.dialect,
            "tools": toolkit.get_tools(),
            "iteration_count": 0,
            "max_iterations": max_iterations,
            "intermediate_steps": [],
        }

        try:
            with get_openai_callback() as cb:
                # Stream the graph execution
                for event in graph.stream(initial_state, {"metadata": metadata}):
                    for node_name, node_output in event.items():
                        if node_name == "agent":
                            messages = node_output.get("messages", [])
                            for msg in messages:
                                if isinstance(msg, AIMessage):
                                    if msg.content:
                                        queue.put(
                                            self.format_sql_query_intermediate_steps(msg.content)
                                            + "\n"
                                        )
                                    if msg.tool_calls:
                                        for tool_call in msg.tool_calls:
                                            queue.put(
                                                f"\n**Action:** {tool_call['name']}\n"
                                                f"**Input:** {tool_call['args']}\n"
                                            )
                        elif node_name == "tools":
                            messages = node_output.get("messages", [])
                            for msg in messages:
                                if isinstance(msg, ToolMessage):
                                    truncated = self.truncate_observations(msg.content)
                                    queue.put(
                                        f"\n**Observation:**\n{self.format_sql_query_intermediate_steps(truncated)}\n"
                                    )

                # Get final result
                final_result = graph.invoke(initial_state, {"metadata": metadata})
                messages = final_result.get("messages", [])

                sql_query = ""
                if messages:
                    final_message = messages[-1]
                    if isinstance(final_message, AIMessage):
                        content = final_message.content or ""
                        queue.put(f"\n**Final Answer:**\n{self.format_sql_query_intermediate_steps(content)}")
                        if "```sql" in content:
                            sql_query = self.remove_markdown(content)
                        else:
                            intermediate_steps = extract_intermediate_steps(messages)
                            sql_query = self.extract_query_from_intermediate_steps(
                                intermediate_steps
                            )

                response.sql = replace_unprocessable_characters(sql_query)
                response.input_tokens_used = cb.prompt_tokens
                response.output_tokens_used = cb.completion_tokens
                response.completed_at = str(datetime.now())

                if response.sql:
                    response = self.create_sql_query_status(
                        self.database,
                        response.sql,
                        response,
                    )
                else:
                    response.status = "INVALID"
                    response.error = "No SQL query generated"

        except Exception as e:
            logger.exception("LangGraph streaming failed")
            response.sql = ""
            response.status = "INVALID"
            response.error = str(e)
        finally:
            queue.put(None)
