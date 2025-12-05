"""Session graph nodes for LangGraph."""
import uuid
from datetime import datetime
from typing import Any

from app.api.requests import PromptRequest
from app.modules.session.graph.state import SessionState, MessageDict
from app.modules.session.constants import (
    MAX_FULL_MESSAGES,
    SUMMARIZE_THRESHOLD_MESSAGES,
    MAX_SUMMARY_TOKENS,
    SUMMARIZATION_PROMPT,
)
from app.modules.session.prompts import ROUTER_PROMPT, REASONING_PROMPT


def should_summarize(state: SessionState) -> bool:
    """
    Determine if conversation history should be summarized.

    Args:
        state: Current session state

    Returns:
        True if summarization is needed
    """
    message_count = len(state.get("messages", []))
    return message_count > SUMMARIZE_THRESHOLD_MESSAGES


def format_context_for_llm(state: SessionState) -> str:
    """
    Format conversation context for LLM consumption.

    Combines summary (if exists) with recent full messages.

    Args:
        state: Current session state

    Returns:
        Formatted context string
    """
    context_parts = []

    # Add summary if exists
    if state.get("summary"):
        context_parts.append(f"Previous context:\n{state['summary']}")

    # Add recent messages in full
    messages = state.get("messages", [])
    recent_messages = messages[-MAX_FULL_MESSAGES:] if messages else []

    for msg in recent_messages:
        parts = [f"Q: {msg.get('query', '')}"]
        if msg.get("sql"):
            parts.append(f"SQL: {msg['sql']}")
        if msg.get("results_summary"):
            parts.append(f"Result: {msg['results_summary']}")
        if msg.get("analysis"):
            parts.append(f"Response: {msg['analysis']}")
        context_parts.append("\n".join(parts))

    return "\n\n".join(context_parts)


def format_history_for_summarization(messages: list[MessageDict]) -> str:
    """
    Format message history for summarization prompt.

    Args:
        messages: List of messages to summarize

    Returns:
        Formatted history string
    """
    history_parts = []
    for msg in messages:
        entry = f"Q: {msg.get('query', '')}"
        if msg.get("sql"):
            entry += f"\nSQL: {msg['sql']}"
        if msg.get("results_summary"):
            entry += f"\nResult: {msg['results_summary']}"
        if msg.get("analysis"):
            analysis = msg["analysis"]
            # Truncate long analysis
            if len(analysis) > 200:
                analysis = analysis[:200] + "..."
            entry += f"\nAnalysis: {analysis}"
        history_parts.append(entry)
    return "\n---\n".join(history_parts)


async def build_context_node(state: SessionState) -> dict[str, Any]:
    """
    Build context from conversation history.

    This node prepares the context for SQL generation by
    combining summary and recent messages.

    Args:
        state: Current session state

    Returns:
        State update with built context (stored in metadata)
    """
    context = format_context_for_llm(state)

    return {
        "metadata": {
            **state.get("metadata", {}),
            "built_context": context
        },
        "status": "processing"
    }


async def route_query_node(
    state: SessionState,
    llm: Any
) -> dict[str, Any]:
    """
    Route query to appropriate processing path.

    Uses LLM to classify whether the query needs database access
    or can be answered from conversation context alone.

    Args:
        state: Current session state
        llm: Language model for classification

    Returns:
        State update with query_intent set
    """
    context = state.get("metadata", {}).get("built_context", "")
    query = state["current_query"]
    messages = state.get("messages", [])

    # If no conversation context, always route to database
    if not context or not messages:
        return {"query_intent": "database_query"}

    prompt = ROUTER_PROMPT.format(context=context, query=query)

    try:
        response = await llm.ainvoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)

        if "REASONING" in response_text.upper():
            return {"query_intent": "reasoning_only"}
        return {"query_intent": "database_query"}
    except Exception:
        # Default to database query on error
        return {"query_intent": "database_query"}


