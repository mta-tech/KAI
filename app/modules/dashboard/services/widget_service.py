"""Widget execution and query generation service."""
from __future__ import annotations

import json
import logging
import time
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage

from app.data.db.storage import Storage
from app.modules.dashboard.models import (
    Widget,
    WidgetResult,
    WidgetType,
)
from app.modules.dashboard.prompts import QUERY_GENERATION_PROMPT, SQL_FIX_PROMPT
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.sql_generation.models import LLMConfig
from app.modules.table_description.repositories import TableDescriptionRepository
from app.modules.visualization.services.chart_service import ChartService
from app.server.config import Settings
from app.utils.model.chat_model import ChatModel
from app.utils.sql_database.sql_database import SQLDatabase

logger = logging.getLogger(__name__)


class WidgetService:
    """Service for widget query generation and execution."""

    def __init__(self, storage: Storage):
        self.storage = storage
        self.table_repo = TableDescriptionRepository(storage)
        self.db_conn_repo = DatabaseConnectionRepository(storage)
        self.chart_service = ChartService()
        self.settings = Settings()

    async def generate_widget_query(
        self,
        widget: Widget,
        db_connection_id: str,
        llm_config: Optional[LLMConfig] = None,
    ) -> str:
        """
        Generate SQL query for a widget using LLM.

        Args:
            widget: Widget definition with query_description
            db_connection_id: Database connection ID
            llm_config: Optional LLM configuration

        Returns:
            SQL query string
        """
        if widget.query:
            # Query already provided
            return widget.query

        if not widget.query_description:
            raise ValueError(f"Widget {widget.name} has no query or query_description")

        # Get database dialect
        db_connection = self.db_conn_repo.find_by_id(db_connection_id)
        db_dialect = db_connection.dialect if db_connection else "postgresql"

        # Build schema context
        schema_info = await self._get_schema_info(db_connection_id)

        # Get LLM
        llm = self._get_llm(llm_config)

        # Build prompt
        prompt = QUERY_GENERATION_PROMPT.format(
            widget_name=widget.name,
            widget_type=widget.widget_type.value,
            query_description=widget.query_description,
            db_dialect=db_dialect,
            schema_info=schema_info,
        )

        messages = [
            SystemMessage(content="You are a SQL expert. Generate only the SQL query, no explanations."),
            HumanMessage(content=prompt),
        ]

        try:
            response = await llm.ainvoke(messages)
            query = self._extract_sql(response.content)
            return query
        except Exception as e:
            logger.error(f"Query generation failed for widget {widget.name}: {e}")
            raise

    async def generate_and_validate_query(
        self,
        widget: Widget,
        db_connection_id: str,
        database: SQLDatabase,
        llm_config: Optional[LLMConfig] = None,
        max_retries: int = 3,
    ) -> tuple[str, Optional[str]]:
        """
        Generate SQL, validate by execution, fix if error, retry up to max_retries.

        Args:
            widget: Widget definition with query_description
            db_connection_id: Database connection ID
            database: SQLDatabase instance for validation
            llm_config: Optional LLM configuration
            max_retries: Maximum number of fix attempts

        Returns:
            tuple[str, Optional[str]]: (sql_query, error_message or None)
        """
        # Generate initial SQL
        try:
            sql = await self.generate_widget_query(widget, db_connection_id, llm_config)
        except Exception as e:
            return "", f"Failed to generate SQL: {e}"

        # Try to validate and fix
        for attempt in range(max_retries + 1):
            error = self._validate_sql(sql, database)

            if error is None:
                # SQL is valid
                logger.info(f"Widget '{widget.name}' SQL validated on attempt {attempt + 1}")
                return sql, None

            if attempt < max_retries:
                # Try to fix the SQL
                logger.warning(
                    f"Widget '{widget.name}' SQL failed (attempt {attempt + 1}/{max_retries + 1}): {error}"
                )
                try:
                    sql = await self._fix_sql(sql, error, db_connection_id, llm_config)
                except Exception as fix_error:
                    logger.error(f"Failed to fix SQL: {fix_error}")
                    return sql, str(error)
            else:
                # Max retries reached
                logger.error(
                    f"Widget '{widget.name}' SQL validation failed after {max_retries + 1} attempts"
                )
                return sql, str(error)

        return sql, "Unknown error"

    def _validate_sql(self, sql: str, database: SQLDatabase) -> Optional[str]:
        """
        Validate SQL by executing it.

        Returns:
            None if valid, error message if invalid
        """
        try:
            # Parse to filter dangerous commands
            query = database.parser_to_filter_commands(sql)
            # Execute with LIMIT 1 to validate without fetching all data
            database.run_sql(query)
            return None
        except Exception as e:
            return str(e)

    async def _fix_sql(
        self,
        original_sql: str,
        error_message: str,
        db_connection_id: str,
        llm_config: Optional[LLMConfig] = None,
    ) -> str:
        """
        Use LLM to fix a SQL query based on error message.

        Args:
            original_sql: The SQL that failed
            error_message: The error message from execution
            db_connection_id: Database connection ID
            llm_config: Optional LLM configuration

        Returns:
            Fixed SQL query
        """
        # Get database dialect
        db_connection = self.db_conn_repo.find_by_id(db_connection_id)
        db_dialect = db_connection.dialect if db_connection else "postgresql"

        # Get schema info
        schema_info = await self._get_schema_info(db_connection_id)

        # Get LLM
        llm = self._get_llm(llm_config)

        # Build prompt
        prompt = SQL_FIX_PROMPT.format(
            original_sql=original_sql,
            error_message=error_message,
            db_dialect=db_dialect,
            schema_info=schema_info,
        )

        messages = [
            SystemMessage(content="You are a SQL expert. Fix the SQL query to resolve the error."),
            HumanMessage(content=prompt),
        ]

        response = await llm.ainvoke(messages)
        fixed_sql = self._extract_sql(response.content)

        logger.info(f"Fixed SQL: {fixed_sql[:100]}...")
        return fixed_sql

    async def execute_widget(
        self,
        widget: Widget,
        db_connection_id: str,
        database: SQLDatabase,
        theme: str = "default",
    ) -> WidgetResult:
        """
        Execute widget query and generate visualization.

        Args:
            widget: Widget with SQL query
            db_connection_id: Database connection ID
            database: SQLDatabase instance
            theme: Theme name for charts

        Returns:
            WidgetResult with data and rendered output
        """
        start_time = time.time()
        result = WidgetResult(widget_id=widget.id, status="running")

        try:
            if not widget.query:
                raise ValueError(f"Widget {widget.name} has no query")

            # Execute query - run_sql returns (str_repr, result_dict)
            # Note: str_repr is Python str() not JSON, use result_dict instead
            _, result_dict = database.run_sql(widget.query)

            # Extract data from result dict (handles Decimal and other types)
            data = result_dict.get("result", [])

            # Convert non-JSON-serializable types
            def convert_value(v):
                from datetime import date, datetime
                import numpy as np

                if v is None:
                    return None
                if isinstance(v, (date, datetime)):
                    return v.isoformat() if isinstance(v, datetime) else str(v)
                if isinstance(v, np.ndarray):
                    return v.tolist()
                if hasattr(v, "__float__"):  # Handles Decimal
                    return float(v)
                return v

            data = [
                {k: convert_value(v) for k, v in row.items()}
                for row in data
            ]

            result.data = data
            result.row_count = len(data)

            # Generate output based on widget type
            if widget.widget_type == WidgetType.KPI:
                result = self._render_kpi(widget, data, result)
            elif widget.widget_type == WidgetType.CHART:
                result = await self._render_chart(widget, data, result, theme)
            elif widget.widget_type == WidgetType.TABLE:
                result = self._render_table(widget, data, result)

            result.status = "completed"

        except Exception as e:
            logger.error(f"Widget execution failed for {widget.name}: {e}")
            result.status = "failed"
            result.error = str(e)

        result.execution_time_ms = int((time.time() - start_time) * 1000)
        return result

    def _render_kpi(
        self, widget: Widget, data: list[dict], result: WidgetResult
    ) -> WidgetResult:
        """Render KPI widget."""
        if not data:
            result.value = 0
            result.formatted_value = "N/A"
            return result

        # Get the first numeric value from the result
        row = data[0]
        value = None

        if widget.kpi_config and widget.kpi_config.metric_column:
            value = row.get(widget.kpi_config.metric_column)

        # Fall back to first numeric value if metric_column not found or not specified
        if value is None:
            for v in row.values():
                if isinstance(v, (int, float)):
                    value = v
                    break

        if value is not None:
            result.value = float(value)

            # Format value
            kpi_config = widget.kpi_config
            if kpi_config:
                if kpi_config.format == "currency":
                    prefix = kpi_config.prefix or "$"
                    result.formatted_value = f"{prefix}{value:,.{kpi_config.decimals}f}"
                elif kpi_config.format == "percentage":
                    suffix = kpi_config.suffix or "%"
                    result.formatted_value = f"{value:,.{kpi_config.decimals}f}{suffix}"
                else:
                    result.formatted_value = f"{value:,.{kpi_config.decimals}f}"
            else:
                result.formatted_value = f"{value:,.0f}"

            # Calculate change if comparison data exists
            if len(data) > 1 and "previous" in data[1]:
                prev_value = data[1].get("previous", 0)
                if prev_value and prev_value != 0:
                    change = ((value - prev_value) / prev_value) * 100
                    result.change = round(change, 1)
                    result.change_direction = "up" if change > 0 else "down" if change < 0 else "neutral"
        else:
            result.formatted_value = "N/A"

        # Generate simple HTML
        change_class = result.change_direction or "neutral"
        change_html = ""
        if result.change is not None:
            arrow = "↑" if result.change > 0 else "↓" if result.change < 0 else "→"
            change_html = f'<div class="kpi-change {change_class}">{arrow} {abs(result.change)}%</div>'

        result.html = f"""
        <div class="kpi-widget">
            <div class="kpi-value">{result.formatted_value}</div>
            {change_html}
        </div>
        """

        return result

    async def _render_chart(
        self, widget: Widget, data: list[dict], result: WidgetResult, theme: str
    ) -> WidgetResult:
        """Render chart widget using ChartService."""
        if not data:
            result.html = '<div class="no-data">No data available</div>'
            return result

        try:
            # Convert list of dicts to DataFrame for chart service
            import pandas as pd
            df = pd.DataFrame(data)
            available_columns = list(df.columns)

            # Get chart config
            chart_config = widget.chart_config
            if not chart_config:
                # Try to infer chart type
                chart_type = "bar"
                x_col = None
                y_col = None
            else:
                chart_type = chart_config.chart_type.value
                x_col = chart_config.x_column
                y_col = chart_config.y_column

            # Helper to find similar column name
            def find_similar_column(target: str, columns: list[str]) -> Optional[str]:
                """Find column with similar name (case-insensitive, partial match)."""
                if not target:
                    return None
                target_lower = target.lower()
                # Exact match (case-insensitive)
                for col in columns:
                    if col.lower() == target_lower:
                        return col
                # Partial match (target in column or column in target)
                for col in columns:
                    col_lower = col.lower()
                    if target_lower in col_lower or col_lower in target_lower:
                        return col
                # Word match (any word in common)
                target_words = set(target_lower.replace('_', ' ').split())
                for col in columns:
                    col_words = set(col.lower().replace('_', ' ').split())
                    if target_words & col_words:
                        return col
                return None

            # Validate columns exist, try fuzzy match, otherwise infer from actual data
            if x_col and x_col not in available_columns:
                matched = find_similar_column(x_col, available_columns)
                if matched:
                    logger.info(f"x_column '{x_col}' matched to '{matched}'")
                    x_col = matched
                else:
                    logger.warning(f"x_column '{x_col}' not in data columns {available_columns}, inferring")
                    x_col = None
            if y_col and y_col not in available_columns:
                matched = find_similar_column(y_col, available_columns)
                if matched:
                    logger.info(f"y_column '{y_col}' matched to '{matched}'")
                    y_col = matched
                else:
                    logger.warning(f"y_column '{y_col}' not in data columns {available_columns}, inferring")
                    y_col = None

            # Infer columns from data if needed
            if not x_col or not y_col:
                # Find datetime/string column for x, numeric for y
                for col in available_columns:
                    sample_val = df[col].iloc[0] if len(df) > 0 else None
                    if sample_val is not None:
                        if not x_col and (isinstance(sample_val, str) or pd.api.types.is_datetime64_any_dtype(df[col])):
                            x_col = col
                        elif not y_col and isinstance(sample_val, (int, float)) and not isinstance(sample_val, bool):
                            y_col = col
                # If still no x_col, use first column
                if not x_col and available_columns:
                    x_col = available_columns[0]
                # If still no y_col, use first numeric column
                if not y_col:
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    if numeric_cols:
                        y_col = numeric_cols[0]

            # Generate chart
            from app.modules.visualization.models import ChartConfig

            # Validate color_column if specified (with fuzzy match)
            color_col = None
            if chart_config and chart_config.color_column:
                if chart_config.color_column in available_columns:
                    color_col = chart_config.color_column
                else:
                    matched = find_similar_column(chart_config.color_column, available_columns)
                    if matched:
                        logger.info(f"color_column '{chart_config.color_column}' matched to '{matched}'")
                        color_col = matched

            config = ChartConfig(
                chart_type=chart_type,
                x_column=x_col,
                y_column=y_col,
                color_column=color_col,
                title=widget.name,
                theme=theme,
            )

            chart_result = self.chart_service.generate_chart(df, config)

            result.html = chart_result.html
            result.plotly_json = chart_result.json_spec

        except Exception as e:
            logger.error(f"Chart rendering failed: {e}")
            result.html = f'<div class="chart-error">Chart error: {e}</div>'

        return result

    def _render_table(
        self, widget: Widget, data: list[dict], result: WidgetResult
    ) -> WidgetResult:
        """Render table widget."""
        if not data:
            result.html = '<div class="no-data">No data available</div>'
            return result

        # Get columns
        table_config = widget.table_config
        if table_config and table_config.columns:
            columns = table_config.columns
        else:
            columns = list(data[0].keys())

        # Limit rows - REMOVED for DataTables support
        # page_size = table_config.page_size if table_config else 10
        # display_data = data[:page_size]
        display_data = data

        # Build HTML table
        html_parts = ['<table class="data-table">']

        # Header
        html_parts.append("<thead><tr>")
        for col in columns:
            html_parts.append(f"<th>{col}</th>")
        html_parts.append("</tr></thead>")

        # Body
        html_parts.append("<tbody>")
        for row in display_data:
            html_parts.append("<tr>")
            for col in columns:
                value = row.get(col, "")
                # Format value
                if isinstance(value, float):
                    value = f"{value:,.2f}"
                elif value is None:
                    value = ""
                html_parts.append(f"<td>{value}</td>")
            html_parts.append("</tr>")
        html_parts.append("</tbody>")

        html_parts.append("</table>")
        
        # Footer removed as DataTables handles information display

        result.html = "\n".join(html_parts)
        return result

    async def _get_schema_info(self, db_connection_id: str) -> str:
        """Get schema information for query generation."""
        table_descriptions = self.table_repo.find_by(
            {"db_connection_id": db_connection_id}
        )

        lines = []
        for table in table_descriptions:
            columns = []
            for col in table.columns:
                col_info = f"  - {col.name} ({col.data_type})"
                if col.is_primary_key:
                    col_info += " [PK]"
                if col.foreign_key:
                    col_info += f" [FK -> {col.foreign_key.reference_table}]"
                columns.append(col_info)

            lines.append(f"Table: {table.table_name}")
            lines.extend(columns)
            lines.append("")

        return "\n".join(lines) or "No schema information available"

    def _get_llm(self, llm_config: Optional[LLMConfig]):
        """Get LLM instance."""
        if llm_config:
            model_family = llm_config.model_family
            model_name = llm_config.model_name
        else:
            model_family = self.settings.CHAT_FAMILY or "google"
            model_name = self.settings.CHAT_MODEL or "gemini-2.0-flash"

        return ChatModel().get_model(
            database_connection=None,
            model_family=model_family,
            model_name=model_name,
            temperature=0.0,  # Deterministic SQL generation
        )

    def _extract_sql(self, content: str) -> str:
        """Extract SQL query from LLM response."""
        content = content.strip()

        # Handle markdown code blocks
        if "```sql" in content:
            content = content.split("```sql")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        # Clean up
        content = content.strip().rstrip(";") + ";"

        return content


__all__ = ["WidgetService"]
