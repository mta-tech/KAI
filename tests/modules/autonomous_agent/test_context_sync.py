"""Tests for ContextSyncService and helpers in context_sync.py."""
import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Load context_sync.py directly to avoid the heavy import chain.
# Jinja2 is a real dependency so we let that load normally.
# Heavy KAI modules (repositories, asset service, SQL database) are stubbed
# inside the sync() method via lazy imports so they don't fire at module-load.
# ---------------------------------------------------------------------------

def _load_module():
    module_path = (
        Path(__file__).resolve().parents[3]
        / "app" / "modules" / "autonomous_agent" / "context_sync.py"
    )
    spec = importlib.util.spec_from_file_location("context_sync_direct", str(module_path))
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load_module()
_sanitize_alias = _mod._sanitize_alias
ContextSyncService = _mod.ContextSyncService
ContextSyncResult = _mod.ContextSyncResult


# ---------------------------------------------------------------------------
# _sanitize_alias
# ---------------------------------------------------------------------------

class TestSanitizeAlias:
    def test_alphanumeric_unchanged(self):
        assert _sanitize_alias("mydb") == "mydb"

    def test_underscore_and_dash_preserved(self):
        assert _sanitize_alias("my_db-v2") == "my_db-v2"

    def test_spaces_replaced(self):
        assert _sanitize_alias("my database") == "my-database"

    def test_special_chars_replaced(self):
        assert _sanitize_alias("db/name:foo") == "db-name-foo"

    def test_unicode_replaced(self):
        result = _sanitize_alias("db名前")
        assert result == "db--"

    def test_empty_string_unchanged(self):
        assert _sanitize_alias("") == ""


# ---------------------------------------------------------------------------
# ContextSyncService.sync — directory management
# ---------------------------------------------------------------------------

class TestContextSyncDirectoryManagement:
    """Verify that sync() clears and recreates the output directory."""

    def _make_service(self):
        return ContextSyncService(storage=MagicMock())

    def _stub_repos(self, monkeypatch, tables=None, glossary_assets=None, instruction_assets=None):
        """Patch all lazy imports inside sync() to return controlled data."""
        tables = tables or []
        glossary_assets = glossary_assets or []
        instruction_assets = instruction_assets or []

        mock_table_repo = MagicMock()
        mock_table_repo.find_by.return_value = tables

        mock_asset_service = MagicMock()
        mock_asset_service.list_assets.side_effect = [glossary_assets, instruction_assets]

        mock_db_repo = MagicMock()
        mock_db_repo.find_by_id.return_value = None  # no DB connection needed

        stub_table_repo_cls = MagicMock(return_value=mock_table_repo)
        stub_asset_service_cls = MagicMock(return_value=mock_asset_service)
        stub_db_repo_cls = MagicMock(return_value=mock_db_repo)

        # Stub the lazy-imported classes
        sys.modules["app.modules.table_description.repositories"] = MagicMock(
            TableDescriptionRepository=stub_table_repo_cls
        )
        sys.modules["app.modules.context_platform.services.asset_service"] = MagicMock(
            ContextAssetService=stub_asset_service_cls
        )
        sys.modules["app.modules.context_platform.models.asset"] = MagicMock(
            ContextAssetType=MagicMock(GLOSSARY="glossary", INSTRUCTION="instruction"),
            LifecycleState=MagicMock(PUBLISHED="published"),
        )
        sys.modules["app.modules.database_connection.repositories"] = MagicMock(
            DatabaseConnectionRepository=stub_db_repo_cls
        )

        return mock_table_repo, mock_asset_service

    def test_creates_base_directory(self, tmp_path, monkeypatch):
        self._stub_repos(monkeypatch)
        svc = self._make_service()
        result = svc.sync("conn-1", output_dir=str(tmp_path), db_alias="testdb")
        assert (tmp_path / "testdb").is_dir()

    def test_clears_stale_files_before_sync(self, tmp_path, monkeypatch):
        self._stub_repos(monkeypatch)
        # Pre-populate the directory with a stale file
        stale_dir = tmp_path / "testdb"
        stale_dir.mkdir()
        stale_file = stale_dir / "stale.md"
        stale_file.write_text("old content")

        svc = self._make_service()
        svc.sync("conn-1", output_dir=str(tmp_path), db_alias="testdb")

        assert not stale_file.exists(), "Stale file should have been removed"

    def test_alias_sanitized_for_directory_name(self, tmp_path, monkeypatch):
        self._stub_repos(monkeypatch)
        svc = self._make_service()
        svc.sync("conn-1", output_dir=str(tmp_path), db_alias="My Database/v2")
        assert (tmp_path / "My-Database-v2").is_dir()

    def test_returns_context_sync_result(self, tmp_path, monkeypatch):
        self._stub_repos(monkeypatch)
        svc = self._make_service()
        result = svc.sync("conn-1", output_dir=str(tmp_path), db_alias="testdb")
        assert isinstance(result, ContextSyncResult)


