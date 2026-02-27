"""Agentic learning integration for automatic memory injection.

This module wraps agent executions with the learning() context manager
from agentic-learning SDK, enabling automatic memory injection into LLM
calls and conversation capture for future learning.

The integration is transparent - if auto-learning is not configured,
the context managers fall through silently.

IMPORTANT: The learning() context manager does NOT auto-create agents.
Agents must be explicitly created using client.agents.create() before
using the learning context. This module handles agent creation automatically.
"""

import logging
import warnings
from contextlib import contextmanager, asynccontextmanager
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Cache for created agents to avoid repeated API calls
_agents_cache: set[str] = set()


def get_learning_client():
    """Get AgenticLearning client if configured.

    Returns:
        AgenticLearning client instance, or None if not configured.
    """
    from app.server.config import get_settings

    settings = get_settings()

    if not settings.ENABLE_AUTO_LEARNING:
        return None

    letta_api_key = settings.LETTA_API_KEY
    if not letta_api_key:
        logger.warning("ENABLE_AUTO_LEARNING=True but LETTA_API_KEY not set")
        return None

    try:
        from agentic_learning import AgenticLearning  # type: ignore[import-untyped]

        return AgenticLearning(
            api_key=letta_api_key,
            base_url=settings.LETTA_BASE_URL,
        )
    except ImportError:
        logger.debug("agentic-learning not installed — skipping")
        return None


# Cached async client instance
_async_client_instance = None


def get_async_learning_client():
    """Get AsyncAgenticLearning client if configured.

    Uses a cached singleton to avoid creating multiple client instances.

    Returns:
        AsyncAgenticLearning client instance, or None if not configured.
    """
    global _async_client_instance

    # Return cached instance if available
    if _async_client_instance is not None:
        return _async_client_instance

    from app.server.config import get_settings

    settings = get_settings()

    if not settings.ENABLE_AUTO_LEARNING:
        return None

    letta_api_key = settings.LETTA_API_KEY
    if not letta_api_key:
        logger.warning("ENABLE_AUTO_LEARNING=True but LETTA_API_KEY not set")
        return None

    try:
        from agentic_learning import AsyncAgenticLearning  # type: ignore[import-untyped]

        _async_client_instance = AsyncAgenticLearning(
            api_key=letta_api_key,
            base_url=settings.LETTA_BASE_URL,
        )
        return _async_client_instance
    except ImportError:
        logger.debug("agentic-learning not installed — skipping")
        return None


def get_shared_agent_name(db_connection_id: str) -> str:
    """Generate shared Letta agent name for shared memory.

    Args:
        db_connection_id: The database connection identifier.

    Returns:
        Sanitized shared agent name for Letta.
    """
    sanitized_db = db_connection_id.replace("-", "_").replace(" ", "_")
    return f"kai_shared_{sanitized_db}"


def get_shared_memory_blocks() -> list[str]:
    """Get shared memory block labels.

    These blocks are stored in the shared agent and are visible to all sessions.

    Returns:
        List of shared memory block labels.
    """
    from app.server.config import get_settings

    settings = get_settings()
    shared_block = getattr(settings, "AUTO_LEARNING_SHARED_MEMORY_BLOCK", "shared_knowledge")
    return [shared_block]


def get_memory_context(db_connection_id: str, session_id: str | None = None) -> str | None:
    """Retrieve memory context for prompt injection (sync).

    Retrieves memory from both shared agent (shared_knowledge) and session agent,
    combining them for comprehensive context injection.

    Args:
        db_connection_id: The database connection identifier.
        session_id: Optional session ID for session-scoped memory.

    Returns:
        Memory context string to inject into prompts, or None if unavailable.
    """
    client = get_learning_client()
    if client is None:
        return None

    try:
        contexts = []

        # 1. Get shared memory context first (shared_knowledge)
        shared_agent_name = get_shared_agent_name(db_connection_id)
        shared_memory_blocks = get_shared_memory_blocks()

        # Ensure shared agent exists
        ensure_agent_exists(client, shared_agent_name, shared_memory_blocks)

        # Retrieve shared memory context
        shared_context = client.memory.context.retrieve(agent=shared_agent_name)
        if shared_context:
            logger.debug(f"Retrieved shared memory context from: {shared_agent_name}")
            contexts.append(shared_context)

        # 2. Get session-specific memory context
        session_agent_name = get_agent_name(db_connection_id, session_id)
        session_memory_blocks = get_memory_blocks()

        # Ensure session agent exists
        ensure_agent_exists(client, session_agent_name, session_memory_blocks)

        # Retrieve session memory context
        session_context = client.memory.context.retrieve(agent=session_agent_name)
        if session_context:
            logger.debug(f"Retrieved session memory context from: {session_agent_name}")
            contexts.append(session_context)

        # Combine contexts
        if contexts:
            return "\n\n".join(contexts)
        return None

    except Exception as e:
        logger.warning(f"Failed to retrieve memory context: {e}")
        return None


