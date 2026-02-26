"""Tests for session graph nodes."""
import pytest
from datetime import datetime

from app.modules.session.graph.state import SessionState, create_initial_state
from app.modules.session.graph.nodes import (
    should_summarize,
    format_context_for_llm,
    format_history_for_summarization,
)


def test_should_summarize_when_messages_exceed_threshold():
    """Should return True when messages exceed threshold."""
    state = create_initial_state("sess_123", "db_456")
    state["messages"] = [
        {"id": f"msg_{i}", "role": "human", "query": f"Query {i}", "sql": None, "results_summary": None, "analysis": None, "timestamp": "2024-01-01T00:00:00"}
        for i in range(6)
    ]

    assert should_summarize(state) is True


def test_should_not_summarize_when_few_messages():
    """Should return False when messages are under threshold."""
    state = create_initial_state("sess_123", "db_456")
    state["messages"] = [
        {"id": "msg_1", "role": "human", "query": "Query 1", "sql": None, "results_summary": None, "analysis": None, "timestamp": "2024-01-01T00:00:00"}
    ]

    assert should_summarize(state) is False


def test_format_context_for_llm_with_summary():
    """Should include summary and recent messages."""
    state = create_initial_state("sess_123", "db_456")
    state["summary"] = "Previous discussion about sales data."
    state["messages"] = [
        {"id": "msg_1", "role": "human", "query": "Show revenue", "sql": "SELECT SUM(revenue)...", "results_summary": "Total: $1M", "analysis": None, "timestamp": "2024-01-01T00:00:00"},
        {"id": "msg_2", "role": "human", "query": "By region", "sql": "SELECT region, SUM(revenue)...", "results_summary": "Top: West", "analysis": None, "timestamp": "2024-01-01T00:00:00"},
    ]

    context = format_context_for_llm(state)

    assert "Previous discussion about sales data" in context
    assert "Show revenue" in context
    assert "By region" in context


def test_format_context_for_llm_without_summary():
    """Should only include recent messages when no summary."""
    state = create_initial_state("sess_123", "db_456")
    state["messages"] = [
        {"id": "msg_1", "role": "human", "query": "Show customers", "sql": "SELECT * FROM customers", "results_summary": "10 rows", "analysis": None, "timestamp": "2024-01-01T00:00:00"},
    ]

    context = format_context_for_llm(state)

    assert "Show customers" in context
    assert "Previous context" not in context


def test_format_context_limits_to_recent_messages():
    """Should only include last 3 messages."""
    state = create_initial_state("sess_123", "db_456")
    state["messages"] = [
        {"id": f"msg_{i}", "role": "human", "query": f"Query {i}", "sql": f"SQL {i}", "results_summary": f"Result {i}", "analysis": None, "timestamp": "2024-01-01T00:00:00"}
        for i in range(5)
    ]

    context = format_context_for_llm(state)

    # Should have last 3 (indices 2, 3, 4)
    assert "Query 2" in context
    assert "Query 3" in context
    assert "Query 4" in context
    # Should not have older ones
    assert "Query 0" not in context
    assert "Query 1" not in context


def test_format_history_for_summarization():
    """Should format messages for summarization."""
    messages = [
        {"id": "msg_1", "role": "human", "query": "Query 1", "sql": "SELECT 1", "results_summary": "Result 1", "analysis": "Analysis 1", "timestamp": "2024-01-01T00:00:00"},
        {"id": "msg_2", "role": "human", "query": "Query 2", "sql": "SELECT 2", "results_summary": "Result 2", "analysis": None, "timestamp": "2024-01-01T00:00:00"},
    ]

    history = format_history_for_summarization(messages)

    assert "Query 1" in history
    assert "SELECT 1" in history
    assert "Result 1" in history
    assert "Query 2" in history
    assert "---" in history  # Separator
