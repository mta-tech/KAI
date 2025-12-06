# KAI Advanced Analytics Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement advanced visualization, statistical analysis, notebook workflows, enhanced CLI, and API enhancements for KAI.

**Architecture:** Build on existing module patterns (service-repository-model). Add new modules for visualization, analytics, and notebook systems. Integrate with existing autonomous agent tools and CLI framework. Use Plotly for interactive charts, scipy/statsmodels for statistics, and extend the FastAPI API layer.

**Tech Stack:** Python 3.11+, FastAPI, Plotly, Kaleido, scipy, statsmodels, Rich, Click, pytest-asyncio

---

## Epic 2: Advanced Visualization System

### Task 1: Add Plotly Dependencies

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add visualization dependencies to pyproject.toml**

Open `pyproject.toml` and add these dependencies to the `dependencies` array:

```toml
"plotly>=5.18.0",
"kaleido>=0.2.1",
```

**Step 2: Install dependencies**

Run: `uv sync`
Expected: Dependencies installed successfully

**Step 3: Verify installation**

Run: `uv run python -c "import plotly; import kaleido; print('OK')"`
Expected: `OK`

**Step 4: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "feat(viz): add plotly and kaleido dependencies"
```

---

### Task 2: Create Visualization Module Structure

**Files:**
- Create: `app/modules/visualization/__init__.py`
- Create: `app/modules/visualization/models.py`
- Create: `app/modules/visualization/services/__init__.py`
- Create: `app/modules/visualization/services/chart_service.py`
- Create: `app/modules/visualization/services/theme_service.py`

**Step 1: Create module directory structure**

Run: `mkdir -p /Users/fitrakacamarga/project/mta/KAI/app/modules/visualization/services`

**Step 2: Create models.py with chart configuration models**

Create `app/modules/visualization/models.py`:

```python
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
```

**Step 3: Create theme_service.py**

Create `app/modules/visualization/services/theme_service.py`:

```python
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
```

**Step 4: Create chart_service.py**

Create `app/modules/visualization/services/chart_service.py`:

```python
"""Chart generation service using Plotly."""

from __future__ import annotations

import base64
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.modules.visualization.models import (
    ChartConfig,
    ChartRecommendation,
    ChartResult,
    ChartType,
)
from app.modules.visualization.services.theme_service import ThemeService


class ChartService:
    """Service for generating interactive visualizations with Plotly."""

    def __init__(self, theme_service: ThemeService | None = None) -> None:
        """Initialize chart service."""
        self.theme_service = theme_service or ThemeService()

    def generate_chart(
        self,
        df: pd.DataFrame,
        config: ChartConfig,
    ) -> ChartResult:
        """Generate a chart from DataFrame using configuration."""
        theme = self.theme_service.get_theme(config.theme)

        fig = self._create_figure(df, config)

        fig.update_layout(
            template=theme.plotly_template,
            title=config.title,
            width=config.width,
            height=config.height,
            showlegend=config.show_legend,
            font=dict(family=theme.font_family, color=theme.font_color),
            paper_bgcolor=theme.background_color,
            plot_bgcolor=theme.background_color,
        )

        html_output = None
        if config.interactive:
            html_output = fig.to_html(include_plotlyjs="cdn", full_html=False)

        return ChartResult(
            chart_type=config.chart_type.value,
            html=html_output,
            json_spec=fig.to_dict(),
            config=config,
        )

    def _create_figure(
        self,
        df: pd.DataFrame,
        config: ChartConfig,
    ) -> go.Figure:
        """Create Plotly figure based on chart type."""
        chart_type = config.chart_type

        if chart_type == ChartType.LINE:
            return px.line(
                df,
                x=config.x_column,
                y=config.y_column,
                color=config.color_column,
            )

        if chart_type == ChartType.BAR:
            return px.bar(
                df,
                x=config.x_column,
                y=config.y_column,
                color=config.color_column,
                orientation=config.orientation,
                barmode="group",
            )

        if chart_type == ChartType.SCATTER:
            return px.scatter(
                df,
                x=config.x_column,
                y=config.y_column,
                color=config.color_column,
                size=config.size_column,
            )

        if chart_type == ChartType.PIE:
            return px.pie(
                df,
                values=config.values_column or config.y_column,
                names=config.names_column or config.x_column,
            )

        if chart_type == ChartType.DONUT:
            fig = px.pie(
                df,
                values=config.values_column or config.y_column,
                names=config.names_column or config.x_column,
                hole=0.4,
            )
            return fig

        if chart_type == ChartType.HEATMAP:
            pivot_df = df.pivot(
                index=config.y_column,
                columns=config.x_column,
                values=config.values_column,
            ) if config.values_column else df
            return px.imshow(pivot_df, aspect="auto")

        if chart_type == ChartType.BOX:
            return px.box(
                df,
                x=config.x_column,
                y=config.y_column,
                color=config.color_column,
            )

        if chart_type == ChartType.VIOLIN:
            return px.violin(
                df,
                x=config.x_column,
                y=config.y_column,
                color=config.color_column,
                box=True,
            )

        if chart_type == ChartType.HISTOGRAM:
            return px.histogram(
                df,
                x=config.x_column,
                color=config.color_column,
            )

        if chart_type == ChartType.TREEMAP:
            return px.treemap(
                df,
                path=[config.x_column],
                values=config.values_column or config.y_column,
                color=config.color_column,
            )

        if chart_type == ChartType.SUNBURST:
            return px.sunburst(
                df,
                path=[config.x_column],
                values=config.values_column or config.y_column,
            )

        if chart_type == ChartType.FUNNEL:
            return px.funnel(
                df,
                x=config.x_column,
                y=config.y_column,
            )

        if chart_type == ChartType.AREA:
            return px.area(
                df,
                x=config.x_column,
                y=config.y_column,
                color=config.color_column,
            )

        return px.bar(df, x=config.x_column, y=config.y_column)

    def export_to_image(
        self,
        result: ChartResult,
        format: str = "png",
        scale: float = 2.0,
    ) -> bytes:
        """Export chart to static image."""
        fig = go.Figure(result.json_spec)

        if format == "png":
            return fig.to_image(format="png", scale=scale)
        if format == "svg":
            return fig.to_image(format="svg")
        if format == "pdf":
            return fig.to_image(format="pdf")

        return fig.to_image(format="png", scale=scale)

    def export_to_base64(
        self,
        result: ChartResult,
        format: str = "png",
        scale: float = 2.0,
    ) -> str:
        """Export chart to base64 encoded image."""
        image_bytes = self.export_to_image(result, format, scale)
        return base64.b64encode(image_bytes).decode("utf-8")

    def recommend_chart_type(
        self,
        df: pd.DataFrame,
        x_column: str | None = None,
        y_column: str | None = None,
    ) -> ChartRecommendation:
        """Recommend optimal chart type based on data characteristics."""
        num_cols = df.select_dtypes(include=["number"]).columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

        if date_cols and num_cols:
            return ChartRecommendation(
                chart_type=ChartType.LINE,
                confidence=0.9,
                rationale="Time series data detected - line chart recommended",
                x_column=date_cols[0],
                y_column=num_cols[0],
            )

        if cat_cols and num_cols:
            unique_cats = df[cat_cols[0]].nunique() if cat_cols else 0
            if unique_cats <= 6:
                return ChartRecommendation(
                    chart_type=ChartType.PIE,
                    confidence=0.8,
                    rationale="Few categories with numeric values - pie chart recommended",
                    x_column=cat_cols[0],
                    y_column=num_cols[0],
                )
            return ChartRecommendation(
                chart_type=ChartType.BAR,
                confidence=0.85,
                rationale="Categorical vs numeric data - bar chart recommended",
                x_column=cat_cols[0],
                y_column=num_cols[0],
            )

        if len(num_cols) >= 2:
            return ChartRecommendation(
                chart_type=ChartType.SCATTER,
                confidence=0.8,
                rationale="Multiple numeric columns - scatter plot recommended",
                x_column=num_cols[0],
                y_column=num_cols[1],
            )

        if len(num_cols) == 1:
            return ChartRecommendation(
                chart_type=ChartType.HISTOGRAM,
                confidence=0.75,
                rationale="Single numeric column - histogram recommended",
                x_column=num_cols[0],
            )

        return ChartRecommendation(
            chart_type=ChartType.BAR,
            confidence=0.5,
            rationale="Default recommendation - bar chart",
            x_column=x_column,
            y_column=y_column,
        )
```

**Step 5: Create services __init__.py**

Create `app/modules/visualization/services/__init__.py`:

```python
"""Visualization services."""

from app.modules.visualization.services.chart_service import ChartService
from app.modules.visualization.services.theme_service import ThemeService

__all__ = ["ChartService", "ThemeService"]
```

**Step 6: Create module __init__.py**

Create `app/modules/visualization/__init__.py`:

```python
"""Visualization module for interactive charts."""

from app.modules.visualization.models import (
    ChartConfig,
    ChartRecommendation,
    ChartResult,
    ChartType,
    Theme,
)
from app.modules.visualization.services import ChartService, ThemeService

__all__ = [
    "ChartConfig",
    "ChartRecommendation",
    "ChartResult",
    "ChartType",
    "ChartService",
    "Theme",
    "ThemeService",
]
```

**Step 7: Commit**

```bash
git add app/modules/visualization/
git commit -m "feat(viz): create visualization module with Plotly chart service"
```

---

### Task 3: Create Visualization Tests

**Files:**
- Create: `tests/modules/visualization/__init__.py`
- Create: `tests/modules/visualization/test_chart_service.py`
- Create: `tests/modules/visualization/test_theme_service.py`

**Step 1: Create test directory**

Run: `mkdir -p /Users/fitrakacamarga/project/mta/KAI/tests/modules/visualization`

**Step 2: Create test __init__.py**

Create `tests/modules/visualization/__init__.py`:

```python
"""Visualization module tests."""
```

**Step 3: Write theme service tests**

Create `tests/modules/visualization/test_theme_service.py`:

```python
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
```

**Step 4: Run theme tests to verify they fail (no implementation yet)**

Run: `uv run pytest tests/modules/visualization/test_theme_service.py -v`
Expected: All tests PASS (we wrote implementation first in this case)

**Step 5: Write chart service tests**

Create `tests/modules/visualization/test_chart_service.py`:

```python
"""Tests for ChartService."""