async def get_memory_context_async(db_connection_id: str, session_id: str | None = None) -> str | None:
    """Retrieve memory context for prompt injection (async).

    Retrieves memory from both shared agent (shared_knowledge) and session agent,
    combining them for comprehensive context injection.

    Args:
        db_connection_id: The database connection identifier.
        session_id: Optional session ID for session-scoped memory.

    Returns:
        Memory context string to inject into prompts, or None if unavailable.
    """
    client = get_async_learning_client()
    if client is None:
        return None

    # Suppress RuntimeWarning from agentic_learning SDK's internal coroutine handling
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*was never awaited.*")

        try:
            contexts = []

            # 1. Get shared memory context first (shared_knowledge)
            shared_agent_name = get_shared_agent_name(db_connection_id)
            shared_memory_blocks = get_shared_memory_blocks()

            # Ensure shared agent exists
            await ensure_agent_exists_async(client, shared_agent_name, shared_memory_blocks)

            # Retrieve shared memory context
            shared_context = await client.memory.context.retrieve(agent=shared_agent_name)
            if shared_context:
                logger.debug(f"Retrieved shared memory context from: {shared_agent_name}")
                contexts.append(shared_context)

            # 2. Get session-specific memory context
            session_agent_name = get_agent_name(db_connection_id, session_id)
            session_memory_blocks = get_memory_blocks()

            # Ensure session agent exists
            await ensure_agent_exists_async(client, session_agent_name, session_memory_blocks)

            # Retrieve session memory context
            session_context = await client.memory.context.retrieve(agent=session_agent_name)
            if session_context:
                logger.debug(f"Retrieved session memory context from: {session_agent_name}")
                contexts.append(session_context)

            # Combine contexts
            if contexts:
                return "\n\n".join(contexts)
            return None

        except Exception as e:
            logger.warning(f"Failed to retrieve memory context: {e}")
            return None


def ensure_agent_exists(client: Any, agent_name: str, memory_blocks: list[str]) -> bool:
    """Ensure Letta agent exists, creating it if necessary (sync).

    Args:
        client: AgenticLearning client instance.
        agent_name: Name of the agent to ensure exists.
        memory_blocks: List of memory block labels to create.

    Returns:
        True if agent exists or was created, False on error.
    """
    global _agents_cache

    # Check cache first
    if agent_name in _agents_cache:
        return True

    try:
        # Check if agent exists
        existing = client.agents.retrieve(agent=agent_name)
        if existing:
            _agents_cache.add(agent_name)
            logger.debug(f"Agent already exists: {agent_name}")
            return True

        # Create the agent with memory blocks
        logger.info(f"Creating Letta agent: {agent_name} with blocks: {memory_blocks}")
        client.agents.create(
            agent=agent_name,
            memory=memory_blocks,
        )
        _agents_cache.add(agent_name)
        logger.info(f"Created Letta agent: {agent_name}")
        return True

    except Exception as e:
        logger.warning(f"Failed to ensure agent exists: {e}")
        return False


async def ensure_agent_exists_async(client: Any, agent_name: str, memory_blocks: list[str]) -> bool:
    """Ensure Letta agent exists, creating it if necessary (async).

    Args:
        client: AsyncAgenticLearning client instance.
        agent_name: Name of the agent to ensure exists.
        memory_blocks: List of memory block labels to create.

    Returns:
        True if agent exists or was created, False on error.
    """
    global _agents_cache

    # Check cache first
    if agent_name in _agents_cache:
        return True

    try:
        # Check if agent exists
        existing = await client.agents.retrieve(agent=agent_name)
        if existing:
            _agents_cache.add(agent_name)
            logger.debug(f"Agent already exists: {agent_name}")
            return True

        # Create the agent with memory blocks
        logger.info(f"Creating Letta agent: {agent_name} with blocks: {memory_blocks}")
        await client.agents.create(
            agent=agent_name,
            memory=memory_blocks,
        )
        _agents_cache.add(agent_name)
        logger.info(f"Created Letta agent: {agent_name}")
        return True

    except Exception as e:
        logger.warning(f"Failed to ensure agent exists: {e}")
        return False


