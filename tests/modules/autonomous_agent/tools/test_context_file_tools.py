"""Tests for file-based context agent tools (context_file_tools.py)."""
import importlib.util
import json
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Load context_file_tools.py directly — zero heavy imports at module level.
# ---------------------------------------------------------------------------

def _load_module():
    module_path = (
        Path(__file__).resolve().parents[4]
        / "app" / "modules" / "autonomous_agent" / "tools" / "context_file_tools.py"
    )
    spec = importlib.util.spec_from_file_location("context_file_tools_direct", str(module_path))
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load_module()
create_search_context_files_tool = _mod.create_search_context_files_tool
create_read_context_file_tool = _mod.create_read_context_file_tool


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def context_dir(tmp_path):
    """Create a minimal context directory tree for 'mydb'."""
    db_dir = tmp_path / "mydb"

    # tables/orders/columns.md
    orders_dir = db_dir / "tables" / "orders"
    orders_dir.mkdir(parents=True)
    (orders_dir / "columns.md").write_text(
        "# orders\n\nRevenue and order records.\n\n| Column | Type |\n| id | INTEGER |\n| amount | NUMERIC |\n",
        encoding="utf-8",
    )
    (orders_dir / "preview.md").write_text(
        "# Preview: orders\n\n| id | amount |\n| 1 | 100 |\n",
        encoding="utf-8",
    )

    # tables/users/columns.md
    users_dir = db_dir / "tables" / "users"
    users_dir.mkdir(parents=True)
    (users_dir / "columns.md").write_text(
        "# users\n\nCustomer account records.\n\n| Column | Type |\n| id | INTEGER |\n| email | TEXT |\n",
        encoding="utf-8",
    )

    # glossary/revenue.md
    glossary_dir = db_dir / "glossary"
    glossary_dir.mkdir()
    (glossary_dir / "revenue.md").write_text(
        "# Revenue\n\nTotal net revenue after discounts.\n",
        encoding="utf-8",
    )

    # instructions/tenant-filter.md
    instructions_dir = db_dir / "instructions"
    instructions_dir.mkdir()
    (instructions_dir / "tenant-filter.md").write_text(
        "# Tenant Filter\n\nAlways add WHERE tenant_id = :tenant_id.\n",
        encoding="utf-8",
    )

    return tmp_path


# ---------------------------------------------------------------------------
# search_context_files — basic search
# ---------------------------------------------------------------------------

class TestSearchContextFiles:

    def test_finds_match_in_tables(self, context_dir):
        tool = create_search_context_files_tool(str(context_dir), "mydb")
        result = json.loads(tool("Revenue"))
        assert result["success"] is True
        assert result["total_matches"] >= 1
        files = [m["file"] for m in result["matches"]]
        assert any("glossary" in f or "columns" in f for f in files)

    def test_case_insensitive_search(self, context_dir):
        tool = create_search_context_files_tool(str(context_dir), "mydb")
        result_lower = json.loads(tool("revenue"))
        result_upper = json.loads(tool("REVENUE"))
        assert result_lower["total_matches"] == result_upper["total_matches"]

    def test_no_matches_returns_empty_list(self, context_dir):
        tool = create_search_context_files_tool(str(context_dir), "mydb")
        result = json.loads(tool("zzz_no_such_term_zzz"))
        assert result["success"] is True
        assert result["matches"] == []

    def test_filter_by_file_type_tables(self, context_dir):
        tool = create_search_context_files_tool(str(context_dir), "mydb")
        result = json.loads(tool("id", file_type="tables"))
        files = [m["file"] for m in result["matches"]]
        assert all(f.startswith("tables/") for f in files)

    def test_filter_by_file_type_glossary(self, context_dir):
        tool = create_search_context_files_tool(str(context_dir), "mydb")
        result = json.loads(tool("Revenue", file_type="glossary"))
        files = [m["file"] for m in result["matches"]]
        assert all(f.startswith("glossary/") for f in files)

    def test_filter_by_file_type_instructions(self, context_dir):
        tool = create_search_context_files_tool(str(context_dir), "mydb")
        result = json.loads(tool("tenant", file_type="instructions"))
        files = [m["file"] for m in result["matches"]]
        assert all(f.startswith("instructions/") for f in files)

    def test_match_includes_excerpt(self, context_dir):
        tool = create_search_context_files_tool(str(context_dir), "mydb")
        result = json.loads(tool("email"))
        assert result["total_matches"] >= 1
        match = result["matches"][0]
        assert "excerpt" in match
        assert "email" in match["excerpt"].lower()

    def test_match_includes_line_number(self, context_dir):
        tool = create_search_context_files_tool(str(context_dir), "mydb")
        result = json.loads(tool("email"))
        assert result["matches"][0]["line"] >= 1

    def test_respects_max_matches_limit(self, tmp_path):
        db_dir = tmp_path / "testdb"
        db_dir.mkdir()
        # Create 30 files each containing the search term
        for i in range(30):
            f = db_dir / f"file_{i}.md"
            f.write_text(f"# File {i}\n\nThis has the word needle in it.\n")
        tool = create_search_context_files_tool(str(tmp_path), "testdb")
        result = json.loads(tool("needle"))
        assert result["total_matches"] <= 20

    def test_missing_context_dir_returns_empty(self, tmp_path):
        tool = create_search_context_files_tool(str(tmp_path), "nonexistent_db")
        result = json.loads(tool("anything"))
        assert result["success"] is True
        assert result["matches"] == []

    def test_query_echoed_in_result(self, context_dir):
        tool = create_search_context_files_tool(str(context_dir), "mydb")
        result = json.loads(tool("orders"))
        assert result["query"] == "orders"