# ---------------------------------------------------------------------------
# ContextSyncService.sync — table file generation
# ---------------------------------------------------------------------------

class TestContextSyncTableFiles:

    def _make_table(self, name="orders"):
        col = MagicMock()
        col.name = "id"
        col.data_type = "INTEGER"
        col.description = "Primary key"
        col.is_primary_key = True
        col.nullable = False
        col.low_cardinality = False
        col.categories = []
        col.foreign_key = None

        table = MagicMock()
        table.table_name = name
        table.db_schema = None
        table.description = "Order records"
        table.columns = [col]
        return table

    def _stub_repos(self, tables):
        mock_table_repo = MagicMock()
        mock_table_repo.find_by.return_value = tables

        mock_asset_service = MagicMock()
        mock_asset_service.list_assets.side_effect = [[], []]

        sys.modules["app.modules.table_description.repositories"] = MagicMock(
            TableDescriptionRepository=MagicMock(return_value=mock_table_repo)
        )
        sys.modules["app.modules.context_platform.services.asset_service"] = MagicMock(
            ContextAssetService=MagicMock(return_value=mock_asset_service)
        )
        sys.modules["app.modules.context_platform.models.asset"] = MagicMock(
            ContextAssetType=MagicMock(GLOSSARY="glossary", INSTRUCTION="instruction"),
            LifecycleState=MagicMock(PUBLISHED="published"),
        )
        sys.modules["app.modules.database_connection.repositories"] = MagicMock(
            DatabaseConnectionRepository=MagicMock(return_value=MagicMock(find_by_id=MagicMock(return_value=None)))
        )

    def test_writes_columns_md_for_each_table(self, tmp_path):
        self._stub_repos([self._make_table("orders")])
        svc = ContextSyncService(storage=MagicMock())
        result = svc.sync(
            "conn-1",
            output_dir=str(tmp_path),
            include_preview=False,
            db_alias="mydb",
        )
        assert (tmp_path / "mydb" / "tables" / "orders" / "columns.md").exists()
        assert result.table_count == 1
        assert result.file_count == 1

    def test_skips_preview_when_disabled(self, tmp_path):
        self._stub_repos([self._make_table("orders")])
        svc = ContextSyncService(storage=MagicMock())
        svc.sync(
            "conn-1",
            output_dir=str(tmp_path),
            include_preview=False,
            db_alias="mydb",
        )
        assert not (tmp_path / "mydb" / "tables" / "orders" / "preview.md").exists()

    def test_writes_preview_when_sql_db_available(self, tmp_path):
        self._stub_repos([self._make_table("orders")])
        svc = ContextSyncService(storage=MagicMock())
        # Stub _fetch_preview to return controlled data
        svc._fetch_preview = MagicMock(return_value=(
            [{"id": "1"}],
            ["id"],
        ))
        svc._get_sql_database = MagicMock(return_value=MagicMock())
        svc.sync(
            "conn-1",
            output_dir=str(tmp_path),
            include_preview=True,
            preview_rows=5,
            db_alias="mydb",
        )
        assert (tmp_path / "mydb" / "tables" / "orders" / "preview.md").exists()

    def test_columns_md_contains_table_name(self, tmp_path):
        self._stub_repos([self._make_table("orders")])
        svc = ContextSyncService(storage=MagicMock())
        svc.sync(
            "conn-1",
            output_dir=str(tmp_path),
            include_preview=False,
            db_alias="mydb",
        )
        content = (tmp_path / "mydb" / "tables" / "orders" / "columns.md").read_text()
        assert "orders" in content

    def test_increments_table_count(self, tmp_path):
        tables = [self._make_table("a"), self._make_table("b"), self._make_table("c")]
        self._stub_repos(tables)
        svc = ContextSyncService(storage=MagicMock())
        result = svc.sync(
            "conn-1",
            output_dir=str(tmp_path),
            include_preview=False,
            db_alias="mydb",
        )
        assert result.table_count == 3


# ---------------------------------------------------------------------------
# ContextSyncService.sync — glossary and instruction files
# ---------------------------------------------------------------------------

