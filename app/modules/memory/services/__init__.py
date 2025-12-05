"""Service for long-term memory management.

This service provides a consistent interface for memory operations regardless
of the underlying backend (TypeSense or Letta).
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from app.data.db.storage import Storage
from app.modules.memory.backends import MemoryBackend, create_memory_backend
from app.modules.memory.models import Memory, MemorySearchResult

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for managing long-term memories - storing, retrieving, and searching.

    This service wraps the memory backend and provides a consistent interface
    regardless of which backend is configured (TypeSense or Letta).
    """

    def __init__(
        self,
        storage: Storage = None,
        backend: MemoryBackend | None = None,
    ):
        """Initialize memory service with storage or explicit backend.

        Args:
            storage: TypeSense storage instance (for backward compatibility).
            backend: Explicit backend to use (overrides auto-detection).
        """
        if backend:
            self._backend = backend
        else:
            self._backend = create_memory_backend(storage)

        # Keep storage reference for backward compatibility
        self.storage = storage

    @property
    def backend_type(self) -> str:
        """Return the type of backend being used."""
        return self._backend.__class__.__name__

    def remember(
        self,
        db_connection_id: str,
        namespace: str,
        key: str,
        value: dict[str, Any],
        importance: float = 0.5,
        session_id: str | None = None,
    ) -> Memory:
        """Store a memory with automatic content text generation.

        If a memory with the same namespace and key exists, it will be updated.

        Args:
            db_connection_id: Database connection to associate memory with.
            namespace: Category of memory (e.g., "user_preferences", "facts").
            key: Unique identifier within namespace.
            value: The memory content as a dictionary.
            importance: How important this memory is (0-1 scale).
            session_id: Optional session ID. If None, memory is shared at database level.

        Returns:
            The stored or updated Memory.
        """
        return self._backend.remember(
            db_connection_id, namespace, key, value, importance, session_id
        )

    def recall(
        self,
        db_connection_id: str,
        query: str,
        namespace: str | None = None,
        limit: int = 5,
        session_id: str | None = None,
        include_shared: bool = True,
    ) -> list[MemorySearchResult]:
        """Recall relevant memories using semantic search.

        Args:
            db_connection_id: Database connection to search within.
            query: What to search for.
            namespace: Optional namespace to filter by.
            limit: Maximum number of memories to return.
            session_id: Optional session ID. If None, returns only shared memories.
            include_shared: If True and session_id is set, include shared memories.

        Returns:
            List of MemorySearchResult sorted by relevance.
        """
        return self._backend.recall(
            db_connection_id, query, namespace, limit, session_id, include_shared
        )

    def get_memory(
        self,
        db_connection_id: str,
        namespace: str,
        key: str,
        session_id: str | None = None,
    ) -> Memory | None:
        """Get a specific memory by namespace and key.

        Args:
            db_connection_id: Database connection ID.
            namespace: Memory namespace.
            key: Memory key.
            session_id: Optional session ID. If None, gets shared memory.

        Returns:
            The Memory if found, None otherwise.
        """
        return self._backend.get_memory(db_connection_id, namespace, key, session_id)

    def forget(
        self,
        db_connection_id: str,
        namespace: str,
        key: str,
        session_id: str | None = None,
    ) -> bool:
        """Delete a specific memory.

        Args:
            db_connection_id: Database connection ID.
            namespace: Memory namespace.
            key: Memory key.
            session_id: Optional session ID. If None, deletes shared memory.

        Returns:
            True if memory was deleted, False if not found.
        """
        return self._backend.forget(db_connection_id, namespace, key, session_id)

    def list_memories(
        self,
        db_connection_id: str,
        namespace: str | None = None,
        limit: int = 100,
        session_id: str | None = None,
        include_shared: bool = True,
    ) -> list[Memory]:
        """List memories, optionally filtered by namespace and session.

        Args:
            db_connection_id: Database connection ID.
            namespace: Optional namespace to filter by.
            limit: Maximum number of memories to return.
            session_id: Optional session ID to filter by.
            include_shared: If True and session_id is set, include shared memories.

        Returns:
            List of Memory objects.
        """
        return self._backend.list_memories(
            db_connection_id, namespace, limit, session_id, include_shared
        )

    def list_namespaces(self, db_connection_id: str) -> list[str]:
        """List all namespaces for a database connection.

        Args:
            db_connection_id: Database connection ID.

        Returns:
            List of namespace names.
        """
        return self._backend.list_namespaces(db_connection_id)

    def clear_namespace(
        self,
        db_connection_id: str,
        namespace: str,
    ) -> int:
        """Clear all memories in a namespace.

        Args:
            db_connection_id: Database connection ID.
            namespace: Namespace to clear.

        Returns:
            Number of memories deleted.
        """
        return self._backend.clear_namespace(db_connection_id, namespace)

    def clear_all(self, db_connection_id: str) -> int:
        """Clear all memories for a database connection.

        Args:
            db_connection_id: Database connection ID.

        Returns:
            Number of memories deleted.
        """
        return self._backend.clear_all(db_connection_id)

    def format_memories_for_prompt(
        self,
        db_connection_id: str,
        query: str | None = None,
        namespace: str | None = None,
        limit: int = 10,
    ) -> str:
        """Format memories as a string for the agent prompt.

        If a query is provided, uses semantic search to find relevant memories.
        Otherwise lists memories in the namespace or all memories.

        Args:
            db_connection_id: Database connection ID.
            query: Optional query for semantic search.
            namespace: Optional namespace to filter by.
            limit: Maximum number of memories to include.

        Returns:
            Formatted string of memories.
        """
        # Check if backend has format_memories_for_prompt method
        if hasattr(self._backend, "format_memories_for_prompt"):
            return self._backend.format_memories_for_prompt(
                db_connection_id, query, namespace, limit
            )

        # Fallback implementation
        if query:
            results = self.recall(db_connection_id, query, namespace, limit)
            if not results:
                return "No relevant memories found."

            lines = ["# Relevant Memories\n"]
            for result in results:
                memory = result.memory
                lines.append(f"## [{memory.namespace}] {memory.key}")
                lines.append(f"**Relevance:** {result.score:.2f}")
                lines.append(f"**Content:** {memory.value}")
                lines.append("")
            return "\n".join(lines)

        else:
            memories = self.list_memories(db_connection_id, namespace, limit)
            if not memories:
                return "No memories stored."

            lines = ["# Stored Memories\n"]
            current_namespace = None
            for memory in sorted(memories, key=lambda m: (m.namespace, m.key)):
                if memory.namespace != current_namespace:
                    current_namespace = memory.namespace
                    lines.append(f"\n## {current_namespace}\n")
                lines.append(f"- **{memory.key}:** {memory.value}")

            return "\n".join(lines)

    # =========================================================================
    # Correction Learning Methods
    # =========================================================================

    def remember_correction(
        self,
        db_connection_id: str,
        correction: str,
        context: str | None = None,
        session_id: str | None = None,
        category: str = "general",
    ) -> Memory:
        """Store a correction or learning for future reference.

        Corrections are stored in a special 'corrections' namespace and are
        searchable for prompt injection.

        Args:
            db_connection_id: Database connection ID.
            correction: The correction or learning to remember.
            context: Optional context (e.g., the previous answer that was corrected).
            session_id: Optional session ID. If None, correction is shared at database level.
            category: Category of correction (e.g., 'sql', 'geography', 'general').

        Returns:
            The stored Memory.
        """
        # Generate unique key for this correction
        correction_id = f"corr_{uuid.uuid4().hex[:12]}"

        value = {
            "correction": correction,
            "context": context,
            "category": category,
            "timestamp": datetime.now().isoformat(),
        }

        # Store with high importance since corrections are important learnings
        return self.remember(
            db_connection_id=db_connection_id,
            namespace="corrections",
            key=correction_id,
            value=value,
            importance=0.9,  # High importance for corrections
            session_id=session_id,
        )

    def get_corrections_for_prompt(
        self,
        db_connection_id: str,
        query: str | None = None,
        session_id: str | None = None,
        limit: int = 10,
    ) -> str:
        """Get corrections formatted for prompt injection.

        Args:
            db_connection_id: Database connection ID.
            query: Optional query for semantic search of relevant corrections.
            session_id: Optional session ID to include session-specific corrections.
            limit: Maximum number of corrections to include.

        Returns:
            Formatted string of corrections for prompt injection.
        """
        if query:
            # Use semantic search to find relevant corrections
            results = self.recall(
                db_connection_id=db_connection_id,
                query=query,
                namespace="corrections",
                limit=limit,
                session_id=session_id,
                include_shared=True,
            )

            if not results:
                return ""

            lines = ["# Important Corrections & Learnings\n"]
            lines.append("Remember these corrections from previous interactions:\n")

            for result in results:
                memory = result.memory
                value = memory.value
                correction = value.get("correction", "")
                context = value.get("context")
                category = value.get("category", "general")

                lines.append(f"- **[{category}]** {correction}")
                if context:
                    # Truncate context if too long
                    ctx_preview = context[:200] + "..." if len(context) > 200 else context
                    lines.append(f"  - Context: {ctx_preview}")

            return "\n".join(lines)

        else:
            # List all corrections
            memories = self.list_memories(
                db_connection_id=db_connection_id,
                namespace="corrections",
                limit=limit,
                session_id=session_id,
                include_shared=True,
            )

            if not memories:
                return ""

            lines = ["# Important Corrections & Learnings\n"]
            lines.append("Remember these corrections from previous interactions:\n")

            for memory in memories:
                value = memory.value
                correction = value.get("correction", "")
                category = value.get("category", "general")

                lines.append(f"- **[{category}]** {correction}")

            return "\n".join(lines)

    def detect_and_store_correction(
        self,
        db_connection_id: str,
        user_message: str,
        previous_answer: str | None = None,
        session_id: str | None = None,
    ) -> Memory | None:
        """Detect if a message is a correction and store it if so.

        Uses pattern matching to detect corrections in user messages.

        Args:
            db_connection_id: Database connection ID.
            user_message: The user's message to check.
            previous_answer: The previous assistant answer (context for the correction).
            session_id: Optional session ID.

        Returns:
            The stored Memory if a correction was detected, None otherwise.
        """
        from app.modules.autonomous_agent.learning import (
            is_correction_message,
            detect_correction_category,
        )

        if not is_correction_message(user_message):
            return None

        # Detect category of correction
        category = detect_correction_category(user_message)

        logger.info(f"Detected correction in user message (category: {category})")

        return self.remember_correction(
            db_connection_id=db_connection_id,
            correction=user_message,
            context=previous_answer,
            session_id=session_id,
            category=category,
        )
