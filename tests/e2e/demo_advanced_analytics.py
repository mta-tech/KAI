#!/usr/bin/env python
"""
Interactive Demo: KAI Advanced Analytics Capabilities
======================================================

This script demonstrates all newly implemented analytics features:
1. Visualization with Plotly (multiple chart types)
2. Statistical Analysis (t-test, ANOVA, correlation)
3. Anomaly Detection (Z-score, IQR, Isolation Forest)
4. Notebook Workflow (cell dependencies)
5. Rich CLI Output (formatted tables, syntax highlighting)

Run with: python tests/e2e/demo_advanced_analytics.py
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def generate_sales_data(n_records: int = 500) -> pd.DataFrame:
    """Generate realistic e-commerce sales data."""
    np.random.seed(42)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, periods=n_records)

    regions = ["North", "South", "East", "West", "Central"]
    categories = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books"]

    day_of_year = np.array([d.timetuple().tm_yday for d in dates])
    seasonality = 1 + 0.3 * np.sin(2 * np.pi * day_of_year / 365)

    region_base = {"North": 150, "South": 120, "East": 130, "West": 140, "Central": 110}

    data = []
    for i in range(n_records):
        region = np.random.choice(regions, p=[0.25, 0.20, 0.18, 0.22, 0.15])
        category = np.random.choice(categories)
        base = region_base[region] * seasonality[i]
        amount = np.random.gamma(shape=2, scale=base / 2)

        if np.random.random() < 0.02:
            amount *= np.random.choice([3, 4, 5])

        data.append({
            "date": dates[i],
            "region": region,
            "category": category,
            "amount": round(amount, 2),
            "quantity": np.random.randint(1, 10),
        })

    return pd.DataFrame(data)


def demo_rich_output():
    """Demonstrate Rich CLI output utilities."""
    from app.utils.rich_output import (
        console,
        dataframe_to_table,
        dict_to_table,
        format_number,
        print_error,
        print_info,
        print_panel,
        print_sql,
        print_success,
        print_warning,
    )

    console.rule("[bold blue]Rich CLI Output Demo")

    print_panel(
        "KAI Advanced Analytics provides beautiful CLI output\n"
        "using the Rich library for formatted tables, syntax\n"
        "highlighting, and styled messages.",
        title="Welcome",
        style="cyan",
    )

    # Message types
    print_success("Analysis completed successfully")
    print_warning("Large dataset detected - processing may take time")
    print_info("Using default parameters for analysis")
    print_error("Example error message (not a real error)")

    # SQL syntax highlighting
    print_sql(
        """
SELECT region,
       SUM(amount) as total_sales,
       AVG(amount) as avg_order,
       COUNT(*) as order_count
