"""Typesense collection schema for sessions."""

SESSIONS_SCHEMA = {
    "name": "sessions",
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "db_connection_id", "type": "string", "facet": True},
        {"name": "status", "type": "string", "facet": True},
        {"name": "summary", "type": "string", "optional": True},
        {"name": "messages", "type": "string"},  # JSON stringified array
        {"name": "checkpoint", "type": "string", "optional": True},  # LangGraph checkpoint
        {"name": "checkpoint_metadata", "type": "string", "optional": True},
        {"name": "metadata", "type": "object", "optional": True},
        {"name": "created_at", "type": "int64"},
        {"name": "updated_at", "type": "int64"},
    ],
    "default_sorting_field": "updated_at"
}


async def ensure_sessions_collection(storage) -> None:
    """
    Ensure sessions collection exists in Typesense.

    Creates the collection if it doesn't exist.

    Args:
        storage: Typesense storage instance
    """
    try:
        await storage.create_collection(SESSIONS_SCHEMA)
    except Exception as e:
        # Collection may already exist
        if "already exists" not in str(e).lower():
            raise


__all__ = ["SESSIONS_SCHEMA", "ensure_sessions_collection"]
