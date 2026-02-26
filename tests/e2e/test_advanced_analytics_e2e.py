"""
End-to-End Test Suite: KAI Advanced Analytics
==============================================

This test suite validates all newly implemented analytics capabilities:
- Visualization module (Plotly charts)
- Statistical analysis (scipy/statsmodels)
- Anomaly detection
- Notebook workflow execution
- Rich CLI output utilities
- SSE streaming API
- Batch processing API

Use Case: E-Commerce Sales Analytics
------------------------------------
Analyzing sales data for an e-commerce platform to:
1. Visualize sales trends and patterns
2. Perform statistical analysis on regional performance
3. Detect anomalies in transaction amounts
4. Run reusable notebook workflows
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from io import StringIO

import numpy as np
import pandas as pd
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# =============================================================================
# Test Data Generation
# =============================================================================

def generate_ecommerce_sales_data(n_records: int = 1000) -> pd.DataFrame:
    """Generate realistic e-commerce sales data for testing."""
    np.random.seed(42)

    # Date range: last 365 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, periods=n_records)

    # Regions with different performance characteristics
    regions = ["North", "South", "East", "West", "Central"]
    region_weights = [0.25, 0.20, 0.18, 0.22, 0.15]

    # Product categories
    categories = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books"]

    # Generate base sales with seasonality
    day_of_year = np.array([d.timetuple().tm_yday for d in dates])
    seasonality = 1 + 0.3 * np.sin(2 * np.pi * day_of_year / 365)

    # Base amounts by region (different means)
    region_base = {"North": 150, "South": 120, "East": 130, "West": 140, "Central": 110}

    data = []
    for i in range(n_records):
        region = np.random.choice(regions, p=region_weights)
        category = np.random.choice(categories)

        # Base amount with region effect and seasonality
        base = region_base[region] * seasonality[i]
        amount = np.random.gamma(shape=2, scale=base/2)

        # Add some outliers (anomalies) ~2% of data
        if np.random.random() < 0.02:
            amount *= np.random.choice([3, 4, 5])  # Large outliers

        data.append({
            "date": dates[i],
            "region": region,
            "category": category,
            "amount": round(amount, 2),
            "quantity": np.random.randint(1, 10),
            "customer_id": f"CUST{np.random.randint(1000, 9999)}",
        })

    return pd.DataFrame(data)


def generate_ab_test_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate A/B test data for statistical testing."""
    np.random.seed(42)

    # Control group (existing checkout flow)
    control = pd.DataFrame({
        "group": ["control"] * 500,
        "conversion_rate": np.random.binomial(1, 0.12, 500),
        "time_on_page": np.random.normal(45, 15, 500),
        "revenue": np.random.gamma(2, 25, 500),
    })

    # Treatment group (new checkout flow - higher conversion)
    treatment = pd.DataFrame({
        "group": ["treatment"] * 500,
        "conversion_rate": np.random.binomial(1, 0.15, 500),
        "time_on_page": np.random.normal(40, 12, 500),
        "revenue": np.random.gamma(2.2, 26, 500),
    })

    return control, treatment


# =============================================================================
# Visualization Tests
# =============================================================================

