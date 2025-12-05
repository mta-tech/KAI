"""Analysis result models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.modules.sql_generation.models import LLMConfig


class Insight(BaseModel):
    """A single insight extracted from query results."""

    title: str
    description: str
    significance: str  # "high", "medium", "low"
    data_points: list | None = None  # Can be list of dicts or strings


class ChartRecommendation(BaseModel):
    """A chart/visualization recommendation for the data."""

    chart_type: str  # "bar", "line", "pie", "scatter", "table", etc.
    title: str
    description: str
    x_axis: str | None = None
    y_axis: str | None = None
    columns: list[str] | None = None  # For table type
    rationale: str | None = None


class AnalysisResult(BaseModel):
    """Comprehensive analysis result from SQL query execution."""

    id: str | None = None
    sql_generation_id: str
    prompt_id: str | None = None
    summary: str = ""  # Natural language summary of results
    insights: list[Insight] = Field(default_factory=list)
    chart_recommendations: list[ChartRecommendation] = Field(default_factory=list)
    row_count: int = 0
    column_count: int = 0
    llm_config: LLMConfig | None = None
    input_tokens_used: int = 0
    output_tokens_used: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    completed_at: str | None = None
    error: str | None = None
    metadata: dict | None = None