def get_agent_name(db_connection_id: str, session_id: str | None = None) -> str:
    """Generate Letta agent name from db_connection_id with optional session scope.

    Args:
        db_connection_id: The database connection identifier.
        session_id: Optional session ID for session-scoped agent.

    Returns:
        Sanitized agent name for Letta.
    """
    sanitized_db = db_connection_id.replace("-", "_").replace(" ", "_")
    if session_id:
        # Use complete session_id to avoid collisions between sessions
        sanitized_session = session_id.replace("-", "_").replace(" ", "_")
        return f"kai_agent_{sanitized_db}_{sanitized_session}"
    return f"kai_agent_{sanitized_db}"


def get_memory_blocks() -> list[str]:
    """Get configured memory block labels for session agent.

    Returns:
        List of memory block labels to inject (session-specific).
    """
    from app.server.config import get_settings

    settings = get_settings()
    blocks_str = settings.AUTO_LEARNING_MEMORY_BLOCKS
    return [b.strip() for b in blocks_str.split(",") if b.strip()]


@contextmanager
def learning_context(db_connection_id: str, session_id: str | None = None):
    """Sync context manager for automatic learning.

    Wraps agent execution with memory injection and capture.
    Falls through silently if learning is not configured.

    This function automatically creates the Letta agent if it doesn't exist,
    ensuring that memory injection works from the first session.

    Usage:
        with learning_context(db_connection.id, session_id=task.session_id):
            result = agent.invoke(input_state, config=config)

    Args:
        db_connection_id: The database connection identifier for agent scoping.
        session_id: Optional session ID for session-scoped memory.

    Yields:
        None - this is a context manager for wrapping execution.
    """
    client = get_learning_client()

    if client is None:
        # Learning not configured, run without wrapper
        yield
        return

    from app.server.config import get_settings
    settings = get_settings()

    try:
        from agentic_learning import learning  # type: ignore[import-untyped]

        agent_name = get_agent_name(db_connection_id, session_id)
        memory_blocks = get_memory_blocks()
        capture_only = settings.AUTO_LEARNING_CAPTURE_ONLY

        # Ensure agent exists before entering learning context
        # This is required because learning() does NOT auto-create agents
        ensure_agent_exists(client, agent_name, memory_blocks)

        with learning(
            agent=agent_name,
            client=client,
            memory=memory_blocks,
            capture_only=capture_only,
        ):
            logger.debug(f"Learning context active: agent={agent_name}")
            yield

    except Exception as e:
        logger.warning(f"Learning context failed, continuing without: {e}")
        yield


@asynccontextmanager
async def async_learning_context(db_connection_id: str, session_id: str | None = None):
    """Async context manager for automatic learning.

    Ensures Letta agents exist for memory operations. Does NOT use the SDK's
    learning() context manager to avoid ContextVar issues across async contexts.

    Memory injection and conversation capture are handled manually via:
    - get_memory_context_async() for injection
    - capture_with_correction_detection() for capture

    Usage:
        async with async_learning_context(db_connection.id, session_id=task.session_id):
            async for event in agent.astream_events(...):
                yield event

    Args:
        db_connection_id: The database connection identifier for agent scoping.
        session_id: Optional session ID for session-scoped memory.

    Yields:
        None - this is a context manager for wrapping execution.
    """
    # Use async client for async context
    client = get_async_learning_client()

    if client is None:
        yield
        return

    try:
        # Ensure both shared and session agents exist
        # This is required for memory operations to work
        shared_agent_name = get_shared_agent_name(db_connection_id)
        shared_memory_blocks = get_shared_memory_blocks()
        await ensure_agent_exists_async(client, shared_agent_name, shared_memory_blocks)

        session_agent_name = get_agent_name(db_connection_id, session_id)
        session_memory_blocks = get_memory_blocks()
        await ensure_agent_exists_async(client, session_agent_name, session_memory_blocks)

        logger.debug(f"Learning agents ready: shared={shared_agent_name}, session={session_agent_name}")
        yield

    except Exception as e:
        logger.warning(f"Failed to ensure learning agents exist: {e}")
        yield