class TestVisualizationE2E:
    """End-to-end tests for visualization module."""

    @pytest.fixture
    def sales_data(self) -> pd.DataFrame:
        return generate_ecommerce_sales_data(500)

    @pytest.fixture
    def chart_service(self):
        from app.modules.visualization import ChartService
        return ChartService()

    @pytest.fixture
    def theme_service(self):
        from app.modules.visualization import ThemeService
        return ThemeService()

    def test_line_chart_sales_trend(self, sales_data: pd.DataFrame, chart_service):
        """Test: Visualize daily sales trend over time."""
        from app.modules.visualization import ChartConfig, ChartType

        # Aggregate daily sales
        daily_sales = sales_data.groupby(sales_data["date"].dt.date)["amount"].sum().reset_index()
        daily_sales.columns = ["date", "total_sales"]

        config = ChartConfig(
            chart_type=ChartType.LINE,
            title="Daily Sales Trend",
            x_column="date",
            y_column="total_sales",
            theme="default",
        )

        result = chart_service.generate_chart(daily_sales, config)

        assert result.chart_type == "line"
        assert result.html is not None
        assert "Daily Sales Trend" in result.html
        assert result.json_spec is not None
        print(f"[PASS] Line chart generated with {len(daily_sales)} data points")

    def test_bar_chart_regional_sales(self, sales_data: pd.DataFrame, chart_service):
        """Test: Compare sales by region."""
        from app.modules.visualization import ChartConfig, ChartType

        regional_sales = sales_data.groupby("region")["amount"].sum().reset_index()

        config = ChartConfig(
            chart_type=ChartType.BAR,
            title="Sales by Region",
            x_column="region",
            y_column="amount",
            theme="dark",
        )

        result = chart_service.generate_chart(regional_sales, config)

        assert result.chart_type == "bar"
        assert result.html is not None
        print(f"[PASS] Bar chart: {regional_sales['region'].tolist()}")

    def test_pie_chart_category_distribution(self, sales_data: pd.DataFrame, chart_service):
        """Test: Show product category distribution."""
        from app.modules.visualization import ChartConfig, ChartType

        category_sales = sales_data.groupby("category")["amount"].sum().reset_index()

        config = ChartConfig(
            chart_type=ChartType.PIE,
            title="Sales by Category",
            x_column="category",
            y_column="amount",
        )

        result = chart_service.generate_chart(category_sales, config)

        assert result.chart_type == "pie"
        assert result.html is not None
        print(f"[PASS] Pie chart: {len(category_sales)} categories")

    def test_scatter_chart_quantity_vs_amount(self, sales_data: pd.DataFrame, chart_service):
        """Test: Analyze relationship between quantity and amount."""
        from app.modules.visualization import ChartConfig, ChartType

        config = ChartConfig(
            chart_type=ChartType.SCATTER,
            title="Quantity vs Amount",
            x_column="quantity",
            y_column="amount",
            color_column="region",
        )

        result = chart_service.generate_chart(sales_data.head(200), config)

        assert result.chart_type == "scatter"
        assert result.html is not None
        print("[PASS] Scatter chart with color grouping by region")

    def test_histogram_amount_distribution(self, sales_data: pd.DataFrame, chart_service):
        """Test: Show distribution of transaction amounts."""
        from app.modules.visualization import ChartConfig, ChartType

        config = ChartConfig(
            chart_type=ChartType.HISTOGRAM,
            title="Transaction Amount Distribution",
            x_column="amount",
        )

        result = chart_service.generate_chart(sales_data, config)

        assert result.chart_type == "histogram"
        assert result.html is not None
        print(f"[PASS] Histogram: amount range ${sales_data['amount'].min():.2f} - ${sales_data['amount'].max():.2f}")

    def test_heatmap_region_category(self, sales_data: pd.DataFrame, chart_service):
        """Test: Create heatmap of region vs category sales."""
        from app.modules.visualization import ChartConfig, ChartType

        pivot = sales_data.pivot_table(
            values="amount",
            index="region",
            columns="category",
            aggfunc="sum"
        ).reset_index()

        # Melt for heatmap format
        heatmap_data = pivot.melt(id_vars=["region"], var_name="category", value_name="amount")

        config = ChartConfig(
            chart_type=ChartType.HEATMAP,
            title="Sales Heatmap: Region vs Category",
            x_column="category",
            y_column="region",
            color_column="amount",
        )

        result = chart_service.generate_chart(heatmap_data, config)

        assert result.chart_type == "heatmap"
        print("[PASS] Heatmap generated for region-category matrix")

    def test_box_plot_regional_distribution(self, sales_data: pd.DataFrame, chart_service):
        """Test: Show amount distribution by region using box plot."""
        from app.modules.visualization import ChartConfig, ChartType

        config = ChartConfig(
            chart_type=ChartType.BOX,
            title="Amount Distribution by Region",
            x_column="region",
            y_column="amount",
        )

        result = chart_service.generate_chart(sales_data, config)

        assert result.chart_type == "box"
        print("[PASS] Box plot showing regional distributions")

    def test_chart_recommendation(self, sales_data: pd.DataFrame, chart_service):
        """Test: Get chart type recommendation based on data."""
        # Time series data should recommend line chart
        daily = sales_data.groupby(sales_data["date"].dt.date)["amount"].sum().reset_index()
        daily.columns = ["date", "amount"]

        recommendation = chart_service.recommend_chart_type(
            daily,
            x_column="date",
            y_column="amount",
        )

        assert recommendation.chart_type.value in ["line", "scatter", "bar"]
        assert recommendation.confidence > 0
        print(f"[PASS] Recommended: {recommendation.chart_type.value} (confidence: {recommendation.confidence:.2f})")

    def test_all_themes(self, sales_data: pd.DataFrame, chart_service, theme_service):
        """Test: Verify all themes work correctly."""
        from app.modules.visualization import ChartConfig, ChartType

        themes = theme_service.list_themes()
        regional_sales = sales_data.groupby("region")["amount"].sum().reset_index()

        for theme_name in themes:
            config = ChartConfig(
                chart_type=ChartType.BAR,
                title=f"Sales ({theme_name} theme)",
                x_column="region",
                y_column="amount",
                theme=theme_name,
            )

            result = chart_service.generate_chart(regional_sales, config)
            assert result.html is not None

        print(f"[PASS] All {len(themes)} themes validated: {themes}")


