"""Tests for session models."""
import pytest
from datetime import datetime
from app.modules.session.models import Session, Message, SessionStatus


def test_message_creation():
    msg = Message(
        id="msg_123",
        role="human",
        query="Show me top customers",
        sql=None,
        results_summary=None,
        analysis=None,
        timestamp=datetime.now()
    )
    assert msg.id == "msg_123"
    assert msg.role == "human"
    assert msg.query == "Show me top customers"


def test_session_creation():
    session = Session(
        id="sess_123",
        db_connection_id="db_456",
        messages=[],
        summary=None,
        status=SessionStatus.IDLE,
        metadata={},
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    assert session.id == "sess_123"
    assert session.status == SessionStatus.IDLE
    assert session.messages == []


def test_session_status_enum():
    assert SessionStatus.IDLE.value == "idle"
    assert SessionStatus.PROCESSING.value == "processing"
    assert SessionStatus.ERROR.value == "error"
    assert SessionStatus.CLOSED.value == "closed"


def test_message_to_dict():
    now = datetime.now()
    msg = Message(
        id="msg_123",
        role="human",
        query="Test query",
        sql="SELECT 1",
        results_summary="1 row",
        analysis="Test analysis",
        timestamp=now
    )
    d = msg.to_dict()
    assert d["id"] == "msg_123"
    assert d["role"] == "human"
    assert d["sql"] == "SELECT 1"
    assert d["timestamp"] == now.isoformat()


def test_message_from_dict():
    data = {
        "id": "msg_456",
        "role": "assistant",
        "query": "Show data",
        "sql": "SELECT * FROM t",
        "results_summary": "5 rows",
        "analysis": "Analysis here",
        "timestamp": "2024-01-01T12:00:00"
    }
    msg = Message.from_dict(data)
    assert msg.id == "msg_456"
    assert msg.role == "assistant"
    assert msg.sql == "SELECT * FROM t"


def test_session_to_dict():
    now = datetime.now()
    session = Session(
        id="sess_123",
        db_connection_id="db_456",
        messages=[],
        summary="Test summary",
        status=SessionStatus.PROCESSING,
        metadata={"key": "value"},
        created_at=now,
        updated_at=now
    )
    d = session.to_dict()
    assert d["id"] == "sess_123"
    assert d["status"] == "processing"
    assert d["summary"] == "Test summary"
    assert d["metadata"] == {"key": "value"}


def test_session_from_dict():
    data = {
        "id": "sess_789",
        "db_connection_id": "db_111",
        "messages": [],
        "summary": None,
        "status": "idle",
        "metadata": {},
        "created_at": "2024-01-01T12:00:00",
        "updated_at": "2024-01-01T12:00:00"
    }
    session = Session.from_dict(data)
    assert session.id == "sess_789"
    assert session.db_connection_id == "db_111"
    assert session.status == SessionStatus.IDLE
