"""MDL Semantic Lookup tool for autonomous agent."""

from typing import Any, Optional

from langchain_core.tools import BaseTool
from pydantic import Field

from app.modules.mdl.models import MDLManifest, JoinType


class MDLSemanticLookupTool(BaseTool):
    """
    Tool for looking up semantic layer definitions from MDL manifest.

    This tool helps the agent understand:
    - Business-friendly names for tables and columns
    - Pre-defined metrics and their SQL expressions
    - Relationships between tables (join paths)
    - Calculated columns and their expressions
    """

    name: str = "mdl_semantic_lookup"
    description: str = """Look up semantic layer definitions for business terms.

Use this tool to:
1. Find the correct table/column when user uses business terms
2. Get pre-defined metric formulas (e.g., "revenue", "conversion rate")
3. Discover join paths between tables
4. Find calculated column expressions

Input: A business term or question about the data model
Output: Relevant semantic definitions including table names, column mappings, and SQL expressions"""

    mdl_manifest: MDLManifest = Field(description="MDL manifest with semantic definitions")

    class Config:
        arbitrary_types_allowed = True

    def _run(self, query: str) -> str:
        """Look up semantic definitions matching the query."""
        query_lower = query.lower()
        results = []

        # Search models (tables)
        matching_models = self._search_models(query_lower)
        if matching_models:
            results.append("## Matching Tables/Models:\n" + matching_models)

        # Search relationships (joins)
        matching_relationships = self._search_relationships(query_lower)
        if matching_relationships:
            results.append("## Available Joins:\n" + matching_relationships)

        # Search metrics
        matching_metrics = self._search_metrics(query_lower)
        if matching_metrics:
            results.append("## Business Metrics:\n" + matching_metrics)

        # Search calculated columns
        calculated_cols = self._search_calculated_columns(query_lower)
        if calculated_cols:
            results.append("## Calculated Columns:\n" + calculated_cols)

        if not results:
            return f"No semantic definitions found for '{query}'. Try different terms or use table_schema tool."

        return "\n\n".join(results)

    def _search_models(self, query: str) -> str:
        """Search for models matching the query."""
        matches = []

        for model in self.mdl_manifest.models:
            # Check model name
            if query in model.name.lower():
                matches.append(self._format_model(model))
                continue

            # Check model description
            if model.properties and model.properties.get("description"):
                if query in model.properties["description"].lower():
                    matches.append(self._format_model(model))
                    continue

            # Check column names and descriptions
            for col in model.columns:
                if query in col.name.lower():
                    matches.append(self._format_model(model))
                    break
                if col.properties and col.properties.get("description"):
                    if query in col.properties["description"].lower():
                        matches.append(self._format_model(model))
                        break

        return "\n".join(matches) if matches else ""

    def _format_model(self, model) -> str:
        """Format a model for display."""
        desc = ""
        if model.properties and model.properties.get("description"):
            desc = f" - {model.properties['description']}"

        cols = []
        for col in model.columns[:10]:  # Limit columns shown
            col_desc = ""
            if col.properties and col.properties.get("description"):
                col_desc = f" ({col.properties['description']})"
            calc = " [CALCULATED]" if col.is_calculated else ""
            cols.append(f"  - {col.name}: {col.type}{calc}{col_desc}")

        pk = f", PK: {model.primary_key}" if model.primary_key else ""

        return f"**{model.name}**{desc}{pk}\nColumns:\n" + "\n".join(cols)

    def _search_relationships(self, query: str) -> str:
        """Search for relationships matching the query."""
        matches = []

        for rel in self.mdl_manifest.relationships:
            # Check if query matches any model in relationship
            if any(query in m.lower() for m in rel.models):
                matches.append(self._format_relationship(rel))
            elif query in rel.name.lower():
                matches.append(self._format_relationship(rel))

        return "\n".join(matches) if matches else ""

    def _format_relationship(self, rel) -> str:
        """Format a relationship for display."""
        join_type_map = {
            JoinType.ONE_TO_ONE: "1:1",
            JoinType.ONE_TO_MANY: "1:N",
            JoinType.MANY_TO_ONE: "N:1",
            JoinType.MANY_TO_MANY: "N:N",
        }
        jt = join_type_map.get(rel.join_type, rel.join_type.value)
        return f"**{rel.name}**: {rel.models[0]} {jt} {rel.models[1]}\n  JOIN: {rel.condition}"

    def _search_metrics(self, query: str) -> str:
        """Search for metrics matching the query."""
        matches = []

        for metric in self.mdl_manifest.metrics:
            if query in metric.name.lower():
                matches.append(self._format_metric(metric))
            elif metric.properties and metric.properties.get("description"):
                if query in metric.properties["description"].lower():
                    matches.append(self._format_metric(metric))

        return "\n".join(matches) if matches else ""

    def _format_metric(self, metric) -> str:
        """Format a metric for display."""
        desc = ""
        if metric.properties and metric.properties.get("description"):
            desc = f" - {metric.properties['description']}"

        parts = [f"**{metric.name}**{desc}", f"  Base: {metric.base_object}"]

        if metric.dimension:
            dims = [d.name for d in metric.dimension]
            parts.append(f"  Dimensions: {', '.join(dims)}")

        if metric.measure:
            for m in metric.measure:
                expr = m.expression or m.name
                parts.append(f"  Measure: {m.name} = {expr}")

        if metric.time_grain:
            for tg in metric.time_grain:
                parts.append(f"  Time Grain: {tg.name} on {tg.ref_column}")

        return "\n".join(parts)

    def _search_calculated_columns(self, query: str) -> str:
        """Search for calculated columns matching the query."""
        matches = []

        for model in self.mdl_manifest.models:
            for col in model.columns:
                if col.is_calculated and col.expression:
                    if query in col.name.lower() or (
                        col.properties and
                        col.properties.get("description") and
                        query in col.properties["description"].lower()
                    ):
                        matches.append(
                            f"**{model.name}.{col.name}**: {col.expression}"
                        )

        return "\n".join(matches) if matches else ""

    async def _arun(self, query: str) -> str:
        """Async version - delegates to sync."""
        return self._run(query)


