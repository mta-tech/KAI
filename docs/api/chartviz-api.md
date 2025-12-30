# Chart Visualization API Documentation

API for generating JavaScript-compatible chart configurations using AI-powered analysis.

**Base URL:** `/api/v2/chartviz`

**Compatible JS Libraries:** Chart.js, Apache ECharts, Recharts, D3.js, Plotly.js

---

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/generate` | Generate chart with specific type |
| POST | `/recommend` | AI recommends best chart type |
| POST | `/auto` | Recommend + generate in one call |
| GET | `/types` | List available chart types |
| POST | `/from-analysis` | Generate from analysis result |

---

## Data Types

### ChartType (Enum)

```typescript
type ChartType = "line" | "bar" | "pie" | "scatter" | "area" | "kpi" | "table";
```

| Value | Use Case |
|-------|----------|
| `line` | Time series, sequential trends |
| `bar` | Category comparisons |
| `pie` | Proportions, percentages |
| `scatter` | Correlation between variables |
| `area` | Cumulative trends, stacked data |
| `kpi` | Single metric with change delta |
| `table` | Detailed row-by-row data |

### ChartWidget (Response)

```typescript
interface ChartWidget {
  widget_id: string;           // UUID
  widget_title: string;        // Human-readable title
  widget_type: ChartType;      // Chart type
  widget_data: Record<string, any>[]; // Data array
  widget_delta_percentages?: number;  // % change (for KPI/trends)
  x_axis_label?: string;       // X axis label
  y_axis_label?: string;       // Y axis label
  x_axis_key?: string;         // Key in data for X axis
  y_axis_key?: string;         // Key in data for Y axis
  category_key?: string;       // Key for categorical grouping
  value_key?: string;          // Key for numeric values
}
```

### ChartRecommendation (Response)

```typescript
interface ChartRecommendation {
  chart_type: ChartType;    // Recommended type
  confidence: number;       // 0.0 - 1.0
  rationale: string;        // Explanation
}
```

---

## POST /generate

Generate chart configuration for a specific chart type.

### Request

```typescript
interface GenerateChartRequest {
  chart_type: ChartType;              // Required
  data: Record<string, any>[];        // Required - SQL result data
  user_prompt?: string;               // Optional - Original question
  language?: "id" | "en";             // Default: "id"
}
```

### Response

```typescript
ChartWidget
```

### Example

**Request:**
```json
{
  "chart_type": "line",
  "data": [
    {"bulan": "Januari 2024", "pendapatan": 52000000},
    {"bulan": "Februari 2024", "pendapatan": 58000000},
    {"bulan": "Maret 2024", "pendapatan": 61000000}
  ],
  "user_prompt": "Tampilkan tren pendapatan bulanan",
  "language": "id"
}
```

**Response:**
```json
{
  "widget_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "widget_title": "Tren Pendapatan Bulanan",
  "widget_type": "line",
  "widget_data": [
    {"bulan": "Januari 2024", "pendapatan": 52000000},
    {"bulan": "Februari 2024", "pendapatan": 58000000},
    {"bulan": "Maret 2024", "pendapatan": 61000000}
  ],
  "widget_delta_percentages": 17.31,
  "x_axis_label": "Bulan",
  "y_axis_label": "Pendapatan (Rp)",
  "x_axis_key": "bulan",
  "y_axis_key": "pendapatan"
}
```

### cURL

```bash
curl -X POST "http://localhost:8015/api/v2/chartviz/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "chart_type": "line",
    "data": [
      {"bulan": "Januari 2024", "pendapatan": 52000000},
      {"bulan": "Februari 2024", "pendapatan": 58000000}
    ],
    "language": "id"
  }'
```

---

## POST /recommend

AI recommends the best chart type for the provided data.

### Request

```typescript
interface RecommendChartRequest {
  data: Record<string, any>[];        // Required - SQL result data
  user_prompt?: string;               // Optional - Original question
  language?: "id" | "en";             // Default: "id"
}
```

### Response

```typescript
ChartRecommendation
```

### Example

**Request:**
```json
{
  "data": [
    {"kategori": "Elektronik", "total": 150000000},
    {"kategori": "Fashion", "total": 120000000},
    {"kategori": "Makanan", "total": 80000000}
  ],
  "user_prompt": "Bandingkan penjualan per kategori",
  "language": "id"
}
```

**Response:**
```json
{
  "chart_type": "bar",
  "confidence": 0.92,
  "rationale": "Data menunjukkan perbandingan antar kategori yang cocok untuk bar chart"
}
```

### cURL

```bash
curl -X POST "http://localhost:8015/api/v2/chartviz/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"kategori": "Elektronik", "total": 150000000},
      {"kategori": "Fashion", "total": 120000000}
    ],
    "language": "id"
  }'
