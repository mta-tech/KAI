"""Session data models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Literal


class SessionStatus(str, Enum):
    """Session lifecycle status."""
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    CLOSED = "closed"


@dataclass
class Message:
    """A single message in a session conversation."""
    id: str
    role: Literal["human", "assistant"]
    query: str
    sql: str | None = None
    results_summary: str | None = None
    analysis: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "role": self.role,
            "query": self.query,
            "sql": self.sql,
            "results_summary": self.results_summary,
            "analysis": self.analysis,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            role=data["role"],
            query=data["query"],
            sql=data.get("sql"),
            results_summary=data.get("results_summary"),
            analysis=data.get("analysis"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if isinstance(data.get("timestamp"), str) else data.get("timestamp", datetime.now())
        )


@dataclass
class Session:
    """A multi-query conversation session."""
    id: str
    db_connection_id: str
    messages: list[Message] = field(default_factory=list)
    summary: str | None = None
    status: SessionStatus = SessionStatus.IDLE
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "db_connection_id": self.db_connection_id,
            "messages": [m.to_dict() for m in self.messages],
            "summary": self.summary,
            "status": self.status.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            db_connection_id=data["db_connection_id"],
            messages=[Message.from_dict(m) for m in data.get("messages", [])],
            summary=data.get("summary"),
            status=SessionStatus(data.get("status", "idle")),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data.get("created_at"), str) else data.get("created_at", datetime.now()),
            updated_at=datetime.fromisoformat(data["updated_at"]) if isinstance(data.get("updated_at"), str) else data.get("updated_at", datetime.now())
        )


__all__ = ["Session", "Message", "SessionStatus"]
