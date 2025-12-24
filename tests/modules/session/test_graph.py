"""Tests for session graph builder."""
import pytest
from unittest.mock import MagicMock, AsyncMock

from app.modules.session.graph import build_session_graph


def test_build_session_graph_returns_compiled_graph():
    """Should return a compiled LangGraph."""
    mock_sql_service = MagicMock()
    mock_analysis_service = MagicMock()
    mock_llm = MagicMock()
    mock_checkpointer = MagicMock()

    graph = build_session_graph(
        sql_generation_service=mock_sql_service,
        analysis_service=mock_analysis_service,
        llm=mock_llm,
        checkpointer=mock_checkpointer
    )

    assert graph is not None
    # LangGraph compiled graphs have invoke/ainvoke
    assert hasattr(graph, 'invoke') or hasattr(graph, 'ainvoke')


def test_build_session_graph_without_checkpointer():
    """Should build graph without checkpointer."""
    mock_sql_service = MagicMock()
    mock_analysis_service = MagicMock()
    mock_llm = MagicMock()

    graph = build_session_graph(
        sql_generation_service=mock_sql_service,
        analysis_service=mock_analysis_service,
        llm=mock_llm,
        checkpointer=None
    )

    assert graph is not None
