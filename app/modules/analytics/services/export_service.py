"""Export service for analytics results."""

from __future__ import annotations

import io
import json
from datetime import datetime
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pydantic import BaseModel

from app.modules.analytics.models import (
    AnomalyResult,
    CorrelationMatrixResult,
    CorrelationResult,
    DescriptiveStats,
    ExportFormat,
    ForecastResult,
    StatisticalTestResult,
)

# Use non-interactive backend for PDF generation
matplotlib.use("Agg")


class ExportService:
    """Service for exporting analytics results to various formats."""

    def __init__(self) -> None:
        """Initialize export service."""
        self._content_types = {
            ExportFormat.JSON: "application/json",
            ExportFormat.CSV: "text/csv",
            ExportFormat.PDF: "application/pdf",
        }

    def get_content_type(self, format: ExportFormat) -> str:
        """Get MIME content type for export format."""
        return self._content_types.get(format, "application/octet-stream")

    def generate_filename(
        self,
        base_name: str,
        format: ExportFormat,
        custom_filename: str | None = None,
    ) -> str:
        """Generate export filename with extension."""
        if custom_filename:
            base_name = custom_filename

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = format.value
        return f"{base_name}_{timestamp}.{extension}"

    def export_to_json(
        self,
        data: BaseModel | dict[str, Any] | list[Any],
        include_metadata: bool = True,
    ) -> bytes:
        """Export data to JSON format."""
        if isinstance(data, BaseModel):
            result = data.model_dump()
        elif isinstance(data, dict):
            result = data
        else:
            result = {"data": data}

        if include_metadata:
            output = {
                "metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "format": "json",
                },
                "result": result,
            }
        else:
            output = result

        return json.dumps(output, indent=2, default=str).encode("utf-8")

    def export_to_csv(
        self,
        data: BaseModel | dict[str, Any] | list[dict[str, Any]] | pd.DataFrame,
        include_metadata: bool = True,
    ) -> bytes:
        """Export data to CSV format."""
        buffer = io.StringIO()

        if include_metadata:
            buffer.write(f"# Exported at: {datetime.now().isoformat()}\n")
            buffer.write("# Format: CSV\n")
            buffer.write("#\n")

        df = self._to_dataframe(data)
        df.to_csv(buffer, index=False)

        return buffer.getvalue().encode("utf-8")

    def export_to_pdf(
        self,
        data: BaseModel | dict[str, Any] | list[dict[str, Any]],
        title: str = "Analytics Report",
        include_chart: bool = True,
    ) -> bytes:
        """Export data to PDF format with tables and optional charts."""
        buffer = io.BytesIO()

        df = self._to_dataframe(data)

        # Determine figure size based on content
        num_rows = len(df)
        num_cols = len(df.columns)
        fig_height = max(4, 2 + 0.3 * num_rows)
        fig_width = max(8, 2 + 0.8 * num_cols)

        if include_chart and self._can_generate_chart(data):
            fig, axes = plt.subplots(2, 1, figsize=(fig_width, fig_height + 4))
            ax_table, ax_chart = axes

            # Render table
            self._render_table(ax_table, df, title)

            # Render chart
            self._render_chart(ax_chart, data)
        else:
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            self._render_table(ax, df, title)

        plt.tight_layout()
        fig.savefig(buffer, format="pdf", bbox_inches="tight", dpi=150)
        plt.close(fig)

        return buffer.getvalue()

    def export_descriptive_stats(
        self,
        stats: DescriptiveStats | list[DescriptiveStats],
        format: ExportFormat,
        include_metadata: bool = True,
    ) -> bytes:
        """Export descriptive statistics in specified format."""
        if isinstance(stats, list):
            data = [s.model_dump() for s in stats]
        else:
            data = stats.model_dump()

        return self._export_by_format(
            data,
            format,
            title="Descriptive Statistics",
            include_metadata=include_metadata,
        )

    def export_correlation(
        self,
        result: CorrelationResult,
        format: ExportFormat,
        include_metadata: bool = True,
    ) -> bytes:
        """Export correlation result in specified format."""
        return self._export_by_format(
            result.model_dump(),
            format,
            title="Correlation Analysis",
            include_metadata=include_metadata,
        )

    def export_correlation_matrix(
        self,
        result: CorrelationMatrixResult,
        format: ExportFormat,
        include_metadata: bool = True,
    ) -> bytes:
        """Export correlation matrix in specified format."""
        if format == ExportFormat.CSV:
            # For CSV, convert matrix to proper DataFrame
            matrix_df = pd.DataFrame(result.matrix)
            return self.export_to_csv(matrix_df, include_metadata)
        elif format == ExportFormat.PDF:
            # For PDF, render the matrix as a heatmap
            return self._export_correlation_matrix_pdf(result)
        else:
            return self.export_to_json(result, include_metadata)

    def export_forecast(
        self,
        result: ForecastResult,
        format: ExportFormat,
        include_metadata: bool = True,
    ) -> bytes:
        """Export forecast result in specified format."""
        if format == ExportFormat.CSV:
            # Create a structured DataFrame for forecast data
            forecast_data = {
                "date": result.forecast_dates,
                "forecast": result.forecast_values,
                "lower_bound": result.lower_bound,
                "upper_bound": result.upper_bound,
            }
            df = pd.DataFrame(forecast_data)
            return self.export_to_csv(df, include_metadata)
        elif format == ExportFormat.PDF:
            return self._export_forecast_pdf(result)
        else:
            return self.export_to_json(result, include_metadata)

    def export_anomalies(
        self,
        result: AnomalyResult,
        format: ExportFormat,
        include_metadata: bool = True,
    ) -> bytes:
        """Export anomaly detection result in specified format."""
        if format == ExportFormat.CSV:
            # Export anomalies as rows
            if result.anomalies:
                df = pd.DataFrame(result.anomalies)
            else:
                df = pd.DataFrame({"message": ["No anomalies detected"]})

            buffer = io.StringIO()
            if include_metadata:
                buffer.write(f"# Method: {result.method}\n")
                buffer.write(f"# Total Points: {result.total_points}\n")
                buffer.write(f"# Anomaly Count: {result.anomaly_count}\n")
                buffer.write(f"# Anomaly Percentage: {result.anomaly_percentage}%\n")
                buffer.write(f"# Threshold: {result.threshold}\n")
                buffer.write(f"# Interpretation: {result.interpretation}\n")
                buffer.write("#\n")
            df.to_csv(buffer, index=False)
            return buffer.getvalue().encode("utf-8")
        elif format == ExportFormat.PDF:
            return self._export_anomaly_pdf(result)
        else:
            return self.export_to_json(result, include_metadata)

    def export_statistical_test(
        self,
        result: StatisticalTestResult,
        format: ExportFormat,
        include_metadata: bool = True,
    ) -> bytes:
        """Export statistical test result in specified format."""
        return self._export_by_format(
            result.model_dump(),
            format,
            title=result.test_name,
            include_metadata=include_metadata,
        )

    def _export_by_format(
        self,
        data: dict[str, Any] | list[dict[str, Any]],
        format: ExportFormat,
        title: str = "Analytics Report",
        include_metadata: bool = True,
    ) -> bytes:
        """Export data in specified format."""
        if format == ExportFormat.JSON:
            return self.export_to_json(data, include_metadata)
        elif format == ExportFormat.CSV:
            return self.export_to_csv(data, include_metadata)
        elif format == ExportFormat.PDF:
            return self.export_to_pdf(data, title)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _to_dataframe(
        self,
        data: BaseModel | dict[str, Any] | list[dict[str, Any]] | pd.DataFrame,
    ) -> pd.DataFrame:
        """Convert various data types to DataFrame."""
        if isinstance(data, pd.DataFrame):
            return data
        if isinstance(data, BaseModel):
            data = data.model_dump()
        if isinstance(data, dict):
            # Flatten nested dict for table display
            flat_data = self._flatten_dict(data)
            return pd.DataFrame([flat_data])
        if isinstance(data, list):
            if data and isinstance(data[0], dict):
                return pd.DataFrame(data)
            return pd.DataFrame({"value": data})
        return pd.DataFrame()

    def _flatten_dict(
        self,
        d: dict[str, Any],
        parent_key: str = "",
        sep: str = "_",
    ) -> dict[str, Any]:
        """Flatten nested dictionary."""
        items: list[tuple[str, Any]] = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            elif isinstance(v, list) and v and isinstance(v[0], dict):
                # Keep list of dicts as JSON string
                items.append((new_key, json.dumps(v)))
            elif isinstance(v, list):
                items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        return dict(items)

    def _can_generate_chart(self, data: BaseModel | dict[str, Any]) -> bool:
        """Check if data can generate a meaningful chart."""
        if isinstance(data, (ForecastResult, AnomalyResult)):
            return True
        if isinstance(data, dict):
            return "forecast_values" in data or "anomalies" in data
        return False

    def _render_table(
        self,
        ax: plt.Axes,
        df: pd.DataFrame,
        title: str,
    ) -> None:
        """Render DataFrame as a table on matplotlib axes."""
        ax.axis("off")
        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)

        if df.empty:
            ax.text(
                0.5, 0.5,
                "No data available",
                ha="center", va="center",
                fontsize=12,
            )
            return

        # Truncate long values for display
        display_df = df.copy()
        for col in display_df.columns:
            display_df[col] = display_df[col].astype(str).str[:50]

        table = ax.table(
            cellText=display_df.values,
            colLabels=display_df.columns,
            cellLoc="center",
            loc="center",
            colColours=["#4472C4"] * len(display_df.columns),
        )

        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.5)

        # Style header
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_text_props(fontweight="bold", color="white")
            else:
                cell.set_facecolor("#E7E6E6" if row % 2 == 0 else "white")

    def _render_chart(
        self,
        ax: plt.Axes,
        data: BaseModel | dict[str, Any],
    ) -> None:
        """Render appropriate chart based on data type."""
        if isinstance(data, ForecastResult):
            self._render_forecast_chart(ax, data)
        elif isinstance(data, dict) and "forecast_values" in data:
            # Convert dict to ForecastResult for chart
            forecast = ForecastResult(**data)
            self._render_forecast_chart(ax, forecast)
        else:
            ax.text(
                0.5, 0.5,
                "Chart not available for this data type",
                ha="center", va="center",
            )

    def _render_forecast_chart(self, ax: plt.Axes, result: ForecastResult) -> None:
        """Render forecast chart."""
        dates = range(len(result.forecast_values))

        ax.fill_between(
            dates,
            result.lower_bound,
            result.upper_bound,
            alpha=0.3,
            color="blue",
            label=f"{int(result.confidence_level * 100)}% CI",
        )
        ax.plot(
            dates,
            result.forecast_values,
            color="blue",
            linewidth=2,
            label="Forecast",
        )

        ax.set_xlabel("Period")
        ax.set_ylabel("Value")
        ax.set_title(f"{result.model_name} Forecast ({result.trend} trend)")
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _export_correlation_matrix_pdf(self, result: CorrelationMatrixResult) -> bytes:
        """Export correlation matrix as PDF with heatmap."""
        buffer = io.BytesIO()

        matrix_df = pd.DataFrame(result.matrix)

        fig_size = max(8, len(result.columns) * 0.8)
        fig, ax = plt.subplots(figsize=(fig_size, fig_size))

        im = ax.imshow(matrix_df.values, cmap="RdBu_r", vmin=-1, vmax=1)

        ax.set_xticks(np.arange(len(result.columns)))
        ax.set_yticks(np.arange(len(result.columns)))
        ax.set_xticklabels(result.columns, rotation=45, ha="right")
        ax.set_yticklabels(result.columns)

        # Add correlation values as text
        for i in range(len(result.columns)):
            for j in range(len(result.columns)):
                value = matrix_df.iloc[i, j]
                color = "white" if abs(value) > 0.5 else "black"
                ax.text(j, i, f"{value:.2f}", ha="center", va="center", color=color)

        ax.set_title(f"Correlation Matrix ({result.method.title()})")
        fig.colorbar(im, ax=ax, label="Correlation Coefficient")

        plt.tight_layout()
        fig.savefig(buffer, format="pdf", bbox_inches="tight", dpi=150)
        plt.close(fig)

        return buffer.getvalue()

    def _export_forecast_pdf(self, result: ForecastResult) -> bytes:
        """Export forecast result as PDF with chart."""
        buffer = io.BytesIO()

        fig, axes = plt.subplots(2, 1, figsize=(10, 10))

        # Summary table
        ax_summary = axes[0]
        ax_summary.axis("off")
        ax_summary.set_title(
            f"{result.model_name} Forecast Report",
            fontsize=14,
            fontweight="bold",
        )

        summary_data = [
            ["Model", result.model_name],
            ["Trend", result.trend],
            ["Confidence Level", f"{result.confidence_level * 100:.0f}%"],
            ["Periods", str(len(result.forecast_values))],
            ["Min Forecast", f"{min(result.forecast_values):.2f}"],
            ["Max Forecast", f"{max(result.forecast_values):.2f}"],
        ]

        table = ax_summary.table(
            cellText=summary_data,
            colLabels=["Metric", "Value"],
            cellLoc="left",
            loc="center",
            colColours=["#4472C4", "#4472C4"],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)

        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_text_props(fontweight="bold", color="white")

        # Forecast chart
        self._render_forecast_chart(axes[1], result)

        # Add interpretation
        fig.text(
            0.1, 0.02,
            f"Interpretation: {result.interpretation}",
            fontsize=9,
            wrap=True,
        )

        plt.tight_layout(rect=[0, 0.05, 1, 1])
        fig.savefig(buffer, format="pdf", bbox_inches="tight", dpi=150)
        plt.close(fig)

        return buffer.getvalue()

    def _export_anomaly_pdf(self, result: AnomalyResult) -> bytes:
        """Export anomaly detection result as PDF."""
        buffer = io.BytesIO()

        fig, ax = plt.subplots(figsize=(10, 8))
        ax.axis("off")
        ax.set_title(
            f"Anomaly Detection Report ({result.method.upper()})",
            fontsize=14,
            fontweight="bold",
            pad=20,
        )

        # Summary
        summary_data = [
            ["Detection Method", result.method],
            ["Total Data Points", str(result.total_points)],
            ["Anomalies Found", str(result.anomaly_count)],
            ["Anomaly Percentage", f"{result.anomaly_percentage:.2f}%"],
            ["Threshold", str(result.threshold) if result.threshold else "N/A"],
        ]

        table = ax.table(
            cellText=summary_data,
            colLabels=["Metric", "Value"],
            cellLoc="left",
            loc="upper center",
            colColours=["#4472C4", "#4472C4"],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)

        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_text_props(fontweight="bold", color="white")

        # Add interpretation
        fig.text(
            0.1, 0.3,
            f"Interpretation:\n{result.interpretation}",
            fontsize=10,
            wrap=True,
            verticalalignment="top",
        )

        # Add anomaly details if available
        if result.anomalies and len(result.anomalies) <= 10:
            fig.text(
                0.1, 0.15,
                f"Top Anomalies: {json.dumps(result.anomalies[:5], indent=2)}",
                fontsize=8,
                fontfamily="monospace",
                wrap=True,
                verticalalignment="top",
            )

        plt.tight_layout()
        fig.savefig(buffer, format="pdf", bbox_inches="tight", dpi=150)
        plt.close(fig)

        return buffer.getvalue()