async def reasoning_only_node(
    state: SessionState,
    llm: Any
) -> dict[str, Any]:
    """
    Answer query using only conversation context.

    This node generates a response based on previous analyses
    without executing any database queries.

    Args:
        state: Current session state
        llm: Language model for response generation

    Returns:
        State update with analysis from reasoning
    """
    context = state.get("metadata", {}).get("built_context", "")
    query = state["current_query"]

    prompt = REASONING_PROMPT.format(context=context, query=query)

    try:
        response = await llm.ainvoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)

        return {
            "current_sql": None,
            "current_results": None,
            "current_analysis": {
                "summary": response_text,
                "insights": [],
                "chart_recommendations": [],
                "reasoning_only": True
            },
            "metadata": {
                **state.get("metadata", {}),
                "results_summary": "Answered from conversation context"
            },
            "status": "processing"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


async def receive_query_node(state: SessionState, query: str) -> dict[str, Any]:
    """
    Receive and store new query.

    Args:
        state: Current session state
        query: New natural language query

    Returns:
        State update with current query set
    """
    return {
        "current_query": query,
        "current_sql": None,
        "current_results": None,
        "current_analysis": None,
        "error": None,
        "status": "processing"
    }


async def process_query_node(
    state: SessionState,
    analysis_service: Any
) -> dict[str, Any]:
    """
    Process query using comprehensive analysis service.

    This node uses AnalysisService.create_comprehensive_analysis which
    handles the full pipeline: Prompt -> SQL Generation -> Execution -> Analysis.

    Args:
        state: Current session state
        analysis_service: Analysis service instance

    Returns:
        State update with SQL, results, and analysis
    """
    context = state.get("metadata", {}).get("built_context", "")
    query = state["current_query"]
    db_connection_id = state["db_connection_id"]

    # Build prompt with context
    contextualized_query = query
    if context:
        contextualized_query = f"Context from previous conversation:\n{context}\n\nCurrent question: {query}"

    try:
        # Create prompt request
        prompt_request = PromptRequest(
            text=contextualized_query,
            db_connection_id=db_connection_id
        )

        # Call comprehensive analysis service (does SQL gen + execution + analysis)
        # Using deep agent for more accurate SQL generation
        result = await analysis_service.create_comprehensive_analysis(
            prompt_request=prompt_request,
            max_rows=100,
            use_deep_agent=True
        )

        # Create results summary for context
        row_count = result.get("row_count", 0)
        results_summary = f"{row_count} rows returned"

        return {
            "current_sql": result.get("sql"),
            "current_results": None,  # Results are processed in the analysis
            "current_analysis": {
                "summary": result.get("summary", ""),
                "insights": result.get("insights", []),
                "chart_recommendations": result.get("chart_recommendations", []),
                "sql_status": result.get("sql_status"),
                "error": result.get("error"),
            },
            "metadata": {
                **state.get("metadata", {}),
                "results_summary": results_summary,
                "prompt_id": result.get("prompt_id"),
                "sql_generation_id": result.get("sql_generation_id"),
                "analysis_id": result.get("analysis_id"),
            },
            "status": "processing" if not result.get("error") else "error",
            "error": result.get("error")
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


async def summarize_node(
    state: SessionState,
    llm: Any
) -> dict[str, Any]:
    """
    Summarize older conversation history.

    Called when message count exceeds threshold.

    Args:
        state: Current session state
        llm: Language model for summarization

    Returns:
        State update with new summary and trimmed messages
    """
    if not should_summarize(state):
        return {}

    messages = state.get("messages", [])

    # Messages to summarize (older ones)
    messages_to_summarize = messages[:-MAX_FULL_MESSAGES]

    # Combine existing summary with messages to summarize
    existing_summary = state.get("summary", "")
    history = format_history_for_summarization(messages_to_summarize)

    if existing_summary:
        history = f"Previous summary:\n{existing_summary}\n\nNew messages:\n{history}"

    prompt = SUMMARIZATION_PROMPT.format(
        max_tokens=MAX_SUMMARY_TOKENS,
        history=history
    )

    try:
        response = await llm.ainvoke(prompt)
        new_summary = response.content if hasattr(response, 'content') else str(response)

        # Keep only recent messages
        recent_messages = messages[-MAX_FULL_MESSAGES:]

        return {
            "summary": new_summary,
            "messages": recent_messages
        }
    except Exception as e:
        # Summarization failure is non-fatal, keep messages
        return {}


async def save_message_node(state: SessionState) -> dict[str, Any]:
    """
    Save current query/response as a message.

    Args:
        state: Current session state

    Returns:
        State update with new message to be added (reducer handles accumulation)
    """
    new_message: MessageDict = {
        "id": f"msg_{uuid.uuid4().hex[:8]}",
        "role": "assistant",
        "query": state["current_query"] or "",
        "sql": state["current_sql"],
        "results_summary": state.get("metadata", {}).get("results_summary"),
        "analysis": state["current_analysis"].get("summary") if state.get("current_analysis") else None,
        "timestamp": datetime.now().isoformat()
    }

    # Return list with single message - the add reducer will accumulate
    return {
        "messages": [new_message],
        "status": "idle" if not state.get("error") else "error"
    }


__all__ = [
    "should_summarize",
    "format_context_for_llm",
    "format_history_for_summarization",
    "build_context_node",
    "route_query_node",
    "reasoning_only_node",
    "receive_query_node",
    "process_query_node",
    "summarize_node",
    "save_message_node",
]
