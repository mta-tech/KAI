"""Session repository for Typesense storage."""
import uuid
import json
from datetime import datetime
from typing import Optional, Any

from app.modules.session.models import Session, Message, SessionStatus
from app.modules.session.constants import SESSION_COLLECTION_NAME


class SessionRepository:
    """
    Repository for session CRUD operations.

    Uses Typesense as the storage backend.
    Note: Storage methods are synchronous, but we keep async interface
    for consistency with the rest of the codebase.
    """

    def __init__(self, storage: Any):
        """
        Initialize repository with storage.

        Args:
            storage: Typesense storage instance
        """
        self.storage = storage
        self.collection = SESSION_COLLECTION_NAME

    async def create(
        self,
        db_connection_id: str,
        metadata: dict | None = None
    ) -> str:
        """
        Create a new session.

        Args:
            db_connection_id: Database connection for this session
            metadata: Optional custom metadata

        Returns:
            Created session ID
        """
        now = datetime.now()

        session_data = {
            "db_connection_id": db_connection_id,
            "messages": "[]",  # JSON string for Typesense
            "summary": None,
            "status": SessionStatus.IDLE.value,
            "metadata": metadata or {},
            "checkpoint": None,
            "checkpoint_metadata": "{}",
            "created_at": int(now.timestamp()),
            "updated_at": int(now.timestamp())
        }

        # Storage methods are sync - insert_one returns the created ID
        session_id = self.storage.insert_one(self.collection, session_data)
        return session_id

    async def get(self, session_id: str) -> Optional[Session]:
        """
        Get session by ID.

        Args:
            session_id: Session ID to retrieve

        Returns:
            Session if found, None otherwise
        """
        # Storage methods are sync
        doc = self.storage.find_by_id(self.collection, session_id)

        if not doc:
            return None

        return self._doc_to_session(doc)

    async def list(
        self,
        db_connection_id: str | None = None,
        status: SessionStatus | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Session]:
        """
        List sessions with optional filters.

        Args:
            db_connection_id: Filter by database connection
            status: Filter by status
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of matching sessions
        """
        filters = {}
        if db_connection_id:
            filters["db_connection_id"] = db_connection_id
        if status:
            filters["status"] = status.value

        # Storage methods are sync
        docs = self.storage.find(
            self.collection,
            filter=filters,
            limit=limit,
            page=offset // limit if limit > 0 else 0
        )

        return [self._doc_to_session(doc) for doc in docs]

    async def update(self, session: Session) -> None:
        """
        Update an existing session.

        Args:
            session: Session with updated data
        """
        session_data = {
            "messages": json.dumps([m.to_dict() for m in session.messages]),
            "summary": session.summary,
            "status": session.status.value,
            "metadata": session.metadata,
            "updated_at": int(datetime.now().timestamp())
        }

        # Storage methods are sync
        self.storage.update_or_create(
            self.collection,
            {"id": session.id},
            session_data
        )

    async def delete(self, session_id: str) -> None:
        """
        Delete a session.

        Args:
            session_id: Session ID to delete
        """
        # Storage methods are sync
        self.storage.delete_by_id(self.collection, session_id)

    async def close(self, session_id: str) -> None:
        """
        Close a session (soft delete / status change).

        Args:
            session_id: Session ID to close
        """
        # Storage methods are sync
        self.storage.update_or_create(
            self.collection,
            {"id": session_id},
            {
                "status": SessionStatus.CLOSED.value,
                "updated_at": int(datetime.now().timestamp())
            }
        )

    def _doc_to_session(self, doc: dict) -> Session:
        """
        Convert Typesense document to Session model.

        Args:
            doc: Raw document from Typesense

        Returns:
            Session instance
        """
        # Parse messages from JSON string
        messages_raw = doc.get("messages", "[]")
        if isinstance(messages_raw, str):
            messages_data = json.loads(messages_raw)
        else:
            messages_data = messages_raw

        messages = [Message.from_dict(m) for m in messages_data]

        # Parse timestamps
        created_at = doc.get("created_at")
        updated_at = doc.get("updated_at")

        if isinstance(created_at, int):
            created_at = datetime.fromtimestamp(created_at)
        elif isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = datetime.now()

        if isinstance(updated_at, int):
            updated_at = datetime.fromtimestamp(updated_at)
        elif isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        else:
            updated_at = datetime.now()

        return Session(
            id=doc["id"],
            db_connection_id=doc["db_connection_id"],
            messages=messages,
            summary=doc.get("summary"),
            status=SessionStatus(doc.get("status", "idle")),
            metadata=doc.get("metadata", {}),
            created_at=created_at,
            updated_at=updated_at
        )


__all__ = ["SessionRepository"]
