# Autonomous Deep Agent Implementation Plan

## Overview

Implement a fully autonomous AI agent in KAI using the official **LangChain DeepAgents** framework that can:
1. Multi-step reasoning and planning (via built-in `write_todos`)
2. Execute SQL queries and analyze results
3. Run Python scripts for data analysis (via `execute` tool with sandbox)
4. Operate via CLI command interface

## DeepAgents Framework Reference

**Source**: https://github.com/langchain-ai/deepagents

### Built-in Tools (Automatically Available)
| Tool | Purpose |
|------|---------|
| `write_todos` / `read_todos` | Task planning and progress tracking |
| `ls` | List directory contents |
| `read_file` | Read file with pagination |
| `write_file` | Create/overwrite files |
| `edit_file` | Exact string replacements |
| `glob` | Find files matching patterns |
| `grep` | Search text within files |
| `execute` | Run shell commands (requires SandboxBackendProtocol) |
| `task` | Delegate to sub-agents |

### Built-in Middleware (Auto-applied)
1. **TodoListMiddleware** - Task planning
2. **FilesystemMiddleware** - File I/O, auto-saves results >20K tokens
3. **SubAgentMiddleware** - Isolated task delegation
4. **SummarizationMiddleware** - Compresses at 170K tokens
5. **AnthropicPromptCachingMiddleware** - Cost optimization
6. **HumanInTheLoopMiddleware** - Approval checkpoints

### Backend Options
- `StateBackend` (default) - Ephemeral in-memory
- `FilesystemBackend` - Real disk operations
- `StoreBackend` - Persistent LangGraph Store
- `CompositeBackend` - Route paths to different backends

### Existing KAI Architecture
- `app/agents/deep_agent_factory.py` - Factory for SQL-focused deep agents
- `app/utils/deep_agent/` - Custom tools, prompts, subagents
- Already has `deepagents>=0.2.8` dependency
- SQL tools: `sql_db_query`, `table_schema`, `tables_with_scores`, etc.

---

## Implementation Plan

### Phase 1: Core Autonomous Agent Module

#### 1.1 Create New Module Structure
**Location**: `app/modules/autonomous_agent/`

```
app/modules/autonomous_agent/
├── __init__.py
├── models.py               # AgentTask, AgentResult, ChartSpec, Insight
├── service.py              # AutonomousAgentService
├── tools/
│   ├── __init__.py
│   ├── sql_tools.py        # SQL query execution
│   ├── chart_tools.py      # Text-to-Chart generation
│   ├── insights_tools.py   # AI insights extraction
│   ├── analysis_tools.py   # Pandas analysis
│   └── suggestions_tools.py # Follow-up question suggestions
├── semantic/
│   ├── __init__.py
│   ├── layer.py            # Semantic layer management
│   └── models.py           # Metric, Dimension, Relationship definitions
├── subagents.py            # Specialized subagent definitions
├── prompts.py              # System prompts for autonomous mode
└── cli.py                  # CLI command implementation
```

> **Note**: We leverage deepagents' built-in tools (`write_todos`, `read_file`, `write_file`, etc.) and add KAI-specific tools for GenBI capabilities.

#### 1.2 Define Models
**File**: `app/modules/autonomous_agent/models.py`

```python
from dataclasses import dataclass, field
from typing import Literal, Any
from datetime import datetime


@dataclass
class AgentTask:
    """Task submitted to the autonomous agent."""
    id: str
    prompt: str
    db_connection_id: str
    mode: Literal["analysis", "query", "script", "full_autonomy"] = "full_autonomy"
    context: dict | None = None
    metadata: dict | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ChartSpec:
    """Specification for generated chart."""
    chart_type: Literal["line", "bar", "pie", "scatter", "area", "heatmap"]
    title: str
    x_column: str
    y_column: str | list[str]
    data: list[dict]
    color_column: str | None = None
    config: dict = field(default_factory=dict)  # Additional chart config


@dataclass
class Insight:
    """AI-generated insight from data."""
    category: Literal["trend", "anomaly", "comparison", "summary", "recommendation"]
    title: str
    description: str
    importance: Literal["high", "medium", "low"]
    supporting_data: dict | None = None


@dataclass
class SuggestedQuestion:
    """Follow-up question suggestion."""
    question: str
    category: Literal["drill_down", "compare", "trend", "filter", "aggregate"]
    rationale: str  # Why this question is relevant


@dataclass
class AgentResult:
    """Result from autonomous agent execution."""
    task_id: str
    status: Literal["completed", "failed", "partial"]
    final_answer: str
    # GenBI outputs
    charts: list[ChartSpec] = field(default_factory=list)
    insights: list[Insight] = field(default_factory=list)
    suggested_questions: list[SuggestedQuestion] = field(default_factory=list)
    # Execution details
    sql_queries: list[str] = field(default_factory=list)
    artifacts: list[dict] = field(default_factory=list)
    execution_time_ms: int = 0
    error: str | None = None
```

### Phase 2: GenBI Tools Implementation

#### 2.0 Tools Module Init
**File**: `app/modules/autonomous_agent/tools/__init__.py`

```python
"""GenBI tools for autonomous agent."""
from app.modules.autonomous_agent.tools.sql_tools import create_sql_query_tool
from app.modules.autonomous_agent.tools.chart_tools import create_chart_tool
from app.modules.autonomous_agent.tools.insights_tools import create_insights_tool
from app.modules.autonomous_agent.tools.suggestions_tools import create_suggestions_tool
from app.modules.autonomous_agent.tools.analysis_tools import (
    create_pandas_analysis_tool,
    create_python_execute_tool,
)

__all__ = [
    "create_sql_query_tool",
    "create_chart_tool",
    "create_insights_tool",
    "create_suggestions_tool",
    "create_pandas_analysis_tool",
    "create_python_execute_tool",
]
```

#### 2.1 SQL Tools
**File**: `app/modules/autonomous_agent/tools/sql_tools.py`

```python
"""SQL query execution tools."""
import json
from app.utils.sql_database.sql_database import SQLDatabase


def create_sql_query_tool(database: SQLDatabase, max_rows: int = 1000):
    """Create SQL query execution tool."""

    def sql_query(query: str) -> str:
        """Execute a read-only SQL query and return results.

        Args:
            query: SQL SELECT query to execute

        Returns:
            JSON string with query results and metadata
        """
        try:
            result = database.run_sql(query, max_rows)
            rows = result[1].get("result", []) if isinstance(result, tuple) else []
            return json.dumps({
                "success": True,
                "row_count": len(rows),
                "columns": list(rows[0].keys()) if rows else [],
                "data": rows[:100],
                "truncated": len(rows) > 100,
            })
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return sql_query
```