class TestContextSyncAssetFiles:

    def _make_asset(self, name, canonical_key, content):
        asset = MagicMock()
        asset.name = name
        asset.canonical_key = canonical_key
        asset.description = ""
        asset.content = content
        return asset

    def _stub_repos(self, glossary_assets=None, instruction_assets=None):
        mock_table_repo = MagicMock()
        mock_table_repo.find_by.return_value = []

        mock_asset_service = MagicMock()
        mock_asset_service.list_assets.side_effect = [
            glossary_assets or [],
            instruction_assets or [],
        ]

        sys.modules["app.modules.table_description.repositories"] = MagicMock(
            TableDescriptionRepository=MagicMock(return_value=mock_table_repo)
        )
        sys.modules["app.modules.context_platform.services.asset_service"] = MagicMock(
            ContextAssetService=MagicMock(return_value=mock_asset_service)
        )
        sys.modules["app.modules.context_platform.models.asset"] = MagicMock(
            ContextAssetType=MagicMock(GLOSSARY="glossary", INSTRUCTION="instruction"),
            LifecycleState=MagicMock(PUBLISHED="published"),
        )
        sys.modules["app.modules.database_connection.repositories"] = MagicMock(
            DatabaseConnectionRepository=MagicMock(return_value=MagicMock(find_by_id=MagicMock(return_value=None)))
        )

    def test_writes_glossary_file(self, tmp_path):
        asset = self._make_asset("Revenue", "revenue", {"definition": "Total net revenue"})
        self._stub_repos(glossary_assets=[asset])
        svc = ContextSyncService(storage=MagicMock())
        result = svc.sync("conn-1", output_dir=str(tmp_path), db_alias="mydb")
        assert (tmp_path / "mydb" / "glossary" / "revenue.md").exists()
        assert result.glossary_count == 1

    def test_glossary_file_contains_definition(self, tmp_path):
        asset = self._make_asset("Revenue", "revenue", {"definition": "Total net revenue"})
        self._stub_repos(glossary_assets=[asset])
        svc = ContextSyncService(storage=MagicMock())
        svc.sync("conn-1", output_dir=str(tmp_path), db_alias="mydb")
        content = (tmp_path / "mydb" / "glossary" / "revenue.md").read_text()
        assert "Total net revenue" in content

    def test_writes_instruction_file(self, tmp_path):
        asset = self._make_asset("Always filter by tenant", "tenant-filter", {"rule": "Always add WHERE tenant_id = ?"})
        self._stub_repos(instruction_assets=[asset])
        svc = ContextSyncService(storage=MagicMock())
        result = svc.sync("conn-1", output_dir=str(tmp_path), db_alias="mydb")
        assert (tmp_path / "mydb" / "instructions" / "tenant-filter.md").exists()
        assert result.instruction_count == 1

    def test_instruction_key_sanitized(self, tmp_path):
        asset = self._make_asset("My Rule", "my rule/special", {"rule": "content"})
        self._stub_repos(instruction_assets=[asset])
        svc = ContextSyncService(storage=MagicMock())
        svc.sync("conn-1", output_dir=str(tmp_path), db_alias="mydb")
        assert (tmp_path / "mydb" / "instructions" / "my-rule-special.md").exists()

    def test_no_glossary_dir_when_no_assets(self, tmp_path):
        self._stub_repos(glossary_assets=[], instruction_assets=[])
        svc = ContextSyncService(storage=MagicMock())
        svc.sync("conn-1", output_dir=str(tmp_path), db_alias="mydb")
        assert not (tmp_path / "mydb" / "glossary").exists()


# ---------------------------------------------------------------------------
# ContextSyncService._fetch_preview
# ---------------------------------------------------------------------------

class TestFetchPreview:

    def _make_service(self):
        return ContextSyncService(storage=MagicMock())

    def test_returns_empty_when_no_sql_db(self):
        svc = self._make_service()
        rows, cols = svc._fetch_preview(None, None, "orders", 5)
        assert rows == []
        assert cols == []

    def test_returns_empty_when_run_sql_returns_no_results(self):
        svc = self._make_service()
        sql_db = MagicMock()
        sql_db.run_sql.return_value = ("SELECT ...", {"result": []})
        rows, cols = svc._fetch_preview(sql_db, None, "orders", 5)
        assert rows == []

    def test_truncates_long_values(self):
        svc = self._make_service()
        sql_db = MagicMock()
        long_val = "x" * 200
        sql_db.run_sql.return_value = ("SELECT ...", {"result": [{"col": long_val}]})
        rows, cols = svc._fetch_preview(sql_db, None, "orders", 5)
        assert len(rows) == 1
        assert len(rows[0]["col"]) <= 101  # 100 chars + ellipsis char

    def test_excludes_binary_columns(self):
        svc = self._make_service()
        sql_db = MagicMock()
        sql_db.run_sql.return_value = ("SELECT ...", {"result": [
            {"name": "Alice", "blob_col": b"\x00\x01\x02"}
        ]})
        rows, cols = svc._fetch_preview(sql_db, None, "users", 5)
        assert "blob_col" not in cols
        assert "name" in cols

    def test_qualifies_with_schema(self):
        svc = self._make_service()
        sql_db = MagicMock()
        sql_db.run_sql.return_value = ("SELECT ...", {"result": []})
        svc._fetch_preview(sql_db, "public", "orders", 5)
        call_args = sql_db.run_sql.call_args[0][0]
        assert '"public"."orders"' in call_args

    def test_handles_exception_gracefully(self):
        svc = self._make_service()
        sql_db = MagicMock()
        sql_db.run_sql.side_effect = RuntimeError("DB error")
        rows, cols = svc._fetch_preview(sql_db, None, "orders", 5)
        assert rows == []
        assert cols == []