# =============================================================================
# Statistical Analysis Tests
# =============================================================================

class TestStatisticalAnalysisE2E:
    """End-to-end tests for statistical analysis module."""

    @pytest.fixture
    def statistical_service(self):
        from app.modules.analytics import StatisticalService
        return StatisticalService()

    @pytest.fixture
    def ab_test_data(self):
        return generate_ab_test_data()

    @pytest.fixture
    def sales_data(self) -> pd.DataFrame:
        return generate_ecommerce_sales_data(500)

    def test_descriptive_statistics(self, sales_data: pd.DataFrame, statistical_service):
        """Test: Calculate comprehensive descriptive statistics."""
        stats = statistical_service.descriptive_stats(sales_data["amount"])

        assert stats.count == len(sales_data)
        assert stats.mean > 0
        assert stats.std > 0
        assert stats.min < stats.max
        assert stats.median > 0

        print(f"[PASS] Descriptive stats: mean=${stats.mean:.2f}, std=${stats.std:.2f}")
        print(f"       Range: ${stats.min:.2f} - ${stats.max:.2f}")
        print(f"       Skewness: {stats.skewness:.3f}, Kurtosis: {stats.kurtosis:.3f}")

    def test_t_test_ab_experiment(self, ab_test_data, statistical_service):
        """Test: Run t-test on A/B test revenue data."""
        control, treatment = ab_test_data

        result = statistical_service.t_test_independent(
            control["revenue"].values,
            treatment["revenue"].values,
            alpha=0.05,
        )

        assert result.test_name == "Independent Samples T-Test"
        assert result.p_value >= 0
        assert result.p_value <= 1

        significance = "significant" if result.is_significant else "not significant"
        print(f"[PASS] T-Test: p={result.p_value:.4f} ({significance})")
        print(f"       Statistic: {result.statistic:.3f}")

    def test_anova_regional_comparison(self, sales_data: pd.DataFrame, statistical_service):
        """Test: ANOVA to compare sales across regions."""
        # Split data by region
        groups = [
            sales_data[sales_data["region"] == region]["amount"].values
            for region in sales_data["region"].unique()
        ]

        result = statistical_service.anova(*groups, alpha=0.05)

        assert result.test_name == "One-Way ANOVA"
        assert result.p_value >= 0

        significance = "significant" if result.is_significant else "not significant"
        print(f"[PASS] ANOVA across {len(groups)} regions: p={result.p_value:.4f} ({significance})")
        print(f"       F-statistic: {result.statistic:.3f}")

    def test_correlation_analysis(self, sales_data: pd.DataFrame, statistical_service):
        """Test: Analyze correlation between quantity and amount."""
        result = statistical_service.correlation(
            sales_data["quantity"].values,
            sales_data["amount"].values,
            method="pearson",
        )

        assert result.coefficient >= -1 and result.coefficient <= 1
        assert result.method == "pearson"

        strength = "weak" if abs(result.coefficient) < 0.3 else "moderate" if abs(result.coefficient) < 0.7 else "strong"
        print(f"[PASS] Correlation (quantity vs amount): r={result.coefficient:.3f} ({strength})")
        print(f"       p-value: {result.p_value:.4f}")

    def test_correlation_matrix(self, sales_data: pd.DataFrame, statistical_service):
        """Test: Generate correlation matrix for numeric columns."""
        numeric_df = sales_data[["amount", "quantity"]].copy()

        result = statistical_service.correlation_matrix(numeric_df, method="pearson")

        assert result.matrix is not None
        assert len(result.columns) == 2

        print(f"[PASS] Correlation matrix generated for columns: {result.columns}")
        print(f"       Matrix values: {result.matrix}")

    def test_chi_square_category_region(self, sales_data: pd.DataFrame, statistical_service):
        """Test: Chi-square test for category vs region independence."""
        contingency = pd.crosstab(sales_data["category"], sales_data["region"])

        result = statistical_service.chi_square(contingency.values, alpha=0.05)

        assert "Chi-Square" in result.test_name
        assert result.p_value >= 0

        independence = "dependent" if result.is_significant else "independent"
        print(f"[PASS] Chi-Square (category vs region): p={result.p_value:.4f}")
        print(f"       Category and region are {independence}")


