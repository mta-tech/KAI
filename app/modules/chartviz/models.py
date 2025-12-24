"""Chart visualization models for JS chart libraries."""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ChartType(str, Enum):
    """Supported chart types for visualization."""

    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    KPI = "kpi"
    TABLE = "table"


class ChartWidget(BaseModel):
    """
    Chart widget configuration for JavaScript chart libraries.

    This format is compatible with:
    - Chart.js
    - Apache ECharts
    - Recharts
    - D3.js
    - Plotly.js

    The widget_data uses flexible key-value format where keys are
    column names from SQL results, making it easy to map to chart axes.
    """

    widget_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the widget",
    )
    widget_title: str = Field(
        ...,
        description="Human-readable title for the chart",
    )
    widget_type: ChartType = Field(
        ...,
        description="Type of chart to render",
    )
    widget_data: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Chart data as list of key-value records",
    )
    widget_delta_percentages: float | None = Field(
        default=None,
        description="Percentage change for KPI/trend charts",
    )
    x_axis_label: str | None = Field(
        default=None,
        description="Label for X axis (for line, bar, scatter, area)",
    )
    y_axis_label: str | None = Field(
        default=None,
        description="Label for Y axis (for line, bar, scatter, area)",
    )
    x_axis_key: str | None = Field(
        default=None,
        description="Key in widget_data to use for X axis",
    )
    y_axis_key: str | None = Field(
        default=None,
        description="Key in widget_data to use for Y axis",
    )
    category_key: str | None = Field(
        default=None,
        description="Key for categorical grouping (pie, grouped charts)",
    )
    value_key: str | None = Field(
        default=None,
        description="Key for numeric values",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "widget_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "widget_title": "Trend Pendapatan Bulanan",
                "widget_type": "line",
                "widget_data": [
                    {"Bulan": "Januari 2024", "Pendapatan": 52000000},
                    {"Bulan": "Februari 2024", "Pendapatan": 58000000},
                    {"Bulan": "Maret 2024", "Pendapatan": 61000000},
                ],
                "widget_delta_percentages": 5.17,
                "x_axis_label": "Bulan",
                "y_axis_label": "Pendapatan (Rp)",
                "x_axis_key": "Bulan",
                "y_axis_key": "Pendapatan",
            }
        }


class ChartRecommendation(BaseModel):
    """AI recommendation for best chart type."""

    chart_type: ChartType = Field(
        ...,
        description="Recommended chart type",
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score (0-1)",
    )
    rationale: str = Field(
        ...,
        description="Explanation for the recommendation",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "chart_type": "line",
                "confidence": 0.92,
                "rationale": "Time series data dengan tren yang jelas cocok untuk line chart",
            }
        }


class GenerateChartRequest(BaseModel):
    """Request to generate a chart from SQL results."""

    chart_type: ChartType = Field(
        ...,
        description="Type of chart to generate",
    )
    data: list[dict[str, Any]] = Field(
        ...,
        description="SQL result data to visualize",
    )
    user_prompt: str | None = Field(
        default=None,
        description="Original user question for context",
    )
    language: str = Field(
        default="id",
        description="Language for title and labels (id/en)",
    )


class RecommendChartRequest(BaseModel):
    """Request for chart type recommendation."""

    data: list[dict[str, Any]] = Field(
        ...,
        description="SQL result data to analyze",
    )
    user_prompt: str | None = Field(
        default=None,
        description="Original user question for context",
    )
    language: str = Field(
        default="id",
        description="Language for response (id/en)",
    )


class AutoChartRequest(BaseModel):
    """Request for automatic chart generation (recommend + generate)."""

    data: list[dict[str, Any]] = Field(
        ...,
        description="SQL result data to visualize",
    )
    user_prompt: str | None = Field(
        default=None,
        description="Original user question for context",
    )
    language: str = Field(
        default="id",
        description="Language for title and labels (id/en)",
    )


class SessionVisualizeRequest(BaseModel):
    """Request to visualize session analysis result."""

    chart_type: ChartType | None = Field(
        default=None,
        description="Specific chart type (if None, will recommend)",
    )
    language: str = Field(
        default="id",
        description="Language for title and labels (id/en)",
    )


__all__ = [
    "ChartType",
    "ChartWidget",
    "ChartRecommendation",
    "GenerateChartRequest",
    "RecommendChartRequest",
    "AutoChartRequest",
    "SessionVisualizeRequest",
]
