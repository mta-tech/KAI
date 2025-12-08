"""LLM-based dashboard planning service."""
from __future__ import annotations

import json
import logging
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage

from app.data.db.storage import Storage
from app.modules.dashboard.models import (
    AggregationType,
    ChartType,
    ChartWidgetConfig,
    DashboardPlan,
    KPIWidgetConfig,
    TableWidgetConfig,
    Widget,
    WidgetSize,
    WidgetType,
)
from app.modules.dashboard.prompts import (
    DASHBOARD_PLANNER_SYSTEM_PROMPT,
    DASHBOARD_PLANNER_USER_PROMPT,
    DASHBOARD_REFINE_SYSTEM_PROMPT,
    DASHBOARD_REFINE_USER_PROMPT,
)
from app.modules.mdl.repositories import MDLRepository
from app.modules.sql_generation.models import LLMConfig
from app.modules.table_description.repositories import TableDescriptionRepository
from app.server.config import Settings
from app.utils.model.chat_model import ChatModel

logger = logging.getLogger(__name__)


class DashboardPlannerService:
    """LLM-based dashboard planning from natural language."""

    def __init__(self, storage: Storage):
        self.storage = storage
        self.mdl_repo = MDLRepository(storage)
        self.table_repo = TableDescriptionRepository(storage)
        self.settings = Settings()

    async def plan_dashboard(
        self,
        user_request: str,
        db_connection_id: str,
        llm_config: Optional[LLMConfig] = None,
    ) -> DashboardPlan:
        """
        Generate a dashboard plan from natural language request.

        Args:
            user_request: Natural language description of desired dashboard
            db_connection_id: Database connection ID
            llm_config: Optional LLM configuration

        Returns:
            DashboardPlan with widget specifications
        """
        # Build context
        context = await self._build_context(db_connection_id)

        # Get LLM
        llm = self._get_llm(llm_config)

        # Format prompt
        user_prompt = DASHBOARD_PLANNER_USER_PROMPT.format(
            user_request=user_request,
            schema_info=context["schema_info"],
            table_names=context["table_names"],
            mdl_metrics=context["mdl_metrics"],
            sample_data=context["sample_data"],
        )

        # Call LLM
        messages = [
            SystemMessage(content=DASHBOARD_PLANNER_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = await llm.ainvoke(messages)
            plan = self._parse_plan_response(response.content)
            return plan
        except Exception as e:
            logger.error(f"Dashboard planning failed: {e}")
            # Return a basic fallback plan
            return self._create_fallback_plan(user_request, context)

    async def refine_dashboard(
        self,
        current_dashboard: dict,
        refinement_request: str,
        db_connection_id: str,
        llm_config: Optional[LLMConfig] = None,
    ) -> DashboardPlan:
        """
        Refine an existing dashboard based on user feedback.

        Args:
            current_dashboard: Current dashboard configuration
            refinement_request: Natural language refinement request
            db_connection_id: Database connection ID
            llm_config: Optional LLM configuration

        Returns:
            Updated DashboardPlan
        """
        context = await self._build_context(db_connection_id)
        llm = self._get_llm(llm_config)

        user_prompt = DASHBOARD_REFINE_USER_PROMPT.format(
            current_dashboard=json.dumps(current_dashboard, indent=2),
            refinement_request=refinement_request,
            schema_info=context["schema_info"],
        )

        messages = [
            SystemMessage(content=DASHBOARD_REFINE_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = await llm.ainvoke(messages)
            return self._parse_plan_response(response.content)
        except Exception as e:
            logger.error(f"Dashboard refinement failed: {e}")
            raise

    async def _build_context(self, db_connection_id: str) -> dict:
        """Build context information for LLM."""
        # Get table descriptions
        table_descriptions = self.table_repo.find_by(
            {"db_connection_id": db_connection_id}
        )

        # Build schema info
        schema_lines = []
        table_names = []
        sample_data_lines = []

        for table in table_descriptions:
            table_names.append(table.table_name)

            columns = []
            for col in table.columns:
                col_info = f"  - {col.name} ({col.data_type})"
                if col.description:
                    col_info += f": {col.description}"
                if col.is_primary_key:
                    col_info += " [PK]"
                if col.foreign_key:
                    col_info += f" [FK -> {col.foreign_key.reference_table}]"
                columns.append(col_info)

            schema_lines.append(f"**{table.table_name}**")
            if table.table_description:
                schema_lines.append(f"  Description: {table.table_description}")
            schema_lines.append("  Columns:")
            schema_lines.extend(columns)
            schema_lines.append("")

            # Add sample data
            if table.examples:
                sample_data_lines.append(f"**{table.table_name}** samples:")
                for i, row in enumerate(table.examples[:2]):
                    sample_data_lines.append(
                        f"  Row {i+1}: {json.dumps(row, default=str)}"
                    )

        # Get MDL metrics
        mdl_metrics = "None defined"
        manifest = await self.mdl_repo.get_by_db_connection(db_connection_id)
        if manifest and manifest.metrics:
            metric_lines = []
            for metric in manifest.metrics:
                metric_lines.append(f"- {metric.name}: {metric.description or 'No description'}")
            mdl_metrics = "\n".join(metric_lines)

        return {
            "schema_info": "\n".join(schema_lines) or "No schema information available",
            "table_names": ", ".join(table_names) or "No tables found",
            "mdl_metrics": mdl_metrics,
            "sample_data": "\n".join(sample_data_lines) or "No sample data available",
        }

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
            temperature=0.3,  # Lower temperature for more consistent plans
        )

    def _parse_plan_response(self, content: str) -> DashboardPlan:
        """Parse LLM response into DashboardPlan."""
        try:
            # Clean response
            content = content.strip()

            # Handle markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            data = json.loads(content)

            return DashboardPlan(
                dashboard_name=data.get("dashboard_name", "Dashboard"),
                description=data.get("description"),
                widgets=data.get("widgets", []),
                suggested_filters=data.get("suggested_filters", []),
                theme=data.get("theme", "default"),
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse dashboard plan: {e}")
            raise ValueError(f"Invalid dashboard plan response: {e}")

    def _create_fallback_plan(
        self, user_request: str, context: dict
    ) -> DashboardPlan:
        """Create a basic fallback plan if LLM fails."""
        return DashboardPlan(
            dashboard_name=f"Dashboard: {user_request[:50]}",
            description="Auto-generated dashboard",
            widgets=[
                {
                    "name": "Overview",
                    "widget_type": "table",
                    "size": "full",
                    "query_description": f"Show data relevant to: {user_request}",
                    "table_config": {"sortable": True, "page_size": 10},
                }
            ],
            suggested_filters=[],
        )

    def plan_to_widgets(self, plan: DashboardPlan) -> list[Widget]:
        """Convert DashboardPlan to Widget objects."""
        widgets = []

        for i, w in enumerate(plan.widgets):
            widget_type = WidgetType(w.get("widget_type", "chart"))
            size = WidgetSize(w.get("size", "medium"))

            widget = Widget(
                name=w.get("name", f"Widget {i+1}"),
                widget_type=widget_type,
                size=size,
                query_description=w.get("query_description"),
            )

            # Parse type-specific config
            if widget_type == WidgetType.CHART and w.get("chart_config"):
                cc = w["chart_config"]
                widget.chart_config = ChartWidgetConfig(
                    chart_type=ChartType(cc.get("chart_type", "bar")),
                    x_column=cc.get("x_column"),
                    y_column=cc.get("y_column"),
                    color_column=cc.get("color_column"),
                    aggregation=AggregationType(cc["aggregation"])
                    if cc.get("aggregation")
                    else None,
                )

            elif widget_type == WidgetType.KPI and w.get("kpi_config"):
                kc = w["kpi_config"]
                widget.kpi_config = KPIWidgetConfig(
                    metric_column=kc.get("metric_column", ""),
                    aggregation=AggregationType(kc.get("aggregation", "sum")),
                    format=kc.get("format", "number"),
                    prefix=kc.get("prefix"),
                    comparison_period=kc.get("comparison_period"),
                )

            elif widget_type == WidgetType.TABLE and w.get("table_config"):
                tc = w["table_config"]
                widget.table_config = TableWidgetConfig(
                    columns=tc.get("columns", []),
                    sortable=tc.get("sortable", True),
                    page_size=tc.get("page_size", 10),
                )

            widgets.append(widget)

        return widgets


__all__ = ["DashboardPlannerService"]