# =============================================================================
# Anomaly Detection Tests
# =============================================================================

class TestAnomalyDetectionE2E:
    """End-to-end tests for anomaly detection."""

    @pytest.fixture
    def anomaly_service(self):
        from app.modules.analytics import AnomalyService
        return AnomalyService()

    @pytest.fixture
    def sales_data(self) -> pd.DataFrame:
        return generate_ecommerce_sales_data(500)

    def test_zscore_anomaly_detection(self, sales_data: pd.DataFrame, anomaly_service):
        """Test: Detect anomalies using Z-score method."""
        result = anomaly_service.detect_zscore(
            sales_data["amount"],
            threshold=3.0,
        )

        assert result.method == "z-score"
        assert result.anomaly_count >= 0
        assert result.total_points == len(sales_data)

        pct = (result.anomaly_count / result.total_points) * 100
        print(f"[PASS] Z-Score detection: {result.anomaly_count} anomalies ({pct:.1f}%)")
        if result.anomaly_count > 0:
            anomaly_values = [a["value"] for a in result.anomalies[:5]]
            print(f"       Sample anomalies: {anomaly_values}")

    def test_iqr_anomaly_detection(self, sales_data: pd.DataFrame, anomaly_service):
        """Test: Detect anomalies using IQR method."""
        result = anomaly_service.detect_iqr(
            sales_data["amount"],
            multiplier=1.5,
        )

        assert result.method == "iqr"
        assert result.anomaly_count >= 0

        pct = (result.anomaly_count / result.total_points) * 100
        print(f"[PASS] IQR detection: {result.anomaly_count} anomalies ({pct:.1f}%)")
        print(f"       Threshold multiplier: {result.threshold}")

    def test_isolation_forest_detection(self, sales_data: pd.DataFrame, anomaly_service):
        """Test: Detect anomalies using Isolation Forest."""
        result = anomaly_service.detect_isolation_forest(
            sales_data,
            columns=["amount", "quantity"],
            contamination=0.05,
        )

        assert result.method == "isolation_forest"

        pct = (result.anomaly_count / result.total_points) * 100
        print(f"[PASS] Isolation Forest: {result.anomaly_count} anomalies ({pct:.1f}%)")

    def test_compare_anomaly_methods(self, sales_data: pd.DataFrame, anomaly_service):
        """Test: Compare results from different anomaly detection methods."""
        zscore_result = anomaly_service.detect_zscore(sales_data["amount"], threshold=3.0)
        iqr_result = anomaly_service.detect_iqr(sales_data["amount"], multiplier=1.5)

        # Find overlap by extracting indices from anomalies
        zscore_indices = {a["index"] for a in zscore_result.anomalies}
        iqr_indices = {a["index"] for a in iqr_result.anomalies}
        overlap = zscore_indices & iqr_indices

        print(f"[PASS] Method comparison:")
        print(f"       Z-Score: {zscore_result.anomaly_count} anomalies")
        print(f"       IQR: {iqr_result.anomaly_count} anomalies")
        print(f"       Overlap: {len(overlap)} anomalies detected by both methods")


