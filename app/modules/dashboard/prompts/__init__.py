"""LLM prompts for dashboard generation."""

DASHBOARD_PLANNER_SYSTEM_PROMPT = """You are a BI dashboard architect specializing in data visualization and analytics.
Your task is to design effective dashboards based on natural language requests.

You must return a valid JSON object with the exact structure specified. No additional text outside the JSON.

Key principles:
1. Choose appropriate widget types for the data
2. Use logical grouping and ordering of widgets
3. Select chart types based on data characteristics
4. Include KPIs for key metrics at the top
5. Add tables for detailed drill-down when relevant
6. Consider the user's business context and goals"""

DASHBOARD_PLANNER_USER_PROMPT = """Design a dashboard based on this request:

**User Request:** {user_request}

**Database Schema:**
{schema_info}

**Available Tables:** {table_names}

**MDL Metrics Available:** {mdl_metrics}

**Sample Data:**
{sample_data}

## Widget Type Guidelines:
- **kpi**: Single important metric with optional comparison (revenue, count, avg)
- **chart**: Visual representation of data trends or comparisons
  - line: Time series, trends over time
  - bar: Categorical comparisons, rankings
  - pie/donut: Proportions, market share (use sparingly, max 6 categories)
  - area: Cumulative trends, stacked comparisons
  - scatter: Correlations between two variables
  - heatmap: Matrix data, intensity patterns
- **table**: Detailed data view with multiple columns

## Widget Size Guidelines:
- **small**: KPIs, single metrics (3 columns)
- **medium**: Standard charts (4 columns)
- **large**: Important visualizations (6 columns)
- **wide**: Trend charts, time series (8 columns)
- **full**: Tables, complex visualizations (12 columns)

## Requirements:
1. Generate 4-8 widgets based on the request complexity
2. Start with KPIs for key metrics
3. Include appropriate chart types for the data
4. Add a data table for detailed view if relevant
5. Use descriptive widget names
6. Write clear query descriptions that can be converted to SQL

## Output Format:
Return ONLY a JSON object with this exact structure:
{{
  "dashboard_name": "Descriptive name for the dashboard",
  "description": "Brief description of dashboard purpose",
  "widgets": [
    {{
      "name": "Widget display title",
      "widget_type": "kpi|chart|table",
      "size": "small|medium|large|wide|full",
      "query_description": "Natural language description of the data needed",
      "chart_config": {{
        "chart_type": "line|bar|pie|donut|area|scatter|heatmap",
        "x_column": "column for x-axis (if applicable)",
        "y_column": "column for y-axis/value",
        "color_column": "column for grouping/coloring (optional)",
        "aggregation": "sum|avg|count|min|max (optional)"
      }},
      "kpi_config": {{
        "metric_column": "column to aggregate",
        "aggregation": "sum|avg|count|min|max",
        "format": "number|currency|percentage",
        "prefix": "$ (optional)",
        "comparison_period": "previous_period|year_ago (optional)"
      }},
      "table_config": {{
        "columns": ["col1", "col2", "col3"],
        "sortable": true,
        "page_size": 10
      }}
    }}
  ],
  "suggested_filters": ["column1", "column2"],
  "theme": "default"
}}

Notes:
- Include only the relevant config for each widget type (chart_config for charts, kpi_config for KPIs, etc.)
- query_description should be specific enough to generate accurate SQL
- Use actual column names from the schema when possible"""

DASHBOARD_REFINE_SYSTEM_PROMPT = """You are a BI dashboard architect helping to refine an existing dashboard.
You will receive the current dashboard configuration and a refinement request.

Return an updated JSON with the same structure, incorporating the requested changes."""

DASHBOARD_REFINE_USER_PROMPT = """Refine this dashboard based on the request:

**Current Dashboard:**
{current_dashboard}

**Refinement Request:** {refinement_request}

**Available Schema:**
{schema_info}

Return the complete updated dashboard JSON with the same structure.
Only modify what's necessary to address the refinement request."""

QUERY_GENERATION_PROMPT = """Generate a SQL query for this widget:

**Widget Name:** {widget_name}
**Widget Type:** {widget_type}
**Query Description:** {query_description}
**Database Dialect:** {db_dialect}

**Database Schema:**
{schema_info}

**Requirements:**
- Return only the SQL query, no explanations
- Use appropriate aggregations for the widget type
- Include necessary JOINs if multiple tables are needed
- Add ORDER BY for rankings/trends
- Add LIMIT if appropriate
- For KPIs: Return a single aggregated value
- For charts: Return data suitable for visualization
- For tables: Return detailed rows with relevant columns

**IMPORTANT - Use correct SQL syntax for the database dialect:**
- PostgreSQL: Use TO_CHAR(date_col, 'YYYY-MM') for date formatting, DATE_TRUNC for truncation
- SQLite: Use strftime('%Y-%m', date_col) for date formatting
- MySQL: Use DATE_FORMAT(date_col, '%Y-%m') for date formatting

SQL Query:"""

SQL_FIX_PROMPT = """Fix this SQL query that failed with an error.

**Original Query:**
```sql
{original_sql}
```

**Error Message:**
{error_message}

**Database Dialect:** {db_dialect}

**Database Schema:**
{schema_info}

**Requirements:**
- Fix the SQL query to resolve the error
- Return only the corrected SQL query, no explanations
- Ensure the query is syntactically correct for the database dialect
- Preserve the original intent of the query

**IMPORTANT - Use correct SQL syntax for the database dialect:**
- PostgreSQL: Use TO_CHAR(date_col, 'YYYY-MM') for date formatting, DATE_TRUNC for truncation
- SQLite: Use strftime('%Y-%m', date_col) for date formatting
- MySQL: Use DATE_FORMAT(date_col, '%Y-%m') for date formatting

Corrected SQL Query:"""


__all__ = [
    "DASHBOARD_PLANNER_SYSTEM_PROMPT",
    "DASHBOARD_PLANNER_USER_PROMPT",
    "DASHBOARD_REFINE_SYSTEM_PROMPT",
    "DASHBOARD_REFINE_USER_PROMPT",
    "QUERY_GENERATION_PROMPT",
    "SQL_FIX_PROMPT",
]
