"""Session graph state definition for LangGraph."""
from typing import TypedDict, Literal, Annotated
from operator import add


class MessageDict(TypedDict):
    """Message representation in state."""
    id: str
    role: Literal["human", "assistant"]
    query: str
    sql: str | None
    results_summary: str | None
    analysis: str | None
    timestamp: str


class SessionState(TypedDict):
    """
    LangGraph state for session management.

    This state flows through the session graph, accumulating
    results from each processing step.
    """
    # Session identification
    session_id: str
    db_connection_id: str

    # Conversation history (use Annotated to accumulate messages across nodes)
    messages: Annotated[list[MessageDict], add]
    summary: str | None

    # Current query processing
    current_query: str | None
    current_sql: str | None
    current_results: list[dict] | None
    current_analysis: dict | None

    # Query routing
    query_intent: Literal["database_query", "reasoning_only"] | None

    # Status tracking
    status: Literal["idle", "processing", "error", "closed"]
    error: str | None

    # Custom metadata
    metadata: dict


def create_initial_state(
    session_id: str,
    db_connection_id: str,
    metadata: dict | None = None
) -> SessionState:
    """
    Create initial session state for a new session.

    Args:
        session_id: Unique session identifier
        db_connection_id: Database connection to use for queries
        metadata: Optional custom metadata

    Returns:
        Initial SessionState with default values
    """
    return SessionState(
        session_id=session_id,
        db_connection_id=db_connection_id,
        messages=[],
        summary=None,
        current_query=None,
        current_sql=None,
        current_results=None,
        current_analysis=None,
        query_intent=None,
        status="idle",
        error=None,
        metadata=metadata or {}
    )


__all__ = ["SessionState", "MessageDict", "create_initial_state"]