#### 2.2 Text-to-Chart Tools (GenBI Feature #1)
**File**: `app/modules/autonomous_agent/tools/chart_tools.py`

```python
"""Text-to-Chart generation tools."""
import json
import base64
from io import BytesIO
from typing import Literal

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend


def create_chart_tool(output_dir: str = "./agent_results"):
    """Create chart generation tool."""

    def generate_chart(
        data_json: str,
        chart_type: Literal["line", "bar", "pie", "scatter", "area", "heatmap"],
        x_column: str,
        y_column: str,
        title: str = "Chart",
        color_column: str | None = None,
        save_path: str | None = None,
    ) -> str:
        """Generate a chart from data.

        Args:
            data_json: JSON string of data (list of dicts)
            chart_type: Type of chart (line, bar, pie, scatter, area, heatmap)
            x_column: Column name for x-axis
            y_column: Column name for y-axis (or values for pie)
            title: Chart title
            color_column: Optional column for color grouping
            save_path: Optional path to save chart image

        Returns:
            JSON with chart info and base64 image data
        """
        try:
            data = json.loads(data_json)
            df = pd.DataFrame(data)

            fig, ax = plt.subplots(figsize=(10, 6))

            if chart_type == "line":
                if color_column and color_column in df.columns:
                    for name, group in df.groupby(color_column):
                        ax.plot(group[x_column], group[y_column], label=name, marker='o')
                    ax.legend()
                else:
                    ax.plot(df[x_column], df[y_column], marker='o')

            elif chart_type == "bar":
                if color_column and color_column in df.columns:
                    pivot = df.pivot_table(index=x_column, columns=color_column, values=y_column)
                    pivot.plot(kind='bar', ax=ax)
                else:
                    ax.bar(df[x_column], df[y_column])

            elif chart_type == "pie":
                ax.pie(df[y_column], labels=df[x_column], autopct='%1.1f%%')

            elif chart_type == "scatter":
                ax.scatter(df[x_column], df[y_column])

            elif chart_type == "area":
                ax.fill_between(df[x_column], df[y_column], alpha=0.5)
                ax.plot(df[x_column], df[y_column])

            elif chart_type == "heatmap":
                pivot = df.pivot_table(index=x_column, columns=color_column or y_column, values=y_column)
                im = ax.imshow(pivot.values, aspect='auto')
                plt.colorbar(im, ax=ax)

            ax.set_title(title)
            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            # Save to file or return base64
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                plt.close()
                return json.dumps({
                    "success": True,
                    "chart_type": chart_type,
                    "saved_to": save_path,
                })
            else:
                # Return base64 encoded image
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                buf.seek(0)
                img_base64 = base64.b64encode(buf.read()).decode('utf-8')
                plt.close()
                return json.dumps({
                    "success": True,
                    "chart_type": chart_type,
                    "image_base64": img_base64[:100] + "...",  # Truncated for context
                    "full_image_available": True,
                })

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return generate_chart
```

#### 2.3 AI Insights Tools (GenBI Feature #2)
**File**: `app/modules/autonomous_agent/tools/insights_tools.py`

```python
"""AI-powered insights extraction tools."""
import json
import pandas as pd
from typing import Literal


def create_insights_tool():
    """Create automated insights extraction tool."""

    def extract_insights(
        data_json: str,
        context: str = "",
    ) -> str:
        """Extract key insights from data automatically.

        Args:
            data_json: JSON string of data (list of dicts)
            context: Optional context about what the data represents

        Returns:
            JSON with extracted insights
        """
        try:
            data = json.loads(data_json)
            df = pd.DataFrame(data)
            insights = []

            # 1. Summary statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                stats = df[col].describe()
                insights.append({
                    "category": "summary",
                    "title": f"{col} Overview",
                    "description": f"Range: {stats['min']:.2f} to {stats['max']:.2f}, "
                                   f"Average: {stats['mean']:.2f}, Median: {stats['50%']:.2f}",
                    "importance": "medium",
                    "supporting_data": {"column": col, "stats": stats.to_dict()}
                })

            # 2. Trend detection (if data has time-like column)
            if len(df) > 2 and len(numeric_cols) > 0:
                for col in numeric_cols[:3]:  # Check first 3 numeric columns
                    values = df[col].dropna().values
                    if len(values) > 2:
                        # Simple trend: compare first third vs last third
                        first_third = values[:len(values)//3].mean()
                        last_third = values[-len(values)//3:].mean()
                        change_pct = ((last_third - first_third) / first_third * 100) if first_third != 0 else 0

                        if abs(change_pct) > 10:
                            trend = "increasing" if change_pct > 0 else "decreasing"
                            insights.append({
                                "category": "trend",
                                "title": f"{col} is {trend}",
                                "description": f"{col} shows a {abs(change_pct):.1f}% {trend} trend",
                                "importance": "high" if abs(change_pct) > 25 else "medium",
                                "supporting_data": {"change_percent": change_pct}
                            })

            # 3. Anomaly detection (values outside 2 std devs)
            for col in numeric_cols[:3]:
                mean = df[col].mean()
                std = df[col].std()
                if std > 0:
                    outliers = df[(df[col] < mean - 2*std) | (df[col] > mean + 2*std)]
                    if len(outliers) > 0 and len(outliers) < len(df) * 0.1:
                        insights.append({
                            "category": "anomaly",
                            "title": f"Outliers detected in {col}",
                            "description": f"Found {len(outliers)} unusual values in {col}",
                            "importance": "high",
                            "supporting_data": {"outlier_count": len(outliers)}
                        })

            # 4. Top/Bottom performers (for categorical + numeric)
            cat_cols = df.select_dtypes(include=['object']).columns
            if len(cat_cols) > 0 and len(numeric_cols) > 0:
                cat_col = cat_cols[0]
                num_col = numeric_cols[0]
                top = df.nlargest(3, num_col)[[cat_col, num_col]]
                insights.append({
                    "category": "comparison",
                    "title": f"Top performers by {num_col}",
                    "description": f"Highest {num_col}: " + ", ".join(
                        f"{row[cat_col]} ({row[num_col]:.2f})" for _, row in top.iterrows()
                    ),
                    "importance": "medium",
                    "supporting_data": {"top_3": top.to_dict('records')}
                })

            return json.dumps({
                "success": True,
                "insight_count": len(insights),
                "insights": insights
            })

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return extract_insights
```