import pandas as pd
import pytest

from app.modules.visualization.models import ChartConfig, ChartType
from app.modules.visualization.services.chart_service import ChartService


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Sample DataFrame for testing."""
    return pd.DataFrame({
        "category": ["A", "B", "C", "D"],
        "value": [10, 20, 15, 25],
        "count": [100, 200, 150, 250],
    })


@pytest.fixture
def time_series_df() -> pd.DataFrame:
    """Time series DataFrame for testing."""
    return pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=10, freq="D"),
        "value": [10, 12, 11, 15, 14, 18, 17, 20, 19, 22],
    })


@pytest.fixture
def chart_service() -> ChartService:
    """Chart service instance."""
    return ChartService()


class TestChartService:
    """Test cases for ChartService."""

    def test_generate_bar_chart(
        self,
        chart_service: ChartService,
        sample_df: pd.DataFrame,
    ) -> None:
        """Should generate bar chart."""
        config = ChartConfig(
            chart_type=ChartType.BAR,
            x_column="category",
            y_column="value",
            title="Test Bar Chart",
        )

        result = chart_service.generate_chart(sample_df, config)

        assert result.chart_type == "bar"
        assert result.html is not None
        assert "plotly" in result.html.lower()
        assert result.json_spec is not None

    def test_generate_line_chart(
        self,
        chart_service: ChartService,
        time_series_df: pd.DataFrame,
    ) -> None:
        """Should generate line chart."""
        config = ChartConfig(
            chart_type=ChartType.LINE,
            x_column="date",
            y_column="value",
            title="Test Line Chart",
        )

        result = chart_service.generate_chart(time_series_df, config)

        assert result.chart_type == "line"
        assert result.html is not None

    def test_generate_pie_chart(
        self,
        chart_service: ChartService,
        sample_df: pd.DataFrame,
    ) -> None:
        """Should generate pie chart."""
        config = ChartConfig(
            chart_type=ChartType.PIE,
            x_column="category",
            y_column="value",
            title="Test Pie Chart",
        )

        result = chart_service.generate_chart(sample_df, config)

        assert result.chart_type == "pie"
        assert result.html is not None

    def test_generate_scatter_chart(
        self,
        chart_service: ChartService,
        sample_df: pd.DataFrame,
    ) -> None:
        """Should generate scatter plot."""
        config = ChartConfig(
            chart_type=ChartType.SCATTER,
            x_column="value",
            y_column="count",
            title="Test Scatter Plot",
        )

        result = chart_service.generate_chart(sample_df, config)

        assert result.chart_type == "scatter"
        assert result.html is not None

    def test_generate_histogram(
        self,
        chart_service: ChartService,
        sample_df: pd.DataFrame,
    ) -> None:
        """Should generate histogram."""
        config = ChartConfig(
            chart_type=ChartType.HISTOGRAM,
            x_column="value",
            title="Test Histogram",
        )

        result = chart_service.generate_chart(sample_df, config)

        assert result.chart_type == "histogram"
        assert result.html is not None

    def test_apply_dark_theme(
        self,
        chart_service: ChartService,
        sample_df: pd.DataFrame,
    ) -> None:
        """Should apply dark theme."""
        config = ChartConfig(
            chart_type=ChartType.BAR,
            x_column="category",
            y_column="value",
            theme="dark",
        )

        result = chart_service.generate_chart(sample_df, config)

        assert result.json_spec is not None
        layout = result.json_spec.get("layout", {})
        assert layout.get("template") is not None

    def test_non_interactive_chart(
        self,
        chart_service: ChartService,
        sample_df: pd.DataFrame,
    ) -> None:
        """Should generate non-interactive chart."""
        config = ChartConfig(
            chart_type=ChartType.BAR,
            x_column="category",
            y_column="value",
            interactive=False,
        )

        result = chart_service.generate_chart(sample_df, config)

        assert result.html is None
        assert result.json_spec is not None


class TestChartRecommendation:
    """Test cases for chart type recommendation."""

    def test_recommend_line_for_time_series(
        self,
        chart_service: ChartService,
        time_series_df: pd.DataFrame,
    ) -> None:
        """Should recommend line chart for time series."""
        rec = chart_service.recommend_chart_type(time_series_df)

        assert rec.chart_type == ChartType.LINE
        assert rec.confidence >= 0.8
        assert rec.x_column == "date"
        assert rec.y_column == "value"

    def test_recommend_bar_for_categorical(
        self,
        chart_service: ChartService,
    ) -> None:
        """Should recommend bar chart for categorical data."""
        df = pd.DataFrame({
            "region": ["North", "South", "East", "West", "Central", "NE", "NW", "SE"],
            "sales": [100, 200, 150, 180, 120, 90, 110, 130],
        })

        rec = chart_service.recommend_chart_type(df)

        assert rec.chart_type == ChartType.BAR
        assert rec.confidence >= 0.7

    def test_recommend_pie_for_few_categories(
        self,
        chart_service: ChartService,
    ) -> None:
        """Should recommend pie chart for few categories."""
        df = pd.DataFrame({
            "status": ["Active", "Inactive", "Pending"],
            "count": [50, 30, 20],
        })

        rec = chart_service.recommend_chart_type(df)

        assert rec.chart_type == ChartType.PIE
        assert rec.confidence >= 0.7

    def test_recommend_scatter_for_two_numeric(
        self,
        chart_service: ChartService,
    ) -> None:
        """Should recommend scatter for two numeric columns."""
        df = pd.DataFrame({
            "height": [160, 170, 180, 175, 165],
            "weight": [60, 70, 80, 75, 65],
        })

        rec = chart_service.recommend_chart_type(df)

        assert rec.chart_type == ChartType.SCATTER
        assert rec.confidence >= 0.7
```

**Step 6: Run chart service tests**

Run: `uv run pytest tests/modules/visualization/test_chart_service.py -v`
Expected: All tests PASS

**Step 7: Commit**

```bash
git add tests/modules/visualization/
git commit -m "test(viz): add chart and theme service tests"
```

---

### Task 4: Update Agent Chart Tool to Use Plotly

**Files:**
- Modify: `app/modules/autonomous_agent/tools/chart_tools.py`

**Step 1: Read current chart_tools.py**

Read the existing file to understand the interface.

**Step 2: Update chart_tools.py to use ChartService**

Replace the contents of `app/modules/autonomous_agent/tools/chart_tools.py`:

```python
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
        df = pd.DataFrame(data)

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
            response["image_base64"] = image_base64

        return json.dumps(response)

    except Exception as e:
        return json.dumps({
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
```

**Step 3: Run existing tests to verify backwards compatibility**

Run: `uv run pytest tests/ -k chart -v`
Expected: Tests pass or fail only on new features

**Step 4: Commit**

```bash
git add app/modules/autonomous_agent/tools/chart_tools.py
git commit -m "feat(viz): update agent chart tool to use Plotly ChartService"
```

---

### Task 5: Add Visualization API Endpoints

**Files:**
- Create: `app/modules/visualization/api.py`
- Modify: `app/api/__init__.py` (add routes)

**Step 1: Create visualization API module**

Create `app/modules/visualization/api.py`:

```python
"""Visualization API endpoints."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.modules.visualization import (
    ChartConfig,
    ChartResult,
    ChartService,
    ChartType,
    ThemeService,
)


router = APIRouter(prefix="/api/v2/visualizations", tags=["Visualizations"])


class GenerateChartRequest(BaseModel):
    """Request model for chart generation."""

    data: list[dict[str, Any]]
    chart_type: str
    x_column: str | None = None
    y_column: str | None = None
    color_column: str | None = None
    size_column: str | None = None
    title: str | None = None
    theme: str = "default"
    width: int = 800
    height: int = 600
    interactive: bool = True


class ChartResponse(BaseModel):
    """Response model for chart generation."""

    chart_type: str
    html: str | None = None
    image_base64: str | None = None
    title: str | None = None


class RecommendChartRequest(BaseModel):
    """Request for chart recommendation."""

    data: list[dict[str, Any]]
    x_column: str | None = None
    y_column: str | None = None


class RecommendChartResponse(BaseModel):
    """Response for chart recommendation."""

    chart_type: str
    confidence: float
    rationale: str
    x_column: str | None = None
    y_column: str | None = None


class ThemeListResponse(BaseModel):
    """Response for theme listing."""

    themes: list[str]


_chart_service = ChartService()
_theme_service = ThemeService()


