"""Dashboard models for BI dashboard generation."""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class WidgetType(str, Enum):
    """Types of dashboard widgets."""

    CHART = "chart"  # Visualizations (line, bar, pie, etc.)
    KPI = "kpi"  # Single metric with comparison
    TABLE = "table"  # Data table with sorting/filtering
    TEXT = "text"  # Markdown text block
    FILTER = "filter"  # Interactive filter control


class WidgetSize(str, Enum):
    """Widget size presets for grid layout."""

    SMALL = "small"  # 3 columns (1/4 width)
    MEDIUM = "medium"  # 4 columns (1/3 width)
    LARGE = "large"  # 6 columns (1/2 width)
    WIDE = "wide"  # 8 columns (2/3 width)
    TALL = "tall"  # 4 columns, 2 rows
    FULL = "full"  # 12 columns (full width)


class ChartType(str, Enum):
    """Supported chart types."""

    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    PIE = "pie"
    DONUT = "donut"
    AREA = "area"
    HEATMAP = "heatmap"
    HISTOGRAM = "histogram"
    BOX = "box"
    TREEMAP = "treemap"
    FUNNEL = "funnel"


class AggregationType(str, Enum):
    """Aggregation functions for metrics."""

    SUM = "sum"
    AVG = "avg"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    DISTINCT_COUNT = "distinct_count"


class ChartWidgetConfig(BaseModel):
    """Configuration for chart widgets."""

    chart_type: ChartType = ChartType.BAR
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    color_column: Optional[str] = None
    size_column: Optional[str] = None
    aggregation: Optional[AggregationType] = None
    sort_by: Optional[str] = None
    limit: Optional[int] = None


class KPIWidgetConfig(BaseModel):
    """Configuration for KPI widgets."""

    metric_column: str
    aggregation: AggregationType = AggregationType.SUM
    comparison_period: Optional[str] = None  # "previous_period", "year_ago"
    format: str = "number"  # number, currency, percentage
    prefix: Optional[str] = None  # e.g., "$"
    suffix: Optional[str] = None  # e.g., "%"
    decimals: int = 0


class TableWidgetConfig(BaseModel):
    """Configuration for table widgets."""

    columns: list[str] = Field(default_factory=list)
    sortable: bool = True
    page_size: int = 10
    show_row_numbers: bool = False


class FilterWidgetConfig(BaseModel):
    """Configuration for filter widgets."""

    filter_column: str
    filter_type: str = "dropdown"  # dropdown, date_range, slider
    default_value: Optional[Any] = None
    multi_select: bool = False


class TextWidgetConfig(BaseModel):
    """Configuration for text widgets."""

    content: str = ""
    markdown: bool = True


class Widget(BaseModel):
    """Dashboard widget definition."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    widget_type: WidgetType
    size: WidgetSize = WidgetSize.MEDIUM

    # Data source
    query: Optional[str] = None  # SQL query
    query_description: Optional[str] = None  # NL description for query generation
    data_source: Optional[str] = None  # Reference to MDL metric

    # Type-specific config
    chart_config: Optional[ChartWidgetConfig] = None
    kpi_config: Optional[KPIWidgetConfig] = None
    table_config: Optional[TableWidgetConfig] = None
    filter_config: Optional[FilterWidgetConfig] = None
    text_config: Optional[TextWidgetConfig] = None

    # Positioning (grid coordinates)
    row: int = 0
    col: int = 0
    row_span: int = 1
    col_span: int = 4  # Default to medium width

    def get_col_span(self) -> int:
        """Get column span based on size."""
        size_map = {
            WidgetSize.SMALL: 3,
            WidgetSize.MEDIUM: 4,
            WidgetSize.LARGE: 6,
            WidgetSize.WIDE: 8,
            WidgetSize.TALL: 4,
            WidgetSize.FULL: 12,
        }
        return size_map.get(self.size, 4)

    def get_row_span(self) -> int:
        """Get row span based on size."""
        if self.size == WidgetSize.TALL:
            return 2
        return 1


class DashboardLayout(BaseModel):
    """Dashboard layout configuration."""

    columns: int = 12  # 12-column grid (like Bootstrap)
    row_height: int = 300  # pixels per row unit
    gap: int = 16  # gap between widgets in pixels
    widgets: list[Widget] = Field(default_factory=list)


class DashboardTheme(BaseModel):
    """Dashboard theme configuration."""

    name: str = "default"
    background: str = "#f8fafc"
    card_background: str = "#ffffff"
    text_color: str = "#1e293b"
    primary_color: str = "#3b82f6"
    accent_color: str = "#10b981"
    font_family: str = "Inter, system-ui, sans-serif"


class Dashboard(BaseModel):
    """Complete dashboard definition."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    db_connection_id: str

    # Layout
    layout: DashboardLayout = Field(default_factory=DashboardLayout)

    # Global filters
    filters: list[Widget] = Field(default_factory=list)

    # Styling
    theme: str = "default"

    # Behavior
    refresh_interval: Optional[int] = None  # seconds, None = no auto-refresh

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Sharing
    is_public: bool = False
    share_token: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        data = self.model_dump()
        data["created_at"] = int(self.created_at.timestamp())
        data["updated_at"] = int(self.updated_at.timestamp())
        data["layout_json"] = self.layout.model_dump_json()
        data["filters_json"] = [f.model_dump() for f in self.filters]
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Dashboard":
        """Create from dictionary."""
        if "created_at" in data and isinstance(data["created_at"], (int, float)):
            data["created_at"] = datetime.fromtimestamp(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], (int, float)):
            data["updated_at"] = datetime.fromtimestamp(data["updated_at"])
        if "layout_json" in data:
            import json

            layout_data = json.loads(data["layout_json"])
            data["layout"] = DashboardLayout(**layout_data)
            del data["layout_json"]
        if "filters_json" in data:
            data["filters"] = [Widget(**f) for f in data["filters_json"]]
            del data["filters_json"]
        return cls(**data)