#### 2.4 Follow-up Suggestions Tools (GenBI Features #4 & #5)
**File**: `app/modules/autonomous_agent/tools/suggestions_tools.py`

```python
"""Follow-up question and exploration suggestion tools."""
import json
import pandas as pd


def create_suggestions_tool():
    """Create follow-up question suggestion tool."""

    def suggest_questions(
        data_json: str,
        original_question: str,
        columns_used: list[str] | None = None,
    ) -> str:
        """Suggest follow-up questions based on data and context.

        Args:
            data_json: JSON string of current data results
            original_question: The question that produced this data
            columns_used: Columns involved in the analysis

        Returns:
            JSON with suggested follow-up questions
        """
        try:
            data = json.loads(data_json)
            df = pd.DataFrame(data)
            suggestions = []

            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            cat_cols = df.select_dtypes(include=['object']).columns.tolist()
            all_cols = numeric_cols + cat_cols

            # 1. Drill-down suggestions
            for col in cat_cols[:2]:
                unique_values = df[col].nunique()
                if unique_values > 1 and unique_values < 20:
                    top_value = df[col].value_counts().index[0]
                    suggestions.append({
                        "question": f"Show me details for {col} = '{top_value}'",
                        "category": "drill_down",
                        "rationale": f"Drill into the most common {col} value"
                    })

            # 2. Comparison suggestions
            if len(cat_cols) >= 2:
                suggestions.append({
                    "question": f"Compare {numeric_cols[0] if numeric_cols else 'values'} across different {cat_cols[0]}",
                    "category": "compare",
                    "rationale": "Compare performance across categories"
                })

            # 3. Trend suggestions
            if len(numeric_cols) > 0:
                suggestions.append({
                    "question": f"Show me the trend of {numeric_cols[0]} over time",
                    "category": "trend",
                    "rationale": "Understand how values change over time"
                })

            # 4. Filter suggestions
            if len(numeric_cols) > 0:
                col = numeric_cols[0]
                median = df[col].median()
                suggestions.append({
                    "question": f"Show only records where {col} is above {median:.2f}",
                    "category": "filter",
                    "rationale": "Focus on above-average performers"
                })

            # 5. Aggregation suggestions
            if len(cat_cols) > 0 and len(numeric_cols) > 0:
                suggestions.append({
                    "question": f"What is the total and average {numeric_cols[0]} by {cat_cols[0]}?",
                    "category": "aggregate",
                    "rationale": "Summarize metrics by category"
                })

            # 6. Context-aware suggestions based on original question
            if "top" in original_question.lower() or "best" in original_question.lower():
                suggestions.append({
                    "question": "Now show me the bottom performers",
                    "category": "compare",
                    "rationale": "Compare with worst performers"
                })

            if "total" in original_question.lower() or "sum" in original_question.lower():
                suggestions.append({
                    "question": "Break this down by month",
                    "category": "drill_down",
                    "rationale": "See temporal distribution"
                })

            return json.dumps({
                "success": True,
                "suggestion_count": len(suggestions),
                "suggestions": suggestions[:5]  # Return top 5
            })

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return suggest_questions
```

#### 2.5 Analysis Tools
**File**: `app/modules/autonomous_agent/tools/analysis_tools.py`

```python
"""Pandas data analysis tools."""
import json
import pandas as pd


def create_pandas_analysis_tool():
    """Create pandas data analysis tool."""

    def analyze_data(
        data_json: str,
        analysis_type: str = "summary",
    ) -> str:
        """Analyze data using pandas.

        Args:
            data_json: JSON string of data (list of dicts)
            analysis_type: One of "summary", "correlation", "describe", "value_counts", "groupby"

        Returns:
            Analysis results as string
        """
        try:
            data = json.loads(data_json)
            df = pd.DataFrame(data)

            if analysis_type == "summary":
                return df.describe(include='all').to_string()
            elif analysis_type == "correlation":
                numeric_df = df.select_dtypes(include=['number'])
                if len(numeric_df.columns) < 2:
                    return "Need at least 2 numeric columns for correlation"
                return numeric_df.corr().to_string()
            elif analysis_type == "describe":
                return df.describe().to_string()
            elif analysis_type == "value_counts":
                results = {}
                for col in df.select_dtypes(include=['object']).columns[:5]:
                    results[col] = df[col].value_counts().head(10).to_dict()
                return json.dumps(results, indent=2)
            else:
                return f"Unknown analysis type: {analysis_type}"
        except Exception as e:
            return f"Analysis error: {e}"

    return analyze_data


def create_python_execute_tool():
    """Create safe Python code execution tool."""
    SAFE_BUILTINS = {
        'print': print, 'len': len, 'range': range, 'sum': sum,
        'min': min, 'max': max, 'abs': abs, 'round': round,
        'sorted': sorted, 'list': list, 'dict': dict, 'str': str,
        'int': int, 'float': float, 'bool': bool, 'enumerate': enumerate,
        'zip': zip, 'map': map, 'filter': filter,
    }

    def python_execute(code: str) -> str:
        """Execute Python code in a restricted environment."""
        import io, contextlib, json, math, statistics, datetime, collections

        restricted_globals = {
            '__builtins__': SAFE_BUILTINS,
            'json': json, 'math': math, 'statistics': statistics,
            'datetime': datetime, 'collections': collections,
        }

        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                exec(code, restricted_globals)
            return output.getvalue() or "Code executed successfully (no output)"
        except Exception as e:
            return f"Execution error: {e}"

    return python_execute
```

#### 2.6 Semantic Layer (GenBI Feature #3)
**File**: `app/modules/autonomous_agent/semantic/models.py`

