"""Deep Agent factory for KAI SQL generation.

This module provides the factory function to create LangGraph ReAct agents
for SQL generation using the Deep Agent pattern.
"""

from __future__ import annotations

import logging
import os
from typing import Annotated, Any, Dict, List

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

# Type hints only - avoid circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.database_connection.models import DatabaseConnection
    from app.modules.sql_generation.models import LLMConfig
    from app.utils.sql_database.sql_database import SQLDatabase
    from app.utils.deep_agent.tools import KaiToolContext

logger = logging.getLogger(__name__)


class DeepAgentRuntimeUnavailable(Exception):
    """Raised when deep agent runtime is not available."""
    pass


class DeepAgentState(TypedDict):
    """State schema for the Deep Agent LangGraph."""
    messages: Annotated[list[BaseMessage], add_messages]
    iteration_count: int
    max_iterations: int


def _build_system_prompt(
    dialect: str,
    tenant_id: str,
    prompt_builder,
    extra_instructions: list[str] | None = None,
    tool_names: list[str] | None = None,
) -> str:
    """Build the full system prompt for the Deep Agent."""
    base_prompt = prompt_builder(
        dialect=dialect,
        tenant_id=tenant_id,
        extra_instructions=extra_instructions,
    )

    tools_info = ""
    if tool_names:
        tools_info = f"\n\nYou have access to the following tools: {', '.join(tool_names)}"

    return f"""{base_prompt}
{tools_info}

When you need to use a tool, you MUST use the tool calling format.
After gathering enough information, provide your final answer with the SQL query in ```sql``` format.

Important:
- Use tools to explore the database schema and validate your queries
- Always test your SQL query using the sql_db_query tool before providing the final answer
- If a query fails, analyze the error and try again
- Format your final SQL in a ```sql code block
"""


def _create_agent_node(llm_with_tools, system_prompt: str):
    """Create the agent node that invokes the LLM with bound tools."""

    def agent_node(state: DeepAgentState) -> Dict[str, Any]:
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


def _should_continue(state: DeepAgentState) -> str:
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


def create_kai_sql_agent(
    tenant_id: str,
    sql_generation_id: str,
    db_connection: "DatabaseConnection",
    database: "SQLDatabase",
    context: list[dict] | None,
    tool_context: "KaiToolContext",
    metadata: dict | None,
    extra_instructions: list[str] | None,
    llm_config: "LLMConfig",
):
    """
    Create a LangGraph ReAct agent for SQL generation.

    This factory creates a compiled LangGraph that can be used for both
    synchronous `.invoke()` and streaming `.stream()` execution.

    Args:
        tenant_id: Tenant identifier for isolation
        sql_generation_id: Unique ID for this generation request
        db_connection: Database connection configuration
        database: SQLDatabase instance for query execution
        context: Optional conversation context
        tool_context: KaiToolContext with schema and tool configuration
        metadata: Optional metadata for the generation
        extra_instructions: Additional instructions to include in prompt
        llm_config: LLM configuration (model family, name, etc.)

    Returns:
        Compiled LangGraph agent with `.invoke()` and `.stream()` methods
    """
    # Lazy imports to avoid circular dependencies
    from app.utils.model.chat_model import ChatModel
    from app.utils.deep_agent.tools import build_tool_specs
    from app.utils.deep_agent.prompts import build_sql_agent_system_prompt

    logger.info(f"[DEEPAGENT] Creating KAI SQL agent for tenant: {tenant_id}")

    # Build tools from tool context
    tool_specs = build_tool_specs(tool_context)
    tools = []
    tool_names = []

    for spec in tool_specs:
        try:
            tool = spec.build()
            tools.append(tool)
            tool_names.append(spec.name)
            logger.debug(f"[DEEPAGENT] Built tool: {spec.name}")
        except Exception as e:
            logger.warning(f"[DEEPAGENT] Failed to build tool {spec.name}: {e}")

    if not tools:
        raise DeepAgentRuntimeUnavailable("No tools available for Deep Agent")

    logger.info(f"[DEEPAGENT] Built {len(tools)} tools: {tool_names}")

    # Get LLM
    chat_model = ChatModel()
    llm = chat_model.get_model(
        database_connection=db_connection,
        model_family=llm_config.model_family,
        model_name=llm_config.model_name,
        api_base=llm_config.api_base,
        temperature=0,
    )

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)

    # Build system prompt
    system_prompt = _build_system_prompt(
        dialect=database.dialect,
        tenant_id=tenant_id,
        prompt_builder=build_sql_agent_system_prompt,
        extra_instructions=extra_instructions,
        tool_names=tool_names,
    )

    # Get max iterations from environment
    max_iterations = int(os.getenv("AGENT_MAX_ITERATIONS", "15"))

    # Create graph
    graph = StateGraph(DeepAgentState)

    # Add nodes
    agent_node = _create_agent_node(llm_with_tools, system_prompt)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))

    # Add edges
    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent",
        _should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )
    graph.add_edge("tools", "agent")

    # Compile and return
    compiled_graph = graph.compile()

    logger.info(f"[DEEPAGENT] Agent compiled successfully with {len(tools)} tools")

    return compiled_graph


__all__ = ["create_kai_sql_agent", "DeepAgentRuntimeUnavailable"]
