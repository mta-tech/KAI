"""Abstract base for memory backends.

Defines the MemoryBackend protocol that all memory backends must implement.
This enables switching between different storage engines (TypeSense, Letta, etc.)
while maintaining a consistent interface.
"""

from typing import Any, Protocol

from app.modules.memory.models import Memory, MemorySearchResult


class MemoryBackend(Protocol):
    """Protocol defining the memory backend interface.

    All memory backends (TypeSense, Letta, etc.) must implement this protocol
    to ensure consistent behavior across different storage engines.
    """

    def remember(
        self,
        db_connection_id: str,
        namespace: str,
        key: str,
        value: dict[str, Any],
        importance: float = 0.5,
        session_id: str | None = None,
    ) -> Memory:
        """Store a memory.

        Args:
            db_connection_id: Database connection to associate memory with.
            namespace: Category of memory (e.g., "user_preferences", "business_facts").
            key: Unique identifier within namespace.
            value: The memory content as a dictionary.
            importance: How important this memory is (0-1 scale).
            session_id: Optional session ID for session-scoped memory.
                        If None, memory is shared at database level.

        Returns:
            The stored Memory object.
        """
        ...

    def recall(
        self,
        db_connection_id: str,
        query: str,
        namespace: str | None = None,
        limit: int = 5,
        session_id: str | None = None,
        include_shared: bool = True,
    ) -> list[MemorySearchResult]:
        """Search memories semantically.

        Args:
            db_connection_id: Database connection to search within.
            query: What to search for.
            namespace: Optional namespace to filter by.
            limit: Maximum number of memories to return.
            session_id: Optional session ID to filter by. If None, returns
                        only shared (database-level) memories.
            include_shared: If True and session_id is set, also include
                            shared memories in results. Default True.

        Returns:
            List of MemorySearchResult sorted by relevance.
        """
        ...

    def get_memory(
        self,
        db_connection_id: str,
        namespace: str,
        key: str,
        session_id: str | None = None,
    ) -> Memory | None:
        """Get specific memory by key.

        Args:
            db_connection_id: Database connection ID.
            namespace: Memory namespace.
            key: Memory key.
            session_id: Optional session ID. If None, gets shared memory.

        Returns:
            The Memory if found, None otherwise.
        """
        ...

    def forget(
        self,
        db_connection_id: str,
        namespace: str,
        key: str,
        session_id: str | None = None,
    ) -> bool:
        """Delete a memory.

        Args:
            db_connection_id: Database connection ID.
            namespace: Memory namespace.
            key: Memory key.
            session_id: Optional session ID. If None, deletes shared memory.

        Returns:
            True if memory was deleted, False if not found.
        """
        ...

    def list_memories(
        self,
        db_connection_id: str,
        namespace: str | None = None,
        limit: int = 100,
        session_id: str | None = None,
        include_shared: bool = True,
    ) -> list[Memory]:
        """List memories.

        Args:
            db_connection_id: Database connection ID.
            namespace: Optional namespace to filter by.
            limit: Maximum number of memories to return.
            session_id: Optional session ID to filter by.
            include_shared: If True and session_id is set, include shared memories.

        Returns:
            List of Memory objects.
        """
        ...

    def list_namespaces(
        self,
        db_connection_id: str,
    ) -> list[str]:
        """List all namespaces.

        Args:
            db_connection_id: Database connection ID.

        Returns:
            List of namespace names.
        """
        ...

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
        ...

    def clear_all(
        self,
        db_connection_id: str,
    ) -> int:
        """Clear all memories for a database connection.

        Args:
            db_connection_id: Database connection ID.

        Returns:
            Number of memories deleted.
        """
        ...