FROM sales
WHERE date >= '2024-01-01'
GROUP BY region
ORDER BY total_sales DESC
        """.strip(),
        title="Sample SQL Query",
    )

    # Number formatting
    console.print("\n[bold]Number Formatting:[/bold]")
    console.print(f"  1,500,000 -> {format_number(1500000)}")
    console.print(f"  75,000    -> {format_number(75000)}")
    console.print(f"  999       -> {format_number(999)}")

    # Dictionary table
    stats = {
        "Total Revenue": 1250000.50,
        "Average Order": 125.75,
        "Total Orders": 9941,
        "Top Region": "North",
        "Growth Rate": "15.3%",
    }
    table = dict_to_table(stats, title="Sales Summary")
    console.print(table)

    # DataFrame table
    df = generate_sales_data(10)
    table = dataframe_to_table(df, title="Sample Sales Data", max_rows=10)
    console.print(table)


def demo_visualization():
    """Demonstrate visualization capabilities."""
    from app.utils.rich_output import console, print_success

    console.rule("[bold green]Visualization Demo")

    from app.modules.visualization import ChartConfig, ChartService, ChartType, ThemeService

    sales_data = generate_sales_data(500)
    chart_service = ChartService()
    theme_service = ThemeService()

    console.print("[bold]Available Themes:[/bold]", theme_service.list_themes())
    console.print("[bold]Available Chart Types:[/bold]", [ct.value for ct in ChartType])

    # 1. Line Chart - Daily Sales Trend
    daily = sales_data.groupby(sales_data["date"].dt.date)["amount"].sum().reset_index()
    daily.columns = ["date", "amount"]

    result = chart_service.generate_chart(
        daily,
        ChartConfig(
            chart_type=ChartType.LINE,
            title="Daily Sales Trend",
            x_column="date",
            y_column="amount",
            theme="default",
        ),
    )
    print_success(f"Line chart generated: {len(daily)} data points")

    # 2. Bar Chart - Regional Sales
    regional = sales_data.groupby("region")["amount"].sum().reset_index()
    result = chart_service.generate_chart(
        regional,
        ChartConfig(
            chart_type=ChartType.BAR,
            title="Sales by Region",
            x_column="region",
            y_column="amount",
            theme="dark",
        ),
    )
    print_success(f"Bar chart generated: {len(regional)} regions")

    # 3. Pie Chart - Category Distribution
    category_sales = sales_data.groupby("category")["amount"].sum().reset_index()
    result = chart_service.generate_chart(
        category_sales,
        ChartConfig(
            chart_type=ChartType.PIE,
            title="Sales by Category",
            x_column="category",
            y_column="amount",
        ),
    )
    print_success(f"Pie chart generated: {len(category_sales)} categories")

    # 4. Histogram - Amount Distribution
    result = chart_service.generate_chart(
        sales_data,
        ChartConfig(
            chart_type=ChartType.HISTOGRAM,
            title="Transaction Amount Distribution",
            x_column="amount",
        ),
    )
    print_success(f"Histogram generated: range ${sales_data['amount'].min():.2f} - ${sales_data['amount'].max():.2f}")

    # 5. Box Plot - Regional Distribution
    result = chart_service.generate_chart(
        sales_data,
        ChartConfig(
            chart_type=ChartType.BOX,
            title="Amount Distribution by Region",
            x_column="region",
            y_column="amount",
        ),
    )
    print_success("Box plot generated for regional distributions")

    # 6. Scatter Plot
    result = chart_service.generate_chart(
        sales_data.head(200),
        ChartConfig(
            chart_type=ChartType.SCATTER,
            title="Quantity vs Amount",
            x_column="quantity",
            y_column="amount",
            color_column="region",
        ),
    )
    print_success("Scatter plot generated with regional coloring")

    # Chart Recommendation
    recommendation = chart_service.recommend_chart_type(
        daily, x_column="date", y_column="amount"
    )
    console.print(
        f"\n[bold]Chart Recommendation:[/bold] {recommendation.chart_type.value} "
        f"(confidence: {recommendation.confidence:.0%})"
    )
    console.print(f"[dim]Rationale: {recommendation.rationale}[/dim]")


def demo_statistical_analysis():
    """Demonstrate statistical analysis capabilities."""
    from app.utils.rich_output import console, dict_to_table, print_info

    console.rule("[bold yellow]Statistical Analysis Demo")

    from app.modules.analytics import StatisticalService

    sales_data = generate_sales_data(500)
    stat_service = StatisticalService()

    # 1. Descriptive Statistics
    print_info("Calculating descriptive statistics...")
    stats = stat_service.descriptive_stats(sales_data["amount"])

    stats_dict = {
        "Count": stats.count,
        "Mean": f"${stats.mean:.2f}",
        "Std Dev": f"${stats.std:.2f}",
        "Min": f"${stats.min:.2f}",
        "25%": f"${stats.q25:.2f}",
        "Median": f"${stats.median:.2f}",
        "75%": f"${stats.q75:.2f}",
        "Max": f"${stats.max:.2f}",
        "Skewness": f"{stats.skewness:.3f}" if stats.skewness else "N/A",
        "Kurtosis": f"{stats.kurtosis:.3f}" if stats.kurtosis else "N/A",
    }
    table = dict_to_table(stats_dict, title="Descriptive Statistics")
    console.print(table)

    # 2. ANOVA - Regional Comparison
    print_info("Running ANOVA across regions...")
    groups = [
        sales_data[sales_data["region"] == r]["amount"].values
        for r in sales_data["region"].unique()
    ]
    anova_result = stat_service.anova(*groups)

    console.print(f"\n[bold]One-Way ANOVA Results:[/bold]")
    console.print(f"  F-statistic: {anova_result.statistic:.3f}")
    console.print(f"  p-value: {anova_result.p_value:.4f}")
    console.print(
        f"  Conclusion: {'[green]Significant[/green]' if anova_result.is_significant else '[red]Not Significant[/red]'}"
    )
    console.print(f"  [dim]{anova_result.interpretation}[/dim]")

    # 3. Correlation Analysis
    print_info("Analyzing correlation between quantity and amount...")
    corr_result = stat_service.correlation(
        sales_data["quantity"].values,
        sales_data["amount"].values,
    )

    console.print(f"\n[bold]Correlation Analysis:[/bold]")
    console.print(f"  Coefficient (r): {corr_result.coefficient:.4f}")
    console.print(f"  p-value: {corr_result.p_value:.4f}")
    console.print(f"  [dim]{corr_result.interpretation}[/dim]")

    # 4. Correlation Matrix
    print_info("Generating correlation matrix...")
    numeric_df = sales_data[["amount", "quantity"]]
    matrix_result = stat_service.correlation_matrix(numeric_df)

    console.print(f"\n[bold]Correlation Matrix:[/bold]")
    for col in matrix_result.columns:
        row_vals = [f"{matrix_result.matrix[col][c]:.3f}" for c in matrix_result.columns]
        console.print(f"  {col}: {row_vals}")

    # 5. Chi-Square Test
    print_info("Running Chi-Square test for category vs region independence...")
    contingency = pd.crosstab(sales_data["category"], sales_data["region"])
    chi_result = stat_service.chi_square(contingency)

    console.print(f"\n[bold]Chi-Square Test:[/bold]")
    console.print(f"  Chi-Square statistic: {chi_result.statistic:.3f}")
    console.print(f"  p-value: {chi_result.p_value:.4f}")
    console.print(f"  Degrees of freedom: {chi_result.degrees_of_freedom:.0f}")
    console.print(
        f"  Conclusion: {'[green]Significant association[/green]' if chi_result.is_significant else '[yellow]No significant association[/yellow]'}"
    )


def demo_anomaly_detection():
    """Demonstrate anomaly detection capabilities."""
    from app.utils.rich_output import console, print_info, print_warning

    console.rule("[bold red]Anomaly Detection Demo")

    from app.modules.analytics import AnomalyService

    sales_data = generate_sales_data(500)
    anomaly_service = AnomalyService()

    # 1. Z-Score Method
    print_info("Detecting anomalies using Z-Score method (threshold=3.0)...")
    zscore_result = anomaly_service.detect_zscore(sales_data["amount"], threshold=3.0)

    console.print(f"\n[bold]Z-Score Anomaly Detection:[/bold]")
    console.print(f"  Total points: {zscore_result.total_points}")
    console.print(f"  Anomalies found: {zscore_result.anomaly_count}")
    console.print(f"  Anomaly rate: {zscore_result.anomaly_percentage:.1f}%")

    if zscore_result.anomalies:
        console.print(f"  Sample anomalies:")
        for a in zscore_result.anomalies[:3]:
            console.print(f"    - Index {a['index']}: ${a['value']:.2f} (z={a['z_score']:.2f})")

    # 2. IQR Method
    print_info("Detecting anomalies using IQR method (multiplier=1.5)...")
    iqr_result = anomaly_service.detect_iqr(sales_data["amount"], multiplier=1.5)

    console.print(f"\n[bold]IQR Anomaly Detection:[/bold]")
    console.print(f"  Total points: {iqr_result.total_points}")
    console.print(f"  Anomalies found: {iqr_result.anomaly_count}")
    console.print(f"  Anomaly rate: {iqr_result.anomaly_percentage:.1f}%")

    if iqr_result.anomalies:
        high_anomalies = [a for a in iqr_result.anomalies if a.get("direction") == "high"]
        low_anomalies = [a for a in iqr_result.anomalies if a.get("direction") == "low"]
        console.print(f"  High outliers: {len(high_anomalies)}")
        console.print(f"  Low outliers: {len(low_anomalies)}")

    # 3. Isolation Forest
    print_info("Detecting anomalies using Isolation Forest (contamination=0.05)...")
    if_result = anomaly_service.detect_isolation_forest(
        sales_data, columns=["amount", "quantity"], contamination=0.05
    )

    console.print(f"\n[bold]Isolation Forest Detection:[/bold]")
    console.print(f"  Total points: {if_result.total_points}")
    console.print(f"  Anomalies found: {if_result.anomaly_count}")
    console.print(f"  Anomaly rate: {if_result.anomaly_percentage:.1f}%")

    # Comparison
    console.print(f"\n[bold]Method Comparison:[/bold]")
    zscore_indices = {a["index"] for a in zscore_result.anomalies}
    iqr_indices = {a["index"] for a in iqr_result.anomalies}
    overlap = zscore_indices & iqr_indices

    console.print(f"  Z-Score detected: {len(zscore_indices)} anomalies")
    console.print(f"  IQR detected: {len(iqr_indices)} anomalies")
    console.print(f"  Overlap (both methods): {len(overlap)} anomalies")

    if overlap:
        print_warning(f"{len(overlap)} transactions flagged by multiple methods - high confidence anomalies")


def demo_notebook_workflow():
    """Demonstrate notebook workflow capabilities."""
    from app.utils.rich_output import console, print_info, print_success

    console.rule("[bold magenta]Notebook Workflow Demo")

    from app.modules.notebook import Cell, CellStatus, CellType, Notebook, NotebookExecutor, Parameter
    import uuid

    # Create a sample analytics notebook
    notebook = Notebook(
        id=str(uuid.uuid4()),
        name="Sales Performance Analysis",
        description="Automated workflow for analyzing regional sales performance",
        parameters=[
            Parameter(name="start_date", param_type="date", required=True, description="Analysis start date"),
            Parameter(name="region", param_type="string", required=False, default="all", options=["all", "North", "South", "East", "West"]),
            Parameter(name="threshold", param_type="number", default=3.0, description="Anomaly detection threshold"),
        ],
        cells=[
            Cell(
                id="fetch_data",
                name="Fetch Sales Data",
                cell_type=CellType.QUERY,
                prompt="SELECT * FROM sales WHERE date >= :start_date AND (:region = 'all' OR region = :region)",
            ),
            Cell(
                id="calc_stats",
                name="Calculate Statistics",
                cell_type=CellType.CODE,
                code="stats = df.groupby('region').agg({'amount': ['sum', 'mean', 'count']})",
                depends_on=["fetch_data"],
            ),
            Cell(
                id="detect_anomalies",
                name="Detect Anomalies",
                cell_type=CellType.CODE,
                code="anomalies = detect_zscore(df['amount'], threshold=:threshold)",
                depends_on=["fetch_data"],
            ),
            Cell(
                id="viz_trend",
                name="Sales Trend Visualization",
                cell_type=CellType.VISUALIZATION,
                code='{"chart_type": "line", "x": "date", "y": "amount", "title": "Daily Sales Trend"}',
                depends_on=["fetch_data"],
            ),
            Cell(
                id="viz_regional",
                name="Regional Comparison",
                cell_type=CellType.VISUALIZATION,
                code='{"chart_type": "bar", "x": "region", "y": "amount", "title": "Sales by Region"}',
                depends_on=["calc_stats"],
            ),
            Cell(
                id="summary",
                name="Generate Summary",
                cell_type=CellType.TEXT,
                prompt="Generate executive summary of the analysis results",
                depends_on=["calc_stats", "detect_anomalies", "viz_trend", "viz_regional"],
            ),
        ],
        tags=["sales", "analytics", "automated"],
    )

    console.print(f"\n[bold]Notebook: {notebook.name}[/bold]")
    console.print(f"ID: {notebook.id}")
    console.print(f"Description: {notebook.description}")
    console.print(f"Tags: {notebook.tags}")

    # Display parameters
    console.print(f"\n[bold]Parameters ({len(notebook.parameters)}):[/bold]")
    for param in notebook.parameters:
        required = "[red]*[/red]" if param.required else ""
        default = f" (default: {param.default})" if param.default is not None else ""
        console.print(f"  - {param.name}{required}: {param.param_type}{default}")

    # Display cells
    console.print(f"\n[bold]Cells ({len(notebook.cells)}):[/bold]")
    for cell in notebook.cells:
        deps = f" [dim](depends on: {', '.join(cell.depends_on)})[/dim]" if cell.depends_on else ""
        console.print(f"  [{cell.cell_type.value}] {cell.name}{deps}")

    # Demonstrate dependency resolution
    executor = NotebookExecutor()
    execution_order = executor._resolve_dependencies(notebook.cells)

    console.print(f"\n[bold]Execution Order (dependency-resolved):[/bold]")
    for i, cell in enumerate(execution_order, 1):
        console.print(f"  {i}. {cell.name} ({cell.id})")

    print_success(f"Notebook ready for execution with {len(notebook.cells)} cells")


def demo_streaming_and_batch():
    """Demonstrate SSE streaming and batch processing APIs."""
    import asyncio
    import json
    import uuid
    from datetime import datetime
    from typing import Any, AsyncGenerator

    from pydantic import BaseModel, Field
    from app.utils.rich_output import console, print_info, print_success

    console.rule("[bold cyan]SSE Streaming & Batch Processing Demo")

    # SSE Streaming Demo - inline implementation to avoid circular import
    print_info("Demonstrating SSE event generation...")

    async def event_generator(task_id: str, total_steps: int = 5) -> AsyncGenerator[dict[str, Any], None]:
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
            await asyncio.sleep(0.1)

        yield {
            "event": "complete",
            "data": json.dumps({
                "task_id": task_id,
                "status": "completed",
                "message": "Task completed successfully",
                "timestamp": datetime.utcnow().isoformat(),
            }),
        }

    async def show_events():
        events = []
        async for event in event_generator("demo-task-123", total_steps=3):
            events.append(event)
            data = json.loads(event["data"])
            console.print(f"  [{event['event']}] Step {data.get('step', '-')}: {data.get('message', data.get('status', ''))}")
        return events

    events = asyncio.run(show_events())
    print_success(f"Generated {len(events)} SSE events")

    # Batch Processing Demo - inline implementation
    print_info("\nDemonstrating batch processing...")

    class AnalysisRequest(BaseModel):
        prompt: str
        database_alias: str | None = None
        options: dict[str, Any] = Field(default_factory=dict)

    class BatchStatus(BaseModel):
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
        job = _batch_jobs[batch_id]
        job.status = "running"
        job.updated_at = datetime.utcnow()

        for i, request in enumerate(requests):
            await asyncio.sleep(0.1)
            job.results[f"request_{i}"] = {
                "status": "completed",
                "prompt": request.prompt,
                "result": {"message": f"Processed: {request.prompt[:50]}..."},
            }
            job.completed += 1
            job.updated_at = datetime.utcnow()

        job.status = "completed" if job.failed == 0 else "partial"
        job.updated_at = datetime.utcnow()

    requests = [
        AnalysisRequest(prompt="Analyze Q1 sales performance"),
        AnalysisRequest(prompt="Compare regional growth rates"),
        AnalysisRequest(prompt="Identify top 10 customers"),
        AnalysisRequest(prompt="Forecast Q2 revenue"),
    ]

    batch_id = str(uuid.uuid4())
    now = datetime.utcnow()

    job = BatchStatus(
        batch_id=batch_id,
        status="pending",
        total=len(requests),
        completed=0,
        failed=0,
        created_at=now,
        updated_at=now,
    )
    _batch_jobs[batch_id] = job

    console.print(f"\n[bold]Batch Job Created:[/bold]")
    console.print(f"  ID: {batch_id}")
    console.print(f"  Total requests: {len(requests)}")

    # Process batch
    asyncio.run(process_batch(batch_id, requests))

    final_job = _batch_jobs[batch_id]
    console.print(f"\n[bold]Batch Job Completed:[/bold]")
    console.print(f"  Status: {final_job.status}")
    console.print(f"  Completed: {final_job.completed}/{final_job.total}")
    console.print(f"  Failed: {final_job.failed}")

    print_success(f"Batch processing completed: {final_job.completed} requests processed")


def main():
    """Run all demos."""
    from app.utils.rich_output import console

    console.print("\n")
    console.print("[bold blue]=" * 60)
    console.print("[bold blue]   KAI ADVANCED ANALYTICS - INTERACTIVE DEMO")
    console.print("[bold blue]=" * 60)
    console.print("\n")

    try:
        demo_rich_output()
        console.print("\n")

        demo_visualization()
        console.print("\n")

        demo_statistical_analysis()
        console.print("\n")

        demo_anomaly_detection()
        console.print("\n")

        demo_notebook_workflow()
        console.print("\n")

        demo_streaming_and_batch()
        console.print("\n")

        console.print("[bold green]=" * 60)
        console.print("[bold green]   ALL DEMOS COMPLETED SUCCESSFULLY!")
        console.print("[bold green]=" * 60)
        console.print("\n")

    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