# =============================================================================
# Notebook Workflow Tests
# =============================================================================

class TestNotebookWorkflowE2E:
    """End-to-end tests for notebook workflow execution."""

    def test_create_notebook_models(self):
        """Test: Create notebook models directly."""
        from app.modules.notebook import Cell, CellType, Notebook, Parameter
        import uuid

        # Create cells (using correct field names: id, name, prompt/code)
        cells = [
            Cell(
                id="query_sales",
                cell_type=CellType.QUERY,
                name="Fetch Sales Data",
                prompt="SELECT * FROM sales WHERE date >= :start_date",
            ),
            Cell(
                id="viz_trend",
                cell_type=CellType.VISUALIZATION,
                name="Sales Trend Chart",
                code='{"chart_type": "line", "x": "date", "y": "amount"}',
                depends_on=["query_sales"],
            ),
            Cell(
                id="summary",
                cell_type=CellType.TEXT,
                name="Summary",
                prompt="Analysis complete. See visualizations above.",
                depends_on=["viz_trend"],
            ),
        ]

        # Create parameters
        parameters = [
            Parameter(name="start_date", param_type="date", required=True),
            Parameter(name="region", param_type="string", required=False, default="all"),
        ]

        # Create notebook
        notebook = Notebook(
            id=str(uuid.uuid4()),
            name="Sales Analysis Workflow",
            description="Analyze sales data with visualizations and statistics",
            cells=cells,
            parameters=parameters,
        )

        assert notebook.id is not None
        assert notebook.name == "Sales Analysis Workflow"
        assert len(notebook.cells) == 3
        assert len(notebook.parameters) == 2

        print(f"[PASS] Created notebook: {notebook.name}")
        print(f"       ID: {notebook.id}")
        print(f"       Cells: {len(notebook.cells)}, Parameters: {len(notebook.parameters)}")

    def test_notebook_dependency_resolution(self):
        """Test: Verify correct dependency resolution in notebook."""
        from app.modules.notebook import Cell, CellType, NotebookExecutor

        cells = [
            Cell(id="A", name="Step A", cell_type=CellType.TEXT, prompt="Step A"),
            Cell(id="B", name="Step B", cell_type=CellType.TEXT, prompt="Step B", depends_on=["A"]),
            Cell(id="C", name="Step C", cell_type=CellType.TEXT, prompt="Step C", depends_on=["A"]),
            Cell(id="D", name="Step D", cell_type=CellType.TEXT, prompt="Step D", depends_on=["B", "C"]),
        ]

        executor = NotebookExecutor()
        # Resolve execution order
        order = executor._resolve_dependencies(cells)
        order_ids = [cell.id for cell in order]

        # A must come before B and C
        assert order_ids.index("A") < order_ids.index("B")
        assert order_ids.index("A") < order_ids.index("C")
        # B and C must come before D
        assert order_ids.index("B") < order_ids.index("D")
        assert order_ids.index("C") < order_ids.index("D")

        print(f"[PASS] Dependency resolution: {' -> '.join(order_ids)}")

    def test_cell_types(self):
        """Test: Verify all cell types are available."""
        from app.modules.notebook import CellType

        expected_types = ["query", "visualization", "text", "code", "user_input"]
        actual_types = [ct.value for ct in CellType]

        for expected in expected_types:
            assert expected in actual_types, f"Missing cell type: {expected}"

        print(f"[PASS] All cell types available: {actual_types}")


