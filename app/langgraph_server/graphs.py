"""
LangGraph Server Graph Definitions

This module creates and configures graphs for LangGraph server deployment.
Each graph is a compiled StateGraph that can be invoked via the LangGraph API.

The graphs are designed to work with:
- LangGraph Platform's built-in checkpointing
- Custom Typesense checkpointer (for self-hosted)
- LangGraph Studio for development/debugging
"""

import os
import logging
from typing import Any, Literal
from functools import partial

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict, Annotated

from app.server.config import Settings
from app.utils.model.chat_model import ChatModel


logger = logging.getLogger(__name__)

# Initialize settings
settings = Settings()


# =============================================================================
# Session Graph
# =============================================================================

class SessionGraphState(TypedDict):
    """Simplified session state for LangGraph server deployment."""
    # Thread identification (managed by LangGraph server)
    session_id: str
    db_connection_id: str

    # Messages use LangGraph's message reducer
    messages: Annotated[list, add_messages]

    # Current processing state
    current_query: str | None
    current_response: str | None

    # Query routing
    query_intent: Literal["database_query", "reasoning_only"] | None

    # Status
    status: Literal["idle", "processing", "error"]
    error: str | None


def get_llm():
    """Get configured LLM from environment."""
    chat_model = ChatModel()
    return chat_model.get_model(
        database_connection=None,
        temperature=0,
        model_family=settings.CHAT_FAMILY,
        model_name=settings.CHAT_MODEL,
    )


async def session_route_query(state: SessionGraphState) -> dict:
    """Route query to appropriate handler based on intent."""
    query = state.get("current_query", "")
    messages = state.get("messages", [])

    # Simple heuristic: if no previous messages, always go to database
    if not messages or len(messages) < 2:
        return {"query_intent": "database_query"}

    # Check for follow-up question patterns
    follow_up_patterns = [
        "what about", "how about", "and the", "also",
        "can you explain", "why is", "what does that mean"
    ]
    query_lower = query.lower() if query else ""

    if any(pattern in query_lower for pattern in follow_up_patterns):
        return {"query_intent": "reasoning_only"}

    return {"query_intent": "database_query"}


async def session_process_database_query(state: SessionGraphState) -> dict:
    """
    Process database query.

    In full deployment, this connects to AnalysisService.
    For LangGraph server demo, we return a placeholder response.
    """
    query = state.get("current_query", "")
    db_connection_id = state.get("db_connection_id", "")

    # TODO: In production, inject AnalysisService via graph configuration
    # For now, return informative placeholder
    response = f"""To process this database query, the KAI system needs:
1. Database connection: {db_connection_id}
2. Query: {query}

This graph is deployed to LangGraph server. To enable full SQL generation:
- Configure database connections via the KAI API
- Ensure Typesense is running for schema storage
- Set appropriate LLM credentials

The session graph supports:
- Multi-turn conversations with context
- Query routing (database vs reasoning)
- Automatic summarization of long conversations
"""

    return {
        "current_response": response,
        "status": "idle"
    }


async def session_process_reasoning(state: SessionGraphState) -> dict:
    """Process reasoning-only query using conversation context."""
    query = state.get("current_query", "")
    messages = state.get("messages", [])

    # Build context from recent messages
    context_parts = []
    for msg in messages[-5:]:  # Last 5 messages
        if hasattr(msg, 'content'):
            context_parts.append(msg.content[:200])

    context = "\n".join(context_parts)

    try:
        llm = get_llm()
        prompt = f"""Based on the previous conversation context:
{context}

Answer this follow-up question: {query}

Provide a concise, helpful response based on what was discussed."""

        response = await llm.ainvoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)

        return {
            "current_response": response_text,
            "status": "idle"
        }
    except Exception as e:
        logger.exception("Reasoning query failed")
        return {
            "current_response": f"Error processing query: {str(e)}",
            "status": "error",
            "error": str(e)
        }


async def session_save_response(state: SessionGraphState) -> dict:
    """Save response to message history."""
    from langchain_core.messages import AIMessage

    response = state.get("current_response", "")

    return {
        "messages": [AIMessage(content=response)],
        "current_query": None,
        "current_response": None
    }


def create_session_graph(checkpointer=None):
    """
    Create the session graph for LangGraph server.

    Args:
        checkpointer: Optional checkpointer for state persistence.
                     If None, uses MemorySaver for in-memory persistence.

    Returns:
        Compiled StateGraph
    """
    graph = StateGraph(SessionGraphState)

    # Add nodes
    graph.add_node("route_query", session_route_query)
    graph.add_node("process_database", session_process_database_query)
    graph.add_node("process_reasoning", session_process_reasoning)
    graph.add_node("save_response", session_save_response)

    # Entry point
    graph.set_entry_point("route_query")

    # Conditional routing based on query intent
    def route_by_intent(state: SessionGraphState) -> str:
        intent = state.get("query_intent", "database_query")
        if intent == "reasoning_only":
            return "process_reasoning"
        return "process_database"

    graph.add_conditional_edges(
        "route_query",
        route_by_intent,
        {
            "process_database": "process_database",
            "process_reasoning": "process_reasoning"
        }
    )

    # Both paths lead to save_response
    graph.add_edge("process_database", "save_response")
    graph.add_edge("process_reasoning", "save_response")
    graph.add_edge("save_response", END)

    # Compile - LangGraph API handles checkpointing automatically
    # Only use custom checkpointer if explicitly provided (for non-API usage)
    if checkpointer is not None:
        return graph.compile(checkpointer=checkpointer)
    return graph.compile()


