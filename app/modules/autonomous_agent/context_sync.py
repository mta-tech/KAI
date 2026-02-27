"""Context sync service for writing schema and context assets to filesystem.

Exports database schema, glossary, and instruction assets as Markdown files
organized by database alias. Agents can then read these files directly
without requiring a live Typesense connection.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).parent / "templates" / "context"


def _sanitize_alias(alias: str) -> str:
    """Convert an alias to a filesystem-safe name."""
    return re.sub(r"[^a-zA-Z0-9_-]", "-", alias)


def _load_jinja_env():
    """Load the Jinja2 environment from the templates directory."""
    from jinja2 import Environment, FileSystemLoader, select_autoescape

    return Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=select_autoescape([]),
        keep_trailing_newline=True,
    )


class ContextSyncResult:
    """Summary of a sync operation."""

    def __init__(self):
        self.table_count: int = 0
        self.file_count: int = 0
        self.glossary_count: int = 0
        self.instruction_count: int = 0


class ContextSyncService:
    """Sync context assets from Typesense to the local filesystem.

    Writes files under::

        {output_dir}/{db_alias}/tables/{table_name}/columns.md
        {output_dir}/{db_alias}/tables/{table_name}/preview.md
        {output_dir}/{db_alias}/glossary/{term_key}.md
        {output_dir}/{db_alias}/instructions/{rule_key}.md

    Uses a delete-and-recreate strategy: the ``{output_dir}/{db_alias}/``
    directory is cleared before writing new files.
    """

    def __init__(self, storage):
        self.storage = storage

    def sync(
        self,
        db_connection_id: str,
        output_dir: str = "./context",
        include_preview: bool = True,
        preview_rows: int = 5,
        db_alias: str | None = None,
    ) -> ContextSyncResult:
        """Sync all context assets for a database connection to disk.

        Args:
            db_connection_id: ID of the database connection.
            output_dir: Base output directory (default ``./context``).
            include_preview: Whether to write preview.md files.
            preview_rows: Number of sample rows in preview files.
            db_alias: Override alias for directory naming. If not provided,
                the connection alias or ID is used.

        Returns:
            :class:`ContextSyncResult` with counts of written files.
        """
        from app.modules.table_description.repositories import TableDescriptionRepository
        from app.modules.context_platform.services.asset_service import ContextAssetService
        from app.modules.context_platform.models.asset import ContextAssetType, LifecycleState
        from app.modules.database_connection.repositories import DatabaseConnectionRepository

        result = ContextSyncResult()
        env = _load_jinja_env()

        # Resolve db alias
        if not db_alias:
            db_repo = DatabaseConnectionRepository(self.storage)
            db_conn = db_repo.find_by_id(db_connection_id)
            if db_conn:
                db_alias = db_conn.alias or db_connection_id
            else:
                db_alias = db_connection_id

        safe_alias = _sanitize_alias(db_alias)
        base_path = Path(output_dir) / safe_alias

        # Delete and recreate the base directory
        if base_path.exists():
            import shutil
            shutil.rmtree(base_path)
        base_path.mkdir(parents=True, exist_ok=True)

        # ------------------------------------------------------------------ #
        # Tables
        # ------------------------------------------------------------------ #
        table_repo = TableDescriptionRepository(self.storage)
        tables = table_repo.find_by({"db_connection_id": db_connection_id})

        columns_tmpl = env.get_template("columns.md.j2")
        preview_tmpl = env.get_template("preview.md.j2")

        # Build SQLDatabase only when preview is requested and tables exist
        sql_db = None
        if include_preview and tables:
            sql_db = self._get_sql_database(db_connection_id)

        for table in tables:
            result.table_count += 1
            table_dir = base_path / "tables" / table.table_name
            table_dir.mkdir(parents=True, exist_ok=True)

            # columns.md
            low_cardinality = [
                col for col in table.columns
                if col.low_cardinality and col.categories
            ]
            foreign_keys = [
                col for col in table.columns
                if col.foreign_key
            ]
            columns_content = columns_tmpl.render(
                table=table,
                low_cardinality_columns=low_cardinality,
                foreign_keys=foreign_keys,
            )
            (table_dir / "columns.md").write_text(columns_content, encoding="utf-8")
            result.file_count += 1

            # preview.md
            if include_preview:
                rows, columns = self._fetch_preview(
                    sql_db, table.db_schema, table.table_name, preview_rows
                )
                preview_content = preview_tmpl.render(
                    table_name=table.table_name,
                    rows=rows,
                    columns=columns,
                )
                (table_dir / "preview.md").write_text(preview_content, encoding="utf-8")
                result.file_count += 1

        # ------------------------------------------------------------------ #
        # Glossary & Instructions (from context platform — may not be set up)
        # ------------------------------------------------------------------ #
        try:
            asset_service = ContextAssetService(self.storage)
            glossary_assets = asset_service.list_assets(
                db_connection_id=db_connection_id,
                asset_type=ContextAssetType.GLOSSARY,
                lifecycle_state=LifecycleState.PUBLISHED,
                limit=1000,
            )

            glossary_tmpl = env.get_template("glossary.md.j2")
            glossary_dir = base_path / "glossary"
            if glossary_assets:
                glossary_dir.mkdir(parents=True, exist_ok=True)

            for asset in glossary_assets:
                result.glossary_count += 1
                content = asset.content or {}
                glossary_content = glossary_tmpl.render(
                    name=asset.name,
                    definition=content.get("definition") or asset.description or "",
                    related_tables=content.get("related_tables", []),
                    examples=content.get("examples", []),
                )
                safe_key = _sanitize_alias(asset.canonical_key)
                (glossary_dir / f"{safe_key}.md").write_text(glossary_content, encoding="utf-8")
                result.file_count += 1

            instruction_assets = asset_service.list_assets(
                db_connection_id=db_connection_id,
                asset_type=ContextAssetType.INSTRUCTION,
                lifecycle_state=LifecycleState.PUBLISHED,
                limit=1000,
            )

            instruction_tmpl = env.get_template("instruction.md.j2")
            instructions_dir = base_path / "instructions"
            if instruction_assets:
                instructions_dir.mkdir(parents=True, exist_ok=True)

            for asset in instruction_assets:
                result.instruction_count += 1
                content = asset.content or {}
                instruction_content = instruction_tmpl.render(
                    name=asset.name,
                    content=content.get("rule") or content.get("prompt") or asset.description or "",
                    conditions=content.get("conditions"),
                    priority=content.get("priority"),
                )
                safe_key = _sanitize_alias(asset.canonical_key)
                (instructions_dir / f"{safe_key}.md").write_text(instruction_content, encoding="utf-8")
                result.file_count += 1
        except Exception as exc:
            logger.warning(f"Context platform assets unavailable (skipping glossary/instructions): {exc}")

        logger.info(
            f"Context sync complete for '{safe_alias}': "
            f"{result.table_count} tables, {result.glossary_count} glossary, "
            f"{result.instruction_count} instructions, {result.file_count} files"
        )
        return result

    def _get_sql_database(self, db_connection_id: str):
        """Return a SQLDatabase instance, or None on failure."""
        try:
            from app.modules.database_connection.repositories import DatabaseConnectionRepository
            from app.modules.database_connection.services import DatabaseConnectionService
            from app.utils.sql_database.scanner import SqlAlchemyScanner

            db_repo = DatabaseConnectionRepository(self.storage)
            db_conn = db_repo.find_by_id(db_connection_id)
            if not db_conn:
                return None

            scanner = SqlAlchemyScanner()
            service = DatabaseConnectionService(scanner, self.storage)
            return service.get_sql_database(db_conn)
        except Exception as exc:
            logger.warning(f"Could not connect to database for preview: {exc}")
            return None

    def _fetch_preview(
        self,
        sql_db,
        schema: str | None,
        table_name: str,
        limit: int,
    ) -> tuple[list[dict], list[str]]:
        """Fetch sample rows from a table. Returns (rows, column_names)."""
        if sql_db is None:
            return [], []
        try:
            qualified = f'"{schema}"."{table_name}"' if schema else f'"{table_name}"'
            query = f"SELECT * FROM {qualified} LIMIT {limit}"
            _sql, meta = sql_db.run_sql(query, top_k=limit)
            rows = meta.get("result", [])
            if not rows:
                return [], []
            # Exclude BLOB/binary columns
            columns = [
                k for k in rows[0].keys()
                if not isinstance(rows[0].get(k), (bytes, bytearray))
            ]
            # Truncate values to 100 chars
            clean_rows = []
            for row in rows:
                clean_row = {}
                for col in columns:
                    val = row.get(col)
                    if val is None:
                        clean_row[col] = ""
                    else:
                        s = str(val)
                        clean_row[col] = s[:100] + "…" if len(s) > 100 else s
                clean_rows.append(clean_row)
            return clean_rows, columns
        except Exception as exc:
            logger.warning(f"Preview fetch failed for {table_name}: {exc}")
            return [], []