```python
"""Semantic layer models for business-friendly data representation."""
from dataclasses import dataclass, field
from typing import Literal, Any


@dataclass
class Dimension:
    """A categorical attribute for grouping and filtering."""
    name: str
    source_column: str
    source_table: str
    description: str
    data_type: Literal["string", "date", "datetime", "boolean"]
    display_name: str | None = None
    synonyms: list[str] = field(default_factory=list)  # Alternative names users might use


@dataclass
class Metric:
    """A quantitative measure with aggregation logic."""
    name: str
    source_column: str
    source_table: str
    description: str
    aggregation: Literal["sum", "avg", "count", "min", "max", "count_distinct"]
    display_name: str | None = None
    format: str = "{value}"  # e.g., "${value:,.2f}" for currency
    synonyms: list[str] = field(default_factory=list)


@dataclass
class Relationship:
    """Join relationship between tables."""
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relationship_type: Literal["one_to_one", "one_to_many", "many_to_one", "many_to_many"]


@dataclass
class SemanticModel:
    """Complete semantic model for a database connection."""
    id: str
    name: str
    description: str
    db_connection_id: str
    dimensions: list[Dimension] = field(default_factory=list)
    metrics: list[Metric] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
```

**File**: `app/modules/autonomous_agent/semantic/layer.py`

```python
"""Semantic layer management for business-friendly SQL generation."""
import json
from typing import Any

from app.modules.autonomous_agent.semantic.models import (
    SemanticModel,
    Dimension,
    Metric,
    Relationship,
)


class SemanticLayer:
    """Manages semantic models and translates business terms to SQL.

    The semantic layer provides:
    1. Business-friendly names for database columns
    2. Pre-defined aggregation logic for metrics
    3. Automatic joins via relationship definitions
    4. Synonym support for natural language understanding
    """

    def __init__(self, model: SemanticModel):
        self.model = model
        self._dimension_map = {d.name.lower(): d for d in model.dimensions}
        self._metric_map = {m.name.lower(): m for m in model.metrics}
        self._synonym_map = self._build_synonym_map()

    def _build_synonym_map(self) -> dict[str, str]:
        """Build mapping from synonyms to canonical names."""
        synonym_map = {}
        for dim in self.model.dimensions:
            for syn in dim.synonyms:
                synonym_map[syn.lower()] = dim.name
        for metric in self.model.metrics:
            for syn in metric.synonyms:
                synonym_map[syn.lower()] = metric.name
        return synonym_map

    def resolve_term(self, term: str) -> tuple[str, Literal["dimension", "metric"] | None]:
        """Resolve a business term to its canonical name and type."""
        term_lower = term.lower()

        # Check exact match first
        if term_lower in self._dimension_map:
            return term_lower, "dimension"
        if term_lower in self._metric_map:
            return term_lower, "metric"

        # Check synonyms
        if term_lower in self._synonym_map:
            canonical = self._synonym_map[term_lower].lower()
            if canonical in self._dimension_map:
                return canonical, "dimension"
            if canonical in self._metric_map:
                return canonical, "metric"

        return term, None

    def get_dimension(self, name: str) -> Dimension | None:
        """Get dimension by name or synonym."""
        resolved, term_type = self.resolve_term(name)
        if term_type == "dimension":
            return self._dimension_map.get(resolved)
        return None

    def get_metric(self, name: str) -> Metric | None:
        """Get metric by name or synonym."""
        resolved, term_type = self.resolve_term(name)
        if term_type == "metric":
            return self._metric_map.get(resolved)
        return None

    def build_metric_sql(self, metric: Metric) -> str:
        """Generate SQL expression for a metric."""
        col = f"{metric.source_table}.{metric.source_column}"
        agg = metric.aggregation.upper()

        if agg == "COUNT_DISTINCT":
            return f"COUNT(DISTINCT {col})"
        return f"{agg}({col})"

    def build_dimension_sql(self, dimension: Dimension) -> str:
        """Generate SQL expression for a dimension."""
        return f"{dimension.source_table}.{dimension.source_column}"

    def get_join_path(self, from_table: str, to_table: str) -> list[Relationship]:
        """Find join path between two tables using BFS."""
        if from_table == to_table:
            return []

        # Build adjacency list
        adj: dict[str, list[tuple[str, Relationship]]] = {}
        for rel in self.model.relationships:
            if rel.from_table not in adj:
                adj[rel.from_table] = []
            if rel.to_table not in adj:
                adj[rel.to_table] = []
            adj[rel.from_table].append((rel.to_table, rel))
            adj[rel.to_table].append((rel.from_table, rel))

        # BFS
        from collections import deque
        queue = deque([(from_table, [])])
        visited = {from_table}

        while queue:
            current, path = queue.popleft()
            if current == to_table:
                return path
            for neighbor, rel in adj.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [rel]))

        return []  # No path found

    def build_join_sql(self, relationships: list[Relationship]) -> str:
        """Generate JOIN clauses from relationships."""
        if not relationships:
            return ""

        joins = []
        for rel in relationships:
            join_type = "LEFT JOIN"  # Default to LEFT JOIN for flexibility
            joins.append(
                f"{join_type} {rel.to_table} ON "
                f"{rel.from_table}.{rel.from_column} = {rel.to_table}.{rel.to_column}"
            )
        return "\n".join(joins)

    def to_context_string(self) -> str:
        """Generate context string for LLM prompts."""
        lines = [f"# Semantic Model: {self.model.name}", ""]

        if self.model.dimensions:
            lines.append("## Dimensions (for grouping/filtering):")
            for dim in self.model.dimensions:
                synonyms = f" (also: {', '.join(dim.synonyms)})" if dim.synonyms else ""
                lines.append(f"- {dim.display_name or dim.name}: {dim.description}{synonyms}")
            lines.append("")

        if self.model.metrics:
            lines.append("## Metrics (for aggregation):")
            for metric in self.model.metrics:
                synonyms = f" (also: {', '.join(metric.synonyms)})" if metric.synonyms else ""
                lines.append(
                    f"- {metric.display_name or metric.name}: {metric.description} "
                    f"[{metric.aggregation}]{synonyms}"
                )
            lines.append("")

        return "\n".join(lines)


def create_semantic_tool(semantic_layer: SemanticLayer):
    """Create tool for querying semantic model."""

    def query_semantic_model(question: str) -> str:
        """Look up business terms in the semantic model.

        Args:
            question: Natural language question or business term

        Returns:
            JSON with matching dimensions, metrics, and SQL expressions
        """
        words = question.lower().split()
        results = {
            "dimensions": [],
            "metrics": [],
            "unresolved": [],
        }

        for word in words:
            resolved, term_type = semantic_layer.resolve_term(word)
            if term_type == "dimension":
                dim = semantic_layer.get_dimension(resolved)
                if dim:
                    results["dimensions"].append({
                        "name": dim.name,
                        "display_name": dim.display_name,
                        "sql": semantic_layer.build_dimension_sql(dim),
                        "description": dim.description,
                    })
            elif term_type == "metric":
                metric = semantic_layer.get_metric(resolved)
                if metric:
                    results["metrics"].append({
                        "name": metric.name,
                        "display_name": metric.display_name,
                        "sql": semantic_layer.build_metric_sql(metric),
                        "aggregation": metric.aggregation,
                        "description": metric.description,
                    })

        return json.dumps(results, indent=2)

    return query_semantic_model
```