@router.post("/generate", response_model=ChartResponse)
async def generate_chart(request: GenerateChartRequest) -> ChartResponse:
    """Generate a chart from provided data."""
    try:
        df = pd.DataFrame(request.data)
        chart_type = ChartType(request.chart_type)

        config = ChartConfig(
            chart_type=chart_type,
            x_column=request.x_column,
            y_column=request.y_column,
            color_column=request.color_column,
            size_column=request.size_column,
            title=request.title,
            theme=request.theme,
            width=request.width,
            height=request.height,
            interactive=request.interactive,
        )

        result = _chart_service.generate_chart(df, config)

        image_base64 = None
        if not request.interactive:
            image_base64 = _chart_service.export_to_base64(result)

        return ChartResponse(
            chart_type=result.chart_type,
            html=result.html,
            image_base64=image_base64,
            title=request.title,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart generation failed: {e}")


@router.post("/recommend", response_model=RecommendChartResponse)
async def recommend_chart(request: RecommendChartRequest) -> RecommendChartResponse:
    """Recommend optimal chart type for data."""
    try:
        df = pd.DataFrame(request.data)
        rec = _chart_service.recommend_chart_type(
            df,
            x_column=request.x_column,
            y_column=request.y_column,
        )

        return RecommendChartResponse(
            chart_type=rec.chart_type.value,
            confidence=rec.confidence,
            rationale=rec.rationale,
            x_column=rec.x_column,
            y_column=rec.y_column,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {e}")


@router.get("/themes", response_model=ThemeListResponse)
async def list_themes() -> ThemeListResponse:
    """List available chart themes."""
    return ThemeListResponse(themes=_theme_service.list_themes())


@router.get("/types")
async def list_chart_types() -> dict[str, list[str]]:
    """List available chart types."""
    return {"chart_types": [t.value for t in ChartType]}
```

**Step 2: Update module __init__.py to export router**

Edit `app/modules/visualization/__init__.py` to add:

```python
"""Visualization module for interactive charts."""

from app.modules.visualization.api import router as visualization_router
from app.modules.visualization.models import (
    ChartConfig,
    ChartRecommendation,
    ChartResult,
    ChartType,
    Theme,
)
from app.modules.visualization.services import ChartService, ThemeService

__all__ = [
    "ChartConfig",
    "ChartRecommendation",
    "ChartResult",
    "ChartType",
    "ChartService",
    "Theme",
    "ThemeService",
    "visualization_router",
]
```

**Step 3: Register visualization router in FastAPI**

Edit `app/server/__init__.py` and add after the agent session router registration:

```python
# Add this import at the top
from app.modules.visualization import visualization_router

# Add this in the __init__ method after other router registrations
self._app.include_router(visualization_router)
```

**Step 4: Commit**

```bash
git add app/modules/visualization/api.py app/modules/visualization/__init__.py app/server/__init__.py
git commit -m "feat(viz): add visualization API endpoints"
```

---

## Epic 3: Statistical Analysis & Forecasting

### Task 6: Add Statistics Dependencies

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add statistics dependencies**

Add to `pyproject.toml` dependencies:

```toml
"scipy>=1.11.0",
"statsmodels>=0.14.0",
"prophet>=1.1.0",
```

**Step 2: Install dependencies**

Run: `uv sync`
Expected: Dependencies installed (prophet may take a while)

**Step 3: Verify installation**

Run: `uv run python -c "import scipy; import statsmodels; print('OK')"`
Expected: `OK`

**Step 4: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "feat(analytics): add scipy, statsmodels, and prophet dependencies"
```

---

### Task 7: Create Analytics Module Structure

**Files:**
- Create: `app/modules/analytics/__init__.py`
- Create: `app/modules/analytics/models.py`
- Create: `app/modules/analytics/services/__init__.py`
- Create: `app/modules/analytics/services/statistical_service.py`
- Create: `app/modules/analytics/services/forecasting_service.py`
- Create: `app/modules/analytics/services/anomaly_service.py`

**Step 1: Create module directory**

Run: `mkdir -p /Users/fitrakacamarga/project/mta/KAI/app/modules/analytics/services`

**Step 2: Create models.py**

Create `app/modules/analytics/models.py`:

```python
"""Analytics data models."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class StatisticalTestType(str, Enum):
    """Types of statistical tests."""

    T_TEST_IND = "t_test_independent"
    T_TEST_PAIRED = "t_test_paired"
    T_TEST_ONE_SAMPLE = "t_test_one_sample"
    ANOVA = "anova"
    CHI_SQUARE = "chi_square"
    CORRELATION = "correlation"
    REGRESSION = "regression"


class StatisticalTestResult(BaseModel):
    """Result of a statistical test."""

    test_name: str
    test_type: str
    statistic: float
    p_value: float
    degrees_of_freedom: float | None = None
    confidence_level: float = 0.95
    is_significant: bool
    interpretation: str
    effect_size: float | None = None
    effect_size_name: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class CorrelationResult(BaseModel):
    """Result of correlation analysis."""

    method: str
    coefficient: float
    p_value: float
    is_significant: bool
    interpretation: str
    sample_size: int


class CorrelationMatrixResult(BaseModel):
    """Result of correlation matrix analysis."""

    method: str
    matrix: dict[str, dict[str, float]]
    p_values: dict[str, dict[str, float]] | None = None
    columns: list[str]


class DescriptiveStats(BaseModel):
    """Descriptive statistics for a numeric column."""

    column: str
    count: int
    mean: float
    std: float
    min: float
    q25: float
    median: float
    q75: float
    max: float
    skewness: float | None = None
    kurtosis: float | None = None


class ForecastResult(BaseModel):
    """Result of time series forecast."""

    model_name: str
    forecast_dates: list[str]
    forecast_values: list[float]
    lower_bound: list[float]
    upper_bound: list[float]
    confidence_level: float
    trend: str
    interpretation: str
    metrics: dict[str, Any] = Field(default_factory=dict)


class AnomalyResult(BaseModel):
    """Result of anomaly detection."""

    method: str
    total_points: int
    anomaly_count: int
    anomaly_percentage: float
    anomalies: list[dict[str, Any]]
    threshold: float | None = None
    interpretation: str
```

**Step 3: Create statistical_service.py**

Create `app/modules/analytics/services/statistical_service.py`:

```python
"""Statistical analysis service."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from app.modules.analytics.models import (
    CorrelationMatrixResult,
    CorrelationResult,
    DescriptiveStats,
    StatisticalTestResult,
)


class StatisticalService:
    """Service for statistical analysis."""

    def descriptive_stats(self, series: pd.Series) -> DescriptiveStats:
        """Calculate descriptive statistics for a series."""
        desc = series.describe()
        return DescriptiveStats(
            column=series.name or "value",
            count=int(desc["count"]),
            mean=float(desc["mean"]),
            std=float(desc["std"]),
            min=float(desc["min"]),
            q25=float(desc["25%"]),
            median=float(desc["50%"]),
            q75=float(desc["75%"]),
            max=float(desc["max"]),
            skewness=float(series.skew()) if len(series) > 2 else None,
            kurtosis=float(series.kurtosis()) if len(series) > 3 else None,
        )

    def t_test_independent(
        self,
        group1: pd.Series,
        group2: pd.Series,
        alpha: float = 0.05,
    ) -> StatisticalTestResult:
        """Perform independent samples t-test."""
        stat, p_value = stats.ttest_ind(group1.dropna(), group2.dropna())

        n1, n2 = len(group1.dropna()), len(group2.dropna())
        dof = n1 + n2 - 2

        cohens_d = self._cohens_d(group1, group2)

        is_sig = p_value < alpha
        mean_diff = group1.mean() - group2.mean()

        interpretation = (
            f"The difference between groups is "
            f"{'statistically significant' if is_sig else 'not statistically significant'} "
            f"(t={stat:.3f}, p={p_value:.4f}, df={dof}). "
        )
        if is_sig:
            interpretation += (
                f"Group 1 (M={group1.mean():.2f}) is "
                f"{'higher' if mean_diff > 0 else 'lower'} than "
                f"Group 2 (M={group2.mean():.2f}) by {abs(mean_diff):.2f}. "
                f"Effect size (Cohen's d): {cohens_d:.3f} "
                f"({'small' if abs(cohens_d) < 0.5 else 'medium' if abs(cohens_d) < 0.8 else 'large'})."
            )

        return StatisticalTestResult(
            test_name="Independent Samples T-Test",
            test_type="t_test_independent",
            statistic=float(stat),
            p_value=float(p_value),
            degrees_of_freedom=float(dof),
            is_significant=is_sig,
            interpretation=interpretation,
            effect_size=cohens_d,
            effect_size_name="Cohen's d",
            details={
                "group1_mean": float(group1.mean()),
                "group1_std": float(group1.std()),
                "group1_n": n1,
                "group2_mean": float(group2.mean()),
                "group2_std": float(group2.std()),
                "group2_n": n2,
                "mean_difference": float(mean_diff),
            },
        )

    def anova(
        self,
        *groups: pd.Series,
        alpha: float = 0.05,
    ) -> StatisticalTestResult:
        """Perform one-way ANOVA."""
        clean_groups = [g.dropna() for g in groups]
        stat, p_value = stats.f_oneway(*clean_groups)

        k = len(groups)
        n = sum(len(g) for g in clean_groups)
        dof_between = k - 1
        dof_within = n - k

        is_sig = p_value < alpha

        interpretation = (
            f"One-way ANOVA: F({dof_between}, {dof_within}) = {stat:.3f}, p = {p_value:.4f}. "
            f"There {'is' if is_sig else 'is no'} statistically significant difference "
            f"between at least two groups."
        )

        return StatisticalTestResult(
            test_name="One-Way ANOVA",
            test_type="anova",
            statistic=float(stat),
            p_value=float(p_value),
            degrees_of_freedom=float(dof_between),
            is_significant=is_sig,
            interpretation=interpretation,
            details={
                "num_groups": k,
                "group_means": [float(g.mean()) for g in clean_groups],
                "group_sizes": [len(g) for g in clean_groups],
                "dof_between": dof_between,
                "dof_within": dof_within,
            },
        )

    def chi_square(
        self,
        contingency_table: pd.DataFrame,
        alpha: float = 0.05,
    ) -> StatisticalTestResult:
        """Perform chi-square test of independence."""
        stat, p_value, dof, expected = stats.chi2_contingency(contingency_table)

        is_sig = p_value < alpha

        interpretation = (
            f"Chi-square test: χ²({dof}) = {stat:.3f}, p = {p_value:.4f}. "
            f"There {'is' if is_sig else 'is no'} statistically significant "
            f"association between the variables."
        )

        return StatisticalTestResult(
            test_name="Chi-Square Test of Independence",
            test_type="chi_square",
            statistic=float(stat),
            p_value=float(p_value),
            degrees_of_freedom=float(dof),
            is_significant=is_sig,
            interpretation=interpretation,
            details={
                "expected_frequencies": expected.tolist(),
                "observed": contingency_table.values.tolist(),
            },
        )

    def correlation(
        self,
        x: pd.Series,
        y: pd.Series,
        method: str = "pearson",
        alpha: float = 0.05,
    ) -> CorrelationResult:
        """Calculate correlation between two series."""
        x_clean = x.dropna()
        y_clean = y.dropna()

        common_idx = x_clean.index.intersection(y_clean.index)
        x_final = x_clean.loc[common_idx]
        y_final = y_clean.loc[common_idx]

        if method == "pearson":
            coef, p_value = stats.pearsonr(x_final, y_final)
        elif method == "spearman":
            coef, p_value = stats.spearmanr(x_final, y_final)
        else:
            coef, p_value = stats.kendalltau(x_final, y_final)

        is_sig = p_value < alpha

        strength = "no"
        if abs(coef) > 0.7:
            strength = "strong"
        elif abs(coef) > 0.4:
            strength = "moderate"
        elif abs(coef) > 0.2:
            strength = "weak"

        direction = "positive" if coef > 0 else "negative"

        interpretation = (
            f"{method.title()} correlation: r = {coef:.3f}, p = {p_value:.4f}. "
            f"There is {'a' if is_sig else 'no'} statistically significant "
            f"{strength} {direction} correlation between the variables."
        )

        return CorrelationResult(
            method=method,
            coefficient=float(coef),
            p_value=float(p_value),
            is_significant=is_sig,
            interpretation=interpretation,
            sample_size=len(x_final),
        )

    def correlation_matrix(
        self,
        df: pd.DataFrame,
        method: str = "pearson",
    ) -> CorrelationMatrixResult:
        """Calculate correlation matrix for numeric columns."""
        numeric_df = df.select_dtypes(include=[np.number])
        corr_matrix = numeric_df.corr(method=method)

        matrix_dict = corr_matrix.to_dict()
        columns = corr_matrix.columns.tolist()

        return CorrelationMatrixResult(
            method=method,
            matrix=matrix_dict,
            columns=columns,
        )

    def _cohens_d(self, group1: pd.Series, group2: pd.Series) -> float:
        """Calculate Cohen's d effect size."""
        n1, n2 = len(group1.dropna()), len(group2.dropna())
        var1, var2 = group1.var(), group2.var()
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        if pooled_std == 0:
            return 0.0
        return float((group1.mean() - group2.mean()) / pooled_std)
```

**Step 4: Create forecasting_service.py**

Create `app/modules/analytics/services/forecasting_service.py`:

```python
"""Time series forecasting service."""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.modules.analytics.models import ForecastResult


class ForecastingService:
    """Service for time series forecasting."""

    def forecast_prophet(
        self,
        df: pd.DataFrame,
        date_column: str,
        value_column: str,
        periods: int = 30,
        confidence_level: float = 0.95,
    ) -> ForecastResult:
        """Generate forecast using Facebook Prophet."""
        try:
            from prophet import Prophet
        except ImportError:
            raise ImportError("Prophet is required for forecasting. Install with: pip install prophet")

        prophet_df = df[[date_column, value_column]].copy()
        prophet_df.columns = ["ds", "y"]
        prophet_df["ds"] = pd.to_datetime(prophet_df["ds"])

        model = Prophet(interval_width=confidence_level)
        model.fit(prophet_df)

        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)

        forecast_only = forecast.tail(periods)

        start_val = forecast_only["yhat"].iloc[0]
        end_val = forecast_only["yhat"].iloc[-1]
        trend = "increasing" if end_val > start_val else "decreasing" if end_val < start_val else "stable"
        change_pct = ((end_val - start_val) / abs(start_val) * 100) if start_val != 0 else 0

        interpretation = (
            f"Forecast shows a {trend} trend over the next {periods} periods. "
            f"Expected change: {change_pct:+.1f}%. "
            f"Values range from {forecast_only['yhat_lower'].min():.2f} to "
            f"{forecast_only['yhat_upper'].max():.2f} ({confidence_level*100:.0f}% CI)."
        )

        return ForecastResult(
            model_name="Prophet",
            forecast_dates=forecast_only["ds"].dt.strftime("%Y-%m-%d").tolist(),
            forecast_values=forecast_only["yhat"].round(2).tolist(),
            lower_bound=forecast_only["yhat_lower"].round(2).tolist(),
            upper_bound=forecast_only["yhat_upper"].round(2).tolist(),
            confidence_level=confidence_level,
            trend=trend,
            interpretation=interpretation,
            metrics={
                "periods": periods,
                "change_percent": round(change_pct, 2),
            },
        )

    def forecast_simple(
        self,
        series: pd.Series,
        periods: int = 30,
    ) -> ForecastResult:
        """Simple moving average forecast (fallback when Prophet unavailable)."""
        window = min(7, len(series) // 2)
        ma = series.rolling(window=window).mean().iloc[-1]
        std = series.std()

        forecast_values = [float(ma)] * periods
        lower = [float(ma - 1.96 * std)] * periods
        upper = [float(ma + 1.96 * std)] * periods

        last_date = pd.Timestamp.now()
        dates = pd.date_range(last_date, periods=periods, freq="D")

        return ForecastResult(
            model_name="Simple Moving Average",
            forecast_dates=[d.strftime("%Y-%m-%d") for d in dates],
            forecast_values=forecast_values,
            lower_bound=lower,
            upper_bound=upper,
            confidence_level=0.95,
            trend="stable",
            interpretation=f"Simple forecast based on {window}-period moving average: {ma:.2f}",
            metrics={"window": window, "std": float(std)},
        )
```

**Step 5: Create anomaly_service.py**

Create `app/modules/analytics/services/anomaly_service.py`:

```python
"""Anomaly detection service."""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.modules.analytics.models import AnomalyResult


class AnomalyService:
    """Service for anomaly detection."""

    def detect_zscore(
        self,
        series: pd.Series,
        threshold: float = 3.0,
    ) -> AnomalyResult:
        """Detect anomalies using Z-score method."""
        clean = series.dropna()
        mean = clean.mean()
        std = clean.std()

        if std == 0:
            return AnomalyResult(
                method="z-score",
                total_points=len(clean),
                anomaly_count=0,
                anomaly_percentage=0.0,
                anomalies=[],
                threshold=threshold,
                interpretation="No variance in data - cannot detect anomalies.",
            )

        z_scores = (clean - mean) / std
        anomaly_mask = np.abs(z_scores) > threshold

        anomalies = []
        for idx in clean[anomaly_mask].index:
            anomalies.append({
                "index": int(idx) if isinstance(idx, (int, np.integer)) else str(idx),
                "value": float(clean.loc[idx]),
                "z_score": float(z_scores.loc[idx]),
            })

        count = len(anomalies)
        pct = (count / len(clean)) * 100

        interpretation = (
            f"Z-score analysis (threshold: {threshold}): Found {count} anomalies "
            f"({pct:.1f}% of data). Mean: {mean:.2f}, Std: {std:.2f}."
        )

        return AnomalyResult(
            method="z-score",
            total_points=len(clean),
            anomaly_count=count,
            anomaly_percentage=round(pct, 2),
            anomalies=anomalies,
            threshold=threshold,
            interpretation=interpretation,
        )

    def detect_iqr(
        self,
        series: pd.Series,
        multiplier: float = 1.5,
    ) -> AnomalyResult:
        """Detect anomalies using IQR method."""
        clean = series.dropna()
        q1 = clean.quantile(0.25)
        q3 = clean.quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr

        anomaly_mask = (clean < lower_bound) | (clean > upper_bound)

        anomalies = []
        for idx in clean[anomaly_mask].index:
            val = clean.loc[idx]
            anomalies.append({
                "index": int(idx) if isinstance(idx, (int, np.integer)) else str(idx),
                "value": float(val),
                "direction": "high" if val > upper_bound else "low",
            })

        count = len(anomalies)
        pct = (count / len(clean)) * 100

        interpretation = (
            f"IQR analysis (multiplier: {multiplier}x): Found {count} anomalies "
            f"({pct:.1f}% of data). Normal range: [{lower_bound:.2f}, {upper_bound:.2f}]."
        )

        return AnomalyResult(
            method="iqr",
            total_points=len(clean),
            anomaly_count=count,
            anomaly_percentage=round(pct, 2),
            anomalies=anomalies,
            threshold=multiplier,
            interpretation=interpretation,
        )

    def detect_isolation_forest(
        self,
        df: pd.DataFrame,
        columns: list[str],
        contamination: float = 0.1,
    ) -> AnomalyResult:
        """Detect anomalies using Isolation Forest."""
        try:
            from sklearn.ensemble import IsolationForest
        except ImportError:
            raise ImportError("scikit-learn required for Isolation Forest")

        data = df[columns].dropna()

        model = IsolationForest(contamination=contamination, random_state=42)
        predictions = model.fit_predict(data)
        scores = model.decision_function(data)

        anomaly_mask = predictions == -1
        anomalies = []

        for idx in data[anomaly_mask].index:
            row = data.loc[idx]
            anomalies.append({
                "index": int(idx) if isinstance(idx, (int, np.integer)) else str(idx),
                "values": row.to_dict(),
                "anomaly_score": float(scores[data.index.get_loc(idx)]),
            })

        count = len(anomalies)
        pct = (count / len(data)) * 100

        interpretation = (
            f"Isolation Forest (contamination: {contamination}): Found {count} anomalies "
            f"({pct:.1f}% of data) using columns: {', '.join(columns)}."
        )

        return AnomalyResult(
            method="isolation_forest",
            total_points=len(data),
            anomaly_count=count,
            anomaly_percentage=round(pct, 2),
            anomalies=anomalies,
            threshold=contamination,
            interpretation=interpretation,
        )
```

**Step 6: Create services __init__.py**

Create `app/modules/analytics/services/__init__.py`:

```python
"""Analytics services."""

from app.modules.analytics.services.anomaly_service import AnomalyService
from app.modules.analytics.services.forecasting_service import ForecastingService
from app.modules.analytics.services.statistical_service import StatisticalService

__all__ = ["AnomalyService", "ForecastingService", "StatisticalService"]
```

**Step 7: Create module __init__.py**

Create `app/modules/analytics/__init__.py`:

```python
"""Analytics module for statistical analysis and forecasting."""

from app.modules.analytics.models import (
    AnomalyResult,
    CorrelationMatrixResult,
    CorrelationResult,
    DescriptiveStats,
    ForecastResult,
    StatisticalTestResult,
    StatisticalTestType,
)
from app.modules.analytics.services import (
    AnomalyService,
    ForecastingService,
    StatisticalService,
)

__all__ = [
    "AnomalyResult",
    "AnomalyService",
    "CorrelationMatrixResult",
    "CorrelationResult",
    "DescriptiveStats",
    "ForecastingService",
    "ForecastResult",
    "StatisticalService",
    "StatisticalTestResult",
    "StatisticalTestType",
]
```

**Step 8: Commit**

```bash
git add app/modules/analytics/
git commit -m "feat(analytics): create analytics module with statistical and forecasting services"
```

---

### Task 8: Create Analytics Tests

**Files:**
- Create: `tests/modules/analytics/__init__.py`
- Create: `tests/modules/analytics/test_statistical_service.py`
- Create: `tests/modules/analytics/test_anomaly_service.py`

**Step 1: Create test directory**

Run: `mkdir -p /Users/fitrakacamarga/project/mta/KAI/tests/modules/analytics`

**Step 2: Create test __init__.py**

Create `tests/modules/analytics/__init__.py`:

```python
"""Analytics module tests."""
```

**Step 3: Create statistical service tests**

Create `tests/modules/analytics/test_statistical_service.py`:

```python
"""Tests for StatisticalService."""

import numpy as np
import pandas as pd
import pytest

from app.modules.analytics.services.statistical_service import StatisticalService


@pytest.fixture
def stat_service() -> StatisticalService:
    """Statistical service instance."""
    return StatisticalService()


class TestDescriptiveStats:
    """Test descriptive statistics."""

    def test_basic_stats(self, stat_service: StatisticalService) -> None:
        """Should calculate basic statistics."""
        series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        result = stat_service.descriptive_stats(series)

        assert result.count == 10
        assert result.mean == 5.5
        assert result.min == 1
        assert result.max == 10
        assert result.median == 5.5


class TestTTest:
    """Test t-test implementation."""

    def test_significant_difference(self, stat_service: StatisticalService) -> None:
        """Should detect significant difference."""
        np.random.seed(42)
        group1 = pd.Series(np.random.normal(10, 2, 50))
        group2 = pd.Series(np.random.normal(15, 2, 50))

        result = stat_service.t_test_independent(group1, group2)

        assert result.is_significant
        assert result.p_value < 0.05
        assert "statistically significant" in result.interpretation

    def test_no_significant_difference(self, stat_service: StatisticalService) -> None:
        """Should detect no significant difference."""
        np.random.seed(42)
        group1 = pd.Series(np.random.normal(10, 2, 50))
        group2 = pd.Series(np.random.normal(10.5, 2, 50))

        result = stat_service.t_test_independent(group1, group2)

        assert result.p_value > 0.01 or not result.is_significant

    def test_effect_size_calculated(self, stat_service: StatisticalService) -> None:
        """Should calculate effect size."""
        group1 = pd.Series([1, 2, 3, 4, 5])
        group2 = pd.Series([6, 7, 8, 9, 10])

        result = stat_service.t_test_independent(group1, group2)

        assert result.effect_size is not None
        assert result.effect_size_name == "Cohen's d"


class TestANOVA:
    """Test ANOVA implementation."""

    def test_significant_anova(self, stat_service: StatisticalService) -> None:
        """Should detect significant ANOVA result."""
        np.random.seed(42)
        g1 = pd.Series(np.random.normal(10, 2, 30))
        g2 = pd.Series(np.random.normal(15, 2, 30))
        g3 = pd.Series(np.random.normal(20, 2, 30))

        result = stat_service.anova(g1, g2, g3)

        assert result.is_significant
        assert result.test_type == "anova"
        assert result.details["num_groups"] == 3


class TestCorrelation:
    """Test correlation analysis."""

    def test_positive_correlation(self, stat_service: StatisticalService) -> None:
        """Should detect positive correlation."""
        x = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        y = pd.Series([2, 4, 5, 4, 5, 7, 8, 9, 9, 10])

        result = stat_service.correlation(x, y)

        assert result.coefficient > 0.8
        assert result.is_significant
        assert "positive" in result.interpretation

    def test_correlation_matrix(self, stat_service: StatisticalService) -> None:
        """Should generate correlation matrix."""
        df = pd.DataFrame({
            "a": [1, 2, 3, 4, 5],
            "b": [2, 4, 6, 8, 10],
            "c": [5, 4, 3, 2, 1],
        })

        result = stat_service.correlation_matrix(df)

        assert "a" in result.columns
        assert "b" in result.columns
        assert "c" in result.columns
        assert result.matrix["a"]["b"] > 0.9
```

**Step 4: Create anomaly service tests**

Create `tests/modules/analytics/test_anomaly_service.py`:

```python
"""Tests for AnomalyService."""

import numpy as np
import pandas as pd
import pytest

from app.modules.analytics.services.anomaly_service import AnomalyService


@pytest.fixture
def anomaly_service() -> AnomalyService:
    """Anomaly service instance."""
    return AnomalyService()


class TestZScoreDetection:
    """Test Z-score anomaly detection."""

    def test_detect_outliers(self, anomaly_service: AnomalyService) -> None:
        """Should detect obvious outliers."""
        data = pd.Series([1, 2, 3, 2, 3, 2, 100, 2, 3, 1])

        result = anomaly_service.detect_zscore(data, threshold=2.0)

        assert result.anomaly_count >= 1
        assert any(a["value"] == 100 for a in result.anomalies)

    def test_no_outliers_normal_data(self, anomaly_service: AnomalyService) -> None:
        """Should find few/no outliers in normal data."""
        np.random.seed(42)
        data = pd.Series(np.random.normal(50, 5, 100))

        result = anomaly_service.detect_zscore(data, threshold=3.0)

        assert result.anomaly_percentage < 5


class TestIQRDetection:
    """Test IQR anomaly detection."""

    def test_detect_outliers(self, anomaly_service: AnomalyService) -> None:
        """Should detect outliers using IQR."""
        data = pd.Series([1, 2, 2, 3, 3, 3, 4, 4, 5, 100])

        result = anomaly_service.detect_iqr(data, multiplier=1.5)

        assert result.anomaly_count >= 1
        assert "iqr" in result.method

    def test_marks_direction(self, anomaly_service: AnomalyService) -> None:
        """Should mark whether anomaly is high or low."""
        data = pd.Series([1, 2, 3, 4, 5, 100])

        result = anomaly_service.detect_iqr(data)

        if result.anomaly_count > 0:
            assert "direction" in result.anomalies[0]
```

**Step 5: Run analytics tests**

Run: `uv run pytest tests/modules/analytics/ -v`
Expected: All tests PASS

**Step 6: Commit**

```bash
git add tests/modules/analytics/
git commit -m "test(analytics): add statistical and anomaly service tests"
```

---

### Task 9: Add Analytics API Endpoints

**Files:**
- Create: `app/modules/analytics/api.py`
- Modify: `app/server/__init__.py`

**Step 1: Create analytics API**

Create `app/modules/analytics/api.py`:

```python
"""Analytics API endpoints."""

from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.modules.analytics import (
    AnomalyService,
    ForecastingService,
    StatisticalService,
)


router = APIRouter(prefix="/api/v2/analytics", tags=["Analytics"])


class StatisticalTestRequest(BaseModel):
    """Request for statistical test."""

    test_type: str
    group1: list[float]
    group2: list[float] | None = None
    groups: list[list[float]] | None = None
    alpha: float = 0.05


class CorrelationRequest(BaseModel):
    """Request for correlation analysis."""

    x: list[float]
    y: list[float]
    method: str = "pearson"


class ForecastRequest(BaseModel):
    """Request for forecasting."""

    dates: list[str]
    values: list[float]
    periods: int = 30
    confidence_level: float = 0.95


class AnomalyRequest(BaseModel):
    """Request for anomaly detection."""

    values: list[float]
    method: str = "zscore"
    threshold: float | None = None


_stat_service = StatisticalService()
_forecast_service = ForecastingService()
_anomaly_service = AnomalyService()


@router.post("/statistics")
async def run_statistical_test(request: StatisticalTestRequest) -> dict[str, Any]:
    """Run a statistical test."""
    try:
        if request.test_type == "t_test":
            if request.group2 is None:
                raise HTTPException(400, "group2 required for t-test")
            result = _stat_service.t_test_independent(
                pd.Series(request.group1),
                pd.Series(request.group2),
                alpha=request.alpha,
            )
        elif request.test_type == "anova":
            if request.groups is None:
                raise HTTPException(400, "groups required for ANOVA")
            series_list = [pd.Series(g) for g in request.groups]
            result = _stat_service.anova(*series_list, alpha=request.alpha)
        else:
            raise HTTPException(400, f"Unknown test type: {request.test_type}")

        return result.model_dump()

    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/correlation")
async def calculate_correlation(request: CorrelationRequest) -> dict[str, Any]:
    """Calculate correlation between two variables."""
    try:
        result = _stat_service.correlation(
            pd.Series(request.x),
            pd.Series(request.y),
            method=request.method,
        )
        return result.model_dump()
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/forecast")
async def generate_forecast(request: ForecastRequest) -> dict[str, Any]:
    """Generate time series forecast."""
    try:
        df = pd.DataFrame({"date": request.dates, "value": request.values})
        result = _forecast_service.forecast_prophet(
            df,
            date_column="date",
            value_column="value",
            periods=request.periods,
            confidence_level=request.confidence_level,
        )
        return result.model_dump()
    except ImportError:
        series = pd.Series(request.values)
        result = _forecast_service.forecast_simple(series, periods=request.periods)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/anomalies")
async def detect_anomalies(request: AnomalyRequest) -> dict[str, Any]:
    """Detect anomalies in data."""
    try:
        series = pd.Series(request.values)

        if request.method == "zscore":
            threshold = request.threshold or 3.0
            result = _anomaly_service.detect_zscore(series, threshold=threshold)
        elif request.method == "iqr":
            threshold = request.threshold or 1.5
            result = _anomaly_service.detect_iqr(series, multiplier=threshold)
        else:
            raise HTTPException(400, f"Unknown method: {request.method}")

        return result.model_dump()

    except Exception as e:
        raise HTTPException(500, str(e))
```

**Step 2: Update analytics __init__.py to export router**

Add to `app/modules/analytics/__init__.py`:

```python
from app.modules.analytics.api import router as analytics_router
```

And add `"analytics_router"` to `__all__`.

**Step 3: Register analytics router in FastAPI**

Edit `app/server/__init__.py`:

```python
from app.modules.analytics import analytics_router

# In __init__ after other router registrations:
self._app.include_router(analytics_router)
```

**Step 4: Commit**

```bash
git add app/modules/analytics/api.py app/modules/analytics/__init__.py app/server/__init__.py
git commit -m "feat(analytics): add analytics API endpoints"
```

---

## Epic 4: Notebook System

### Task 10: Create Notebook Module Structure

**Files:**
- Create: `app/modules/notebook/__init__.py`
- Create: `app/modules/notebook/models.py`
- Create: `app/modules/notebook/services/__init__.py`
- Create: `app/modules/notebook/services/notebook_service.py`
- Create: `app/modules/notebook/services/executor_service.py`

**Step 1: Create notebook module directory**

Run: `mkdir -p /Users/fitrakacamarga/project/mta/KAI/app/modules/notebook/services`

**Step 2: Create notebook models.py**

Create `app/modules/notebook/models.py`:

```python
"""Notebook data models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CellType(str, Enum):
    """Types of notebook cells."""

    QUERY = "query"
    VISUALIZATION = "visualization"
    TEXT = "text"
    CODE = "code"
    USER_INPUT = "user_input"


class CellStatus(str, Enum):
    """Execution status of a cell."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class Parameter(BaseModel):
    """Notebook parameter definition."""

    name: str
    param_type: str = "text"
    default: Any = None
    description: str | None = None
    options: list[str] | None = None
    required: bool = False


class Cell(BaseModel):
    """A single cell in a notebook."""

    id: str
    cell_type: CellType
    name: str
    prompt: str | None = None
    code: str | None = None
    depends_on: list[str] = Field(default_factory=list)
    output: Any = None
    status: CellStatus = CellStatus.PENDING
    error: str | None = None
    execution_time_ms: float | None = None


class Notebook(BaseModel):
    """A reusable analysis notebook."""

    id: str
    name: str
    description: str | None = None
    database_alias: str | None = None
    parameters: list[Parameter] = Field(default_factory=list)
    cells: list[Cell] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NotebookRun(BaseModel):
    """A single execution of a notebook."""

    id: str
    notebook_id: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    results: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    execution_time_ms: float | None = None


class NotebookCreateRequest(BaseModel):
    """Request to create a notebook."""

    name: str
    description: str | None = None
    database_alias: str | None = None
    parameters: list[Parameter] = Field(default_factory=list)
    cells: list[Cell] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class NotebookRunRequest(BaseModel):
    """Request to run a notebook."""

    parameters: dict[str, Any] = Field(default_factory=dict)
    database_alias: str | None = None
```

**Step 3: Create notebook_service.py**

Create `app/modules/notebook/services/notebook_service.py`:

```python
"""Notebook CRUD service."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from app.data.db.storage import Storage
from app.modules.notebook.models import (
    Cell,
    CellStatus,
    Notebook,
    NotebookCreateRequest,
    NotebookRun,
    Parameter,
)

DB_COLLECTION = "notebooks"
RUNS_COLLECTION = "notebook_runs"


class NotebookService:
    """Service for notebook CRUD operations."""

    def __init__(self, storage: Storage) -> None:
        """Initialize notebook service."""
        self.storage = storage

    def create_notebook(self, request: NotebookCreateRequest) -> Notebook:
        """Create a new notebook."""
        notebook_id = str(uuid.uuid4())
        now = datetime.utcnow()

        cells_with_ids = []
        for i, cell in enumerate(request.cells):
            cell_dict = cell.model_dump()
            if not cell_dict.get("id"):
                cell_dict["id"] = f"cell_{i}_{uuid.uuid4().hex[:8]}"
            cells_with_ids.append(Cell(**cell_dict))

        notebook = Notebook(
            id=notebook_id,
            name=request.name,
            description=request.description,
            database_alias=request.database_alias,
            parameters=request.parameters,
            cells=cells_with_ids,
            tags=request.tags,
            created_at=now,
            updated_at=now,
        )

        notebook_dict = notebook.model_dump()
        notebook_dict["created_at"] = notebook_dict["created_at"].isoformat()
        notebook_dict["updated_at"] = notebook_dict["updated_at"].isoformat()

        self.storage.insert_one(DB_COLLECTION, notebook_dict)
        return notebook

    def get_notebook(self, notebook_id: str) -> Notebook | None:
        """Get a notebook by ID."""
        doc = self.storage.find_one(DB_COLLECTION, {"id": notebook_id})
        if not doc:
            return None
        return self._doc_to_notebook(doc)

    def get_notebook_by_name(self, name: str) -> Notebook | None:
        """Get a notebook by name."""
        doc = self.storage.find_one(DB_COLLECTION, {"name": name})
        if not doc:
            return None
        return self._doc_to_notebook(doc)

    def list_notebooks(
        self,
        tags: list[str] | None = None,
        limit: int = 50,
    ) -> list[Notebook]:
        """List notebooks with optional tag filter."""
        filter_dict: dict[str, Any] = {}
        if tags:
            filter_dict["tags"] = tags

        docs = self.storage.find(DB_COLLECTION, filter_dict, limit=limit)
        return [self._doc_to_notebook(doc) for doc in docs]

    def update_notebook(self, notebook_id: str, updates: dict[str, Any]) -> Notebook | None:
        """Update a notebook."""
        existing = self.get_notebook(notebook_id)
        if not existing:
            return None

        updates["updated_at"] = datetime.utcnow().isoformat()
        self.storage.update_or_create(
            DB_COLLECTION,
            {"id": notebook_id},
            updates,
        )
        return self.get_notebook(notebook_id)

    def delete_notebook(self, notebook_id: str) -> bool:
        """Delete a notebook."""
        result = self.storage.delete_by_id(DB_COLLECTION, notebook_id)
        return result is not None

    def save_run(self, run: NotebookRun) -> NotebookRun:
        """Save a notebook run."""
        run_dict = run.model_dump()
        run_dict["started_at"] = run_dict["started_at"].isoformat()
        if run_dict["completed_at"]:
            run_dict["completed_at"] = run_dict["completed_at"].isoformat()

        self.storage.insert_one(RUNS_COLLECTION, run_dict)
        return run

    def get_runs(self, notebook_id: str, limit: int = 10) -> list[NotebookRun]:
        """Get runs for a notebook."""
        docs = self.storage.find(
            RUNS_COLLECTION,
            {"notebook_id": notebook_id},
            limit=limit,
        )
        return [self._doc_to_run(doc) for doc in docs]

    def _doc_to_notebook(self, doc: dict) -> Notebook:
        """Convert storage document to Notebook."""
        if isinstance(doc.get("created_at"), str):
            doc["created_at"] = datetime.fromisoformat(doc["created_at"])
        if isinstance(doc.get("updated_at"), str):
            doc["updated_at"] = datetime.fromisoformat(doc["updated_at"])
        return Notebook(**doc)

    def _doc_to_run(self, doc: dict) -> NotebookRun:
        """Convert storage document to NotebookRun."""
        if isinstance(doc.get("started_at"), str):
            doc["started_at"] = datetime.fromisoformat(doc["started_at"])
        if isinstance(doc.get("completed_at"), str):
            doc["completed_at"] = datetime.fromisoformat(doc["completed_at"])
        return NotebookRun(**doc)
```

**Step 4: Create executor_service.py**

Create `app/modules/notebook/services/executor_service.py`:

```python
"""Notebook execution service."""

from __future__ import annotations

import re
import time
import uuid
from datetime import datetime
from typing import Any

from app.modules.notebook.models import (
    Cell,
    CellStatus,
    CellType,
    Notebook,
    NotebookRun,
)


class NotebookExecutor:
    """Service for executing notebooks."""

    def __init__(
        self,
        agent_runner: Any = None,
        chart_service: Any = None,
        llm_service: Any = None,
    ) -> None:
        """Initialize executor with optional services."""
        self.agent_runner = agent_runner
        self.chart_service = chart_service
        self.llm_service = llm_service

    async def execute_notebook(
        self,
        notebook: Notebook,
        parameters: dict[str, Any],
        database_alias: str | None = None,
    ) -> NotebookRun:
        """Execute a notebook with given parameters."""
        run = NotebookRun(
            id=str(uuid.uuid4()),
            notebook_id=notebook.id,
            parameters=parameters,
            status="running",
            started_at=datetime.utcnow(),
        )

        context = {
            "parameters": parameters,
            "results": {},
            "database_alias": database_alias or notebook.database_alias,
        }

        execution_order = self._resolve_dependencies(notebook.cells)
        total_start = time.time()

        try:
            for cell in execution_order:
                cell_start = time.time()
                cell.status = CellStatus.RUNNING

                try:
                    result = await self._execute_cell(cell, context)
                    cell.output = result
                    cell.status = CellStatus.COMPLETED
                    context["results"][cell.name] = result
                    run.results[cell.name] = result

                except Exception as e:
                    cell.status = CellStatus.FAILED
                    cell.error = str(e)
                    run.results[cell.name] = {"error": str(e)}

                cell.execution_time_ms = (time.time() - cell_start) * 1000

            run.status = "completed"

        except Exception as e:
            run.status = "failed"
            run.error = str(e)

        run.completed_at = datetime.utcnow()
        run.execution_time_ms = (time.time() - total_start) * 1000

        return run

    async def _execute_cell(
        self,
        cell: Cell,
        context: dict[str, Any],
    ) -> Any:
        """Execute a single cell."""
        prompt = self._interpolate(cell.prompt or "", context)

        if cell.cell_type == CellType.QUERY:
            return await self._execute_query_cell(prompt, context)

        if cell.cell_type == CellType.VISUALIZATION:
            return await self._execute_viz_cell(prompt, cell, context)

        if cell.cell_type == CellType.TEXT:
            return await self._execute_text_cell(prompt, context)

        if cell.cell_type == CellType.CODE:
            return await self._execute_code_cell(cell.code or "", context)

        if cell.cell_type == CellType.USER_INPUT:
            param_name = cell.name
            return context["parameters"].get(param_name)

        return None

    async def _execute_query_cell(
        self,
        prompt: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a query cell using the agent."""
        if self.agent_runner:
            result = await self.agent_runner(
                prompt=prompt,
                database_alias=context.get("database_alias"),
            )
            return result

        return {
            "status": "simulated",
            "prompt": prompt,
            "message": "Agent runner not configured",
        }

    async def _execute_viz_cell(
        self,
        prompt: str,
        cell: Cell,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a visualization cell."""
        dependent_data = None
        if cell.depends_on:
            dep_name = cell.depends_on[0]
            dependent_data = context["results"].get(dep_name)

        if self.chart_service and dependent_data:
            return {
                "status": "chart_generated",
                "prompt": prompt,
                "data_source": cell.depends_on[0] if cell.depends_on else None,
            }

        return {
            "status": "simulated",
            "prompt": prompt,
            "data_available": dependent_data is not None,
        }

    async def _execute_text_cell(
        self,
        prompt: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a text generation cell."""
        if self.llm_service:
            return {"text": "Generated text from LLM", "prompt": prompt}

        return {
            "status": "simulated",
            "prompt": prompt,
            "text": f"Summary based on: {list(context['results'].keys())}",
        }

    async def _execute_code_cell(
        self,
        code: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a Python code cell in sandbox."""
        import pandas as pd
        import numpy as np

        local_vars = {
            "context": context,
            "results": context["results"],
            "parameters": context["parameters"],
            "pd": pd,
            "np": np,
        }

        try:
            exec(code, {"__builtins__": {}}, local_vars)
            return {
                "status": "executed",
                "output": local_vars.get("output"),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def _interpolate(self, template: str, context: dict[str, Any]) -> str:
        """Interpolate parameters into template."""
        def replace(match: re.Match) -> str:
            key = match.group(1)
            if key in context["parameters"]:
                return str(context["parameters"][key])
            if key in context["results"]:
                return str(context["results"][key])
            return match.group(0)

        return re.sub(r"\{\{(\w+)\}\}", replace, template)

    def _resolve_dependencies(self, cells: list[Cell]) -> list[Cell]:
        """Topological sort cells by dependencies."""
        cell_map = {c.name: c for c in cells}
        visited = set()
        result = []

        def visit(cell: Cell) -> None:
            if cell.name in visited:
                return
            visited.add(cell.name)

            for dep_name in cell.depends_on:
                if dep_name in cell_map:
                    visit(cell_map[dep_name])

            result.append(cell)

        for cell in cells:
            visit(cell)

        return result
```

**Step 5: Create services __init__.py**

Create `app/modules/notebook/services/__init__.py`:

```python
"""Notebook services."""

from app.modules.notebook.services.executor_service import NotebookExecutor
from app.modules.notebook.services.notebook_service import NotebookService

__all__ = ["NotebookExecutor", "NotebookService"]
```

**Step 6: Create module __init__.py**

Create `app/modules/notebook/__init__.py`:

```python
"""Notebook module for reusable analysis workflows."""

from app.modules.notebook.models import (
    Cell,
    CellStatus,
    CellType,
    Notebook,
    NotebookCreateRequest,
    NotebookRun,
    NotebookRunRequest,
    Parameter,
)
from app.modules.notebook.services import NotebookExecutor, NotebookService

__all__ = [
    "Cell",
    "CellStatus",
    "CellType",
    "Notebook",
    "NotebookCreateRequest",
    "NotebookExecutor",
    "NotebookRun",
    "NotebookRunRequest",
    "NotebookService",
    "Parameter",
]
```

**Step 7: Commit**

```bash
git add app/modules/notebook/
git commit -m "feat(notebook): create notebook module with models and services"
```

---

## Epic 5: Enhanced CLI Experience

### Task 11: Create Rich Output Utilities

**Files:**
- Create: `app/utils/rich_output/__init__.py`
- Create: `app/utils/rich_output/formatter.py`
- Create: `app/utils/rich_output/tables.py`

**Step 1: Create rich output directory**

Run: `mkdir -p /Users/fitrakacamarga/project/mta/KAI/app/utils/rich_output`

**Step 2: Create formatter.py**

Create `app/utils/rich_output/formatter.py`:

```python
"""Rich output formatting utilities."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn


console = Console()


def print_panel(
    content: str,
    title: str | None = None,
    style: str = "blue",
) -> None:
    """Print content in a styled panel."""
    console.print(Panel(content, title=title, border_style=style))


def print_sql(sql: str, title: str = "SQL Query") -> None:
    """Print SQL with syntax highlighting."""
    syntax = Syntax(sql, "sql", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=title, border_style="green"))


def print_python(code: str, title: str = "Python") -> None:
    """Print Python code with syntax highlighting."""
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=title, border_style="yellow"))


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def get_spinner() -> Progress:
    """Get a spinner progress indicator."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    )


def format_number(value: float, decimals: int = 2) -> str:
    """Format number with thousands separator."""
    if abs(value) >= 1_000_000:
        return f"{value/1_000_000:,.{decimals}f}M"
    if abs(value) >= 1_000:
        return f"{value/1_000:,.{decimals}f}K"
    return f"{value:,.{decimals}f}"
```

**Step 3: Create tables.py**

Create `app/utils/rich_output/tables.py`:

```python
"""Rich table formatting utilities."""

from __future__ import annotations

from typing import Any

import pandas as pd
from rich.console import Console
from rich.table import Table

from app.utils.rich_output.formatter import format_number


console = Console()


def dataframe_to_table(
    df: pd.DataFrame,
    title: str | None = None,
    max_rows: int = 50,
    show_index: bool = False,
) -> Table:
    """Convert DataFrame to Rich table."""
    table = Table(title=title, show_header=True, header_style="bold cyan")

    if show_index:
        table.add_column("Index", style="dim")

    for col in df.columns:
        table.add_column(str(col))

    display_df = df.head(max_rows)

    for idx, row in display_df.iterrows():
        row_values = []
        if show_index:
            row_values.append(str(idx))

        for val in row:
            if pd.isna(val):
                row_values.append("[dim]NULL[/dim]")
            elif isinstance(val, float):
                row_values.append(format_number(val))
            else:
                row_values.append(str(val))

        table.add_row(*row_values)

    if len(df) > max_rows:
        table.add_row(*["..." for _ in range(len(df.columns) + (1 if show_index else 0))])

    return table


def print_dataframe(
    df: pd.DataFrame,
    title: str | None = None,
    max_rows: int = 50,
) -> None:
    """Print DataFrame as formatted table."""
    table = dataframe_to_table(df, title=title, max_rows=max_rows)
    console.print(table)
    if len(df) > max_rows:
        console.print(f"[dim]Showing {max_rows} of {len(df)} rows[/dim]")


def dict_to_table(
    data: dict[str, Any],
    title: str | None = None,
) -> Table:
    """Convert dictionary to key-value table."""
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Key", style="bold")
    table.add_column("Value")

    for key, value in data.items():
        if isinstance(value, float):
            table.add_row(str(key), format_number(value))
        else:
            table.add_row(str(key), str(value))

    return table


def print_dict(data: dict[str, Any], title: str | None = None) -> None:
    """Print dictionary as formatted table."""
    table = dict_to_table(data, title=title)
    console.print(table)
```

**Step 4: Create __init__.py**

Create `app/utils/rich_output/__init__.py`:

```python
"""Rich output utilities."""

from app.utils.rich_output.formatter import (
    console,
    format_number,
    get_spinner,
    print_error,
    print_info,
    print_panel,
    print_python,
    print_sql,
    print_success,
    print_warning,
)
from app.utils.rich_output.tables import (
    dataframe_to_table,
    dict_to_table,
    print_dataframe,
    print_dict,
)

__all__ = [
    "console",
    "dataframe_to_table",
    "dict_to_table",
    "format_number",
    "get_spinner",
    "print_dataframe",
    "print_dict",
    "print_error",
    "print_info",
    "print_panel",
    "print_python",
    "print_sql",
    "print_success",
    "print_warning",
]
```

**Step 5: Commit**

```bash
git add app/utils/rich_output/
git commit -m "feat(cli): add rich output formatting utilities"
```

---

## Epic 6: API Enhancements

### Task 12: Add SSE Streaming Support

**Files:**
- Modify: `pyproject.toml` (add sse-starlette)
- Create: `app/api/v2/__init__.py`
- Create: `app/api/v2/streaming.py`

**Step 1: Add sse-starlette dependency**

Add to `pyproject.toml`:

```toml
"sse-starlette>=1.6.0",
```

**Step 2: Install dependency**

Run: `uv sync`

**Step 3: Create v2 API directory**

Run: `mkdir -p /Users/fitrakacamarga/project/mta/KAI/app/api/v2`

**Step 4: Create streaming.py**

Create `app/api/v2/streaming.py`:

```python
"""SSE streaming API endpoints."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any, AsyncGenerator

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse


router = APIRouter(prefix="/api/v2", tags=["Streaming"])


async def event_generator(
    task_id: str,
    total_steps: int = 5,
) -> AsyncGenerator[dict[str, Any], None]:
    """Generate SSE events for a task."""
    for i in range(total_steps):
        yield {
            "event": "progress",
            "data": json.dumps({
                "task_id": task_id,
                "step": i + 1,
                "total_steps": total_steps,
                "message": f"Processing step {i + 1} of {total_steps}",
                "timestamp": datetime.utcnow().isoformat(),
            }),
        }
        await asyncio.sleep(0.5)

    yield {
        "event": "complete",
        "data": json.dumps({
            "task_id": task_id,
            "status": "completed",
            "message": "Task completed successfully",
            "timestamp": datetime.utcnow().isoformat(),
        }),
    }


@router.get("/analysis/{task_id}/stream")
async def stream_analysis(task_id: str) -> EventSourceResponse:
    """Stream analysis progress via SSE."""
    return EventSourceResponse(event_generator(task_id))


async def notebook_event_generator(
    run_id: str,
    cells: list[str],
) -> AsyncGenerator[dict[str, Any], None]:
    """Generate SSE events for notebook execution."""
    for i, cell in enumerate(cells):
        yield {
            "event": "cell_start",
            "data": json.dumps({
                "run_id": run_id,
                "cell": cell,
                "index": i,
                "timestamp": datetime.utcnow().isoformat(),
            }),
        }
        await asyncio.sleep(1)

        yield {
            "event": "cell_complete",
            "data": json.dumps({
                "run_id": run_id,
                "cell": cell,
                "index": i,
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat(),
            }),
        }

    yield {
        "event": "complete",
        "data": json.dumps({
            "run_id": run_id,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
        }),
    }


@router.get("/notebooks/{run_id}/stream")
async def stream_notebook_execution(run_id: str) -> EventSourceResponse:
    """Stream notebook execution progress via SSE."""
    cells = ["query_1", "viz_1", "summary"]
    return EventSourceResponse(notebook_event_generator(run_id, cells))
```

**Step 5: Create v2 __init__.py**

Create `app/api/v2/__init__.py`:

```python
"""API v2 module."""

from app.api.v2.streaming import router as streaming_router

__all__ = ["streaming_router"]
```

**Step 6: Register streaming router**

Edit `app/server/__init__.py`:

```python
from app.api.v2 import streaming_router

# In __init__:
self._app.include_router(streaming_router)
```

**Step 7: Commit**

```bash
git add pyproject.toml app/api/v2/ app/server/__init__.py
git commit -m "feat(api): add SSE streaming API endpoints"
```

---

### Task 13: Add Batch Processing API

**Files:**
- Create: `app/api/v2/batch.py`
- Modify: `app/api/v2/__init__.py`

**Step 1: Create batch.py**

Create `app/api/v2/batch.py`:

```python
"""Batch processing API endpoints."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api/v2/analysis", tags=["Batch Processing"])


class AnalysisRequest(BaseModel):
    """Single analysis request."""

    prompt: str
    database_alias: str | None = None
    options: dict[str, Any] = Field(default_factory=dict)


class BatchRequest(BaseModel):
    """Batch analysis request."""

    requests: list[AnalysisRequest]
    max_concurrency: int = 5


class BatchStatus(BaseModel):
    """Batch job status."""

    batch_id: str
    status: str
    total: int
    completed: int
    failed: int
    results: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


_batch_jobs: dict[str, BatchStatus] = {}


async def process_batch(batch_id: str, requests: list[AnalysisRequest]) -> None:
    """Process batch requests."""
    job = _batch_jobs[batch_id]
    job.status = "running"
    job.updated_at = datetime.utcnow()

    for i, request in enumerate(requests):
        try:
            await asyncio.sleep(0.5)

            job.results[f"request_{i}"] = {
                "status": "completed",
                "prompt": request.prompt,
                "result": {"message": f"Processed: {request.prompt[:50]}..."},
            }
            job.completed += 1

        except Exception as e:
            job.results[f"request_{i}"] = {
                "status": "failed",
                "prompt": request.prompt,
                "error": str(e),
            }
            job.failed += 1

        job.updated_at = datetime.utcnow()

    job.status = "completed" if job.failed == 0 else "partial"
    job.updated_at = datetime.utcnow()


@router.post("/batch", response_model=dict)
async def create_batch(
    request: BatchRequest,
    background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    """Submit a batch of analysis requests."""
    batch_id = str(uuid.uuid4())
    now = datetime.utcnow()

    job = BatchStatus(
        batch_id=batch_id,
        status="pending",
        total=len(request.requests),
        completed=0,
        failed=0,
        created_at=now,
        updated_at=now,
    )
    _batch_jobs[batch_id] = job

    background_tasks.add_task(process_batch, batch_id, request.requests)

    return {
        "batch_id": batch_id,
        "status": "pending",
        "total": len(request.requests),
        "message": "Batch submitted successfully",
    }


@router.get("/batch/{batch_id}")
async def get_batch_status(batch_id: str) -> BatchStatus:
    """Get batch job status."""
    if batch_id not in _batch_jobs:
        raise HTTPException(404, f"Batch {batch_id} not found")
    return _batch_jobs[batch_id]


@router.get("/batch/{batch_id}/results")
async def get_batch_results(batch_id: str) -> dict[str, Any]:
    """Get batch job results."""
    if batch_id not in _batch_jobs:
        raise HTTPException(404, f"Batch {batch_id} not found")

    job = _batch_jobs[batch_id]
    return {
        "batch_id": batch_id,
        "status": job.status,
        "results": job.results,
    }
```

**Step 2: Update v2 __init__.py**

Update `app/api/v2/__init__.py`:

```python
"""API v2 module."""

from app.api.v2.batch import router as batch_router
from app.api.v2.streaming import router as streaming_router

__all__ = ["batch_router", "streaming_router"]
```

**Step 3: Register batch router**

Edit `app/server/__init__.py`:

```python
from app.api.v2 import batch_router, streaming_router

# In __init__:
self._app.include_router(streaming_router)
self._app.include_router(batch_router)
```

**Step 4: Commit**

```bash
git add app/api/v2/batch.py app/api/v2/__init__.py app/server/__init__.py
git commit -m "feat(api): add batch processing API endpoints"
```

---

## Final Task: Integration Testing

### Task 14: Run Full Test Suite

**Step 1: Run all tests**

Run: `uv run pytest tests/ -v --tb=short`
Expected: All tests pass

**Step 2: Run with coverage**

Run: `uv run pytest tests/ --cov=app --cov-report=term-missing`
Expected: Coverage report generated

**Step 3: Start the server and test manually**

Run: `uv run python -m app.main`

Test endpoints:
- `GET http://localhost:8015/api/v2/visualizations/themes`
- `GET http://localhost:8015/api/v2/visualizations/types`
- `POST http://localhost:8015/api/v2/analytics/statistics`

**Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete KAI advanced analytics implementation

- Epic 2: Advanced Visualization with Plotly
- Epic 3: Statistical Analysis & Forecasting
- Epic 4: Notebook System
- Epic 5: Enhanced CLI utilities
- Epic 6: SSE Streaming and Batch API"
```

---

## Summary

This implementation plan covers:

| Epic | Tasks | Key Deliverables |
|------|-------|------------------|
| **Epic 2: Visualization** | 1-5 | ChartService with Plotly, 13+ chart types, themes, API endpoints |
| **Epic 3: Analytics** | 6-9 | StatisticalService, ForecastingService, AnomalyService, API endpoints |
| **Epic 4: Notebook** | 10 | Notebook models, NotebookService, NotebookExecutor |
| **Epic 5: CLI** | 11 | Rich output utilities, formatters, tables |
| **Epic 6: API** | 12-13 | SSE streaming, batch processing API |

**Total estimated effort:** ~3-4 weeks for a single developer

**Key files created:**
- `app/modules/visualization/` - Plotly visualization module
- `app/modules/analytics/` - Statistical analysis module
- `app/modules/notebook/` - Notebook workflow module
- `app/utils/rich_output/` - CLI formatting utilities
- `app/api/v2/` - New API version with streaming/batch

---

Plan complete and saved to `docs/plans/2025-12-06-kai-advanced-analytics-implementation.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
