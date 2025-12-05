"""TypeSense-backed implementation of LangGraph BaseStore.

This module provides a LangGraph-compatible store backed by TypeSense,
enabling long-term memory for autonomous agents.
"""

from datetime import datetime
from typing import Any, Iterable, Literal

from langgraph.store.base import (
    BaseStore,
    Item,
    SearchItem,
    GetOp,
    PutOp,
    SearchOp,
    ListNamespacesOp,
    NamespacePath,
)

from app.data.db.storage import Storage
from app.modules.memory.services import MemoryService


class TypesenseStore(BaseStore):
    """LangGraph-compatible store backed by TypeSense.

    Provides long-term memory storage that persists across conversations
    and supports semantic search.

    Example:
        ```python
        from app.modules.memory.store import TypesenseStore

        store = TypesenseStore(storage, db_connection_id="conn-123")

        # Store a memory
        store.put(("user_preferences",), "date_format", {"value": "YYYY-MM-DD"})

        # Retrieve a memory
        item = store.get(("user_preferences",), "date_format")

        # Search memories
        results = store.search(("facts",), query="revenue calculation")
        ```
    """

    def __init__(self, storage: Storage, db_connection_id: str):
        """Initialize the TypeSense store.

        Args:
            storage: TypeSense storage instance.
            db_connection_id: Database connection to scope memories to.
        """
        self.storage = storage
        self.db_connection_id = db_connection_id
        self.service = MemoryService(storage)

    def _namespace_to_str(self, namespace: tuple[str, ...]) -> str:
        """Convert namespace tuple to string representation."""
        return "/".join(namespace)

    def _str_to_namespace(self, namespace_str: str) -> tuple[str, ...]:
        """Convert string representation to namespace tuple."""
        return tuple(namespace_str.split("/"))

    def batch(self, ops: Iterable[Any]) -> list[Any]:
        """Execute multiple operations synchronously in a single batch.

        Args:
            ops: An iterable of operations to execute.

        Returns:
            A list of results corresponding to each operation.
        """
        results = []
        for op in ops:
            if isinstance(op, GetOp):
                result = self._get(op.namespace, op.key)
                results.append(result)
            elif isinstance(op, PutOp):
                self._put(op.namespace, op.key, op.value)
                results.append(None)
            elif isinstance(op, SearchOp):
                result = self._search(
                    op.namespace_prefix,
                    query=op.query,
                    filter=op.filter,
                    limit=op.limit,
                    offset=op.offset,
                )
                results.append(result)
            elif isinstance(op, ListNamespacesOp):
                result = self._list_namespaces(
                    prefix=op.prefix,
                    suffix=op.suffix,
                    max_depth=op.max_depth,
                    limit=op.limit,
                    offset=op.offset,
                )
                results.append(result)
            else:
                # Handle delete operations (check by attribute since DeleteOp may vary)
                if hasattr(op, 'namespace') and hasattr(op, 'key') and not hasattr(op, 'value'):
                    self._delete(op.namespace, op.key)
                    results.append(None)
                else:
                    results.append(None)
        return results

    async def abatch(self, ops: Iterable[Any]) -> list[Any]:
        """Execute multiple operations asynchronously in a single batch.

        Args:
            ops: An iterable of operations to execute.

        Returns:
            A list of results corresponding to each operation.
        """
        # For now, delegate to synchronous implementation
        # TypeSense client operations are synchronous
        return self.batch(ops)

    def _get(self, namespace: tuple[str, ...], key: str) -> Item | None:
        """Internal get implementation."""
        ns_str = self._namespace_to_str(namespace)
        memory = self.service.get_memory(self.db_connection_id, ns_str, key)
        if memory:
            return Item(
                namespace=namespace,
                key=key,
                value=memory.value,
                created_at=datetime.fromisoformat(memory.created_at),
                updated_at=datetime.fromisoformat(memory.updated_at),
            )
        return None

    def _put(
        self,
        namespace: tuple[str, ...],
        key: str,
        value: dict[str, Any],
    ) -> None:
        """Internal put implementation."""
        ns_str = self._namespace_to_str(namespace)
        # Extract importance from value if present, otherwise use default
        importance = value.pop("_importance", 0.5) if "_importance" in value else 0.5
        self.service.remember(
            db_connection_id=self.db_connection_id,
            namespace=ns_str,
            key=key,
            value=value,
            importance=importance,
        )

    def _search(
        self,
        namespace_prefix: tuple[str, ...],
        query: str | None = None,
        filter: dict[str, Any] | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[SearchItem]:
        """Internal search implementation."""
        ns_str = self._namespace_to_str(namespace_prefix) if namespace_prefix else None

        if query:
            # Semantic search
            results = self.service.recall(
                db_connection_id=self.db_connection_id,
                query=query,
                namespace=ns_str,
                limit=limit,
            )
            return [
                SearchItem(
                    namespace=self._str_to_namespace(r.memory.namespace),
                    key=r.memory.key,
                    value=r.memory.value,
                    created_at=datetime.fromisoformat(r.memory.created_at),
                    updated_at=datetime.fromisoformat(r.memory.updated_at),
                    score=r.score,
                )
                for r in results
            ]
        else:
            # List memories in namespace
            memories = self.service.list_memories(
                db_connection_id=self.db_connection_id,
                namespace=ns_str,
                limit=limit,
            )
            return [
                SearchItem(
                    namespace=self._str_to_namespace(m.namespace),
                    key=m.key,
                    value=m.value,
                    created_at=datetime.fromisoformat(m.created_at),
                    updated_at=datetime.fromisoformat(m.updated_at),
                    score=1.0,  # No search score for listing
                )
                for m in memories[offset:offset + limit]
            ]

    def _delete(self, namespace: tuple[str, ...], key: str) -> None:
        """Internal delete implementation."""
        ns_str = self._namespace_to_str(namespace)
        self.service.forget(self.db_connection_id, ns_str, key)

    def _list_namespaces(
        self,
        prefix: NamespacePath | None = None,
        suffix: NamespacePath | None = None,
        max_depth: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[tuple[str, ...]]:
        """Internal list_namespaces implementation."""
        namespaces = self.service.list_namespaces(self.db_connection_id)
        result = [self._str_to_namespace(ns) for ns in namespaces]

        # Apply prefix filter
        if prefix:
            prefix_tuple = tuple(prefix)
            result = [ns for ns in result if ns[:len(prefix_tuple)] == prefix_tuple]

        # Apply suffix filter
        if suffix:
            suffix_tuple = tuple(suffix)
            result = [ns for ns in result if ns[-len(suffix_tuple):] == suffix_tuple]

        # Apply max_depth - truncate namespaces
        if max_depth is not None:
            truncated = set()
            for ns in result:
                if len(ns) > max_depth:
                    truncated.add(ns[:max_depth])
                else:
                    truncated.add(ns)
            result = list(truncated)

        # Sort for consistent ordering
        result = sorted(result)

        # Apply pagination
        return result[offset:offset + limit]

    # Override convenience methods for cleaner API
    def get(
        self,
        namespace: tuple[str, ...],
        key: str,
        *,
        refresh_ttl: bool | None = None,
    ) -> Item | None:
        """Retrieve a single item.

        Args:
            namespace: Hierarchical path for the item.
            key: Unique identifier within the namespace.
            refresh_ttl: Ignored (TTL not supported).

        Returns:
            The retrieved item or None if not found.
        """
        return self._get(namespace, key)

    async def aget(
        self,
        namespace: tuple[str, ...],
        key: str,
        *,
        refresh_ttl: bool | None = None,
    ) -> Item | None:
        """Asynchronously retrieve a single item."""
        return self._get(namespace, key)

    def put(
        self,
        namespace: tuple[str, ...],
        key: str,
        value: dict[str, Any],
        index: Literal[False] | list[str] | None = None,
        *,
        ttl: float | None = None,
    ) -> None:
        """Store or update an item in the store.

        Args:
            namespace: Hierarchical path for the item.
            key: Unique identifier within the namespace.
            value: Dictionary containing the item's data.
            index: Ignored (indexing always enabled).
            ttl: Ignored (TTL not supported).
        """
        self._put(namespace, key, value)

    async def aput(
        self,
        namespace: tuple[str, ...],
        key: str,
        value: dict[str, Any],
        index: Literal[False] | list[str] | None = None,
        *,
        ttl: float | None = None,
    ) -> None:
        """Asynchronously store or update an item in the store."""
        self._put(namespace, key, value)

    def search(
        self,
        namespace_prefix: tuple[str, ...],
        /,
        *,
        query: str | None = None,
        filter: dict[str, Any] | None = None,
        limit: int = 10,
        offset: int = 0,
        refresh_ttl: bool | None = None,
    ) -> list[SearchItem]:
        """Search for items within a namespace prefix.

        Args:
            namespace_prefix: Hierarchical path prefix to search within.
            query: Optional query for semantic search.
            filter: Key-value pairs to filter results (limited support).
            limit: Maximum number of items to return.
            offset: Number of items to skip.
            refresh_ttl: Ignored (TTL not supported).

        Returns:
            List of items matching the search criteria.
        """
        return self._search(namespace_prefix, query, filter, limit, offset)

    async def asearch(
        self,
        namespace_prefix: tuple[str, ...],
        /,
        *,
        query: str | None = None,
        filter: dict[str, Any] | None = None,
        limit: int = 10,
        offset: int = 0,
        refresh_ttl: bool | None = None,
    ) -> list[SearchItem]:
        """Asynchronously search for items within a namespace prefix."""
        return self._search(namespace_prefix, query, filter, limit, offset)

    def delete(self, namespace: tuple[str, ...], key: str) -> None:
        """Delete an item.

        Args:
            namespace: Hierarchical path for the item.
            key: Unique identifier within the namespace.
        """
        self._delete(namespace, key)

    async def adelete(self, namespace: tuple[str, ...], key: str) -> None:
        """Asynchronously delete an item."""
        self._delete(namespace, key)

    def list_namespaces(
        self,
        *,
        prefix: NamespacePath | None = None,
        suffix: NamespacePath | None = None,
        max_depth: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[tuple[str, ...]]:
        """List and filter namespaces in the store.

        Args:
            prefix: Filter namespaces that start with this path.
            suffix: Filter namespaces that end with this path.
            max_depth: Return namespaces up to this depth.
            limit: Maximum number of namespaces to return.
            offset: Number of namespaces to skip.

        Returns:
            A list of namespace tuples matching the criteria.
        """
        return self._list_namespaces(prefix, suffix, max_depth, limit, offset)

    async def alist_namespaces(
        self,
        *,
        prefix: NamespacePath | None = None,
        suffix: NamespacePath | None = None,
        max_depth: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[tuple[str, ...]]:
        """Asynchronously list and filter namespaces in the store."""
        return self._list_namespaces(prefix, suffix, max_depth, limit, offset)