**File**: `app/modules/autonomous_agent/semantic/__init__.py`

```python
"""Semantic layer for business-friendly data modeling."""
from app.modules.autonomous_agent.semantic.models import (
    Dimension,
    Metric,
    Relationship,
    SemanticModel,
)
from app.modules.autonomous_agent.semantic.layer import (
    SemanticLayer,
    create_semantic_tool,
)

__all__ = [
    "Dimension",
    "Metric",
    "Relationship",
    "SemanticModel",
    "SemanticLayer",
    "create_semantic_tool",
]
```

### Phase 3: Autonomous Agent Service

#### 3.1 Main Service
**File**: `app/modules/autonomous_agent/service.py`

```python
"""Autonomous agent service using LangChain DeepAgents."""
import logging
import time
from typing import AsyncGenerator

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, FilesystemBackend

from app.modules.autonomous_agent.models import AgentTask, AgentResult
from app.modules.autonomous_agent.tools import (
    create_sql_query_tool,
    create_pandas_analysis_tool,
    create_python_execute_tool,
)
from app.modules.autonomous_agent.subagents import get_analysis_subagents
from app.modules.autonomous_agent.prompts import get_system_prompt
from app.modules.database_connection.models import DatabaseConnection
from app.utils.sql_database.sql_database import SQLDatabase
from app.utils.model.chat_model import ChatModel

logger = logging.getLogger(__name__)


class AutonomousAgentService:
    """Service for running fully autonomous data analysis tasks.

    Uses LangChain DeepAgents with:
    - Built-in tools: write_todos, read_file, write_file, task, etc.
    - KAI tools: sql_query, analyze_data, python_execute
    - Subagents: query_planner, data_analyst, report_writer
    """

    def __init__(
        self,
        db_connection: DatabaseConnection,
        database: SQLDatabase,
        results_dir: str = "./agent_results",
        llm_config=None,
    ):
        self.db_connection = db_connection
        self.database = database
        self.results_dir = results_dir
        self.llm_config = llm_config

    def _get_llm(self):
        """Get LLM instance."""
        chat_model = ChatModel()
        if self.llm_config:
            return chat_model.get_model(
                database_connection=self.db_connection,
                temperature=0,
                model_family=self.llm_config.model_family,
                model_name=self.llm_config.model_name,
            )
        return chat_model.get_model(
            database_connection=self.db_connection,
            temperature=0,
        )

    def _build_tools(self) -> list:
        """Build KAI-specific tools."""
        return [
            create_sql_query_tool(self.database),
            create_pandas_analysis_tool(),
            create_python_execute_tool(),
        ]

    def _build_backend(self):
        """Build composite backend with file persistence."""
        return CompositeBackend(
            default=StateBackend(),
            routes={
                "/results/": FilesystemBackend(root_dir=self.results_dir),
            },
        )

    def create_agent(self, mode: str = "full_autonomy"):
        """Create autonomous deep agent.

        Args:
            mode: Agent mode (full_autonomy, analysis, query, script)

        Returns:
            Compiled LangGraph agent
        """
        return create_deep_agent(
            model=self._get_llm(),
            tools=self._build_tools(),
            system_prompt=get_system_prompt(
                mode=mode,
                dialect=self.db_connection.dialect,
            ),
            subagents=get_analysis_subagents(),
            backend=self._build_backend(),
        )

    async def execute(self, task: AgentTask) -> AgentResult:
        """Execute task and return final result."""
        start_time = time.time()
        agent = self.create_agent(task.mode)

        config = {"configurable": {"thread_id": task.id}}
        input_state = {
            "messages": [{"role": "user", "content": task.prompt}]
        }

        try:
            result = agent.invoke(input_state, config=config)
            final_message = result["messages"][-1]
            final_answer = (
                final_message.content
                if hasattr(final_message, "content")
                else str(final_message)
            )

            return AgentResult(
                task_id=task.id,
                status="completed",
                final_answer=final_answer,
                execution_time_ms=int((time.time() - start_time) * 1000),
            )
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return AgentResult(
                task_id=task.id,
                status="failed",
                final_answer="",
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
            )

    async def stream_execute(
        self, task: AgentTask
    ) -> AsyncGenerator[dict, None]:
        """Execute task with streaming updates."""
        start_time = time.time()
        agent = self.create_agent(task.mode)

        config = {"configurable": {"thread_id": task.id}}
        input_state = {
            "messages": [{"role": "user", "content": task.prompt}]
        }

        try:
            async for event in agent.astream_events(
                input_state, config=config, version="v2"
            ):
                yield self._process_event(event)

            yield {
                "type": "done",
                "execution_time_ms": int((time.time() - start_time) * 1000),
            }
        except Exception as e:
            yield {"type": "error", "error": str(e)}

    def _process_event(self, event: dict) -> dict:
        """Process LangGraph event for streaming."""
        event_type = event.get("event")

        if event_type == "on_chat_model_stream":
            chunk = event.get("data", {}).get("chunk")
            if chunk:
                content = chunk.content if hasattr(chunk, "content") else ""
                if content:
                    return {"type": "token", "content": content}

        elif event_type == "on_tool_start":
            return {
                "type": "tool_start",
                "tool": event.get("name"),
                "input": event.get("data", {}).get("input"),
            }

        elif event_type == "on_tool_end":
            return {
                "type": "tool_end",
                "tool": event.get("name"),
                "output": str(event.get("data", {}).get("output", ""))[:500],
            }

        return {"type": "other", "event": event_type}
```

