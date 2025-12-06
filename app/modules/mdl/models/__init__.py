"""MDL Pydantic models for semantic layer definitions."""
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class JoinType(str, Enum):
    """Relationship join types."""

    ONE_TO_ONE = "ONE_TO_ONE"
    ONE_TO_MANY = "ONE_TO_MANY"
    MANY_TO_ONE = "MANY_TO_ONE"
    MANY_TO_MANY = "MANY_TO_MANY"


class DatePart(str, Enum):
    """Date parts for time grain."""

    YEAR = "YEAR"
    QUARTER = "QUARTER"
    MONTH = "MONTH"
    WEEK = "WEEK"
    DAY = "DAY"
    HOUR = "HOUR"
    MINUTE = "MINUTE"


class MDLColumn(BaseModel):
    """Column definition within a model."""

    name: str
    type: str
    not_null: bool = False
    is_calculated: bool = False
    expression: str | None = None
    relationship: str | None = None
    is_hidden: bool = False
    properties: dict[str, Any] | None = None


class MDLModel(BaseModel):
    """Model (table) definition in MDL."""

    name: str
    table_reference: dict[str, str] | None = None
    ref_sql: str | None = None
    columns: list[MDLColumn]
    primary_key: str | None = None
    cached: bool = False
    refresh_time: str | None = None
    properties: dict[str, Any] | None = None


class MDLRelationship(BaseModel):
    """Relationship between two models."""

    name: str
    models: list[str]
    join_type: JoinType
    condition: str
    properties: dict[str, Any] | None = None


class MDLTimeGrain(BaseModel):
    """Time grain definition for metrics."""

    name: str
    ref_column: str
    date_parts: list[DatePart]


class MDLMetric(BaseModel):
    """Business metric definition."""

    name: str
    base_object: str
    dimension: list[MDLColumn] | None = None
    measure: list[MDLColumn] | None = None
    time_grain: list[MDLTimeGrain] | None = None
    cached: bool = False
    refresh_time: str | None = None
    properties: dict[str, Any] | None = None


class MDLView(BaseModel):
    """Saved view definition."""

    name: str
    statement: str
    properties: dict[str, Any] | None = None


class MDLEnumValue(BaseModel):
    """Enum value definition."""

    name: str
    value: str | None = None
    properties: dict[str, Any] | None = None


class MDLEnumDefinition(BaseModel):
    """Enum definition."""

    name: str
    values: list[MDLEnumValue]
    properties: dict[str, Any] | None = None


