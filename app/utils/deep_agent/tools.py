"""Tool registry for Deep Agent SQL generation."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List

from app.agents.types import ToolSpec
from app.modules.table_description.models import TableDescription
from app.utils.sql_database.sql_database import SQLDatabase
from app.utils.sql_tools.column_entity_checker import ColumnEntityChecker
from app.utils.sql_tools.get_few_shot_examples import GetFewShotExamples
from app.utils.sql_tools.info_relevant_columns import InfoRelevantColumns
from app.utils.sql_tools.query_sql_database import QuerySQLDataBaseTool
from app.utils.sql_tools.schema_sql_database import SchemaSQLDatabaseTool
from app.utils.sql_tools.tables_sql_database import TablesSQLDatabaseTool
from app.utils.sql_tools.system_time import SystemTime
from app.utils.sql_tools.alias_lookup import AliasLookupTool
from app.utils.deep_agent.result_writer import SqlResultWriterTool
from app.utils.sql_tools.mdl_semantic_lookup import (
    MDLSemanticLookupTool,
    create_mdl_semantic_tool,
)

# Import MDLManifest with TYPE_CHECKING to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.modules.mdl.models import MDLManifest


logger = logging.getLogger(__name__)


@dataclass
class KaiToolContext:
    """Container for objects required to build tool instances."""

    database: SQLDatabase
    db_scan: list[TableDescription] = field(default_factory=list)
    embedding: object | None = None
    context: list[dict] | None = None
    few_shot_examples: list[dict] | None = None
    business_metrics: list[dict] | None = None
    aliases: list[dict] | None = None
    is_multiple_schema: bool = False
    top_k: int | None = None
    tenant_id: str | None = None
    sql_generation_id: str | None = None
    result_dir: str | None = None
    mdl_manifest: "MDLManifest | None" = None  # Semantic layer manifest


def build_tool_specs(ctx: KaiToolContext) -> List[ToolSpec]:
    """Return the default tool specs for a Deep Agent session."""

    tool_specs: List[ToolSpec] = []

    def build_sql_db_query() -> QuerySQLDataBaseTool:
        return QuerySQLDataBaseTool(
            db=ctx.database,
            context=ctx.context,
        )

    class _NullEmbedding:
        def embed_query(self, _: str):  # pragma: no cover - stub fallback
            return [0.0]

        def embed_documents(self, docs):  # pragma: no cover - stub fallback
            return [[0.0] for _ in docs]

    def build_tables_tool() -> TablesSQLDatabaseTool:
        embedding = ctx.embedding or _NullEmbedding()
        if ctx.embedding is None:
            logger.warning("Embedding model missing for tables tool; using stub embedding")
        return TablesSQLDatabaseTool(
            db_scan=ctx.db_scan,
            embedding=embedding,
            few_shot_examples=ctx.few_shot_examples or [],
        )

    def build_schema_tool() -> SchemaSQLDatabaseTool:
        return SchemaSQLDatabaseTool(db_scan=ctx.db_scan)

    def build_columns_tool() -> InfoRelevantColumns:
        return InfoRelevantColumns(db_scan=ctx.db_scan)

    def build_column_entity_checker() -> ColumnEntityChecker:
        return ColumnEntityChecker(
            db=ctx.database,
            context=ctx.context,
            db_scan=ctx.db_scan,
            is_multiple_schema=ctx.is_multiple_schema,
        )

    def build_fewshot_tool() -> GetFewShotExamples:
        return GetFewShotExamples(
            few_shot_examples=ctx.few_shot_examples or [],
            business_metrics=ctx.business_metrics or [],
        )

    def build_system_time() -> SystemTime:
        return SystemTime()

    def build_alias_tool() -> AliasLookupTool:
        return AliasLookupTool(aliases=ctx.aliases or [])

    def build_result_writer() -> SqlResultWriterTool:
        return SqlResultWriterTool(
            result_dir=ctx.result_dir or str(Path("app/data/deep_agent")),
            tenant_id=ctx.tenant_id or "default",
            sql_generation_id=ctx.sql_generation_id or "session",
        )

    def _register(name: str, builder: Callable[[], object], description: str):
        tool_specs.append(ToolSpec(name=name, build=builder, description=description))

    _register(
        "sql_db_query",
        build_sql_db_query,
        "Executes read-only SQL via the existing SqlDbQuery tool.",
    )
    _register(
        "tables_with_scores",
        build_tables_tool,
        "Retrieve relevant tables and their relevance scores for a question.",
    )
    _register(
        "table_schema",
        build_schema_tool,
        "Fetch schemas (columns + descriptions) for selected tables.",
    )
    _register(
        "column_details",
        build_columns_tool,
        "Return detailed column info including descriptions and examples.",
    )
    _register(
        "column_entity_checker",
        build_column_entity_checker,
        "Lookup example values in a column similar to a target entity.",
    )
    _register(
        "fewshot_examples",
        build_fewshot_tool,
        "Return historical question/SQL pairs and business metric formulas.",
    )
    _register(
        "system_time",
        build_system_time,
        "Provide the current date/time for time-bound questions.",
    )
    if ctx.aliases:
        _register(
            "alias_lookup",
            build_alias_tool,
            "Return canonical names for known aliases referenced in the prompt.",
        )
    _register(
        "sql_result_writer",
        build_result_writer,
        "Persist result rows to tenant-scoped storage for later download.",
    )

    # MDL Semantic Layer tool - provides business term resolution and join paths
    if ctx.mdl_manifest is not None:
        def build_mdl_tool() -> MDLSemanticLookupTool:
            return create_mdl_semantic_tool(ctx.mdl_manifest)

        _register(
            "mdl_semantic_lookup",
            build_mdl_tool,
            "Look up semantic layer definitions: business terms, metrics, relationships, and join paths.",
        )
        logger.info(
            f"MDL semantic tool enabled with {len(ctx.mdl_manifest.models)} models, "
            f"{len(ctx.mdl_manifest.relationships)} relationships"
        )

    return tool_specs
