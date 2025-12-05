"""Semantic layer models for business-friendly data representation."""
from dataclasses import dataclass, field
from typing import Literal, Any


@dataclass
class Dimension:
    """A categorical attribute for grouping and filtering."""
    name: str
    source_column: str
    source_table: str
    description: str
    data_type: Literal["string", "date", "datetime", "boolean"]
    display_name: str | None = None
    synonyms: list[str] = field(default_factory=list)  # Alternative names users might use


@dataclass
class Metric:
    """A quantitative measure with aggregation logic."""
    name: str
    source_column: str
    source_table: str
    description: str
    aggregation: Literal["sum", "avg", "count", "min", "max", "count_distinct"]
    display_name: str | None = None
    format: str = "{value}"  # e.g., "${value:,.2f}" for currency
    synonyms: list[str] = field(default_factory=list)


@dataclass
class Relationship:
    """Join relationship between tables."""
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relationship_type: Literal["one_to_one", "one_to_many", "many_to_one", "many_to_many"]


@dataclass
class SemanticModel:
    """Complete semantic model for a database connection."""
    id: str
    name: str
    description: str
    db_connection_id: str
    dimensions: list[Dimension] = field(default_factory=list)
    metrics: list[Metric] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
