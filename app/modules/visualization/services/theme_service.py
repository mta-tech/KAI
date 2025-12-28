"""Theme management service for visualizations."""

from __future__ import annotations

from app.modules.visualization.exceptions import ThemeNotFoundError
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

    def get_theme(self, name: str, strict: bool = False) -> Theme:
        """Get a theme by name.

        Args:
            name: The name of the theme to retrieve.
            strict: If True, raise ThemeNotFoundError when theme doesn't exist.
                   If False (default), fall back to the default theme.

        Returns:
            The requested Theme object.

        Raises:
            ThemeNotFoundError: If strict=True and the theme doesn't exist.
        """
        if name not in self._themes:
            if strict:
                available = list(self._themes.keys())
                raise ThemeNotFoundError(
                    f"Theme '{name}' not found. Available themes: {available}"
                )
            return self._themes["default"]
        return self._themes[name]

    def list_themes(self) -> list[str]:
        """List available theme names."""
        return list(self._themes.keys())

    def validate_theme(self, name: str) -> bool:
        """Check if a theme exists.

        Args:
            name: The name of the theme to check.

        Returns:
            True if the theme exists, False otherwise.
        """
        return name in self._themes

    def get_theme_strict(self, name: str) -> Theme:
        """Get a theme by name, raising an error if not found.

        This is a convenience method equivalent to get_theme(name, strict=True).

        Args:
            name: The name of the theme to retrieve.

        Returns:
            The requested Theme object.

        Raises:
            ThemeNotFoundError: If the theme doesn't exist.
        """
        return self.get_theme(name, strict=True)

    def register_theme(self, theme: Theme) -> None:
        """Register a custom theme.

        Args:
            theme: The Theme object to register.

        Raises:
            ValueError: If the theme name is invalid.
        """
        if not theme.name or not theme.name.strip():
            raise ValueError("Theme name cannot be empty")
        self._themes[theme.name] = theme