### Phase 4: Subagent Definitions

#### 4.1 Specialized Subagents
**File**: `app/modules/autonomous_agent/subagents.py`

```python
"""Subagent definitions for autonomous data analysis.

These subagents are delegated tasks via the built-in `task` tool.
They inherit all tools from the main agent.
"""


def get_analysis_subagents() -> list[dict]:
    """Return subagent definitions for data analysis tasks.

    Format follows deepagents SubAgent TypedDict:
    - name: Unique identifier
    - description: When to use this subagent
    - prompt: System instructions (called 'system_prompt' in older versions)
    """
    return [
        {
            "name": "query_planner",
            "description": "Use when you need to plan complex SQL queries or break down a data question into multiple queries",
            "prompt": """You are a SQL query planning specialist.

Your job is to:
1. Analyze the data question and identify what information is needed
2. Plan the sequence of SQL queries required
3. Consider table relationships, joins, and aggregations
4. Output a clear plan with query descriptions

Use write_todos to track your query plan.
Do NOT execute queries - just plan them.""",
        },
        {
            "name": "data_analyst",
            "description": "Use when you need to analyze query results, find patterns, or generate statistical insights",
            "prompt": """You are a data analyst specialist.

Your job is to:
1. Analyze query results using the analyze_data tool
2. Identify patterns, trends, and anomalies
3. Calculate relevant statistics
4. Generate clear, actionable insights

Focus on answering the user's specific question.
Use python_execute for custom calculations if needed.""",
        },
        {
            "name": "report_writer",
            "description": "Use when you need to synthesize findings into a comprehensive report",
            "prompt": """You are a report writing specialist.

Your job is to:
1. Synthesize analysis findings into clear prose
2. Structure the report with sections and highlights
3. Include key statistics and insights
4. Provide actionable recommendations

Use write_file to save the report to /results/report.md""",
        },
    ]
```

### Phase 5: CLI Implementation

#### 5.1 CLI Command
**File**: `app/modules/autonomous_agent/cli.py`

```python
"""CLI for KAI Autonomous Agent.

Usage:
    kai-agent run "Analyze sales by region" --db conn_123
    kai-agent run "Show top customers" --db conn_123 --mode query
    kai-agent interactive --db conn_123
"""
import asyncio
import json
import uuid
from datetime import datetime

import click
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown

console = Console()


@click.group()
def cli():
    """KAI Autonomous Agent - AI-powered data analysis."""
    pass


@cli.command()
@click.argument("prompt")
@click.option("--db", "db_connection_id", required=True, help="Database connection ID")
@click.option(
    "--mode",
    type=click.Choice(["full_autonomy", "analysis", "query", "script"]),
    default="full_autonomy",
    help="Agent operation mode",
)
@click.option("--output", "-o", type=click.Path(), help="Save result to file")
@click.option("--stream/--no-stream", default=True, help="Stream output")
def run(prompt: str, db_connection_id: str, mode: str, output: str, stream: bool):
    """Run an autonomous analysis task.

    Examples:

        kai-agent run "What are the top 10 products by revenue?" --db conn_123

        kai-agent run "Analyze customer churn patterns" --db conn_123 --mode analysis

        kai-agent run "Write a script to clean the data" --db conn_123 --mode script
    """
    asyncio.run(_run_task(prompt, db_connection_id, mode, output, stream))


async def _run_task(
    prompt: str, db_connection_id: str, mode: str, output: str, stream: bool
):
    """Execute agent task."""
    from app.data.db.storage import Storage
    from app.modules.database_connection.repositories import DatabaseConnectionRepository
    from app.modules.autonomous_agent.service import AutonomousAgentService
    from app.modules.autonomous_agent.models import AgentTask
    from app.utils.sql_database.sql_database import SQLDatabase

    # Initialize
    storage = Storage()
    db_repo = DatabaseConnectionRepository(storage)
    db_connection = db_repo.find_by_id(db_connection_id)

    if not db_connection:
        console.print(f"[red]Error:[/red] Database connection '{db_connection_id}' not found")
        return

    database = SQLDatabase.get_sql_engine(db_connection, False)
    service = AutonomousAgentService(db_connection, database)

    task = AgentTask(
        id=f"cli_{uuid.uuid4().hex[:8]}",
        prompt=prompt,
        db_connection_id=db_connection_id,
        mode=mode,
    )

    console.print(Panel(f"[bold]{prompt}[/bold]", title=f"KAI Agent [{mode}]"))

    if stream:
        # Streaming execution
        with Live(console=console, refresh_per_second=10) as live:
            output_text = ""
            async for event in service.stream_execute(task):
                if event["type"] == "token":
                    output_text += event["content"]
                    live.update(Markdown(output_text))
                elif event["type"] == "tool_start":
                    console.print(f"[dim]Using tool: {event['tool']}[/dim]")
                elif event["type"] == "done":
                    console.print(f"\n[green]Completed in {event['execution_time_ms']}ms[/green]")
                elif event["type"] == "error":
                    console.print(f"[red]Error: {event['error']}[/red]")
    else:
        # Non-streaming execution
        with console.status("[bold]Thinking...[/bold]"):
            result = await service.execute(task)

        if result.status == "completed":
            console.print(Panel(Markdown(result.final_answer), title="Result"))
            console.print(f"[green]Completed in {result.execution_time_ms}ms[/green]")
        else:
            console.print(f"[red]Error: {result.error}[/red]")

        if output and result.final_answer:
            with open(output, "w") as f:
                f.write(result.final_answer)
            console.print(f"[dim]Saved to {output}[/dim]")


@cli.command()
@click.option("--db", "db_connection_id", required=True, help="Database connection ID")
def interactive(db_connection_id: str):
    """Start an interactive agent session.

    Example:
        kai-agent interactive --db conn_123
    """
    asyncio.run(_interactive_session(db_connection_id))


async def _interactive_session(db_connection_id: str):
    """Interactive REPL session."""
    from app.data.db.storage import Storage
    from app.modules.database_connection.repositories import DatabaseConnectionRepository
    from app.modules.autonomous_agent.service import AutonomousAgentService
    from app.modules.autonomous_agent.models import AgentTask
    from app.utils.sql_database.sql_database import SQLDatabase

    storage = Storage()
    db_repo = DatabaseConnectionRepository(storage)
    db_connection = db_repo.find_by_id(db_connection_id)

    if not db_connection:
        console.print(f"[red]Database connection not found[/red]")
        return

    database = SQLDatabase.get_sql_engine(db_connection, False)
    service = AutonomousAgentService(db_connection, database)

    console.print(Panel(
        "[bold]KAI Autonomous Agent[/bold]\n"
        "Type your questions, 'exit' to quit, 'help' for commands",
        title="Interactive Mode"
    ))

    session_id = f"interactive_{uuid.uuid4().hex[:8]}"

    while True:
        try:
            prompt = console.input("\n[bold cyan]kai>[/bold cyan] ").strip()

            if not prompt:
                continue
            if prompt.lower() == "exit":
                break
            if prompt.lower() == "help":
                console.print("Commands: exit, help, clear")
                continue
            if prompt.lower() == "clear":
                console.clear()
                continue

            task = AgentTask(
                id=session_id,
                prompt=prompt,
                db_connection_id=db_connection_id,
            )

            with Live(console=console, refresh_per_second=10) as live:
                output_text = ""
                async for event in service.stream_execute(task):
                    if event["type"] == "token":
                        output_text += event["content"]
                        live.update(Markdown(output_text))

        except KeyboardInterrupt:
            console.print("\n[dim]Use 'exit' to quit[/dim]")
        except EOFError:
            break

    console.print("\n[dim]Session ended[/dim]")


@cli.command()
def list_connections():
    """List available database connections."""
    from app.data.db.storage import Storage
    from app.modules.database_connection.repositories import DatabaseConnectionRepository

    storage = Storage()
    db_repo = DatabaseConnectionRepository(storage)
    connections = db_repo.find_all()

    if not connections:
        console.print("[yellow]No database connections found[/yellow]")
        return

    console.print("[bold]Available Connections:[/bold]")
    for conn in connections:
        console.print(f"  {conn.id}: {conn.alias or conn.dialect} ({conn.dialect})")


if __name__ == "__main__":
    cli()
```

