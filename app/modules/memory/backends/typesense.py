"""TypeSense memory backend implementation.

This is the default memory backend that uses TypeSense for storage and
semantic search. It provides full functionality including hybrid search
combining text and vector similarity.
"""

import logging
from typing import Any

from app.data.db.storage import Storage
from app.modules.memory.models import Memory, MemorySearchResult
from app.modules.memory.repositories import MemoryRepository
from app.utils.model.embedding_model import EmbeddingModel

logger = logging.getLogger(__name__)


class TypeSenseMemoryBackend:
    """Memory backend using TypeSense for storage and search.

    This is the default backend that provides:
    - Hybrid search (text + vector similarity)
    - Local embedding generation
    - Full CRUD operations on memories
    """

    def __init__(self, storage: Storage):
        """Initialize TypeSense backend.

        Args:
            storage: TypeSense storage instance.
        """
        self.storage = storage
        self.repository = MemoryRepository(storage)

    def _generate_content_text(self, value: dict) -> str:
        """Generate searchable text from memory value.

        Flattens dict values into a searchable string representation.
        """
        parts = []
        for k, v in value.items():
            if isinstance(v, str):
                parts.append(v)
            elif isinstance(v, (list, tuple)):
                parts.extend(str(item) for item in v)
            elif isinstance(v, dict):
                # Recursively flatten nested dicts
                parts.append(self._generate_content_text(v))
            else:
                parts.append(str(v))
        return " ".join(parts)

    def _add_embedding(self, memory: Memory) -> Memory:
        """Add embedding to memory for semantic search."""
        try:
            embedding_model = EmbeddingModel().get_model()
            # Use content_text for embedding
            memory.memory_embedding = embedding_model.embed_query(memory.content_text)
        except Exception as e:
            logger.warning(f"Failed to generate embedding for memory '{memory.key}': {e}")
        return memory

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
            db_connection_id: Database connection ID.
            namespace: Memory namespace.
            key: Memory key.
            value: Memory value dict.
            importance: Importance score (0-1).
            session_id: Optional session ID. None for shared (database-level) memory.
        """
        content_text = self._generate_content_text(value)
        memory = self.repository.put(
            db_connection_id, namespace, key, value, content_text, importance, session_id
        )
        # Add embedding for semantic search
        memory = self._add_embedding(memory)
        return self.repository.update(memory)

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
            db_connection_id: Database connection ID.
            query: Search query.
            namespace: Optional namespace filter.
            limit: Max results.
            session_id: Optional session ID. If None, returns only shared memories.
            include_shared: If True and session_id is set, include shared memories.
        """
        try:
            embedding_model = EmbeddingModel().get_model()
            query_embedding = embedding_model.embed_query(query)
            results = self.repository.search(
                db_connection_id,
                query,
                query_embedding,
                namespace,
                limit,
                session_id=session_id,
                include_shared=include_shared,
            )

            # Increment access count for retrieved memories
            for result in results:
                self.repository.increment_access(result.memory)

            return results

        except Exception as e:
            logger.warning(f"Semantic search failed, falling back to text search: {e}")
            return self.repository.search_by_text(
                db_connection_id, query, namespace, limit
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
        """
        memory = self.repository.find_by_key(db_connection_id, namespace, key, session_id)
        if memory:
            self.repository.increment_access(memory)
        return memory

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
        """
        return self.repository.delete_by_key(db_connection_id, namespace, key, session_id)

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
            namespace: Optional namespace filter.
            limit: Maximum results.
            session_id: Optional session ID filter.
            include_shared: If True and session_id is set, include shared memories.
        """
        # Build filter for session scope
        filter_dict = {"db_connection_id": db_connection_id}
        if namespace:
            filter_dict["namespace"] = namespace

        # Get memories based on session scope
        memories = self.repository.find_by(filter_dict, limit=limit)

        # Apply session filtering in Python (TypeSense may not support OR filters well)
        if session_id:
            if include_shared:
                # Include session-scoped and shared memories
                memories = [
                    m for m in memories
                    if m.session_id == session_id or m.session_id is None
                ]
            else:
                # Only session-scoped
                memories = [m for m in memories if m.session_id == session_id]
        else:
            # Only shared memories
            memories = [m for m in memories if m.session_id is None]

        return memories[:limit]

    def list_namespaces(self, db_connection_id: str) -> list[str]:
        """List all namespaces for a database connection."""
        return self.repository.list_namespaces(db_connection_id)

    def clear_namespace(
        self,
        db_connection_id: str,
        namespace: str,
    ) -> int:
        """Clear all memories in a namespace."""
        return self.repository.delete_by_namespace(db_connection_id, namespace)

    def clear_all(self, db_connection_id: str) -> int:
        """Clear all memories for a database connection."""
        memories = self.repository.find_all_for_connection(db_connection_id)
        count = 0
        for memory in memories:
            if memory.id:
                count += self.repository.delete(memory.id)
        return count

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
        """
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