```

---

## POST /auto

Automatically recommend and generate chart in one call.

### Request

```typescript
interface AutoChartRequest {
  data: Record<string, any>[];        // Required - SQL result data
  user_prompt?: string;               // Optional - Original question
  language?: "id" | "en";             // Default: "id"
}
```

### Response

```typescript
ChartWidget  // With AI-selected chart_type
```

### Example

**Request:**
```json
{
  "data": [
    {"produk": "Laptop", "penjualan": 45},
    {"produk": "Smartphone", "penjualan": 78},
    {"produk": "Tablet", "penjualan": 32}
  ],
  "user_prompt": "Visualisasikan penjualan produk",
  "language": "id"
}
```

**Response:**
```json
{
  "widget_id": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
  "widget_title": "Distribusi Penjualan per Produk",
  "widget_type": "bar",
  "widget_data": [
    {"produk": "Laptop", "penjualan": 45},
    {"produk": "Smartphone", "penjualan": 78},
    {"produk": "Tablet", "penjualan": 32}
  ],
  "x_axis_label": "Produk",
  "y_axis_label": "Penjualan",
  "x_axis_key": "produk",
  "y_axis_key": "penjualan"
}
```

### cURL

```bash
curl -X POST "http://localhost:8015/api/v2/chartviz/auto" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"produk": "Laptop", "penjualan": 45},
      {"produk": "Smartphone", "penjualan": 78}
    ],
    "language": "id"
  }'
```

---

## GET /types

List all available chart types with descriptions.

### Response

```typescript
interface ChartTypesResponse {
  chart_types: {
    type: string;
    description: string;
  }[];
}
```

### Example

**Response:**
```json
{
  "chart_types": [
    {"type": "line", "description": "Line chart - for time series or sequential trend data"},
    {"type": "bar", "description": "Bar chart - for comparing across categories"},
    {"type": "pie", "description": "Pie chart - for proportions/percentages of a whole"},
    {"type": "scatter", "description": "Scatter plot - for correlation between two numeric variables"},
    {"type": "area", "description": "Area chart - for cumulative trends or stacked data"},
    {"type": "kpi", "description": "KPI/Big Number - for single metric with change delta"},
    {"type": "table", "description": "Table - for detailed data that needs row-by-row reading"}
  ]
}
```

### cURL

```bash
curl -X GET "http://localhost:8015/api/v2/chartviz/types"
```

---

## POST /from-analysis

Generate chart from an analysis service result object.

### Request

```typescript
// Query parameters
chart_type?: ChartType;    // Optional - specific type (auto if not provided)
language?: "id" | "en";    // Default: "id"

// Body - Analysis result object
interface AnalysisResult {
  data?: Record<string, any>[];      // Data array
  results?: Record<string, any>[];   // Alternative key for data
  rows?: Record<string, any>[];      // Alternative key for data
  prompt?: string;                   // Original user question
  query?: string;                    // Alternative key for prompt
  // ... other analysis fields
}
```

### Response

```typescript
ChartWidget
```

### Example

**Request:**
```json
{
  "data": [
    {"region": "Jakarta", "revenue": 500000000},
    {"region": "Surabaya", "revenue": 350000000},
    {"region": "Bandung", "revenue": 280000000}
  ],
  "prompt": "Bandingkan pendapatan per region",
  "sql": "SELECT region, SUM(amount) as revenue FROM sales GROUP BY region"
}
```

**Query:** `?chart_type=bar&language=id`

**Response:**
```json
{
  "widget_id": "c3d4e5f6-a7b8-9012-cdef-345678901234",
  "widget_title": "Perbandingan Pendapatan per Region",
  "widget_type": "bar",
  "widget_data": [
    {"region": "Jakarta", "revenue": 500000000},
    {"region": "Surabaya", "revenue": 350000000},
    {"region": "Bandung", "revenue": 280000000}
  ],
  "x_axis_label": "Region",
  "y_axis_label": "Pendapatan (Rp)",
  "x_axis_key": "region",
  "y_axis_key": "revenue"
}
```

### cURL

```bash
curl -X POST "http://localhost:8015/api/v2/chartviz/from-analysis?chart_type=bar&language=id" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"region": "Jakarta", "revenue": 500000000},
      {"region": "Surabaya", "revenue": 350000000}
    ],
    "prompt": "Bandingkan pendapatan per region"
  }'
```

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Data cannot be empty"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Chart generation failed: <error message>"
}
```

---

## Temporal Workflow Integration