def capture_conversation(
    db_connection_id: str,
    session_id: str,
    user_message: str,
    assistant_message: str,
    model: str = "gemini-2.5-flash",
) -> bool:
    """Manually capture a conversation turn for learning (sync).

    Since LangChain is not intercepted by the agentic-learning SDK,
    we need to manually capture conversations after agent execution.

    Args:
        db_connection_id: The database connection identifier.
        session_id: The session ID.
        user_message: The user's prompt.
        assistant_message: The agent's response.
        model: The model name used.

    Returns:
        True if captured successfully, False otherwise.
    """
    client = get_learning_client()
    if client is None:
        return False

    try:
        agent_name = get_agent_name(db_connection_id, session_id)
        memory_blocks = get_memory_blocks()

        # Ensure agent exists
        ensure_agent_exists(client, agent_name, memory_blocks)

        # Capture the conversation
        client.messages.capture(
            agent=agent_name,
            request_messages=[{"role": "user", "content": user_message}],
            response_dict={"role": "assistant", "content": assistant_message},
            model=model,
            provider="google",
        )

        logger.info(f"Captured conversation for agent: {agent_name}")
        return True

    except Exception as e:
        logger.warning(f"Failed to capture conversation: {e}")
        return False


async def capture_conversation_async(
    db_connection_id: str,
    session_id: str,
    user_message: str,
    assistant_message: str,
    model: str = "gemini-2.5-flash",
) -> bool:
    """Manually capture a conversation turn for learning (async).

    Since LangChain is not intercepted by the agentic-learning SDK,
    we need to manually capture conversations after agent execution.

    This function:
    1. Captures the conversation messages
    2. Triggers memory.remember() to immediately process and update memory blocks

    Args:
        db_connection_id: The database connection identifier.
        session_id: The session ID.
        user_message: The user's prompt.
        assistant_message: The agent's response.
        model: The model name used.

    Returns:
        True if captured successfully, False otherwise.
    """
    client = get_async_learning_client()
    if client is None:
        return False

    try:
        agent_name = get_agent_name(db_connection_id, session_id)
        memory_blocks = get_memory_blocks()

        # Ensure agent exists
        await ensure_agent_exists_async(client, agent_name, memory_blocks)

        # Capture the conversation
        await client.messages.capture(
            agent=agent_name,
            request_messages=[{"role": "user", "content": user_message}],
            response_dict={"role": "assistant", "content": assistant_message},
            model=model,
            provider="google",
        )

        # Trigger immediate memory processing with remember()
        # This ensures memory blocks are updated right away instead of waiting for sleeptime
        # Truncate messages to avoid token limits
        user_summary = user_message[:300] if len(user_message) > 300 else user_message
        assistant_summary = assistant_message[:500] if len(assistant_message) > 500 else assistant_message
        conversation_summary = f"User: {user_summary}\n\nAssistant: {assistant_summary}"

        # memory.remember() returns a context string, await it to avoid warnings
        memory_result = await client.memory.remember(agent=agent_name, prompt=conversation_summary)
        # If the result is also a coroutine (nested async), await it too
        if hasattr(memory_result, '__await__'):
            await memory_result

        logger.info(f"Captured and processed conversation for agent: {agent_name}")
        return True

    except Exception as e:
        logger.warning(f"Failed to capture conversation: {e}")
        return False


def remember_correction(
    db_connection_id: str,
    session_id: str,
    correction: str,
    context: str | None = None,
) -> str | None:
    """Remember a correction or mistake for ALL future sessions (sync).

    Corrections are stored in the SHARED agent's shared_knowledge block,
    NOT in the session-specific agent. This ensures corrections are available
    to all sessions working with this database.

    Use this when:
    - Human corrects a wrong column name, table name, etc.
    - Human provides clarification (e.g., "Java should include Yogyakarta")
    - Agent made a mistake in SQL query or analysis
    - Any important learning that should persist across all sessions

    Args:
        db_connection_id: The database connection identifier.
        session_id: The session ID (used for logging, not storage).
        correction: The correction or learning to remember.
        context: Optional context about what was wrong.

    Returns:
        Updated memory context if successful, None otherwise.
    """
    client = get_learning_client()
    if client is None:
        return None

    try:
        # Store corrections in SHARED agent, not session agent
        # This makes corrections available to ALL sessions
        shared_agent_name = get_shared_agent_name(db_connection_id)
        shared_memory_blocks = get_shared_memory_blocks()

        # Ensure shared agent exists
        ensure_agent_exists(client, shared_agent_name, shared_memory_blocks)

        # Format as a clear correction/learning for shared knowledge
        if context:
            prompt = f"""IMPORTANT CORRECTION - Update shared_knowledge to remember this:

Context: {context}

Correction: {correction}

This is a mistake that was corrected by the user.
This correction MUST be remembered and applied in ALL future sessions to avoid the same mistake."""
        else:
            prompt = f"""IMPORTANT CORRECTION - Update shared_knowledge to remember this:

{correction}

This correction MUST be remembered and applied in ALL future sessions."""

        # Use the shared sleeptime agent to process and remember
        result = client.memory.remember(agent=shared_agent_name, prompt=prompt)
        logger.info(f"Remembered correction in shared agent: {shared_agent_name} (from session: {session_id})")
        return result

    except Exception as e:
        logger.warning(f"Failed to remember correction: {e}")
        return None