# ---------------------------------------------------------------------------
# read_context_file — happy path
# ---------------------------------------------------------------------------

class TestReadContextFile:

    def test_reads_existing_file(self, context_dir):
        tool = create_read_context_file_tool(str(context_dir), "mydb")
        content = tool("tables/orders/columns.md")
        assert "orders" in content
        assert "INTEGER" in content

    def test_reads_glossary_file(self, context_dir):
        tool = create_read_context_file_tool(str(context_dir), "mydb")
        content = tool("glossary/revenue.md")
        assert "Total net revenue" in content

    def test_reads_instruction_file(self, context_dir):
        tool = create_read_context_file_tool(str(context_dir), "mydb")
        content = tool("instructions/tenant-filter.md")
        assert "tenant_id" in content

    def test_returns_raw_text_not_json(self, context_dir):
        tool = create_read_context_file_tool(str(context_dir), "mydb")
        content = tool("tables/orders/columns.md")
        # Should be plain text, not JSON-wrapped
        try:
            parsed = json.loads(content)
            # If parseable, it must NOT be a success/error wrapper
            assert "success" not in parsed
        except json.JSONDecodeError:
            pass  # expected — raw markdown


# ---------------------------------------------------------------------------
# read_context_file — error cases
# ---------------------------------------------------------------------------

class TestReadContextFileErrors:

    def test_missing_file_returns_error_json(self, context_dir):
        tool = create_read_context_file_tool(str(context_dir), "mydb")
        result = json.loads(tool("tables/nonexistent/columns.md"))
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_path_traversal_blocked(self, context_dir):
        tool = create_read_context_file_tool(str(context_dir), "mydb")
        result = json.loads(tool("../../etc/passwd"))
        assert result["success"] is False
        assert "traversal" in result["error"].lower()

    def test_path_traversal_to_sibling_dir_blocked(self, context_dir):
        # Create a sibling directory with a secret file outside mydb/
        sibling = context_dir / "secrets"
        sibling.mkdir()
        (sibling / "secret.md").write_text("top secret")
        tool = create_read_context_file_tool(str(context_dir), "mydb")
        result = json.loads(tool("../secrets/secret.md"))
        assert result["success"] is False

    def test_absolute_path_blocked(self, context_dir):
        tool = create_read_context_file_tool(str(context_dir), "mydb")
        result = json.loads(tool("/etc/passwd"))
        assert result["success"] is False


# ---------------------------------------------------------------------------
# Tool function names
# ---------------------------------------------------------------------------

class TestToolFunctionNames:

    def test_search_tool_has_correct_name(self, context_dir):
        tool = create_search_context_files_tool(str(context_dir), "mydb")
        assert tool.__name__ == "search_context_files"

    def test_read_tool_has_correct_name(self, context_dir):
        tool = create_read_context_file_tool(str(context_dir), "mydb")
        assert tool.__name__ == "read_context_file"
