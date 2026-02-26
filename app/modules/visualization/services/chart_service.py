"""Chart generation service using Plotly."""

from __future__ import annotations

import base64
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.modules.visualization.exceptions import (
    ChartExportError,
    ChartGenerationError,
    ChartRecommendationError,
    InvalidChartTypeError,
    MissingColumnError,
)
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
        # Validate required columns exist in dataframe
        self._validate_columns(df, config)

        try:
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
        except (MissingColumnError, InvalidChartTypeError):
            raise
        except Exception as e:
            raise ChartGenerationError(f"Failed to generate chart: {e}") from e

    def _validate_columns(self, df: pd.DataFrame, config: ChartConfig) -> None:
        """Validate that required columns exist in the dataframe."""
        columns = df.columns.tolist()

        if config.x_column and config.x_column not in columns:
            raise MissingColumnError(
                f"Required x_column '{config.x_column}' not found in data. "
                f"Available columns: {columns}"
            )
        if config.y_column and config.y_column not in columns:
            raise MissingColumnError(
                f"Required y_column '{config.y_column}' not found in data. "
                f"Available columns: {columns}"
            )
        if config.color_column and config.color_column not in columns:
            raise MissingColumnError(
                f"Specified color_column '{config.color_column}' not found in data. "
                f"Available columns: {columns}"
            )
        if config.size_column and config.size_column not in columns:
            raise MissingColumnError(
                f"Specified size_column '{config.size_column}' not found in data. "
                f"Available columns: {columns}"
            )
        if config.values_column and config.values_column not in columns:
            raise MissingColumnError(
                f"Specified values_column '{config.values_column}' not found in data. "
                f"Available columns: {columns}"
            )
        if config.names_column and config.names_column not in columns:
            raise MissingColumnError(
                f"Specified names_column '{config.names_column}' not found in data. "
                f"Available columns: {columns}"
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
        valid_formats = {"png", "svg", "pdf", "jpeg", "webp"}
        if format not in valid_formats:
            raise ChartExportError(
                f"Invalid export format: '{format}'. "
                f"Valid formats: {', '.join(sorted(valid_formats))}"
            )

        try:
            fig = go.Figure(result.json_spec)

            if format == "png":
                return fig.to_image(format="png", scale=scale)
            if format == "svg":
                return fig.to_image(format="svg")
            if format == "pdf":
                return fig.to_image(format="pdf")

            return fig.to_image(format="png", scale=scale)
        except ChartExportError:
            raise
        except Exception as e:
            raise ChartExportError(f"Failed to export chart to {format}: {e}") from e

    def export_to_base64(
        self,
        result: ChartResult,
        format: str = "png",
        scale: float = 2.0,
    ) -> str:
        """Export chart to base64 encoded image."""
        try:
            image_bytes = self.export_to_image(result, format, scale)
            return base64.b64encode(image_bytes).decode("utf-8")
        except ChartExportError:
            raise
        except Exception as e:
            raise ChartExportError(
                f"Failed to encode chart as base64: {e}"
            ) from e

    def recommend_chart_type(
        self,
        df: pd.DataFrame,
        x_column: str | None = None,
        y_column: str | None = None,
    ) -> ChartRecommendation:
        """Recommend optimal chart type based on data characteristics."""
        if df.empty:
            raise ChartRecommendationError(
                "Cannot recommend chart type for empty dataframe"
            )

        try:
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
        except ChartRecommendationError:
            raise
        except Exception as e:
            raise ChartRecommendationError(
                f"Failed to recommend chart type: {e}"
            ) from e
