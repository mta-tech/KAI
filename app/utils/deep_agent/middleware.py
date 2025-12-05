"""Middleware and backend helpers for Deep Agents.

This module provides backend configuration using the native deepagents library.

Note: The deepagents library includes middleware (planning, filesystem, subagents) 
internally within `create_deep_agent()`. This module provides helpers for 
configuring backends for different storage strategies.
"""

from __future__ import annotations

from typing import Dict, List

from deepagents.backends import StateBackend, CompositeBackend, StoreBackend, FilesystemBackend


def build_backend_factory(*, tenant_id: str, sql_generation_id: str) -> StateBackend:
    """Create a backend for tenant-scoped storage using deepagents backends.
    
    Uses StateBackend for in-memory state storage (default).
    For persistent storage, use CompositeBackend or StoreBackend.
    
    Args:
        tenant_id: Tenant identifier for isolation
        sql_generation_id: Session identifier
        
    Returns:
        StateBackend instance for ephemeral state storage
    """
    # For now, use simple StateBackend (in-memory)
    # CompositeBackend with StoreBackend requires a LangGraph Store to be configured
    return StateBackend()


def build_composite_backend(
    *,
    tenant_id: str,
    sql_generation_id: str,
    store=None,
) -> CompositeBackend:
    """Create a composite backend with different routes for different paths.
    
    This is useful for hybrid storage where some paths persist and others are ephemeral.
    
    Args:
        tenant_id: Tenant identifier for isolation
        sql_generation_id: Session identifier
        store: Optional LangGraph Store for persistent storage
        
    Returns:
        CompositeBackend with configured routes
    """
    default_backend = StateBackend()
    
    if store:
        return CompositeBackend(
            default=default_backend,
            routes={
                f"/tenants/{tenant_id}/": StoreBackend(store=store),
                f"/sessions/{sql_generation_id}/": default_backend,
            },
        )
    
    return CompositeBackend(default=default_backend, routes={})


def build_filesystem_backend(*, root_dir: str) -> FilesystemBackend:
    """Create a filesystem backend for real disk operations.
    
    Args:
        root_dir: Root directory for all file operations
        
    Returns:
        FilesystemBackend instance
    """
    return FilesystemBackend(root_dir=root_dir)


__all__ = [
    "build_backend_factory",
    "build_composite_backend",
    "build_filesystem_backend",
    "StateBackend",
    "CompositeBackend",
    "StoreBackend",
    "FilesystemBackend",
]