#### 5.2 Entry Point Configuration
**Update**: `pyproject.toml`

```toml
[project.scripts]
kai-agent = "app.modules.autonomous_agent.cli:cli"
```

### Phase 6: System Prompts

#### 6.1 Autonomous Agent Prompts
**File**: `app/modules/autonomous_agent/prompts.py`

```python
"""System prompts for autonomous agent modes.

Note: DeepAgents adds its own middleware-injected prompts for built-in tools.
These prompts are APPENDED to those, so avoid duplicating tool documentation.
"""


def get_system_prompt(mode: str, dialect: str) -> str:
    """Get system prompt for the specified mode.

    Args:
        mode: Agent mode (full_autonomy, analysis, query, script)
        dialect: SQL dialect (postgresql, mysql, etc.)

    Returns:
        System prompt string
    """
    base_context = f"""
Database: {dialect}

Available KAI Tools:
- sql_query: Execute read-only SQL and get results as JSON
- analyze_data: Run pandas analysis on JSON data
- python_execute: Execute Python code (restricted environment)

Subagents (use via 'task' tool):
- query_planner: Plan complex multi-query analysis
- data_analyst: Statistical analysis and pattern finding
- report_writer: Generate formatted reports
"""

    if mode == "full_autonomy":
        return f"""You are KAI, an autonomous data analysis agent.

You have FULL AUTONOMY to answer the user's question. This means:
1. Plan your approach using write_todos
2. Execute SQL queries to gather data
3. Analyze results using pandas
4. Run Python code for custom calculations
5. Delegate to subagents for complex tasks
6. Save reports to /results/

WORKFLOW:
1. Understand what the user wants to know
2. Plan the queries needed (use query_planner for complex questions)
3. Execute queries and gather data
4. Analyze the data (use data_analyst for deep analysis)
5. Synthesize findings into a clear answer
6. Optionally save a detailed report

Be thorough but efficient. Explain your reasoning. If you encounter errors, debug and retry.

{base_context}"""

    elif mode == "analysis":
        return f"""You are KAI in analysis mode.

Focus on analyzing data and generating insights:
1. Execute SQL to get the relevant data
2. Use analyze_data for statistical summaries
3. Identify patterns, trends, and anomalies
4. Generate clear, actionable insights

{base_context}"""

    elif mode == "query":
        return f"""You are KAI in query mode.

Focus on SQL query generation and execution:
1. Understand the user's data needs
2. Generate efficient, correct SQL
3. Execute and present results clearly
4. Explain what the query does

{base_context}"""

    elif mode == "script":
        return f"""You are KAI in script mode.

Focus on Python code generation:
1. Write clean, efficient Python code
2. Use available modules (json, math, statistics, datetime, collections)
3. Process and transform data as needed
4. Save results using write_file

{base_context}"""

    # Default to full autonomy
    return get_system_prompt("full_autonomy", dialect)
```

### Phase 7: Integration & Testing

#### 7.1 Add Dependencies
**Update**: `pyproject.toml`

```toml
[project]
dependencies = [
    # ... existing deps ...
    "click>=8.0.0",
    "rich>=13.0.0",
]

[project.scripts]
kai-agent = "app.modules.autonomous_agent.cli:cli"
```

#### 7.2 Unit Tests
**File**: `tests/modules/autonomous_agent/test_tools.py`

```python
import pytest
import json
from app.modules.autonomous_agent.tools import (
    create_pandas_analysis_tool,
    create_python_execute_tool,
)


def test_pandas_analysis_summary():
    """Test pandas summary analysis."""
    analyze = create_pandas_analysis_tool()
    data = json.dumps([
        {"a": 1, "b": 4},
        {"a": 2, "b": 5},
        {"a": 3, "b": 6},
    ])
    result = analyze(data, "summary")
    assert "mean" in result
    assert "count" in result


def test_python_execute_safe():
    """Test safe Python execution."""
    execute = create_python_execute_tool()
    result = execute("print(sum([1, 2, 3]))")
    assert "6" in result


def test_python_execute_restricted():
    """Test that dangerous operations are blocked."""
    execute = create_python_execute_tool()
    result = execute("import os; os.system('ls')")
    assert "error" in result.lower()
```

#### 7.3 Integration Tests
**File**: `tests/modules/autonomous_agent/test_service.py`