class WidgetResult(BaseModel):
    """Result of executing a widget."""

    widget_id: str
    status: str = "pending"  # pending, running, completed, failed
    error: Optional[str] = None

    # Data
    data: Optional[list[dict]] = None
    row_count: int = 0

    # Rendered output
    html: Optional[str] = None
    plotly_json: Optional[dict] = None

    # KPI specific
    value: Optional[float] = None
    formatted_value: Optional[str] = None
    change: Optional[float] = None  # percentage change
    change_direction: Optional[str] = None  # up, down, neutral

    # Execution info
    execution_time_ms: int = 0


class DashboardRun(BaseModel):
    """Executed dashboard with data."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dashboard_id: str
    executed_at: datetime = Field(default_factory=datetime.utcnow)

    # Results
    widget_results: dict[str, WidgetResult] = Field(default_factory=dict)
    total_execution_time_ms: int = 0

    # Status
    status: str = "pending"  # pending, running, completed, failed
    error: Optional[str] = None


class DashboardPlan(BaseModel):
    """Plan generated by LLM for dashboard creation."""

    dashboard_name: str
    description: Optional[str] = None
    widgets: list[dict] = Field(default_factory=list)
    suggested_filters: list[str] = Field(default_factory=list)
    theme: str = "default"


# Request/Response models for API
class CreateDashboardRequest(BaseModel):
    """Request to create a dashboard from natural language."""

    request: str  # Natural language description
    db_connection_id: str
    name: Optional[str] = None
    theme: str = "default"


class UpdateDashboardRequest(BaseModel):
    """Request to update dashboard."""

    name: Optional[str] = None
    description: Optional[str] = None
    theme: Optional[str] = None
    refresh_interval: Optional[int] = None
    is_public: Optional[bool] = None


class RefineDashboardRequest(BaseModel):
    """Request to refine dashboard with natural language."""

    refinement: str  # Natural language refinement request


class DashboardSummary(BaseModel):
    """Summary of a dashboard for list views."""

    id: str
    name: str
    description: Optional[str] = None
    widget_count: int = 0
    created_at: datetime
    updated_at: datetime
    is_public: bool = False


class ShareResponse(BaseModel):
    """Response when sharing a dashboard."""

    share_url: str
    share_token: str
    expires_at: Optional[datetime] = None


# Clarification question models for dashboard creation
class ClarificationOption(BaseModel):
    """A single option for a clarification question."""

    label: str
    description: str


class ClarificationQuestion(BaseModel):
    """A clarification question with multiple choice options."""

    question: str
    options: list[ClarificationOption] = Field(default_factory=list)
    allow_custom: bool = True


class ClarificationResponse(BaseModel):
    """Response from LLM with clarification questions."""

    questions: list[ClarificationQuestion] = Field(default_factory=list)


class ClarificationAnswers(BaseModel):
    """User's answers to clarification questions."""

    answers: dict[str, str] = Field(default_factory=dict)  # question -> answer


__all__ = [
    "WidgetType",
    "WidgetSize",
    "ChartType",
    "AggregationType",
    "ChartWidgetConfig",
    "KPIWidgetConfig",
    "TableWidgetConfig",
    "FilterWidgetConfig",
    "TextWidgetConfig",
    "Widget",
    "DashboardLayout",
    "DashboardTheme",
    "Dashboard",
    "WidgetResult",
    "DashboardRun",
    "DashboardPlan",
    "CreateDashboardRequest",
    "UpdateDashboardRequest",
    "RefineDashboardRequest",
    "DashboardSummary",
    "ShareResponse",
    "ClarificationOption",
    "ClarificationQuestion",
    "ClarificationResponse",
    "ClarificationAnswers",
]