# =============================================================================
# SQL Agent Graph
# =============================================================================

class SQLAgentState(TypedDict):
    """State for the ReAct SQL agent."""
    messages: Annotated[list, add_messages]
    question: str
    dialect: str
    iteration_count: int
    max_iterations: int


def create_sql_agent_node(llm_with_tools, system_prompt: str):
    """Create the agent node that processes messages."""
    from langchain_core.messages import SystemMessage, AIMessage

    async def agent_node(state: SQLAgentState) -> dict:
        messages = list(state.get("messages", []))

        # Ensure system prompt is first
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_prompt)] + messages

        response = await llm_with_tools.ainvoke(messages)

        return {
            "messages": [response],
            "iteration_count": state.get("iteration_count", 0) + 1
        }

    return agent_node


def sql_agent_should_continue(state: SQLAgentState) -> str:
    """Determine if agent should continue with tools or finish."""
    from langchain_core.messages import AIMessage

    messages = state.get("messages", [])
    iteration_count = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 15)

    if not messages:
        return END

    last_message = messages[-1]

    if iteration_count >= max_iterations:
        return END

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    return END


def create_sql_agent_graph(
    tools: list | None = None,
    dialect: str = "postgresql",
    max_iterations: int = 15,
    checkpointer=None
):
    """
    Create the SQL agent graph for LangGraph server.

    Args:
        tools: List of tools for the agent. If None, creates basic SQL tools.
        dialect: SQL dialect (postgresql, mysql, sqlite)
        max_iterations: Maximum tool iterations
        checkpointer: Optional checkpointer for state persistence.

    Returns:
        Compiled StateGraph
    """
    from langchain_core.tools import tool

    # Default tools if none provided
    if tools is None:
        @tool
        def list_tables() -> str:
            """List all available tables in the database."""
            return "Tables: users, orders, products, customers (demo mode - connect database for real schema)"

        @tool
        def get_table_schema(table_name: str) -> str:
            """Get the schema for a specific table."""
            return f"Schema for {table_name}: id (int), created_at (timestamp), ... (demo mode)"

        @tool
        def execute_sql(query: str) -> str:
            """Execute a SQL query and return results."""
            return f"Executed: {query}\nResult: (demo mode - connect database for real execution)"

        tools = [list_tables, get_table_schema, execute_sql]

    # Get LLM and bind tools
    llm = get_llm()
    llm_with_tools = llm.bind_tools(tools)

    # System prompt
    system_prompt = f"""You are an expert SQL analyst. Your task is to help users query databases using {dialect} SQL.

You have access to tools to explore the database schema and execute queries.

Process:
1. Use list_tables to see available tables
2. Use get_table_schema to understand table structure
3. Write and execute SQL using execute_sql
4. Provide clear explanations of your findings

Always validate your SQL before execution. If a query fails, analyze the error and try again."""

    # Create graph
    graph = StateGraph(SQLAgentState)

    # Add nodes
    agent_node = create_sql_agent_node(llm_with_tools, system_prompt)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))

    # Add edges
    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent",
        sql_agent_should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    graph.add_edge("tools", "agent")

    # Compile - LangGraph API handles checkpointing automatically
    # Only use custom checkpointer if explicitly provided (for non-API usage)
    if checkpointer is not None:
        return graph.compile(checkpointer=checkpointer)
    return graph.compile()


# =============================================================================
# Pre-configured Graph Instances
# =============================================================================

# These are the graph instances that LangGraph server will load
# They use MemorySaver by default, but LangGraph Platform overrides this

session_graph = create_session_graph()
sql_agent_graph = create_sql_agent_graph()


# =============================================================================
# Graph Factory Functions (for custom configuration)
# =============================================================================

def get_session_graph_with_typesense():
    """
    Get session graph with Typesense checkpointer.

    Use this for self-hosted deployments that need persistent state.
    """
    try:
        from app.modules.session.graph.checkpointer import TypesenseCheckpointer
        from app.data.db.storage import Storage

        storage = Storage(settings)
        checkpointer = TypesenseCheckpointer(storage.client)
        return create_session_graph(checkpointer=checkpointer)
    except Exception as e:
        logger.warning(f"Failed to create Typesense checkpointer: {e}, using MemorySaver")
        return create_session_graph()


def get_sql_agent_with_database(db_connection_id: str):
    """
    Get SQL agent graph configured for a specific database.

    Args:
        db_connection_id: Database connection ID from KAI

    Returns:
        Configured SQL agent graph with real database tools
    """
    try:
        from app.data.db.storage import Storage
        from app.modules.database_connection.repositories import DatabaseConnectionRepository
        from app.utils.sql_database.sql_database import SQLDatabase
        from app.utils.sql_generator.sql_database_toolkit import SQLDatabaseToolkit
        from app.utils.model.embedding_model import EmbeddingModel

        storage = Storage(settings)
        repo = DatabaseConnectionRepository(storage)
        db_connection = repo.find_by_id(db_connection_id)

        if not db_connection:
            raise ValueError(f"Database connection not found: {db_connection_id}")

        database = SQLDatabase.get_sql_engine(db_connection)
        toolkit = SQLDatabaseToolkit(
            db=database,
            embedding=EmbeddingModel().get_model()
        )

        return create_sql_agent_graph(
            tools=toolkit.get_tools(),
            dialect=database.dialect
        )
    except Exception as e:
        logger.exception(f"Failed to create SQL agent with database: {e}")
        raise
