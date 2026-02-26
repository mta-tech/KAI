"""Memory module for KAI.

Provides long-term memory storage and retrieval using TypeSense.
Memories persist across conversations and can be semantically searched.

This module enables autonomous agents to:
- Remember user preferences and apply them in future conversations
- Store business facts discovered during analysis
- Record data insights and patterns for future reference
- Learn from user corrections to avoid repeating mistakes

Usage:
    from app.modules.memory import MemoryService, TypesenseStore

    # Using the service directly
    service = MemoryService(storage)
    service.remember(db_connection_id, "user_preferences", "date_format", {"content": "YYYY-MM-DD"})
    results = service.recall(db_connection_id, "date format")

    # Using as a LangGraph BaseStore
    store = TypesenseStore(storage, db_connection_id)
    store.put(("user_preferences",), "date_format", {"content": "YYYY-MM-DD"})
    item = store.get(("user_preferences",), "date_format")
"""

from app.modules.memory.models import Memory, MemoryMetadata, MemorySearchResult
from app.modules.memory.repositories import MemoryRepository
from app.modules.memory.services import MemoryService
from app.modules.memory.store import TypesenseStore

__all__ = [
    # Models
    "Memory",
    "MemoryMetadata",
    "MemorySearchResult",
    # Repository
    "MemoryRepository",
    # Service
    "MemoryService",
    # LangGraph Store
    "TypesenseStore",
]
