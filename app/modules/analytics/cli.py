"""CLI for KAI Analytics Export.

Usage:
    kai-analytics export descriptive data.json --format json --output stats.json
    kai-analytics export correlation data.csv --format csv --output corr.csv
    kai-analytics export forecast data.json --format pdf --output forecast.pdf
"""
import json
import sys
from pathlib import Path
from typing import Optional

import click
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from app.modules.analytics.models import ExportFormat
from app.modules.analytics.services import (
    AnomalyService,
    ExportService,
    ForecastingService,
    StatisticalService,
)

console = Console()


def load_data(file_path: str) -> pd.DataFrame:
    """Load data from a file (JSON or CSV)."""
    path = Path(file_path)
    if not path.exists():
        raise click.ClickException(f"File not found: {file_path}")

    suffix = path.suffix.lower()
    if suffix == ".json":
        with open(path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            # If it's a dict with a 'data' key, use that
            if "data" in data:
                return pd.DataFrame(data["data"])
            # Otherwise try to create a DataFrame from the dict
            return pd.DataFrame([data])
    elif suffix == ".csv":
        return pd.read_csv(path)
    else:
        raise click.ClickException(f"Unsupported file format: {suffix}. Use .json or .csv")


def parse_format(format_str: str) -> ExportFormat:
    """Parse format string to ExportFormat enum."""
    try:
        return ExportFormat(format_str.lower())
    except ValueError:
        raise click.ClickException(
            f"Invalid format: {format_str}. Use one of: json, csv, pdf"
        )


def write_output(data: bytes, output_path: Optional[str], format: ExportFormat) -> None:
    """Write export data to file or stdout."""
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        console.print(f"[green]Exported to:[/green] {output_path}")
    else:
        # For stdout, only text formats make sense
        if format == ExportFormat.PDF:
            console.print("[yellow]Warning:[/yellow] PDF output requires --output file path")
            console.print("[yellow]Saving to:[/yellow] export.pdf")
            with open("export.pdf", "wb") as f:
                f.write(data)
        else:
            sys.stdout.buffer.write(data)


@click.group()
def cli():
    """KAI Analytics - Export statistical results to various formats."""
    pass


@cli.group()
def export():
    """Export analytics results to JSON, CSV, or PDF."""
    pass


@export.command("descriptive")
@click.argument("data_file", type=click.Path(exists=True))
@click.option(
    "--column",
    "-c",
    default=None,
    help="Column name to analyze. If not specified, analyzes all numeric columns.",
)
@click.option(
    "--format",
    "-f",
    "format_str",
    type=click.Choice(["json", "csv", "pdf"]),
    default="json",
    help="Export format (default: json)",
)
@click.option(
    "--output",
    "-o",
    "output_path",
    type=click.Path(),
    help="Output file path. If not specified, outputs to stdout (except PDF).",
)
@click.option(
    "--no-metadata",
    is_flag=True,
    help="Exclude metadata from export",
)
def export_descriptive(
    data_file: str,
    column: Optional[str],
    format_str: str,
    output_path: Optional[str],
    no_metadata: bool,
):
    """Export descriptive statistics for a dataset.

    DATA_FILE: Path to the input data file (JSON or CSV)

    Examples:

        kai-analytics export descriptive data.csv --column revenue --format json

        kai-analytics export descriptive data.json --format csv -o stats.csv
    """
    try:
        df = load_data(data_file)
        format = parse_format(format_str)
        stat_service = StatisticalService()
        export_service = ExportService()

        if column:
            if column not in df.columns:
                raise click.ClickException(f"Column '{column}' not found in data")
            series = df[column]
            result = stat_service.descriptive_stats(series)
            stats_list = [result]
        else:
            # Analyze all numeric columns
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            if not numeric_cols:
                raise click.ClickException("No numeric columns found in data")
            stats_list = [stat_service.descriptive_stats(df[col]) for col in numeric_cols]

        export_data = export_service.export_descriptive_stats(
            stats_list if len(stats_list) > 1 else stats_list[0],
            format=format,
            include_metadata=not no_metadata,
        )

        write_output(export_data, output_path, format)

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@export.command("correlation")
@click.argument("data_file", type=click.Path(exists=True))
@click.option(
    "--x",
    "x_col",
    required=True,
    help="Column name for first variable",
)
@click.option(
    "--y",
    "y_col",
    required=True,
    help="Column name for second variable",
)
@click.option(
    "--method",
    "-m",
    type=click.Choice(["pearson", "spearman", "kendall"]),
    default="pearson",
    help="Correlation method (default: pearson)",
)
@click.option(
    "--format",
    "-f",
    "format_str",
    type=click.Choice(["json", "csv", "pdf"]),
    default="json",
    help="Export format (default: json)",
)
@click.option(
    "--output",
    "-o",
    "output_path",
    type=click.Path(),
    help="Output file path. If not specified, outputs to stdout (except PDF).",
)
@click.option(
    "--no-metadata",
    is_flag=True,
    help="Exclude metadata from export",
)
def export_correlation(
    data_file: str,
    x_col: str,
    y_col: str,
    method: str,
    format_str: str,
    output_path: Optional[str],
    no_metadata: bool,
):
    """Export correlation analysis between two variables.

    DATA_FILE: Path to the input data file (JSON or CSV)

    Examples:

        kai-analytics export correlation data.csv --x price --y sales --format json

        kai-analytics export correlation data.csv --x age --y income --method spearman -o corr.pdf
    """
    try:
        df = load_data(data_file)
        format = parse_format(format_str)
        stat_service = StatisticalService()
        export_service = ExportService()

        if x_col not in df.columns:
            raise click.ClickException(f"Column '{x_col}' not found in data")
        if y_col not in df.columns:
            raise click.ClickException(f"Column '{y_col}' not found in data")

        x = df[x_col]
        y = df[y_col]
        result = stat_service.correlation(x, y, method=method)

        export_data = export_service.export_correlation(
            result,
            format=format,
            include_metadata=not no_metadata,
        )

        write_output(export_data, output_path, format)

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@export.command("correlation-matrix")
@click.argument("data_file", type=click.Path(exists=True))
@click.option(
    "--method",
    "-m",
    type=click.Choice(["pearson", "spearman", "kendall"]),
    default="pearson",
    help="Correlation method (default: pearson)",
)
@click.option(
    "--format",
    "-f",
    "format_str",
    type=click.Choice(["json", "csv", "pdf"]),
    default="json",
    help="Export format (default: json)",
)
@click.option(
    "--output",
    "-o",
    "output_path",
    type=click.Path(),
    help="Output file path. If not specified, outputs to stdout (except PDF).",
)
@click.option(
    "--no-metadata",
    is_flag=True,
    help="Exclude metadata from export",
)
def export_correlation_matrix(
    data_file: str,
    method: str,
    format_str: str,
    output_path: Optional[str],
    no_metadata: bool,
):
    """Export correlation matrix for all numeric columns.

    DATA_FILE: Path to the input data file (JSON or CSV)

    Examples:

        kai-analytics export correlation-matrix data.csv --format pdf -o matrix.pdf

        kai-analytics export correlation-matrix data.json --method spearman -o matrix.json
    """
    try:
        df = load_data(data_file)
        format = parse_format(format_str)
        stat_service = StatisticalService()
        export_service = ExportService()

        # Select only numeric columns
        numeric_df = df.select_dtypes(include=["number"])
        if numeric_df.empty or len(numeric_df.columns) < 2:
            raise click.ClickException("Need at least 2 numeric columns for correlation matrix")

        result = stat_service.correlation_matrix(numeric_df, method=method)

        export_data = export_service.export_correlation_matrix(
            result,
            format=format,
            include_metadata=not no_metadata,
        )

        write_output(export_data, output_path, format)

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@export.command("forecast")
@click.argument("data_file", type=click.Path(exists=True))
@click.option(
    "--column",
    "-c",
    default=None,
    help="Column name containing time series values. Uses first numeric column if not specified.",
)
@click.option(
    "--periods",
    "-p",
    type=int,
    default=30,
    help="Number of periods to forecast (default: 30)",
)
@click.option(
    "--format",
    "-f",
    "format_str",
    type=click.Choice(["json", "csv", "pdf"]),
    default="json",
    help="Export format (default: json)",
)
@click.option(
    "--output",
    "-o",
    "output_path",
    type=click.Path(),
    help="Output file path. If not specified, outputs to stdout (except PDF).",
)
@click.option(
    "--no-metadata",
    is_flag=True,
    help="Exclude metadata from export",
)
def export_forecast(
    data_file: str,
    column: Optional[str],
    periods: int,
    format_str: str,
    output_path: Optional[str],
    no_metadata: bool,
):
    """Export time series forecast.

    DATA_FILE: Path to the input data file (JSON or CSV)

    Examples:

        kai-analytics export forecast sales.csv --column revenue --periods 12 --format pdf

        kai-analytics export forecast timeseries.json -p 30 -o forecast.csv
    """
    try:
        df = load_data(data_file)
        format = parse_format(format_str)
        forecast_service = ForecastingService()
        export_service = ExportService()

        if column:
            if column not in df.columns:
                raise click.ClickException(f"Column '{column}' not found in data")
            series = df[column]
        else:
            # Use first numeric column
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            if not numeric_cols:
                raise click.ClickException("No numeric columns found in data")
            series = df[numeric_cols[0]]
            console.print(f"[dim]Using column: {numeric_cols[0]}[/dim]")

        result = forecast_service.forecast_simple(series, periods=periods)

        export_data = export_service.export_forecast(
            result,
            format=format,
            include_metadata=not no_metadata,
        )

        write_output(export_data, output_path, format)

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@export.command("anomalies")
@click.argument("data_file", type=click.Path(exists=True))
@click.option(
    "--column",
    "-c",
    default=None,
    help="Column name to analyze. Uses first numeric column if not specified.",
)
@click.option(
    "--method",
    "-m",
    type=click.Choice(["zscore", "iqr"]),
    default="zscore",
    help="Detection method (default: zscore)",
)
@click.option(
    "--threshold",
    "-t",
    type=float,
    default=3.0,
    help="Detection threshold (z-score threshold or IQR multiplier, default: 3.0)",
)
@click.option(
    "--format",
    "-f",
    "format_str",
    type=click.Choice(["json", "csv", "pdf"]),
    default="json",
    help="Export format (default: json)",
)
@click.option(
    "--output",
    "-o",
    "output_path",
    type=click.Path(),
    help="Output file path. If not specified, outputs to stdout (except PDF).",
)
@click.option(
    "--no-metadata",
    is_flag=True,
    help="Exclude metadata from export",
)
def export_anomalies(
    data_file: str,
    column: Optional[str],
    method: str,
    threshold: float,
    format_str: str,
    output_path: Optional[str],
    no_metadata: bool,
):
    """Export anomaly detection results.

    DATA_FILE: Path to the input data file (JSON or CSV)

    Examples:

        kai-analytics export anomalies data.csv --column price --method zscore -t 2.5

        kai-analytics export anomalies data.json --method iqr --format pdf -o anomalies.pdf
    """
    try:
        df = load_data(data_file)
        format = parse_format(format_str)
        anomaly_service = AnomalyService()
        export_service = ExportService()

        if column:
            if column not in df.columns:
                raise click.ClickException(f"Column '{column}' not found in data")
            series = df[column]
        else:
            # Use first numeric column
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            if not numeric_cols:
                raise click.ClickException("No numeric columns found in data")
            series = df[numeric_cols[0]]
            console.print(f"[dim]Using column: {numeric_cols[0]}[/dim]")

        if method == "zscore":
            result = anomaly_service.detect_zscore(series, threshold=threshold)
        else:
            result = anomaly_service.detect_iqr(series, multiplier=threshold)

        export_data = export_service.export_anomalies(
            result,
            format=format,
            include_metadata=not no_metadata,
        )

        write_output(export_data, output_path, format)

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@export.command("t-test")
@click.argument("data_file", type=click.Path(exists=True))
@click.option(
    "--group1",
    "-g1",
    required=True,
    help="Column name for first group",
)
@click.option(
    "--group2",
    "-g2",
    required=True,
    help="Column name for second group",
)
@click.option(
    "--alpha",
    "-a",
    type=float,
    default=0.05,
    help="Significance level (default: 0.05)",
)
@click.option(
    "--format",
    "-f",
    "format_str",
    type=click.Choice(["json", "csv", "pdf"]),
    default="json",
    help="Export format (default: json)",
)
@click.option(
    "--output",
    "-o",
    "output_path",
    type=click.Path(),
    help="Output file path. If not specified, outputs to stdout (except PDF).",
)
@click.option(
    "--no-metadata",
    is_flag=True,
    help="Exclude metadata from export",
)
def export_t_test(
    data_file: str,
    group1: str,
    group2: str,
    alpha: float,
    format_str: str,
    output_path: Optional[str],
    no_metadata: bool,
):
    """Export t-test results comparing two groups.

    DATA_FILE: Path to the input data file (JSON or CSV)

    Examples:

        kai-analytics export t-test data.csv --group1 control --group2 treatment

        kai-analytics export t-test data.csv -g1 before -g2 after --format pdf -o ttest.pdf
    """
    try:
        df = load_data(data_file)
        format = parse_format(format_str)
        stat_service = StatisticalService()
        export_service = ExportService()

        if group1 not in df.columns:
            raise click.ClickException(f"Column '{group1}' not found in data")
        if group2 not in df.columns:
            raise click.ClickException(f"Column '{group2}' not found in data")

        g1 = df[group1].dropna()
        g2 = df[group2].dropna()
        result = stat_service.t_test_independent(g1, g2, alpha=alpha)

        export_data = export_service.export_statistical_test(
            result,
            format=format,
            include_metadata=not no_metadata,
        )

        write_output(export_data, output_path, format)

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@cli.command("list-formats")
def list_formats():
    """Show available export formats and their descriptions."""
    table = Table(title="Available Export Formats")
    table.add_column("Format", style="cyan")
    table.add_column("MIME Type", style="green")
    table.add_column("Description")

    table.add_row(
        "json",
        "application/json",
        "JSON format with optional metadata. Best for programmatic access.",
    )
    table.add_row(
        "csv",
        "text/csv",
        "CSV format with optional metadata headers. Best for spreadsheets.",
    )
    table.add_row(
        "pdf",
        "application/pdf",
        "PDF format with tables and charts. Best for reports.",
    )

    console.print(table)


@cli.command("info")
def info():
    """Show information about available analytics exports."""
    console.print(Panel(
        "[bold]KAI Analytics Export CLI[/bold]\n\n"
        "Available export commands:\n"
        "  [cyan]descriptive[/cyan]      - Descriptive statistics (mean, std, quartiles, etc.)\n"
        "  [cyan]correlation[/cyan]      - Correlation between two variables\n"
        "  [cyan]correlation-matrix[/cyan] - Correlation matrix for all numeric columns\n"
        "  [cyan]forecast[/cyan]         - Time series forecast with confidence intervals\n"
        "  [cyan]anomalies[/cyan]        - Anomaly detection (z-score or IQR method)\n"
        "  [cyan]t-test[/cyan]           - Independent samples t-test\n\n"
        "Supported formats: JSON, CSV, PDF\n\n"
        "Use [bold]kai-analytics export <command> --help[/bold] for command-specific options.",
        title="Analytics Export",
    ))


if __name__ == "__main__":
    cli()
