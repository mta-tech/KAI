from typing import Any, Dict

from langchain_core.language_models import BaseLLM
from langgraph.graph import StateGraph

from app.utils.sql_generator.graph_agent.state import SQLAgentState
from app.utils.sql_generator.graph_agent.nodes import (
    collect_context,
    identify_relevant_tables,
    analyze_schemas,
    analyze_columns,
    generate_query,
    validate_query,
    format_response,
    should_refine_query,
)


def build_sql_agent_graph(llm: BaseLLM) -> Any:
    """Build and compile the SQL agent graph."""

    # Create a new graph with the SQLAgentState
    graph = StateGraph(SQLAgentState)

    # Add nodes to the graph
    graph.add_node("collect_context", collect_context)
    graph.add_node("identify_tables", identify_relevant_tables)
    graph.add_node("analyze_schemas", analyze_schemas)
    graph.add_node("analyze_columns", analyze_columns)

    # For nodes that require additional parameters (like the LLM),
    # we need to use a lambda to pass them
    graph.add_node("generate_query", lambda state: generate_query(state, llm))

    graph.add_node("validate_query", validate_query)
    graph.add_node("format_response", format_response)

    # Add edges to the graph
    graph.add_edge("collect_context", "identify_tables")
    graph.add_edge("identify_tables", "analyze_schemas")
    graph.add_edge("analyze_schemas", "analyze_columns")
    graph.add_edge("analyze_columns", "generate_query")
    graph.add_edge("generate_query", "validate_query")

    # Add conditional edges
    graph.add_conditional_edges(
        "validate_query",
        should_refine_query,
        {
            "refine": "generate_query",  # Loop back to refine the query
            "complete": "format_response",  # Continue to completion
        },
    )

    # Set entry and exit points
    graph.set_entry_point("collect_context")
    graph.set_finish_point("format_response")

    # Compile the graph
    return graph.compile()