class MDLManifest(BaseModel):
    """Complete MDL manifest for a semantic layer."""

    model_config = {"populate_by_name": True}

    id: str | None = None
    db_connection_id: str | None = None
    name: str | None = None
    catalog: str
    schema_name: str = Field(alias="schema")
    data_source: str | None = None
    models: list[MDLModel] = Field(default_factory=list)
    relationships: list[MDLRelationship] = Field(default_factory=list)
    metrics: list[MDLMetric] = Field(default_factory=list)
    views: list[MDLView] = Field(default_factory=list)
    enum_definitions: list[MDLEnumDefinition] = Field(default_factory=list)
    version: str | None = None
    metadata: dict[str, Any] | None = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str | None = None

    def to_dict(self) -> dict:
        """Convert manifest to dictionary for storage."""
        return {
            "id": self.id,
            "db_connection_id": self.db_connection_id,
            "name": self.name,
            "catalog": self.catalog,
            "schema": self.schema_name,
            "data_source": self.data_source,
            "models": [self._model_to_dict(m) for m in self.models],
            "relationships": [self._relationship_to_dict(r) for r in self.relationships],
            "metrics": [self._metric_to_dict(m) for m in self.metrics],
            "views": [self._view_to_dict(v) for v in self.views],
            "enum_definitions": [self._enum_def_to_dict(e) for e in self.enum_definitions],
            "version": self.version,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def _column_to_dict(self, col: MDLColumn) -> dict:
        """Convert column to dictionary."""
        return {
            "name": col.name,
            "type": col.type,
            "notNull": col.not_null,
            "isCalculated": col.is_calculated,
            "expression": col.expression,
            "relationship": col.relationship,
            "isHidden": col.is_hidden,
            "properties": col.properties,
        }

    def _model_to_dict(self, model: MDLModel) -> dict:
        """Convert model to dictionary."""
        return {
            "name": model.name,
            "tableReference": model.table_reference,
            "refSql": model.ref_sql,
            "columns": [self._column_to_dict(c) for c in model.columns],
            "primaryKey": model.primary_key,
            "cached": model.cached,
            "refreshTime": model.refresh_time,
            "properties": model.properties,
        }

    def _relationship_to_dict(self, rel: MDLRelationship) -> dict:
        """Convert relationship to dictionary."""
        return {
            "name": rel.name,
            "models": rel.models,
            "joinType": rel.join_type.value,
            "condition": rel.condition,
            "properties": rel.properties,
        }

    def _time_grain_to_dict(self, tg: MDLTimeGrain) -> dict:
        """Convert time grain to dictionary."""
        return {
            "name": tg.name,
            "refColumn": tg.ref_column,
            "dateParts": [dp.value for dp in tg.date_parts],
        }

    def _metric_to_dict(self, metric: MDLMetric) -> dict:
        """Convert metric to dictionary."""
        return {
            "name": metric.name,
            "baseObject": metric.base_object,
            "dimension": [self._column_to_dict(c) for c in metric.dimension] if metric.dimension else None,
            "measure": [self._column_to_dict(c) for c in metric.measure] if metric.measure else None,
            "timeGrain": [self._time_grain_to_dict(t) for t in metric.time_grain] if metric.time_grain else None,
            "cached": metric.cached,
            "refreshTime": metric.refresh_time,
            "properties": metric.properties,
        }

    def _view_to_dict(self, view: MDLView) -> dict:
        """Convert view to dictionary."""
        return {
            "name": view.name,
            "statement": view.statement,
            "properties": view.properties,
        }

    def _enum_def_to_dict(self, enum_def: MDLEnumDefinition) -> dict:
        """Convert enum definition to dictionary."""
        return {
            "name": enum_def.name,
            "values": [{"name": v.name, "value": v.value, "properties": v.properties} for v in enum_def.values],
            "properties": enum_def.properties,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MDLManifest":
        """Create manifest from dictionary."""
        models = []
        for m in data.get("models", []):
            columns = [
                MDLColumn(
                    name=c["name"],
                    type=c["type"],
                    not_null=c.get("notNull", False),
                    is_calculated=c.get("isCalculated", False),
                    expression=c.get("expression"),
                    relationship=c.get("relationship"),
                    is_hidden=c.get("isHidden", False),
                    properties=c.get("properties"),
                )
                for c in m.get("columns", [])
            ]
            models.append(
                MDLModel(
                    name=m["name"],
                    table_reference=m.get("tableReference"),
                    ref_sql=m.get("refSql"),
                    columns=columns,
                    primary_key=m.get("primaryKey"),
                    cached=m.get("cached", False),
                    refresh_time=m.get("refreshTime"),
                    properties=m.get("properties"),
                )
            )

        relationships = [
            MDLRelationship(
                name=r["name"],
                models=r["models"],
                join_type=JoinType(r["joinType"]),
                condition=r["condition"],
                properties=r.get("properties"),
            )
            for r in data.get("relationships", [])
        ]

        metrics = []
        for m in data.get("metrics", []):
            dimension = None
            if m.get("dimension"):
                dimension = [
                    MDLColumn(
                        name=c["name"],
                        type=c["type"],
                        not_null=c.get("notNull", False),
                        is_calculated=c.get("isCalculated", False),
                        expression=c.get("expression"),
                        properties=c.get("properties"),
                    )
                    for c in m["dimension"]
                ]
            measure = None
            if m.get("measure"):
                measure = [
                    MDLColumn(
                        name=c["name"],
                        type=c["type"],
                        not_null=c.get("notNull", False),
                        is_calculated=c.get("isCalculated", False),
                        expression=c.get("expression"),
                        properties=c.get("properties"),
                    )
                    for c in m["measure"]
                ]
            time_grain = None
            if m.get("timeGrain"):
                time_grain = [
                    MDLTimeGrain(
                        name=t["name"],
                        ref_column=t["refColumn"],
                        date_parts=[DatePart(dp) for dp in t["dateParts"]],
                    )
                    for t in m["timeGrain"]
                ]
            metrics.append(
                MDLMetric(
                    name=m["name"],
                    base_object=m["baseObject"],
                    dimension=dimension,
                    measure=measure,
                    time_grain=time_grain,
                    cached=m.get("cached", False),
                    refresh_time=m.get("refreshTime"),
                    properties=m.get("properties"),
                )
            )

        views = [
            MDLView(
                name=v["name"],
                statement=v["statement"],
                properties=v.get("properties"),
            )
            for v in data.get("views", [])
        ]

        enum_definitions = []
        for e in data.get("enumDefinitions", data.get("enum_definitions", [])):
            values = [
                MDLEnumValue(
                    name=v["name"],
                    value=v.get("value"),
                    properties=v.get("properties"),
                )
                for v in e.get("values", [])
            ]
            enum_definitions.append(
                MDLEnumDefinition(
                    name=e["name"],
                    values=values,
                    properties=e.get("properties"),
                )
            )

        return cls(
            id=data.get("id"),
            db_connection_id=data.get("db_connection_id"),
            name=data.get("name"),
            catalog=data["catalog"],
            schema_name=data["schema"],
            data_source=data.get("data_source", data.get("dataSource")),
            models=models,
            relationships=relationships,
            metrics=metrics,
            views=views,
            enum_definitions=enum_definitions,
            version=data.get("version"),
            metadata=data.get("metadata"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at"),
        )

    def to_mdl_json(self) -> dict:
        """Export to WrenAI-compatible MDL JSON format."""
        result = {
            "catalog": self.catalog,
            "schema": self.schema_name,
        }

        if self.data_source:
            result["dataSource"] = self.data_source

        if self.models:
            result["models"] = []
            for m in self.models:
                model_dict = {
                    "name": m.name,
                    "columns": [
                        {
                            k: v
                            for k, v in {
                                "name": c.name,
                                "type": c.type,
                                "notNull": c.not_null if c.not_null else None,
                                "isCalculated": c.is_calculated if c.is_calculated else None,
                                "expression": c.expression,
                                "relationship": c.relationship,
                                "isHidden": c.is_hidden if c.is_hidden else None,
                                "properties": c.properties,
                            }.items()
                            if v is not None
                        }
                        for c in m.columns
                    ],
                }
                if m.table_reference:
                    model_dict["tableReference"] = m.table_reference
                if m.ref_sql:
                    model_dict["refSql"] = m.ref_sql
                if m.primary_key:
                    model_dict["primaryKey"] = m.primary_key
                if m.cached:
                    model_dict["cached"] = m.cached
                if m.refresh_time:
                    model_dict["refreshTime"] = m.refresh_time
                if m.properties:
                    model_dict["properties"] = m.properties
                result["models"].append(model_dict)

        if self.relationships:
            result["relationships"] = [
                {
                    "name": r.name,
                    "models": r.models,
                    "joinType": r.join_type.value,
                    "condition": r.condition,
                    **({"properties": r.properties} if r.properties else {}),
                }
                for r in self.relationships
            ]

        if self.metrics:
            result["metrics"] = [self._metric_to_dict(m) for m in self.metrics]

        if self.views:
            result["views"] = [self._view_to_dict(v) for v in self.views]

        if self.enum_definitions:
            result["enumDefinitions"] = [self._enum_def_to_dict(e) for e in self.enum_definitions]

        return result
