"""Analysis suggestion models."""
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SuggestionCategory(str, Enum):
    """Categories for analysis suggestions."""

    TREND = "trend"  # Time-based analysis
    AGGREGATION = "aggregation"  # SUM, COUNT, AVG type questions
    COMPARISON = "comparison"  # Compare across categories
    RELATIONSHIP = "relationship"  # Join-based analysis


class AnalysisSuggestion(BaseModel):
    """A single analysis suggestion."""

    question: str
    category: SuggestionCategory
    rationale: str
    tables_involved: list[str] = Field(default_factory=list)
    columns_involved: list[str] = Field(default_factory=list)
    complexity: str = "simple"  # "simple", "moderate", "complex"


class AnalysisSuggestionsResponse(BaseModel):
    """Response containing all suggestions for a database connection."""

    db_connection_id: str
    suggestions: list[AnalysisSuggestion] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    mdl_available: bool = True
    table_count: int = 0
    relationship_count: int = 0


__all__ = [
    "SuggestionCategory",
    "AnalysisSuggestion",
    "AnalysisSuggestionsResponse",
]