```python
import pytest
from unittest.mock import Mock, AsyncMock
from app.modules.autonomous_agent.service import AutonomousAgentService
from app.modules.autonomous_agent.models import AgentTask


@pytest.fixture
def mock_db_connection():
    conn = Mock()
    conn.dialect = "postgresql"
    return conn


@pytest.fixture
def mock_database():
    db = Mock()
    db.run_sql.return_value = (
        "OK",
        {"result": [{"id": 1, "name": "Test"}]}
    )
    return db


def test_create_agent(mock_db_connection, mock_database):
    """Test agent creation."""
    service = AutonomousAgentService(mock_db_connection, mock_database)
    agent = service.create_agent("full_autonomy")
    assert agent is not None


@pytest.mark.asyncio
async def test_execute_task(mock_db_connection, mock_database):
    """Test task execution."""
    service = AutonomousAgentService(mock_db_connection, mock_database)
    task = AgentTask(
        id="test_1",
        prompt="Show me all users",
        db_connection_id="test_db",
        mode="query",
    )
    result = await service.execute(task)
    assert result.task_id == "test_1"
    assert result.status in ["completed", "failed"]
```

#### 7.4 CLI Test
**File**: `tests/modules/autonomous_agent/test_cli.py`

```python
from click.testing import CliRunner
from app.modules.autonomous_agent.cli import cli


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "KAI Autonomous Agent" in result.output


def test_cli_run_help():
    """Test run command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["run", "--help"])
    assert result.exit_code == 0
    assert "--db" in result.output
    assert "--mode" in result.output
```

---

## File Summary

### New Files to Create (17 files)

#### Core Module (7 files)
| File | Purpose |
|------|---------|
| `app/modules/autonomous_agent/__init__.py` | Module exports |
| `app/modules/autonomous_agent/models.py` | AgentTask, AgentResult, ChartSpec, Insight, SuggestedQuestion |
| `app/modules/autonomous_agent/service.py` | AutonomousAgentService |
| `app/modules/autonomous_agent/subagents.py` | Subagent definitions |
| `app/modules/autonomous_agent/prompts.py` | System prompts per mode |
| `app/modules/autonomous_agent/cli.py` | Click CLI commands |

#### Tools Submodule (6 files) - GenBI Features #1, #2, #4, #5
| File | Purpose |
|------|---------|
| `app/modules/autonomous_agent/tools/__init__.py` | Tool exports |
| `app/modules/autonomous_agent/tools/sql_tools.py` | SQL query execution tool |
| `app/modules/autonomous_agent/tools/chart_tools.py` | Text-to-Chart generation (Feature #1) |
| `app/modules/autonomous_agent/tools/insights_tools.py` | AI insights extraction (Feature #2) |
| `app/modules/autonomous_agent/tools/suggestions_tools.py` | Follow-up questions (Features #4 & #5) |
| `app/modules/autonomous_agent/tools/analysis_tools.py` | Pandas analysis + Python execution |

#### Semantic Submodule (3 files) - GenBI Feature #3
| File | Purpose |
|------|---------|
| `app/modules/autonomous_agent/semantic/__init__.py` | Semantic layer exports |
| `app/modules/autonomous_agent/semantic/models.py` | Dimension, Metric, Relationship, SemanticModel |
| `app/modules/autonomous_agent/semantic/layer.py` | SemanticLayer class + semantic tool |

### Test Files (4 files)

| File | Purpose |
|------|---------|
| `tests/modules/autonomous_agent/__init__.py` | Test module |
| `tests/modules/autonomous_agent/test_tools.py` | Tool unit tests |
| `tests/modules/autonomous_agent/test_service.py` | Service integration tests |
| `tests/modules/autonomous_agent/test_cli.py` | CLI tests |

### Files to Modify (1 file)

| File | Changes |
|------|---------|
| `pyproject.toml` | Add click, rich deps + scripts entry |

---

## Implementation Order

| Phase | Description | Files |
|-------|-------------|-------|
| 1 | Create module structure + models.py | `__init__.py`, `models.py` |
| 2.1 | Implement SQL tools | `tools/__init__.py`, `tools/sql_tools.py` |
| 2.2 | Implement Chart tools (GenBI #1) | `tools/chart_tools.py` |
| 2.3 | Implement Insights tools (GenBI #2) | `tools/insights_tools.py` |
| 2.4 | Implement Suggestions tools (GenBI #4 & #5) | `tools/suggestions_tools.py` |
| 2.5 | Implement Analysis tools | `tools/analysis_tools.py` |
| 2.6 | Implement Semantic Layer (GenBI #3) | `semantic/__init__.py`, `semantic/models.py`, `semantic/layer.py` |
| 3 | Build AutonomousAgentService | `service.py` |
| 4 | Add subagent definitions | `subagents.py` |
| 5 | Create system prompts | `prompts.py` |
| 6 | Implement CLI with Click + Rich | `cli.py` |
| 7 | Write tests + update pyproject.toml | `tests/`, `pyproject.toml` |

### GenBI Features Mapping

| Feature | Phase | Files |
|---------|-------|-------|
| #1 Text-to-Chart | 2.2 | `tools/chart_tools.py` |
| #2 AI-Generated Insights | 2.3 | `tools/insights_tools.py` |
| #3 Semantic Layer / Data Model | 2.6 | `semantic/` |
| #4 Follow-up Questions | 2.4 | `tools/suggestions_tools.py` |
| #5 Data Exploration Flow | 2.4 | `tools/suggestions_tools.py` |

---

## Usage Examples

```bash
# Single query
kai-agent run "Show top 10 customers by revenue" --db conn_123

# Full analysis
kai-agent run "Analyze sales trends and identify growth opportunities" --db conn_123 --mode full_autonomy

# Save output
kai-agent run "Generate quarterly report" --db conn_123 -o report.md

# Interactive session
kai-agent interactive --db conn_123

# List database connections
kai-agent list-connections
```

---

## Sources

- [LangChain DeepAgents GitHub](https://github.com/langchain-ai/deepagents)
- [DeepAgents Quickstarts](https://github.com/langchain-ai/deepagents-quickstarts)
- [LangChain DeepAgents Blog](https://blog.langchain.com/deep-agents/)
- [LangGraph Agent Concepts](https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/)
- [DeepAgents Documentation](https://docs.langchain.com/oss/python/deepagents/overview)
