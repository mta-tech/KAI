"""Shared module helpers for autonomous agent CLI commands."""

from app.data.db.storage import Storage
from app.modules.database_connection.repositories import DatabaseConnectionRepository


def get_db_connection_repository(storage: Storage) -> DatabaseConnectionRepository:
    """Return a DatabaseConnectionRepository for the given storage."""
    return DatabaseConnectionRepository(storage)


def _resolve_db_identifier(identifier: str, repo: DatabaseConnectionRepository):
    """Resolve a database identifier (alias or ID) to a connection dict.

    Args:
        identifier: A database alias or connection ID.
        repo: A DatabaseConnectionRepository instance.

    Returns:
        A dict representation of the connection, or None if not found.
    """
    # Try alias first (more user-friendly)
    db_conn = repo.find_by_alias(identifier)
    if db_conn:
        return db_conn.model_dump() if hasattr(db_conn, "model_dump") else db_conn

    # Try by ID
    db_conn = repo.find_by_id(identifier)
    if db_conn:
        return db_conn.model_dump() if hasattr(db_conn, "model_dump") else db_conn

    return None
