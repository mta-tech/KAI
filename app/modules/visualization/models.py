"""Visualization data models."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class ChartType(str, Enum):
    """Supported chart types."""

    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    PIE = "pie"
    DONUT = "donut"
    HEATMAP = "heatmap"
    BOX = "box"
    VIOLIN = "violin"
    HISTOGRAM = "histogram"
    TREEMAP = "treemap"
    SUNBURST = "sunburst"
    FUNNEL = "funnel"
    AREA = "area"


class ChartConfig(BaseModel):
    """Configuration for chart generation."""

    chart_type: ChartType
    title: str | None = None
    x_column: str | None = None
    y_column: str | None = None
    color_column: str | None = None
    size_column: str | None = None
    values_column: str | None = None
    names_column: str | None = None
    theme: str = "default"
    width: int = 800
    height: int = 600
    interactive: bool = True
    show_legend: bool = True
    orientation: Literal["v", "h"] = "v"


class ChartResult(BaseModel):
    """Result of chart generation."""

    chart_type: str
    html: str | None = None
    json_spec: dict[str, Any] | None = None
    image_base64: str | None = None
    config: ChartConfig


class Theme(BaseModel):
    """Chart theme definition."""

    name: str
    plotly_template: str
    color_palette: list[str]
    background_color: str = "#ffffff"
    font_family: str = "Arial, sans-serif"
    font_color: str = "#333333"
    grid_color: str = "#e0e0e0"


class ChartRecommendation(BaseModel):
    """AI recommendation for chart type."""

    chart_type: ChartType
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    x_column: str | None = None
    y_column: str | None = None
    color_column: str | None = None