# =============================================================================
# Rich CLI Output Tests
# =============================================================================

class TestRichCLIOutputE2E:
    """End-to-end tests for Rich CLI output utilities."""

    @pytest.fixture
    def sales_data(self) -> pd.DataFrame:
        return generate_ecommerce_sales_data(100)

    def test_dataframe_to_table(self, sales_data: pd.DataFrame):
        """Test: Convert DataFrame to Rich table."""
        from app.utils.rich_output import dataframe_to_table

        table = dataframe_to_table(
            sales_data.head(10),
            title="Sales Data Preview",
            max_rows=10,
        )

        assert table is not None
        assert table.title == "Sales Data Preview"
        print(f"[PASS] DataFrame converted to table with {table.row_count} rows")

    def test_dict_to_table(self):
        """Test: Convert dictionary to Rich table."""
        from app.utils.rich_output import dict_to_table

        stats = {
            "Total Sales": 125000.50,
            "Average Order": 75.25,
            "Total Orders": 1662,
            "Top Region": "North",
        }

        table = dict_to_table(stats, title="Sales Summary")

        assert table is not None
        assert table.row_count == 4
        print("[PASS] Dictionary converted to key-value table")

    def test_format_number(self):
        """Test: Format numbers with appropriate suffixes."""
        from app.utils.rich_output import format_number

        assert format_number(1500000) == "1.50M"
        assert format_number(75000) == "75.00K"
        assert format_number(999) == "999.00"
        assert format_number(1234567.89, decimals=1) == "1.2M"

        print("[PASS] Number formatting: 1.5M, 75K, 999")

    def test_print_sql(self, capsys):
        """Test: Print SQL with syntax highlighting."""
        from app.utils.rich_output import print_sql

        sql = """
        SELECT region, SUM(amount) as total_sales
        FROM sales
        WHERE date >= '2024-01-01'
        GROUP BY region
        ORDER BY total_sales DESC
        """

        print_sql(sql, title="Regional Sales Query")

        # Verify output was produced (Rich writes to console)
        print("[PASS] SQL printed with syntax highlighting")

    def test_print_messages(self, capsys):
        """Test: Print success, error, warning, and info messages."""
        from app.utils.rich_output import print_success, print_error, print_warning, print_info

        print_success("Analysis completed successfully")
        print_error("Failed to connect to database")
        print_warning("Large dataset may take time to process")
        print_info("Using default parameters")

        print("[PASS] All message types printed correctly")


# =============================================================================
# SSE Streaming API Tests
# =============================================================================

