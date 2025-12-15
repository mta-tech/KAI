"""LangGraph session graph components."""
from typing import Any, Literal
from functools import partial

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver

from app.modules.session.graph.state import SessionState
from app.modules.session.graph.nodes import (
    build_context_node,
    route_query_node,
    reasoning_only_node,
    process_query_node,
    code_execution_node,
    summarize_node,
    save_message_node,
    should_summarize,
)


def build_session_graph(
    sql_generation_service: Any,
    analysis_service: Any,
    llm: Any,
    checkpointer: BaseCheckpointSaver | None = None,
    storage: Any = None
):
    """
    Build the session LangGraph.

    Graph flow:
    START -> build_context -> route_query -> [process_query | reasoning_only | code_execution] -> check_summarize -> [summarize?] -> save_message -> END

    Args:
        sql_generation_service: SQL generation service instance (not used, kept for API compatibility)
        analysis_service: Analysis service instance (handles full SQL gen + execution + analysis)
        llm: Language model for routing, reasoning, and summarization
        checkpointer: Optional checkpointer for persistence
        storage: Storage instance for code_execution node (autonomous agent)

    Returns:
        Compiled LangGraph
    """
    # Create graph with SessionState
    graph = StateGraph(SessionState)

    # Add nodes with bound services
    graph.add_node("build_context", build_context_node)

    # Route query to determine if database access is needed
    graph.add_node(
        "route_query",
        partial(route_query_node, llm=llm)
    )

    # Single node for SQL generation, execution, and analysis (database path)
    graph.add_node(
        "process_query",
        partial(process_query_node, analysis_service=analysis_service)
    )

    # Reasoning-only node for context-based responses
    graph.add_node(
        "reasoning_only",
        partial(reasoning_only_node, llm=llm)
    )

    # Code execution node for ML, statistical analysis, and complex transformations
    # Routes to autonomous agent for Python code execution
    if storage is not None:
        graph.add_node(
            "code_execution",
            partial(code_execution_node, storage=storage)
        )

    graph.add_node(
        "summarize",
        partial(summarize_node, llm=llm)
    )

    graph.add_node("save_message", save_message_node)

    # Define edges
    graph.set_entry_point("build_context")

    graph.add_edge("build_context", "route_query")

    # Conditional routing based on query intent
    def route_by_intent(state: SessionState) -> Literal["process_query", "reasoning_only", "code_execution"]:
        intent = state.get("query_intent", "database_query")
        if intent == "reasoning_only":
            return "reasoning_only"
        elif intent == "code_execution" and storage is not None:
            return "code_execution"
        return "process_query"

    # Build route map based on available nodes
    route_map = {
        "process_query": "process_query",
        "reasoning_only": "reasoning_only"
    }
    if storage is not None:
        route_map["code_execution"] = "code_execution"

    graph.add_conditional_edges(
        "route_query",
        route_by_intent,
        route_map
    )

    # Conditional edge for summarization (from both paths)
    def check_summarize(state: SessionState) -> Literal["summarize", "save_message"]:
        if should_summarize(state):
            return "summarize"
        return "save_message"

    graph.add_conditional_edges(
        "process_query",
        check_summarize,
        {
            "summarize": "summarize",
            "save_message": "save_message"
        }
    )

    graph.add_conditional_edges(
        "reasoning_only",
        check_summarize,
        {
            "summarize": "summarize",
            "save_message": "save_message"
        }
    )

    # Add conditional edges from code_execution if enabled
    if storage is not None:
        graph.add_conditional_edges(
            "code_execution",
            check_summarize,
            {
                "summarize": "summarize",
                "save_message": "save_message"
            }
        )

    graph.add_edge("summarize", "save_message")
    graph.add_edge("save_message", END)

    # Compile with checkpointer
    return graph.compile(checkpointer=checkpointer)


__all__ = [
    "build_session_graph",
    "SessionState",
]
