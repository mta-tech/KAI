from dataclasses import dataclass, field
from typing import Literal, Any
from datetime import datetime


@dataclass
class AgentSession:
    """Persistent session for autonomous agent."""
    id: str
    db_connection_id: str
    status: Literal["active", "paused", "running", "completed", "failed"]
    mode: Literal["analysis", "query", "script", "full_autonomy"] = "full_autonomy"
    recursion_limit: int = 100
    title: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict | None = None


@dataclass
class AgentTask:
    """Task submitted to the autonomous agent."""
    id: str
    session_id: str  # Links to AgentSession for resumable execution
    prompt: str
    db_connection_id: str
    mode: Literal["analysis", "query", "script", "full_autonomy"] = "full_autonomy"
    context: dict | None = None
    metadata: dict | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ChartSpec:
    """Specification for generated chart."""
    chart_type: Literal["line", "bar", "pie", "scatter", "area", "heatmap"]
    title: str
    x_column: str
    y_column: str | list[str]
    data: list[dict]
    color_column: str | None = None
    config: dict = field(default_factory=dict)  # Additional chart config


@dataclass
class Insight:
    """AI-generated insight from data."""
    category: Literal["trend", "anomaly", "comparison", "summary", "recommendation"]
    title: str
    description: str
    importance: Literal["high", "medium", "low"]
    supporting_data: dict | None = None


@dataclass
class SuggestedQuestion:
    """Follow-up question suggestion."""
    question: str
    category: Literal["drill_down", "compare", "trend", "filter", "aggregate"]
    rationale: str  # Why this question is relevant


@dataclass
class AgentResult:
    """Result from autonomous agent execution."""
    task_id: str
    status: Literal["completed", "failed", "partial"]
    final_answer: str
    # GenBI outputs
    charts: list[ChartSpec] = field(default_factory=list)
    insights: list[Insight] = field(default_factory=list)
    suggested_questions: list[SuggestedQuestion] = field(default_factory=list)
    # Execution details
    sql_queries: list[str] = field(default_factory=list)
    artifacts: list[dict] = field(default_factory=list)
    execution_time_ms: int = 0
    error: str | None = None
