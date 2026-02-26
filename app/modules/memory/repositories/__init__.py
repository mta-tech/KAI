"""Repository for memory storage in TypeSense."""

import json
import time
from datetime import datetime, timezone

from app.data.db.storage import Storage
from app.modules.memory.models import Memory, MemorySearchResult

DB_COLLECTION = "kai_memories"


class MemoryRepository:
    """Repository for managing long-term memories in TypeSense storage."""

    def __init__(self, storage: Storage):
        self.storage = storage

    def _get_composite_key(self, db_connection_id: str, namespace: str, key: str) -> str:
        """Generate a composite key for memory lookup."""
        return f"{db_connection_id}:{namespace}:{key}"

    def insert(self, memory: Memory) -> Memory:
        """Insert a new memory."""
        memory_dict = memory.model_dump(exclude={"id"})
        # Serialize value dict to JSON string for TypeSense
        memory_dict["value"] = json.dumps(memory_dict["value"])
        memory.id = str(self.storage.insert_one(DB_COLLECTION, memory_dict))
        return memory

    def find_by_id(self, id: str) -> Memory | None:
        """Find a memory by its TypeSense ID."""
        row = self.storage.find_one(DB_COLLECTION, {"id": id})
        if not row:
            return None
        # Deserialize value from JSON string
        if isinstance(row.get("value"), str):
            row["value"] = json.loads(row["value"])
        return Memory(**row)

    def find_by_key(
        self,
        db_connection_id: str,
        namespace: str,
        key: str,
        session_id: str | None = None,
    ) -> Memory | None:
        """Find a memory by namespace and key within a database connection.

        Args:
            db_connection_id: Database connection ID.
            namespace: Memory namespace.
            key: Memory key.
            session_id: Optional session ID. If None, finds shared memory.
        """
        filter_dict = {
            "db_connection_id": db_connection_id,
            "namespace": namespace,
            "key": key,
        }
        if session_id:
            filter_dict["session_id"] = session_id
        else:
            # Find shared (database-level) memory where session_id is null
            filter_dict["session_id"] = None

        row = self.storage.find_one(DB_COLLECTION, filter_dict)
        if not row:
            return None
        # Deserialize value from JSON string
        if isinstance(row.get("value"), str):
            row["value"] = json.loads(row["value"])
        return Memory(**row)

    def find_by(
        self, filter: dict, page: int = 0, limit: int = 0
    ) -> list[Memory]:
        """Find memories matching a filter."""
        if page > 0 and limit > 0:
            rows = self.storage.find(DB_COLLECTION, filter, page=page, limit=limit)
        else:
            rows = self.storage.find(DB_COLLECTION, filter)
        result = []
        for row in rows:
            if isinstance(row.get("value"), str):
                row["value"] = json.loads(row["value"])
            result.append(Memory(**row))
        return result

    def find_all_for_connection(self, db_connection_id: str) -> list[Memory]:
        """Find all memories for a database connection."""
        return self.find_by({"db_connection_id": db_connection_id})

    def find_by_namespace(
        self, db_connection_id: str, namespace: str, limit: int = 100
    ) -> list[Memory]:
        """Find all memories in a namespace."""
        rows = self.storage.find(
            DB_COLLECTION,
            {"db_connection_id": db_connection_id, "namespace": namespace},
            limit=limit,
        )
        result = []
        for row in rows:
            if isinstance(row.get("value"), str):
                row["value"] = json.loads(row["value"])
            result.append(Memory(**row))
        return result

    def search(
        self,
        db_connection_id: str,
        query: str,
        query_embedding: list[float],
        namespace: str | None = None,
        limit: int = 10,
        alpha: float = 0.6,
        session_id: str | None = None,
        include_shared: bool = True,
    ) -> list[MemorySearchResult]:
        """Search memories by semantic relevance to a query.

        Uses hybrid search combining text and vector similarity.

        Args:
            db_connection_id: Database connection ID.
            query: Search query text.
            query_embedding: Query embedding vector.
            namespace: Optional namespace filter.
            limit: Maximum results.
            alpha: Hybrid search alpha (0=text, 1=vector).
            session_id: Optional session ID to filter by.
            include_shared: If True and session_id is set, include shared memories.
        """
        filter_by = f"db_connection_id:={db_connection_id}"
        if namespace:
            filter_by += f"&&namespace:={namespace}"

        # Build session filter for hierarchical memory
        if session_id:
            if include_shared:
                # Include both session-scoped and shared memories
                filter_by += f"&&(session_id:={session_id}||session_id:=null)"
            else:
                # Only session-scoped memories
                filter_by += f"&&session_id:={session_id}"
        else:
            # Only shared (database-level) memories
            filter_by += "&&session_id:=null"

        rows = self.storage.hybrid_search(
            collection=DB_COLLECTION,
            query=query,
            query_by="content_text, namespace, key",
            vector_query=f"memory_embedding:({query_embedding}, alpha:{alpha})",
            exclude_fields="memory_embedding",
            filter_by=filter_by,
            limit=limit,
        )
        result = []
        if rows:
            for row in rows:
                score = row.get("score", 0)
                if score >= 0.2:  # Lower threshold for memories
                    if isinstance(row.get("value"), str):
                        row["value"] = json.loads(row["value"])
                    memory = Memory(**row)
                    result.append(MemorySearchResult(
                        memory=memory,
                        score=score,
                        match_type="hybrid",
                    ))
        return result

    def search_by_text(
        self,
        db_connection_id: str,
        query: str,
        namespace: str | None = None,
        limit: int = 10,
    ) -> list[MemorySearchResult]:
        """Search memories by text content."""
        rows = self.storage.full_text_search(
            DB_COLLECTION,
            query,
            columns=["content_text", "namespace", "key"],
        )
        result = []
        if rows:
            for row in rows:
                if row.get("db_connection_id") != db_connection_id:
                    continue
                if namespace and row.get("namespace") != namespace:
                    continue
                if isinstance(row.get("value"), str):
                    row["value"] = json.loads(row["value"])
                memory = Memory(**row)
                result.append(MemorySearchResult(
                    memory=memory,
                    score=row.get("score", 0.5),
                    match_type="text",
                ))
                if len(result) >= limit:
                    break
        return result

    def update(self, memory: Memory) -> Memory:
        """Update an existing memory."""
        memory.updated_at = datetime.now(timezone.utc).isoformat()
        update_data = memory.model_dump(exclude={"id"})
        # Serialize value dict to JSON string for TypeSense
        update_data["value"] = json.dumps(update_data["value"])
        self.storage.update_or_create(
            DB_COLLECTION,
            {"id": memory.id},
            update_data,
        )
        return memory

    def put(
        self,
        db_connection_id: str,
        namespace: str,
        key: str,
        value: dict,
        content_text: str,
        importance: float = 0.5,
        session_id: str | None = None,
    ) -> Memory:
        """Store or update a memory.

        Args:
            db_connection_id: Database connection ID.
            namespace: Memory namespace.
            key: Memory key.
            value: Memory value dict.
            content_text: Searchable text content.
            importance: Importance score (0-1).
            session_id: Optional session ID. None for shared memory.
        """
        existing = self.find_by_key(db_connection_id, namespace, key, session_id)
        now = datetime.now(timezone.utc).isoformat()

        if existing:
            existing.value = value
            existing.content_text = content_text
            existing.importance = importance
            existing.access_count += 1
            existing.last_accessed_at = now
            return self.update(existing)
        else:
            memory = Memory(
                db_connection_id=db_connection_id,
                session_id=session_id,
                namespace=namespace,
                key=key,
                value=value,
                content_text=content_text,
                importance=importance,
                access_count=0,
                created_at=now,
                updated_at=now,
            )
            return self.insert(memory)

    def increment_access(self, memory: Memory) -> Memory:
        """Increment access count and update last accessed time."""
        memory.access_count += 1
        memory.last_accessed_at = datetime.now(timezone.utc).isoformat()
        return self.update(memory)

    def bulk_increment_access(self, memories: list[Memory]) -> None:
        """Increment access count for multiple memories in a batch.

        This is more efficient than calling increment_access in a loop.
        """
        if not memories:
            return

        now = datetime.now(timezone.utc).isoformat()
        updates = []
        for memory in memories:
            if memory.id:
                memory.access_count += 1
                memory.last_accessed_at = now
                memory.updated_at = now
                update_data = {
                    "id": memory.id,
                    "access_count": memory.access_count,
                    "last_accessed_at": memory.last_accessed_at,
                    "updated_at": memory.updated_at,
                }
                updates.append(update_data)

        if updates:
            self.storage.bulk_update(DB_COLLECTION, updates)

    def delete(self, id: str) -> int:
        """Delete a memory by ID."""
        return self.storage.delete_by_id(DB_COLLECTION, id)

    def delete_by_key(
        self,
        db_connection_id: str,
        namespace: str,
        key: str,
        session_id: str | None = None,
    ) -> bool:
        """Delete a memory by namespace and key.

        Args:
            db_connection_id: Database connection ID.
            namespace: Memory namespace.
            key: Memory key.
            session_id: Optional session ID. If None, deletes shared memory.
        """
        memory = self.find_by_key(db_connection_id, namespace, key, session_id)
        if memory and memory.id:
            return self.delete(memory.id) > 0
        return False

    def delete_by_namespace(self, db_connection_id: str, namespace: str) -> int:
        """Delete all memories in a namespace using batch delete."""
        return self.storage.delete_by_filter(
            DB_COLLECTION,
            {"db_connection_id": db_connection_id, "namespace": namespace}
        )

    def delete_by_connection(self, db_connection_id: str) -> int:
        """Delete all memories for a database connection using batch delete."""
        return self.storage.delete_by_filter(
            DB_COLLECTION,
            {"db_connection_id": db_connection_id}
        )

    def list_namespaces(self, db_connection_id: str) -> list[str]:
        """List all unique namespaces for a database connection."""
        memories = self.find_all_for_connection(db_connection_id)
        namespaces = set()
        for memory in memories:
            namespaces.add(memory.namespace)
        return sorted(list(namespaces))
