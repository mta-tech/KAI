"""Dashboard rendering service."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import numpy as np
from jinja2 import Environment, FileSystemLoader


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles numpy types."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

from app.modules.dashboard.models import (
    Dashboard,
    DashboardRun,
    DashboardTheme,
    WidgetResult,
)

logger = logging.getLogger(__name__)

# Default themes
THEMES = {
    "default": DashboardTheme(
        name="default",
        background="#f8fafc",
        card_background="#ffffff",
        text_color="#1e293b",
        primary_color="#3b82f6",
        accent_color="#10b981",
        font_family="Inter, system-ui, sans-serif",
    ),
    "dark": DashboardTheme(
        name="dark",
        background="#0f172a",
        card_background="#1e293b",
        text_color="#f1f5f9",
        primary_color="#60a5fa",
        accent_color="#34d399",
        font_family="Inter, system-ui, sans-serif",
    ),
    "minimal": DashboardTheme(
        name="minimal",
        background="#ffffff",
        card_background="#ffffff",
        text_color="#111827",
        primary_color="#111827",
        accent_color="#059669",
        font_family="Inter, system-ui, sans-serif",
    ),
    "corporate": DashboardTheme(
        name="corporate",
        background="#f3f4f6",
        card_background="#ffffff",
        text_color="#1f2937",
        primary_color="#1e40af",
        accent_color="#047857",
        font_family="Inter, system-ui, sans-serif",
    ),
}


class DashboardRendererService:
    """Service for rendering dashboards to various formats."""

    def __init__(self):
        # Setup Jinja2 template environment
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True,
        )
        # Add custom filters with numpy support
        self.env.filters["tojson"] = lambda obj: json.dumps(obj, cls=NumpyEncoder)

    async def render_to_html(
        self,
        dashboard: Dashboard,
        widget_results: dict[str, WidgetResult],
        theme_name: Optional[str] = None,
    ) -> str:
        """
        Render dashboard to interactive HTML.

        Args:
            dashboard: Dashboard definition
            widget_results: Results for each widget
            theme_name: Theme name to use

        Returns:
            Complete HTML string
        """
        # Get theme
        theme = THEMES.get(theme_name or dashboard.theme, THEMES["default"])

        # Load template
        template = self.env.get_template("dashboard.html")

        # Render
        html = template.render(
            dashboard=dashboard,
            widgets=dashboard.layout.widgets,
            widget_results=widget_results,
            layout=dashboard.layout,
            theme=theme,
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        return html

    async def render_to_json(
        self,
        dashboard: Dashboard,
        widget_results: dict[str, WidgetResult],
    ) -> dict:
        """
        Render dashboard to JSON spec for frontend rendering.

        Args:
            dashboard: Dashboard definition
            widget_results: Results for each widget

        Returns:
            JSON-serializable dictionary
        """
        widgets_data = []

        for widget in dashboard.layout.widgets:
            result = widget_results.get(widget.id)

            widget_data = {
                "id": widget.id,
                "name": widget.name,
                "type": widget.widget_type.value,
                "size": widget.size.value,
                "position": {
                    "row": widget.row,
                    "col": widget.col,
                    "rowSpan": widget.row_span,
                    "colSpan": widget.col_span,
                },
            }

            if result:
                widget_data["result"] = {
                    "status": result.status,
                    "data": result.data,
                    "rowCount": result.row_count,
                    "executionTimeMs": result.execution_time_ms,
                }

                if result.status == "completed":
                    if widget.widget_type.value == "kpi":
                        widget_data["result"]["kpi"] = {
                            "value": result.value,
                            "formattedValue": result.formatted_value,
                            "change": result.change,
                            "changeDirection": result.change_direction,
                        }
                    elif widget.widget_type.value == "chart":
                        widget_data["result"]["plotlySpec"] = result.plotly_json

                elif result.status == "failed":
                    widget_data["result"]["error"] = result.error

            widgets_data.append(widget_data)

        return {
            "dashboard": {
                "id": dashboard.id,
                "name": dashboard.name,
                "description": dashboard.description,
                "theme": dashboard.theme,
                "refreshInterval": dashboard.refresh_interval,
            },
            "layout": {
                "columns": dashboard.layout.columns,
                "rowHeight": dashboard.layout.row_height,
                "gap": dashboard.layout.gap,
            },
            "widgets": widgets_data,
            "generatedAt": datetime.now().isoformat(),
        }

    async def render_to_static_html(
        self,
        dashboard: Dashboard,
        widget_results: dict[str, WidgetResult],
        theme_name: Optional[str] = None,
    ) -> str:
        """
        Render dashboard to static HTML (no external dependencies).

        For PDF generation or offline viewing.

        Args:
            dashboard: Dashboard definition
            widget_results: Results for each widget
            theme_name: Theme name to use

        Returns:
            Self-contained HTML string
        """
        # Get the interactive HTML first
        html = await self.render_to_html(dashboard, widget_results, theme_name)

        # For static version, we could embed Plotly as static images
        # For now, return the same HTML (Plotly JS is loaded from CDN)
        return html

    def get_available_themes(self) -> list[dict]:
        """Get list of available themes."""
        return [
            {
                "name": theme.name,
                "background": theme.background,
                "primaryColor": theme.primary_color,
            }
            for theme in THEMES.values()
        ]


__all__ = ["DashboardRendererService", "THEMES"]
