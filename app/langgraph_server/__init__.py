"""
LangGraph Server Entry Points

This module provides graph definitions for LangGraph server deployment.
These graphs can be deployed to:
- LangGraph Platform (cloud)
- Self-hosted LangGraph server (langgraph up)
- LangGraph Studio (development)

Usage:
    # In langgraph.json:
    {
        "graphs": {
            "session": "app.langgraph_server:session_graph",
            "sql_agent": "app.langgraph_server:sql_agent_graph"
        }
    }
"""

from app.langgraph_server.graphs import (
    session_graph,
    sql_agent_graph,
    create_session_graph,
    create_sql_agent_graph,
)

__all__ = [
    "session_graph",
    "sql_agent_graph",
    "create_session_graph",
    "create_sql_agent_graph",
]
