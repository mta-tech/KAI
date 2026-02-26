"""Repository for AgentSession persistence."""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from app.modules.autonomous_agent.models import AgentSession

logger = logging.getLogger(__name__)

AGENT_SESSION_COLLECTION = "agent_sessions"


class AgentSessionRepository:
    """Repository for managing AgentSession in TypeSense."""

    def __init__(self, storage: Any):
        """Initialize with TypeSense storage.

        Args:
            storage: TypeSense storage instance
        """
        self.storage = storage
        self.collection = AGENT_SESSION_COLLECTION

    def create(
        self,
        db_connection_id: str,
        mode: str = "full_autonomy",
        recursion_limit: int = 100,
        title: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        """Create a new session.

        Args:
            db_connection_id: Database connection ID
            mode: Agent mode
            recursion_limit: Max recursion for LangGraph
            title: Optional session title
            metadata: Optional metadata

        Returns:
            Created session ID
        """
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        doc = {
            "id": session_id,
            "db_connection_id": db_connection_id,
            "status": "active",
            "mode": mode,
            "recursion_limit": recursion_limit,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "metadata": metadata,
        }

        self.storage.upsert(self.collection, doc)
        return session_id

    def get(self, session_id: str) -> AgentSession | None:
        """Get session by ID.

        Args:
            session_id: Session ID

        Returns:
            AgentSession if found, None otherwise
        """
        doc = self.storage.find_by_id(self.collection, session_id)
        if not doc:
            return None

        return AgentSession(
            id=doc["id"],
            db_connection_id=doc["db_connection_id"],
            status=doc["status"],
            mode=doc.get("mode", "full_autonomy"),
            recursion_limit=doc.get("recursion_limit", 100),
            title=doc.get("title"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            metadata=doc.get("metadata"),
        )

    def list(
        self,
        db_connection_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[AgentSession]:
        """List sessions with optional filters.

        Args:
            db_connection_id: Filter by database connection
            status: Filter by status
            limit: Maximum results

        Returns:
            List of AgentSession
        """
        filters = {}
        if db_connection_id:
            filters["db_connection_id"] = db_connection_id
        if status:
            filters["status"] = status

        docs = self.storage.search(
            self.collection,
            query="*",
            filter_by=filters,
            limit=limit,
            sort_by="created_at:desc",
        )

        return [
            AgentSession(
                id=doc["id"],
                db_connection_id=doc["db_connection_id"],
                status=doc["status"],
                mode=doc.get("mode", "full_autonomy"),
                recursion_limit=doc.get("recursion_limit", 100),
                title=doc.get("title"),
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
                metadata=doc.get("metadata"),
            )
            for doc in docs
        ]

    def update(self, session: AgentSession) -> None:
        """Update session.

        Args:
            session: Session to update
        """
        doc = {
            "id": session.id,
            "db_connection_id": session.db_connection_id,
            "status": session.status,
            "mode": session.mode,
            "recursion_limit": session.recursion_limit,
            "title": session.title,
            "created_at": session.created_at,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "metadata": session.metadata,
        }
        self.storage.upsert(self.collection, doc)

    def delete(self, session_id: str, cascade: bool = True) -> bool:
        """Delete session and optionally cascade to related data.

        When cascade=True (default), this also deletes:
        - Session-scoped memories associated with this session

        Args:
            session_id: Session ID to delete
            cascade: If True, delete related session-scoped data

        Returns:
            True if deleted, False if not found
        """
        # Get session first to get db_connection_id for cascade
        session = self.get(session_id)
        if not session:
            return False

        # Cascade delete session-scoped memories
        if cascade:
            try:
                self._cascade_delete_memories(session.db_connection_id, session_id)
            except Exception as e:
                logger.warning(f"Failed to cascade delete memories for session {session_id}: {e}")

        return self.storage.delete(self.collection, session_id)

    def _cascade_delete_memories(self, db_connection_id: str, session_id: str) -> int:
        """Delete all session-scoped memories for a session.

        Args:
            db_connection_id: Database connection ID
            session_id: Session ID

        Returns:
            Number of memories deleted
        """
        try:
            # Use delete_by_filter if available
            count = self.storage.delete_by_filter(
                "kai_memories",
                {"db_connection_id": db_connection_id, "session_id": session_id}
            )
            if count > 0:
                logger.info(f"Cascade deleted {count} memories for session {session_id}")
            return count
        except Exception as e:
            logger.warning(f"Cascade delete memories failed: {e}")
            return 0

    # Async variants for non-blocking API endpoints
    async def acreate(
        self,
        db_connection_id: str,
        mode: str = "full_autonomy",
        recursion_limit: int = 100,
        title: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        """Async version of create - runs sync operation in thread pool."""
        return await asyncio.to_thread(
            self.create, db_connection_id, mode, recursion_limit, title, metadata
        )

    async def aget(self, session_id: str) -> AgentSession | None:
        """Async version of get - runs sync operation in thread pool."""
        return await asyncio.to_thread(self.get, session_id)

    async def alist(
        self,
        db_connection_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[AgentSession]:
        """Async version of list - runs sync operation in thread pool."""
        return await asyncio.to_thread(self.list, db_connection_id, status, limit)

    async def aupdate(self, session: AgentSession) -> None:
        """Async version of update - runs sync operation in thread pool."""
        await asyncio.to_thread(self.update, session)

    async def adelete(self, session_id: str, cascade: bool = True) -> bool:
        """Async version of delete - runs sync operation in thread pool."""
        return await asyncio.to_thread(self.delete, session_id, cascade)


__all__ = ["AgentSessionRepository", "AGENT_SESSION_COLLECTION"]