async def remember_correction_async(
    db_connection_id: str,
    session_id: str,
    correction: str,
    context: str | None = None,
) -> str | None:
    """Remember a correction or mistake for ALL future sessions (async).

    Corrections are stored in the SHARED agent's shared_knowledge block,
    NOT in the session-specific agent. This ensures corrections are available
    to all sessions working with this database.

    Use this when:
    - Human corrects a wrong column name, table name, etc.
    - Human provides clarification (e.g., "Java should include Yogyakarta")
    - Agent made a mistake in SQL query or analysis
    - Any important learning that should persist across all sessions

    Args:
        db_connection_id: The database connection identifier.
        session_id: The session ID (used for logging, not storage).
        correction: The correction or learning to remember.
        context: Optional context about what was wrong.

    Returns:
        Updated memory context if successful, None otherwise.
    """
    client = get_async_learning_client()
    if client is None:
        return None

    try:
        # Store corrections in SHARED agent, not session agent
        # This makes corrections available to ALL sessions
        shared_agent_name = get_shared_agent_name(db_connection_id)
        shared_memory_blocks = get_shared_memory_blocks()

        # Ensure shared agent exists
        await ensure_agent_exists_async(client, shared_agent_name, shared_memory_blocks)

        # Format as a clear correction/learning for shared knowledge
        if context:
            prompt = f"""IMPORTANT CORRECTION - Update shared_knowledge to remember this:

Context: {context}

Correction: {correction}

This is a mistake that was corrected by the user.
This correction MUST be remembered and applied in ALL future sessions to avoid the same mistake."""
        else:
            prompt = f"""IMPORTANT CORRECTION - Update shared_knowledge to remember this:

{correction}

This correction MUST be remembered and applied in ALL future sessions."""

        # Use the shared sleeptime agent to process and remember
        memory_result = await client.memory.remember(agent=shared_agent_name, prompt=prompt)
        # If the result is also a coroutine (nested async), await it too
        if hasattr(memory_result, '__await__'):
            memory_result = await memory_result
        logger.info(f"Remembered correction in shared agent: {shared_agent_name} (from session: {session_id})")
        return memory_result

    except Exception as e:
        logger.warning(f"Failed to remember correction: {e}")
        return None


# Import correction detection utilities from shared location
from app.utils.correction_detection import (
    is_correction_message,
    detect_correction_category,
    CORRECTION_PATTERNS,
)


async def capture_shared_knowledge_async(
    db_connection_id: str,
    knowledge: str,
    context: str | None = None,
) -> str | None:
    """Capture important knowledge to the shared agent's shared_knowledge block.

    Use this for facts that should be shared across ALL sessions:
    - Business facts (e.g., "Java province includes Yogyakarta")
    - Data insights (e.g., "Sales data only goes back to 2020")
    - Database knowledge (e.g., "Active customers have status='A'")

    This is different from session-specific corrections which go to session agents.

    Args:
        db_connection_id: The database connection identifier.
        knowledge: The knowledge/fact to remember.
        context: Optional context about where this knowledge came from.

    Returns:
        Updated memory context if successful, None otherwise.
    """
    client = get_async_learning_client()
    if client is None:
        return None

    try:
        shared_agent_name = get_shared_agent_name(db_connection_id)
        shared_memory_blocks = get_shared_memory_blocks()

        # Ensure shared agent exists
        await ensure_agent_exists_async(client, shared_agent_name, shared_memory_blocks)

        # Format as shared knowledge
        if context:
            prompt = f"""SHARED KNOWLEDGE - This is an important fact about the database/business:

Context: {context}

Knowledge: {knowledge}

This should be remembered and shared with ALL future sessions working with this database."""
        else:
            prompt = f"""SHARED KNOWLEDGE - This is an important fact about the database/business:

{knowledge}

This should be remembered and shared with ALL future sessions working with this database."""

        # Use the sleeptime agent to process and remember
        memory_result = await client.memory.remember(agent=shared_agent_name, prompt=prompt)
        # If the result is also a coroutine (nested async), await it too
        if hasattr(memory_result, '__await__'):
            memory_result = await memory_result
        logger.info(f"Captured shared knowledge for agent: {shared_agent_name}")
        return memory_result

    except Exception as e:
        logger.warning(f"Failed to capture shared knowledge: {e}")
        return None