def create_mdl_semantic_tool(mdl_manifest: MDLManifest) -> MDLSemanticLookupTool:
    """
    Create an MDL semantic lookup tool instance.

    Args:
        mdl_manifest: The MDL manifest containing semantic definitions

    Returns:
        Configured MDLSemanticLookupTool instance
    """
    return MDLSemanticLookupTool(mdl_manifest=mdl_manifest)


def get_mdl_context_prompt(mdl_manifest: MDLManifest) -> str:
    """
    Generate a context prompt describing the MDL semantic layer.

    This can be added to the agent's system prompt to provide
    awareness of the semantic layer without tool calls.

    Args:
        mdl_manifest: The MDL manifest

    Returns:
        Formatted string for system prompt injection
    """
    lines = [
        "## Semantic Layer (MDL) Context",
        "",
        "This database has a semantic layer defined. Use business-friendly names when possible.",
        "",
    ]

    # Models summary
    if mdl_manifest.models:
        lines.append("### Available Tables:")
        for model in mdl_manifest.models:
            desc = ""
            if model.properties and model.properties.get("description"):
                desc = f" - {model.properties['description']}"
            lines.append(f"- **{model.name}**{desc}")
        lines.append("")

    # Relationships summary
    if mdl_manifest.relationships:
        lines.append("### Table Relationships (use these for JOINs):")
        for rel in mdl_manifest.relationships:
            lines.append(f"- {rel.models[0]} → {rel.models[1]}: `{rel.condition}`")
        lines.append("")

    # Metrics summary
    if mdl_manifest.metrics:
        lines.append("### Business Metrics (use these formulas):")
        for metric in mdl_manifest.metrics:
            if metric.measure:
                for m in metric.measure:
                    if m.expression:
                        lines.append(f"- **{metric.name}.{m.name}**: `{m.expression}`")
        lines.append("")

    return "\n".join(lines)