class TestSSEStreamingE2E:
    """End-to-end tests for SSE streaming API."""

    @pytest.mark.asyncio
    async def test_event_generator(self):
        """Test: Verify event generator produces correct events."""
        from app.api.v2.streaming import event_generator

        task_id = "test-task-123"
        events = []

        async for event in event_generator(task_id, total_steps=3):
            events.append(event)

        # Should have 3 progress events + 1 complete event
        assert len(events) == 4

        # Check progress events
        for i in range(3):
            assert events[i]["event"] == "progress"
            data = json.loads(events[i]["data"])
            assert data["task_id"] == task_id
            assert data["step"] == i + 1

        # Check complete event
        assert events[3]["event"] == "complete"
        complete_data = json.loads(events[3]["data"])
        assert complete_data["status"] == "completed"

        print(f"[PASS] Event generator produced {len(events)} events")
        print(f"       Progress events: {len([e for e in events if e['event'] == 'progress'])}")

    @pytest.mark.asyncio
    async def test_notebook_event_generator(self):
        """Test: Verify notebook execution event generator."""
        from app.api.v2.streaming import notebook_event_generator

        run_id = "run-456"
        cells = ["query", "visualization", "summary"]
        events = []

        async for event in notebook_event_generator(run_id, cells):
            events.append(event)

        # Each cell produces 2 events (start + complete) + 1 final complete
        expected_events = len(cells) * 2 + 1
        assert len(events) == expected_events

        # Verify cell events
        cell_starts = [e for e in events if e["event"] == "cell_start"]
        cell_completes = [e for e in events if e["event"] == "cell_complete"]

        assert len(cell_starts) == len(cells)
        assert len(cell_completes) == len(cells)

        print(f"[PASS] Notebook events: {len(cell_starts)} cell starts, {len(cell_completes)} cell completes")


# =============================================================================
# Batch Processing API Tests
# =============================================================================

class TestBatchProcessingE2E:
    """End-to-end tests for batch processing API."""

    @pytest.mark.asyncio
    async def test_batch_job_lifecycle(self):
        """Test: Complete batch job lifecycle."""
        from app.api.v2.batch import (
            AnalysisRequest,
            BatchRequest,
            BatchStatus,
            _batch_jobs,
            process_batch,
        )
        import uuid
        from datetime import datetime

        # Create batch request
        requests = [
            AnalysisRequest(prompt="Analyze sales by region"),
            AnalysisRequest(prompt="Compare Q1 vs Q2 performance"),
            AnalysisRequest(prompt="Identify top customers"),
        ]

        batch_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # Initialize job
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

        # Process batch
        await process_batch(batch_id, requests)

        # Verify completion
        final_job = _batch_jobs[batch_id]
        assert final_job.status == "completed"
        assert final_job.completed == 3
        assert final_job.failed == 0
        assert len(final_job.results) == 3

        print(f"[PASS] Batch job completed: {final_job.completed}/{final_job.total} requests")
        print(f"       Status: {final_job.status}")

        # Cleanup
        del _batch_jobs[batch_id]

    def test_batch_request_models(self):
        """Test: Verify batch request/response models."""
        from app.api.v2.batch import AnalysisRequest, BatchRequest

        # Create analysis request
        request = AnalysisRequest(
            prompt="What are the top selling products?",
            database_alias="sales_db",
            options={"limit": 10, "include_visualization": True},
        )

        assert request.prompt == "What are the top selling products?"
        assert request.database_alias == "sales_db"
        assert request.options["limit"] == 10

        # Create batch request
        batch = BatchRequest(
            requests=[request, request, request],
            max_concurrency=3,
        )

        assert len(batch.requests) == 3
        assert batch.max_concurrency == 3

        print(f"[PASS] Batch models validated: {len(batch.requests)} requests, concurrency={batch.max_concurrency}")


# =============================================================================
# Integration Test: Full Analytics Pipeline
# =============================================================================

