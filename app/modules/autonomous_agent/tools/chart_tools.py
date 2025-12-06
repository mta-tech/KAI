"""Chart generation tools for the autonomous agent using Plotly."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Literal

import pandas as pd

from app.modules.visualization import ChartConfig, ChartService, ChartType


def generate_chart(
    data_json: str,
    chart_type: Literal[
        "line", "bar", "pie", "scatter", "area", "heatmap",
        "box", "violin", "histogram", "treemap", "sunburst", "funnel", "donut"
    ],
    x_column: str,
    y_column: str,
    title: str = "Chart",
    color_column: str | None = None,
    size_column: str | None = None,
    theme: str = "default",
    save_path: str | None = None,
) -> str:
    """Generate an interactive chart from data.

    Args:
        data_json: JSON string containing the data array.
        chart_type: Type of chart to generate.
        x_column: Column name for x-axis.
        y_column: Column name for y-axis/values.
        title: Chart title.
        color_column: Optional column for color grouping.
        size_column: Optional column for size (scatter only).
        theme: Chart theme (default, dark, minimal).
        save_path: Optional path to save the chart HTML.

    Returns:
        JSON string with chart result including HTML or saved path.
    """
    try:
        data = json.loads(data_json)

        # Handle different data formats
        if isinstance(data, dict):
            # Format: {"columns": [...], "data": [...]} or {"data": [...]}
            if "data" in data:
                df = pd.DataFrame(data["data"])
            else:
                # Assume it's a dict of column: values
                df = pd.DataFrame(data)
        elif isinstance(data, list):
            # Format: [{...}, {...}, ...]
            df = pd.DataFrame(data)
        else:
            raise ValueError(f"Unsupported data format: {type(data)}")

        chart_type_enum = ChartType(chart_type)

        config = ChartConfig(
            chart_type=chart_type_enum,
            title=title,
            x_column=x_column,
            y_column=y_column,
            color_column=color_column,
            size_column=size_column,
            values_column=y_column if chart_type in ("pie", "donut", "treemap", "sunburst") else None,
            names_column=x_column if chart_type in ("pie", "donut") else None,
            theme=theme,
            interactive=True,
        )

        service = ChartService()
        result = service.generate_chart(df, config)

        response: dict = {
            "success": True,
            "chart_type": result.chart_type,
            "title": title,
            "interactive": True,
        }

        if save_path:
            path = Path(save_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(result.html or "")
            response["saved_to"] = str(path)
            response["full_chart_available"] = True
        else:
            if result.html and len(result.html) > 50000:
                response["html_preview"] = result.html[:50000] + "..."
                response["full_chart_available"] = True
                response["note"] = "Chart HTML truncated. Use save_path to get full chart."
            else:
                response["html"] = result.html
                response["full_chart_available"] = True

        image_base64 = service.export_to_base64(result, format="png", scale=1.0)
        if len(image_base64) < 100000:
            response["image_base64"] = image_base64[:100] + "..."  # Truncated for context
            response["full_image_available"] = True

        return json.dumps(response)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "chart_type": chart_type,
            "title": title,
        })


def create_chart_tool(output_dir: str | None = None):
    """Create a chart generation tool with optional output directory.

    Args:
        output_dir: Directory to save charts. If None, charts returned inline.

    Returns:
        Chart generation function configured for the output directory.
    """
    def chart_tool(
        data_json: str,
        chart_type: Literal[
            "line", "bar", "pie", "scatter", "area", "heatmap",
            "box", "violin", "histogram", "treemap", "sunburst", "funnel", "donut"
        ],
        x_column: str,
        y_column: str,
        title: str = "Chart",
        color_column: str | None = None,
        size_column: str | None = None,
        theme: str = "default",
    ) -> str:
        """Generate an interactive chart from query results.

        Args:
            data_json: JSON string of data array from SQL query.
            chart_type: Chart type (line, bar, pie, scatter, area, heatmap,
                       box, violin, histogram, treemap, sunburst, funnel, donut).
            x_column: Column for x-axis or categories.
            y_column: Column for y-axis or values.
            title: Chart title.
            color_column: Optional column for color grouping.
            size_column: Optional column for bubble size (scatter only).
            theme: Visual theme (default, dark, minimal).

        Returns:
            JSON with chart HTML or save path.
        """
        save_path = None
        if output_dir:
            import uuid
            filename = f"chart_{uuid.uuid4().hex[:8]}.html"
            save_path = os.path.join(output_dir, filename)

        return generate_chart(
            data_json=data_json,
            chart_type=chart_type,
            x_column=x_column,
            y_column=y_column,
            title=title,
            color_column=color_column,
            size_column=size_column,
            theme=theme,
            save_path=save_path,
        )

    return chart_tool
