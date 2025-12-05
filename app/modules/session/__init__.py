"""
Session module for multi-query conversation management.

This module provides:
- Session CRUD operations (create, get, list, delete)
- Multi-query conversation with memory
- SSE streaming for real-time responses
- LangGraph-based state management
- Typesense persistence with checkpointing

Usage:
    from app.modules.session import SessionService
    from app.modules.session.api import router, set_session_service

    # During startup, configure and set the service
    service = SessionService(repository=repo, graph=graph, checkpointer=checkpointer)
    set_session_service(service)

    # Include router in your FastAPI app
    app.include_router(router, prefix="/api/v1")
"""

from app.modules.session.models import Session, Message, SessionStatus
from app.modules.session.repositories import SessionRepository
from app.modules.session.services import SessionService
from app.modules.session.graph import build_session_graph
from app.modules.session.graph.state import SessionState, create_initial_state
from app.modules.session.graph.checkpointer import TypesenseCheckpointer
from app.modules.session.schema import SESSIONS_SCHEMA, ensure_sessions_collection
from app.modules.session.api import router, set_session_service, get_session_service

__all__ = [
    # Models
    "Session",
    "Message",
    "SessionStatus",
    "SessionState",
    "create_initial_state",
    # Repository & Service
    "SessionRepository",
    "SessionService",
    # Graph
    "build_session_graph",
    "TypesenseCheckpointer",
    # Schema
    "SESSIONS_SCHEMA",
    "ensure_sessions_collection",
    # API
    "router",
    "set_session_service",
    "get_session_service",
]