### Activity Definition

```python
from temporalio import activity
from dataclasses import dataclass
from typing import Any
import httpx

@dataclass
class ChartGenerationInput:
    chart_type: str
    data: list[dict[str, Any]]
    user_prompt: str | None = None
    language: str = "id"

@dataclass
class ChartRecommendationInput:
    data: list[dict[str, Any]]
    user_prompt: str | None = None
    language: str = "id"

@dataclass
class AutoChartInput:
    data: list[dict[str, Any]]
    user_prompt: str | None = None
    language: str = "id"


@activity.defn
async def generate_chart_activity(input: ChartGenerationInput) -> dict:
    """Generate chart with specific type."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://kai-service:8015/api/v2/chartviz/generate",
            json={
                "chart_type": input.chart_type,
                "data": input.data,
                "user_prompt": input.user_prompt,
                "language": input.language,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@activity.defn
async def recommend_chart_activity(input: ChartRecommendationInput) -> dict:
    """Get AI chart recommendation."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://kai-service:8015/api/v2/chartviz/recommend",
            json={
                "data": input.data,
                "user_prompt": input.user_prompt,
                "language": input.language,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@activity.defn
async def auto_generate_chart_activity(input: AutoChartInput) -> dict:
    """Auto recommend and generate chart."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://kai-service:8015/api/v2/chartviz/auto",
            json={
                "data": input.data,
                "user_prompt": input.user_prompt,
                "language": input.language,
            },
            timeout=60.0,  # Longer timeout for recommendation + generation
        )
        response.raise_for_status()
        return response.json()
```

### Workflow Example

```python
from temporalio import workflow
from datetime import timedelta

@workflow.defn
class AnalysisWithVisualizationWorkflow:
    @workflow.run
    async def run(self, analysis_input: AnalysisInput) -> dict:
        # Step 1: Execute SQL and get analysis
        analysis_result = await workflow.execute_activity(
            run_analysis_activity,
            analysis_input,
            start_to_close_timeout=timedelta(seconds=120),
        )

        # Step 2: Generate visualization
        if analysis_result.get("data"):
            chart_input = AutoChartInput(
                data=analysis_result["data"],
                user_prompt=analysis_input.query,
                language=analysis_input.language,
            )

            chart_widget = await workflow.execute_activity(
                auto_generate_chart_activity,
                chart_input,
                start_to_close_timeout=timedelta(seconds=60),
            )

            analysis_result["visualization"] = chart_widget

        return analysis_result
```

### Workflow with Specific Chart Type

```python
@workflow.defn
class DashboardGenerationWorkflow:
    @workflow.run
    async def run(self, dashboard_config: DashboardConfig) -> list[dict]:
        widgets = []

        for panel in dashboard_config.panels:
            # Execute SQL query
            sql_result = await workflow.execute_activity(
                execute_sql_activity,
                panel.sql_query,
                start_to_close_timeout=timedelta(seconds=30),
            )

            # Generate chart with specified type
            chart_input = ChartGenerationInput(
                chart_type=panel.chart_type,
                data=sql_result["rows"],
                user_prompt=panel.title,
                language=dashboard_config.language,
            )

            widget = await workflow.execute_activity(
                generate_chart_activity,
                chart_input,
                start_to_close_timeout=timedelta(seconds=30),
            )

            widgets.append(widget)

        return widgets
```

### Retry Policy Recommendation

```python
from temporalio.common import RetryPolicy

chart_retry_policy = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    maximum_interval=timedelta(seconds=10),
    maximum_attempts=3,
    non_retryable_error_types=["ValueError"],  # Don't retry validation errors
)

# Usage
chart_widget = await workflow.execute_activity(
    generate_chart_activity,
    chart_input,
    start_to_close_timeout=timedelta(seconds=60),
    retry_policy=chart_retry_policy,
)
```

---

## OpenAPI Schema

The full OpenAPI schema is available at:
- **Swagger UI:** `http://localhost:8015/docs`
- **ReDoc:** `http://localhost:8015/redoc`
- **OpenAPI JSON:** `http://localhost:8015/openapi.json`

---

## Rate Limits & Performance

| Metric | Value |
|--------|-------|
| Avg Response Time | 2-5 seconds |
| Max Data Rows | 10,000 recommended |
| Max Concurrent | Limited by LLM provider |
| Timeout | 30 seconds default |

### Performance Tips

1. **Limit data size:** Pre-aggregate data before sending
2. **Use specific chart type:** `/generate` is faster than `/auto`
3. **Cache results:** Widget IDs are stable for same input
4. **Batch requests:** Use parallel activities for multiple charts