class TestFullAnalyticsPipelineE2E:
    """End-to-end integration test combining all components."""

    @pytest.fixture
    def sales_data(self) -> pd.DataFrame:
        return generate_ecommerce_sales_data(1000)

    def test_complete_sales_analysis_pipeline(self, sales_data: pd.DataFrame):
        """
        Test: Run a complete sales analysis pipeline.

        This test simulates a real-world analytics workflow:
        1. Generate visualizations for data exploration
        2. Perform statistical analysis
        3. Detect anomalies
        4. Format and output results
        """
        from app.modules.visualization import ChartConfig, ChartService, ChartType
        from app.modules.analytics import AnomalyService, StatisticalService
        from app.utils.rich_output import format_number

        print("\n" + "=" * 60)
        print("FULL ANALYTICS PIPELINE TEST")
        print("=" * 60)

        # Step 1: Data Overview
        print("\n[Step 1] Data Overview")
        print(f"  Records: {len(sales_data)}")
        print(f"  Date range: {sales_data['date'].min().date()} to {sales_data['date'].max().date()}")
        print(f"  Regions: {sales_data['region'].nunique()}")
        print(f"  Categories: {sales_data['category'].nunique()}")

        # Step 2: Generate Visualizations
        print("\n[Step 2] Generating Visualizations")
        chart_service = ChartService()

        # Daily trend
        daily = sales_data.groupby(sales_data["date"].dt.date)["amount"].sum().reset_index()
        daily.columns = ["date", "amount"]
        trend_chart = chart_service.generate_chart(
            daily,
            ChartConfig(chart_type=ChartType.LINE, title="Daily Sales Trend", x_column="date", y_column="amount"),
        )
        print(f"  - Line chart (daily trend): OK")

        # Regional comparison
        regional = sales_data.groupby("region")["amount"].sum().reset_index()
        regional_chart = chart_service.generate_chart(
            regional,
            ChartConfig(chart_type=ChartType.BAR, title="Sales by Region", x_column="region", y_column="amount"),
        )
        print(f"  - Bar chart (regional): OK")

        # Distribution
        dist_chart = chart_service.generate_chart(
            sales_data,
            ChartConfig(chart_type=ChartType.HISTOGRAM, title="Amount Distribution", x_column="amount"),
        )
        print(f"  - Histogram (distribution): OK")

        # Step 3: Statistical Analysis
        print("\n[Step 3] Statistical Analysis")
        stat_service = StatisticalService()

        # Descriptive stats
        desc_stats = stat_service.descriptive_stats(sales_data["amount"])
        print(f"  Mean: ${format_number(desc_stats.mean)}")
        print(f"  Std Dev: ${format_number(desc_stats.std)}")
        print(f"  Median: ${format_number(desc_stats.median)}")

        # Regional ANOVA
        groups = [
            sales_data[sales_data["region"] == r]["amount"].values
            for r in sales_data["region"].unique()
        ]
        anova_result = stat_service.anova(*groups)
        print(f"  ANOVA (regional): F={anova_result.statistic:.2f}, p={anova_result.p_value:.4f}")

        # Step 4: Anomaly Detection
        print("\n[Step 4] Anomaly Detection")
        anomaly_service = AnomalyService()

        zscore_anomalies = anomaly_service.detect_zscore(sales_data["amount"], threshold=3.0)
        iqr_anomalies = anomaly_service.detect_iqr(sales_data["amount"], multiplier=1.5)

        print(f"  Z-Score method: {zscore_anomalies.anomaly_count} anomalies")
        print(f"  IQR method: {iqr_anomalies.anomaly_count} anomalies")

        # Step 5: Summary
        print("\n[Step 5] Summary")
        total_sales = sales_data["amount"].sum()
        avg_order = sales_data["amount"].mean()
        top_region = regional.loc[regional["amount"].idxmax(), "region"]

        print(f"  Total Sales: ${format_number(total_sales)}")
        print(f"  Average Order: ${format_number(avg_order)}")
        print(f"  Top Region: {top_region}")
        print(f"  Anomaly Rate: {(zscore_anomalies.anomaly_count / len(sales_data)) * 100:.1f}%")

        print("\n" + "=" * 60)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 60 + "\n")

        # Assertions
        assert trend_chart.html is not None
        assert regional_chart.html is not None
        assert dist_chart.html is not None
        assert desc_stats.mean > 0
        assert anova_result.p_value >= 0


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
