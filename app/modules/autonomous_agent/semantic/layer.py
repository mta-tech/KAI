"""Semantic layer management for business-friendly SQL generation."""
import json
from typing import Any, Literal

from app.modules.autonomous_agent.semantic.models import (
    SemanticModel,
    Dimension,
    Metric,
    Relationship,
)


class SemanticLayer:
    """Manages semantic models and translates business terms to SQL.

    The semantic layer provides:
    1. Business-friendly names for database columns
    2. Pre-defined aggregation logic for metrics
    3. Automatic joins via relationship definitions
    4. Synonym support for natural language understanding
    """

    def __init__(self, model: SemanticModel):
        self.model = model
        self._dimension_map = {d.name.lower(): d for d in model.dimensions}
        self._metric_map = {m.name.lower(): m for m in model.metrics}
        self._synonym_map = self._build_synonym_map()

    def _build_synonym_map(self) -> dict[str, str]:
        """Build mapping from synonyms to canonical names."""
        synonym_map = {}
        for dim in self.model.dimensions:
            for syn in dim.synonyms:
                synonym_map[syn.lower()] = dim.name
        for metric in self.model.metrics:
            for syn in metric.synonyms:
                synonym_map[syn.lower()] = metric.name
        return synonym_map

    def resolve_term(self, term: str) -> tuple[str, Literal["dimension", "metric"] | None]:
        """Resolve a business term to its canonical name and type."""
        term_lower = term.lower()

        # Check exact match first
        if term_lower in self._dimension_map:
            return term_lower, "dimension"
        if term_lower in self._metric_map:
            return term_lower, "metric"

        # Check synonyms
        if term_lower in self._synonym_map:
            canonical = self._synonym_map[term_lower].lower()
            if canonical in self._dimension_map:
                return canonical, "dimension"
            if canonical in self._metric_map:
                return canonical, "metric"

        return term, None

    def get_dimension(self, name: str) -> Dimension | None:
        """Get dimension by name or synonym."""
        resolved, term_type = self.resolve_term(name)
        if term_type == "dimension":
            return self._dimension_map.get(resolved)
        return None

    def get_metric(self, name: str) -> Metric | None:
        """Get metric by name or synonym."""
        resolved, term_type = self.resolve_term(name)
        if term_type == "metric":
            return self._metric_map.get(resolved)
        return None

    def build_metric_sql(self, metric: Metric) -> str:
        """Generate SQL expression for a metric."""
        col = f"{metric.source_table}.{metric.source_column}"
        agg = metric.aggregation.upper()

        if agg == "COUNT_DISTINCT":
            return f"COUNT(DISTINCT {col})"
        return f"{agg}({col})"

    def build_dimension_sql(self, dimension: Dimension) -> str:
        """Generate SQL expression for a dimension."""
        return f"{dimension.source_table}.{dimension.source_column}"

    def get_join_path(self, from_table: str, to_table: str) -> list[Relationship]:
        """Find join path between two tables using BFS."""
        if from_table == to_table:
            return []

        # Build adjacency list
        adj: dict[str, list[tuple[str, Relationship]]] = {}
        for rel in self.model.relationships:
            if rel.from_table not in adj:
                adj[rel.from_table] = []
            if rel.to_table not in adj:
                adj[rel.to_table] = []
            adj[rel.from_table].append((rel.to_table, rel))
            adj[rel.to_table].append((rel.from_table, rel))

        # BFS
        from collections import deque
        queue = deque([(from_table, [])])
        visited = {from_table}

        while queue:
            current, path = queue.popleft()
            if current == to_table:
                return path
            for neighbor, rel in adj.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [rel]))

        return []  # No path found

    def build_join_sql(self, relationships: list[Relationship]) -> str:
        """Generate JOIN clauses from relationships."""
        if not relationships:
            return ""

        joins = []
        for rel in relationships:
            join_type = "LEFT JOIN"  # Default to LEFT JOIN for flexibility
            joins.append(
                f"{join_type} {rel.to_table} ON "
                f"{rel.from_table}.{rel.from_column} = {rel.to_table}.{rel.to_column}"
            )
        return "\n".join(joins)

    def to_context_string(self) -> str:
        """Generate context string for LLM prompts."""
        lines = [f"# Semantic Model: {self.model.name}", ""]

        if self.model.dimensions:
            lines.append("## Dimensions (for grouping/filtering):")
            for dim in self.model.dimensions:
                synonyms = f" (also: {', '.join(dim.synonyms)})" if dim.synonyms else ""
                lines.append(f"- {dim.display_name or dim.name}: {dim.description}{synonyms}")
            lines.append("")

        if self.model.metrics:
            lines.append("## Metrics (for aggregation):")
            for metric in self.model.metrics:
                synonyms = f" (also: {', '.join(metric.synonyms)})" if metric.synonyms else ""
                lines.append(
                    f"- {metric.display_name or metric.name}: {metric.description} "
                    f"[{metric.aggregation}]{synonyms}"
                )
            lines.append("")

        return "\n".join(lines)


def create_semantic_tool(semantic_layer: SemanticLayer):
    """Create tool for querying semantic model."""

    def query_semantic_model(question: str) -> str:
        """Look up business terms in the semantic model.

        Args:
            question: Natural language question or business term

        Returns:
            JSON with matching dimensions, metrics, and SQL expressions
        """
        words = question.lower().split()
        results = {
            "dimensions": [],
            "metrics": [],
            "unresolved": [],
        }

        for word in words:
            resolved, term_type = semantic_layer.resolve_term(word)
            if term_type == "dimension":
                dim = semantic_layer.get_dimension(resolved)
                if dim:
                    results["dimensions"].append({
                        "name": dim.name,
                        "display_name": dim.display_name,
                        "sql": semantic_layer.build_dimension_sql(dim),
                        "description": dim.description,
                    })
            elif term_type == "metric":
                metric = semantic_layer.get_metric(resolved)
                if metric:
                    results["metrics"].append({
                        "name": metric.name,
                        "display_name": metric.display_name,
                        "sql": semantic_layer.build_metric_sql(metric),
                        "aggregation": metric.aggregation,
                        "description": metric.description,
                    })

        return json.dumps(results, indent=2)

    return query_semantic_model
