"""Tests for ThemeService."""

import pytest

from app.modules.visualization.models import Theme
from app.modules.visualization.services.theme_service import ThemeService


class TestThemeService:
    """Test cases for ThemeService."""

    def test_default_themes_registered(self) -> None:
        """Default themes should be available."""
        service = ThemeService()
        themes = service.list_themes()

        assert "default" in themes
        assert "dark" in themes
        assert "minimal" in themes

    def test_get_default_theme(self) -> None:
        """Should return default theme."""
        service = ThemeService()
        theme = service.get_theme("default")

        assert theme.name == "default"
        assert theme.plotly_template == "plotly_white"
        assert len(theme.color_palette) > 0

    def test_get_dark_theme(self) -> None:
        """Should return dark theme."""
        service = ThemeService()
        theme = service.get_theme("dark")

        assert theme.name == "dark"
        assert theme.plotly_template == "plotly_dark"
        assert theme.background_color == "#1e1e1e"

    def test_get_nonexistent_theme_returns_default(self) -> None:
        """Unknown theme should return default."""
        service = ThemeService()
        theme = service.get_theme("nonexistent")

        assert theme.name == "default"

    def test_register_custom_theme(self) -> None:
        """Should allow registering custom themes."""
        service = ThemeService()
        custom = Theme(
            name="custom",
            plotly_template="ggplot2",
            color_palette=["#ff0000", "#00ff00"],
        )

        service.register_theme(custom)
        retrieved = service.get_theme("custom")

        assert retrieved.name == "custom"
        assert retrieved.plotly_template == "ggplot2"