# Patterns that indicate shareable business/database knowledge
SHARED_KNOWLEDGE_PATTERNS = [
    # Business facts (English)
    "include",
    "includes",
    "exclude",
    "excludes",
    "part of",
    "belongs to",
    "consists of",
    # Business facts (Indonesian)
    "termasuk",
    "meliputi",
    "terdiri dari",
    "terdiri atas",
    "bagian dari",
    "merupakan bagian",
    "mencakup",
    "tidak termasuk",
    # Data facts (English)
    "data starts",
    "data ends",
    "only has data",
    "no data for",
    "data from",
    # Data facts (Indonesian)
    "data mulai",
    "data berakhir",
    "data dari",
    "tidak ada data",
    # Database structure (English)
    "column means",
    "table contains",
    "status means",
    "active means",
    "inactive means",
    "code means",
    # Database structure (Indonesian)
    "kolom berarti",
    "tabel berisi",
    "status berarti",
    "kode berarti",
    # Domain knowledge (English)
    "definition",
    "refers to",
    "same as",
    "equivalent to",
    # Domain knowledge (Indonesian)
    "definisi",
    "mengacu pada",
    "sama dengan",
    "artinya",
    "maksudnya",
    # Geographic knowledge (common in this codebase)
    "provinsi",
    "province",
    "kabupaten",
    "kelurahan",
    "kecamatan",
    "kota",
    "wilayah",
    "region",
    "indonesia timur",
    "indonesia barat",
    "eastern indonesia",
    "western indonesia"
]


def is_shared_knowledge_message(message: str) -> bool:
    """Check if a message contains shareable business/database knowledge.

    Args:
        message: The message to check.

    Returns:
        True if the message contains shareable knowledge.
    """
    message_lower = message.lower().strip()
    return any(pattern in message_lower for pattern in SHARED_KNOWLEDGE_PATTERNS)


async def capture_with_correction_detection(
    db_connection_id: str,
    session_id: str,
    user_message: str,
    assistant_message: str,
    previous_assistant_message: str | None = None,
    model: str = "gemini-2.5-flash",
) -> bool:
    """Capture conversation with automatic correction detection.

    If the user message appears to be a correction, it will be specially
    processed to ensure the learning is remembered.

    Additionally, if the message contains shareable knowledge (business facts,
    data insights), it will also be captured to the shared agent for all sessions.

    Args:
        db_connection_id: The database connection identifier.
        session_id: The session ID.
        user_message: The user's prompt.
        assistant_message: The agent's response.
        previous_assistant_message: The previous assistant response (for context).
        model: The model name used.

    Returns:
        True if captured successfully, False otherwise.
    """
    # Suppress RuntimeWarning from agentic_learning SDK's internal coroutine handling
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*was never awaited.*")

        # First, capture the normal conversation to session agent
        captured = await capture_conversation_async(
            db_connection_id=db_connection_id,
            session_id=session_id,
            user_message=user_message,
            assistant_message=assistant_message,
            model=model,
        )

        # If this looks like a correction, trigger remember on session agent
        if is_correction_message(user_message):
            logger.info(f"Detected correction in user message, triggering remember")
            context = previous_assistant_message if previous_assistant_message else None
            await remember_correction_async(
                db_connection_id=db_connection_id,
                session_id=session_id,
                correction=user_message,
                context=context,
            )

        # If this contains shareable knowledge, also capture to shared agent
        # This ensures business facts are available to ALL sessions
        if is_shared_knowledge_message(user_message) or is_shared_knowledge_message(assistant_message):
            logger.info(f"Detected shared knowledge, capturing to shared agent")
            # Combine user message and assistant response for context
            knowledge_context = f"User asked: {user_message}"
            knowledge = assistant_message[:1000] if len(assistant_message) > 1000 else assistant_message
            await capture_shared_knowledge_async(
                db_connection_id=db_connection_id,
                knowledge=knowledge,
                context=knowledge_context,
            )

    return captured
