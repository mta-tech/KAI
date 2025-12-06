"""Theme management service for visualizations."""

from __future__ import annotations

from app.modules.visualization.models import Theme


class ThemeService:
    """Service for managing chart themes."""

    _themes: dict[str, Theme] = {}

    def __init__(self) -> None:
        """Initialize with default themes."""
        self._register_default_themes()

    def _register_default_themes(self) -> None:
        """Register built-in themes."""
        self._themes["default"] = Theme(
            name="default",
            plotly_template="plotly_white",
            color_palette=[
                "#636EFA", "#EF553B", "#00CC96", "#AB63FA",
                "#FFA15A", "#19D3F3", "#FF6692", "#B6E880",
            ],
            background_color="#ffffff",
            font_color="#333333",
        )

        self._themes["dark"] = Theme(
            name="dark",
            plotly_template="plotly_dark",
            color_palette=[
                "#636EFA", "#EF553B", "#00CC96", "#AB63FA",
                "#FFA15A", "#19D3F3", "#FF6692", "#B6E880",
            ],
            background_color="#1e1e1e",
            font_color="#ffffff",
            grid_color="#444444",
        )

        self._themes["minimal"] = Theme(
            name="minimal",
            plotly_template="simple_white",
            color_palette=[
                "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
                "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
            ],
            background_color="#ffffff",
            font_color="#333333",
        )

    def get_theme(self, name: str) -> Theme:
        """Get a theme by name."""
        if name not in self._themes:
            return self._themes["default"]
        return self._themes[name]

    def list_themes(self) -> list[str]:
        """List available theme names."""
        return list(self._themes.keys())

    def register_theme(self, theme: Theme) -> None:
        """Register a custom theme."""
        self._themes[theme.name] = theme
