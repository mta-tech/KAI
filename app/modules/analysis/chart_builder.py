"""Chart widget builder for creating meaningful visualizations."""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ChartWidget(BaseModel):
    """Chart widget for frontend rendering."""

    widget_type: str  # "bar", "line", "pie", "table", "kpi", etc.
    widget_title: str
    widget_description: str | None = None
    widget_data: list[dict]
    x_axis_key: str | None = None
    y_axis_key: str | None = None
    is_meaningful: bool = True
    quality_issues: list[str] | None = None


class ChartBuilder:
    """Builder for creating meaningful chart widgets from recommendations and data."""

    # Chart type mapping from LLM recommendation to frontend widget type
    CHART_TYPE_MAP = {
        "bar": "bar",
        "bar_chart": "bar",
        "line": "line",
        "line_chart": "line",
        "pie": "pie",
        "pie_chart": "pie",
        "scatter": "scatter",
        "scatter_plot": "scatter",
        "table": "table",
        "heatmap": "table",  # Fallback to table
        "kpi": "kpi",
        "big_number": "kpi",
        "area": "area",
        "area_chart": "area",
    }

    # Minimum data requirements for meaningful charts
    MIN_ROWS_FOR_LINE = 2
    MIN_ROWS_FOR_PIE = 2
    MAX_CATEGORIES_FOR_PIE = 10
    MIN_ROWS_FOR_BAR = 1

    def __init__(self, result_data: list[dict], chart_recommendations: list[dict]):
        """Initialize builder with data and recommendations.

        Args:
            result_data: Query result rows
            chart_recommendations: LLM-generated chart recommendations
        """
        self.result_data = result_data or []
        self.recommendations = chart_recommendations or []
        self.columns = list(result_data[0].keys()) if result_data else []

    def build_widgets(self) -> list[ChartWidget]:
        """Build chart widgets from recommendations.

        Returns:
            List of validated ChartWidget objects
        """
        widgets = []

        for rec in self.recommendations:
            widget = self._build_widget(rec)
            if widget:
                widgets.append(widget)

        # If no valid widgets, create a smart default
        if not widgets and self.result_data:
            default_widget = self._create_smart_default()
            if default_widget:
                widgets.append(default_widget)

        return widgets

    def _build_widget(self, recommendation: dict) -> ChartWidget | None:
        """Build a single widget from a recommendation.

        Args:
            recommendation: Chart recommendation dict

        Returns:
            ChartWidget if valid, None otherwise
        """
        chart_type = recommendation.get("chart_type", "bar").lower()
        widget_type = self.CHART_TYPE_MAP.get(chart_type, "bar")

        title = recommendation.get("title", "Data Visualization")
        description = recommendation.get("description")
        x_axis = recommendation.get("x_axis")
        y_axis = recommendation.get("y_axis")

        # Validate and resolve axis columns
        x_key, y_key, quality_issues = self._resolve_axes(x_axis, y_axis, widget_type)

        if not x_key:
            logger.warning(f"Could not resolve x-axis for chart: {title}")
            return None

        # Build widget data with proper column ordering
        widget_data = self._prepare_widget_data(x_key, y_key)

        if not widget_data:
            return None

        # Check if chart is meaningful
        is_meaningful, issues = self._validate_chart_quality(
            widget_type, widget_data, x_key, y_key
        )
        quality_issues.extend(issues)

        # Auto-improve chart type if needed
        if not is_meaningful:
            improved_type, improved_data = self._improve_chart(
                widget_type, widget_data, x_key, y_key
            )
            if improved_type:
                widget_type = improved_type
                widget_data = improved_data
                is_meaningful = True
                quality_issues.append(f"Auto-improved from {chart_type} to {widget_type}")

        return ChartWidget(
            widget_type=widget_type,
            widget_title=title,
            widget_description=description,
            widget_data=widget_data,
            x_axis_key=x_key,
            y_axis_key=y_key,
            is_meaningful=is_meaningful,
            quality_issues=quality_issues if quality_issues else None,
        )

    def _resolve_axes(
        self, x_axis: str | None, y_axis: str | None, widget_type: str
    ) -> tuple[str | None, str | None, list[str]]:
        """Resolve axis column names to actual data columns.

        Args:
            x_axis: Recommended x-axis column
            y_axis: Recommended y-axis column
            widget_type: Chart type

        Returns:
            Tuple of (x_key, y_key, quality_issues)
        """
        issues = []

        if not self.columns:
            return None, None, ["No columns in data"]

        # Try to match recommended columns (case-insensitive)
        x_key = self._find_column(x_axis)
        y_key = self._find_column(y_axis)

        # Smart fallback if columns not found
        if not x_key:
            x_key = self._infer_category_column()
            if x_key and x_axis:
                issues.append(f"X-axis '{x_axis}' not found, using '{x_key}'")

        if not y_key:
            y_key = self._infer_numeric_column(exclude=x_key)
            if y_key and y_axis:
                issues.append(f"Y-axis '{y_axis}' not found, using '{y_key}'")

        return x_key, y_key, issues

    def _find_column(self, column_name: str | None) -> str | None:
        """Find a column by name (case-insensitive).

        Args:
            column_name: Column to find

        Returns:
            Actual column name if found
        """
        if not column_name:
            return None

        # Exact match
        if column_name in self.columns:
            return column_name

        # Case-insensitive match
        lower_name = column_name.lower()
        for col in self.columns:
            if col.lower() == lower_name:
                return col

        # Partial match (contains)
        for col in self.columns:
            if lower_name in col.lower() or col.lower() in lower_name:
                return col

        return None

    def _infer_category_column(self) -> str | None:
        """Infer the best column for categories (x-axis).

        Returns:
            Column name for categories
        """
        if not self.result_data:
            return self.columns[0] if self.columns else None

        # Look for string columns or columns with few unique values
        for col in self.columns:
            sample_value = self.result_data[0].get(col)
            if isinstance(sample_value, str):
                return col

        # Fallback to first column
        return self.columns[0] if self.columns else None

    def _infer_numeric_column(self, exclude: str | None = None) -> str | None:
        """Infer the best column for numeric values (y-axis).

        Args:
            exclude: Column to exclude

        Returns:
            Column name for values
        """
        if not self.result_data:
            return None

        for col in self.columns:
            if col == exclude:
                continue
            sample_value = self.result_data[0].get(col)
            if isinstance(sample_value, (int, float)):
                return col

        # Fallback to second column if available
        for col in self.columns:
            if col != exclude:
                return col

        return None

    def _prepare_widget_data(
        self, x_key: str, y_key: str | None
    ) -> list[dict]:
        """Prepare widget data with proper column ordering.

        The first key should be the x-axis (category), second should be y-axis (value).

        Args:
            x_key: X-axis column name
            y_key: Y-axis column name

        Returns:
            Reordered data for widget
        """
        if not self.result_data or not x_key:
            return []

        widget_data = []
        for row in self.result_data:
            # Create new dict with x_key first, y_key second
            new_row = {x_key: row.get(x_key)}
            if y_key and y_key in row:
                new_row[y_key] = row.get(y_key)
            # Add remaining columns
            for col, val in row.items():
                if col not in new_row:
                    new_row[col] = val
            widget_data.append(new_row)

        return widget_data

    def _validate_chart_quality(
        self,
        widget_type: str,
        widget_data: list[dict],
        x_key: str | None,
        y_key: str | None,
    ) -> tuple[bool, list[str]]:
        """Validate if the chart will be meaningful.

        Args:
            widget_type: Type of chart
            widget_data: Prepared data
            x_key: X-axis key
            y_key: Y-axis key

        Returns:
            Tuple of (is_meaningful, issues)
        """
        issues = []
        row_count = len(widget_data)

        if row_count == 0:
            return False, ["No data to display"]

        # Check minimum rows for chart types
        if widget_type == "line" and row_count < self.MIN_ROWS_FOR_LINE:
            issues.append(f"Line chart needs at least {self.MIN_ROWS_FOR_LINE} data points")
            return False, issues

        if widget_type == "pie":
            if row_count < self.MIN_ROWS_FOR_PIE:
                issues.append(f"Pie chart needs at least {self.MIN_ROWS_FOR_PIE} categories")
                return False, issues
            if row_count > self.MAX_CATEGORIES_FOR_PIE:
                issues.append(f"Pie chart has too many categories ({row_count}), max is {self.MAX_CATEGORIES_FOR_PIE}")

        # Check if y-axis values are numeric for non-table charts
        if widget_type not in ("table", "kpi") and y_key:
            non_numeric = 0
            for row in widget_data[:5]:  # Sample first 5 rows
                val = row.get(y_key)
                if val is not None and not isinstance(val, (int, float)):
                    non_numeric += 1

            if non_numeric > 2:
                issues.append(f"Y-axis '{y_key}' contains non-numeric values")

        # Check for meaningful x-axis labels
        if x_key:
            x_values = [row.get(x_key) for row in widget_data[:5]]
            if all(v is None or v == "" for v in x_values):
                issues.append("X-axis values are empty")
                return False, issues

        return len(issues) == 0, issues

    def _improve_chart(
        self,
        widget_type: str,
        widget_data: list[dict],
        x_key: str | None,
        y_key: str | None,
    ) -> tuple[str | None, list[dict]]:
        """Try to improve a non-meaningful chart.

        Args:
            widget_type: Original chart type
            widget_data: Chart data
            x_key: X-axis key
            y_key: Y-axis key

        Returns:
            Tuple of (improved_type, improved_data) or (None, [])
        """
        row_count = len(widget_data)

        # Pie chart with too many categories -> bar chart
        if widget_type == "pie" and row_count > self.MAX_CATEGORIES_FOR_PIE:
            return "bar", widget_data

        # Line chart with single point -> KPI
        if widget_type == "line" and row_count == 1:
            return "kpi", widget_data

        # Single row with multiple columns -> table
        if row_count == 1 and len(self.columns) > 2:
            return "table", widget_data

        return None, []

    def _create_smart_default(self) -> ChartWidget | None:
        """Create a smart default chart when no recommendations work.

        Returns:
            Default ChartWidget
        """
        if not self.result_data:
            return None

        row_count = len(self.result_data)
        col_count = len(self.columns)

        x_key = self._infer_category_column()
        y_key = self._infer_numeric_column(exclude=x_key)

        widget_data = self._prepare_widget_data(x_key, y_key)

        # Choose appropriate chart type
        if row_count == 1:
            widget_type = "kpi" if col_count <= 3 else "table"
        elif row_count <= 10 and y_key:
            widget_type = "bar"
        elif row_count > 10 and y_key:
            widget_type = "line"
        else:
            widget_type = "table"

        return ChartWidget(
            widget_type=widget_type,
            widget_title="Data Visualization",
            widget_description="Auto-generated visualization",
            widget_data=widget_data,
            x_axis_key=x_key,
            y_axis_key=y_key,
            is_meaningful=True,
            quality_issues=["Auto-generated default chart"],
        )


def build_chart_widgets(
    result_data: list[dict],
    chart_recommendations: list[dict],
) -> list[dict]:
    """Build chart widgets from recommendations and data.

    Args:
        result_data: Query result rows
        chart_recommendations: LLM chart recommendations

    Returns:
        List of ChartWidget dicts ready for frontend
    """
    builder = ChartBuilder(result_data, chart_recommendations)
    widgets = builder.build_widgets()
    return [w.model_dump() for w in widgets]
