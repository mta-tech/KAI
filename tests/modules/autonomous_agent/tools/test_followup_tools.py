"""Tests for LLM-powered follow-up question suggestion tool."""
import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Load followup_tools.py directly to avoid the tools/__init__.py import chain
# which pulls in skill_tools -> EmbeddingModel -> google.genai (broken env).
# The module's lazy imports (ChatModel, Settings) are inside the inner
# function body, so they don't run at module-load time.
# ---------------------------------------------------------------------------

def _load_followup_module():
    module_path = (
        Path(__file__).resolve().parents[4]
        / "app" / "modules" / "autonomous_agent" / "tools" / "followup_tools.py"
    )
    spec = importlib.util.spec_from_file_location("followup_tools_direct", str(module_path))
    module = importlib.util.module_from_spec(spec)
    # Stub only the top-level imports in followup_tools.py
    for stub in ["app.modules.database_connection.models", "app.data.db.storage"]:
        sys.modules.setdefault(stub, MagicMock())
    spec.loader.exec_module(module)
    return module


_mod = _load_followup_module()
create_suggest_follow_ups_tool = _mod.create_suggest_follow_ups_tool

VALID_CATEGORIES = {"drill_down", "compare", "trend", "filter", "aggregate"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_tool():
    db_connection = MagicMock()
    db_connection.id = "test-conn-id"
    return create_suggest_follow_ups_tool(db_connection, MagicMock())


def _llm_response(questions: list[dict]) -> MagicMock:
    r = MagicMock()
    r.content = json.dumps({"questions": questions})
    return r


def _run(questions: list[dict], **kwargs) -> dict:
    """Run the tool with a mocked LLM; patch lazy imports inside the closure."""
    mock_settings = MagicMock()
    mock_settings.CHAT_FAMILY = "openai"
    mock_settings.CHAT_MODEL = "gpt-4o-mini"

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = _llm_response(questions)

    mock_chat_model = MagicMock()
    mock_chat_model.get_model.return_value = mock_llm

    tool = _make_tool()

    # Patch at the module level where they will be imported inside the closure
    with patch.dict(sys.modules, {
        "app.server.config": MagicMock(Settings=MagicMock(return_value=mock_settings)),
        "app.utils.model.chat_model": MagicMock(ChatModel=MagicMock(return_value=mock_chat_model)),
    }):
        result = tool(**kwargs)

    return json.loads(result)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_returns_valid_json_structure():
    """Tool returns JSON with success=True and a questions list."""
    questions = [
        {"question": "Trend over time?", "category": "trend", "rationale": "r1"},
        {"question": "Compare by region?", "category": "compare", "rationale": "r2"},
        {"question": "Filter top performers?", "category": "filter", "rationale": "r3"},
    ]
    parsed = _run(
        questions,
        original_question="Total sales by region?",
        analysis_summary="Regional variation found.",
    )
    assert parsed["success"] is True
    assert "questions" in parsed
    assert isinstance(parsed["questions"], list)


def test_returns_3_to_5_questions():
    """Tool returns between 3 and 5 questions."""
    questions = [
        {"question": f"Q{i}?", "category": "trend", "rationale": f"r{i}"}
        for i in range(4)
    ]
    parsed = _run(
        questions,
        original_question="Top products by revenue?",
        analysis_summary="Top 10 = 80% of revenue.",
    )
    assert parsed["success"] is True
    assert 3 <= len(parsed["questions"]) <= 5


def test_question_fields_are_present():
    """Each question has question, category, and rationale."""
    questions = [
        {"question": "Drill into electronics?", "category": "drill_down", "rationale": "Subcategory focus"},
        {"question": "Monthly trend?", "category": "trend", "rationale": "Over time"},
        {"question": "Compare to last year?", "category": "compare", "rationale": "YoY"},
    ]
    parsed = _run(
        questions,
        original_question="What sells most?",
        analysis_summary="Electronics = 45% of sales.",
    )
    for q in parsed["questions"]:
        assert "question" in q
        assert "category" in q
        assert "rationale" in q


def test_categories_are_valid():
    """All returned categories are valid enum values."""
    questions = [
        {"question": "Q1?", "category": "drill_down", "rationale": "r"},
        {"question": "Q2?", "category": "compare", "rationale": "r"},
        {"question": "Q3?", "category": "trend", "rationale": "r"},
        {"question": "Q4?", "category": "filter", "rationale": "r"},
        {"question": "Q5?", "category": "aggregate", "rationale": "r"},
    ]
    parsed = _run(
        questions,
        original_question="Summarize sales",
        analysis_summary="$5M with 10% growth.",
    )
    for q in parsed["questions"]:
        assert q["category"] in VALID_CATEGORIES, f"Bad category: {q['category']}"


def test_invalid_category_falls_back_to_drill_down():
    """Unknown category values are corrected to 'drill_down'."""
    questions = [
        {"question": "Q1?", "category": "invalid_category", "rationale": "r"},
        {"question": "Q2?", "category": "trend", "rationale": "r"},
        {"question": "Q3?", "category": "unknown", "rationale": "r"},
    ]
    parsed = _run(
        questions,
        original_question="Revenue breakdown?",
        analysis_summary="5 regions.",
    )
    assert parsed["success"] is True
    for q in parsed["questions"]:
        assert q["category"] in VALID_CATEGORIES


def test_max_5_questions_returned():
    """Output is capped at 5 even when LLM returns more."""
    questions = [
        {"question": f"Q{i}?", "category": "trend", "rationale": f"r{i}"}
        for i in range(8)
    ]
    parsed = _run(
        questions,
        original_question="Analyze everything",
        analysis_summary="Done.",
    )
    assert len(parsed["questions"]) <= 5


def test_data_columns_included_in_prompt():
    """data_columns values appear in the LLM prompt."""
    mock_settings = MagicMock()
    mock_settings.CHAT_FAMILY = "openai"
    mock_settings.CHAT_MODEL = "gpt-4o-mini"

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = _llm_response([
        {"question": "Q1?", "category": "aggregate", "rationale": "r"},
        {"question": "Q2?", "category": "filter", "rationale": "r"},
        {"question": "Q3?", "category": "compare", "rationale": "r"},
    ])
    mock_chat_model = MagicMock()
    mock_chat_model.get_model.return_value = mock_llm

    tool = _make_tool()
    with patch.dict(sys.modules, {
        "app.server.config": MagicMock(Settings=MagicMock(return_value=mock_settings)),
        "app.utils.model.chat_model": MagicMock(ChatModel=MagicMock(return_value=mock_chat_model)),
    }):
        tool(
            original_question="Sales by category",
            analysis_summary="Analyzed.",
            data_columns=["category", "revenue", "quantity"],
        )

    prompt_text = mock_llm.invoke.call_args[0][0]
    assert "category" in prompt_text
    assert "revenue" in prompt_text


def test_graceful_error_handling():
    """Returns error JSON with empty questions when LLM raises."""
    mock_settings = MagicMock()
    mock_settings.CHAT_FAMILY = "openai"
    mock_settings.CHAT_MODEL = "gpt-4o-mini"

    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = Exception("LLM connection failed")
    mock_chat_model = MagicMock()
    mock_chat_model.get_model.return_value = mock_llm

    tool = _make_tool()
    with patch.dict(sys.modules, {
        "app.server.config": MagicMock(Settings=MagicMock(return_value=mock_settings)),
        "app.utils.model.chat_model": MagicMock(ChatModel=MagicMock(return_value=mock_chat_model)),
    }):
        result = tool(original_question="Analyze sales", analysis_summary="Summary.")

    parsed = json.loads(result)
    assert parsed["success"] is False
    assert parsed["questions"] == []


def test_strips_markdown_code_fences():
    """Handles LLM responses wrapped in markdown code fences."""
    questions = [
        {"question": "Q1?", "category": "trend", "rationale": "r"},
        {"question": "Q2?", "category": "compare", "rationale": "r"},
        {"question": "Q3?", "category": "filter", "rationale": "r"},
    ]
    mock_response = MagicMock()
    mock_response.content = f"```json\n{json.dumps({'questions': questions})}\n```"

    mock_settings = MagicMock()
    mock_settings.CHAT_FAMILY = "openai"
    mock_settings.CHAT_MODEL = "gpt-4o-mini"

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = mock_response
    mock_chat_model = MagicMock()
    mock_chat_model.get_model.return_value = mock_llm

    tool = _make_tool()
    with patch.dict(sys.modules, {
        "app.server.config": MagicMock(Settings=MagicMock(return_value=mock_settings)),
        "app.utils.model.chat_model": MagicMock(ChatModel=MagicMock(return_value=mock_chat_model)),
    }):
        result = tool(
            original_question="Sales trend?",
            analysis_summary="Growing 10% MoM.",
        )

    parsed = json.loads(result)
    assert parsed["success"] is True
    assert len(parsed["questions"]) == 3
