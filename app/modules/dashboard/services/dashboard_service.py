"""Main dashboard orchestration service."""
from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime
from typing import AsyncIterator, Optional

from app.data.db.storage import Storage
from app.modules.dashboard.exceptions import (
    DashboardCreationError,
    DashboardExecutionError,
    DashboardNotFoundError,
    DashboardRenderError,
    ShareTokenError,
)
from app.modules.dashboard.models import (
    CreateDashboardRequest,
    Dashboard,
    DashboardLayout,
    DashboardPlan,
    DashboardRun,
    DashboardSummary,
    RefineDashboardRequest,
    ShareResponse,
    UpdateDashboardRequest,
    Widget,
    WidgetResult,
)
from app.modules.dashboard.repositories import DashboardRepository
from app.modules.dashboard.services.layout_service import LayoutService
from app.modules.dashboard.services.planner_service import DashboardPlannerService
from app.modules.dashboard.services.renderer_service import DashboardRendererService
from app.modules.dashboard.services.widget_service import WidgetService
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.sql_generation.models import LLMConfig
from app.server.config import Settings
from app.utils.sql_database.sql_database import SQLDatabase

logger = logging.getLogger(__name__)


class StreamEvent:
    """Event for streaming dashboard generation progress."""

    def __init__(self, event_type: str, data: dict):
        self.type = event_type
        self.data = data


class DashboardService:
    """
    Main service for dashboard operations.

    Orchestrates planning, widget generation, execution, and rendering.
    """

    def __init__(self, storage: Storage):
        self.storage = storage
        self.repository = DashboardRepository(storage)
        self.planner = DashboardPlannerService(storage)
        self.widget_service = WidgetService(storage)
        self.layout_service = LayoutService()
        self.renderer = DashboardRendererService()
        self.db_conn_repo = DatabaseConnectionRepository(storage)
        self.settings = Settings()

    # =========================================================================
    # Dashboard CRUD Operations
    # =========================================================================

    async def create_from_nl(
        self,
        request: CreateDashboardRequest,
        llm_config: Optional[LLMConfig] = None,
    ) -> Dashboard:
        """
        Create a dashboard from natural language request.

        Args:
            request: CreateDashboardRequest with NL description
            llm_config: Optional LLM configuration

        Returns:
            Created Dashboard
        """
        # Plan the dashboard using LLM
        plan = await self.planner.plan_dashboard(
            user_request=request.request,
            db_connection_id=request.db_connection_id,
            llm_config=llm_config,
        )

        # Convert plan to widgets
        widgets = self.planner.plan_to_widgets(plan)

        # Auto-layout widgets
        widgets = self.layout_service.auto_layout(widgets)

        # Create dashboard
        dashboard = Dashboard(
            name=request.name or plan.dashboard_name,
            description=plan.description,
            db_connection_id=request.db_connection_id,
            layout=DashboardLayout(widgets=widgets),
            theme=request.theme,
        )

        # Get database connection for SQL validation
        db_connection = self.db_conn_repo.find_by_id(request.db_connection_id)
        database = None
        if db_connection:
            database = SQLDatabase.get_sql_engine(db_connection)

        # Generate and validate queries for each widget
        for widget in dashboard.layout.widgets:
            if widget.query_description and not widget.query:
                try:
                    if database:
                        # Use validation with auto-fix
                        sql, error = await self.widget_service.generate_and_validate_query(
                            widget=widget,
                            db_connection_id=request.db_connection_id,
                            database=database,
                            llm_config=llm_config,
                            max_retries=3,
                        )
                        widget.query = sql
                        if error:
                            logger.warning(f"Widget {widget.name} has SQL error: {error}")
                    else:
                        # Fallback: generate without validation
                        widget.query = await self.widget_service.generate_widget_query(
                            widget=widget,
                            db_connection_id=request.db_connection_id,
                            llm_config=llm_config,
                        )
                except Exception as e:
                    logger.warning(f"Failed to generate query for {widget.name}: {e}")

        # Save dashboard
        dashboard = self.repository.create(dashboard)

        return dashboard

    async def create_from_nl_stream(
        self,
        request: CreateDashboardRequest,
        llm_config: Optional[LLMConfig] = None,
    ) -> AsyncIterator[StreamEvent]:
        """
        Create dashboard with streaming progress updates.

        Yields:
            StreamEvent objects for each step
        """
        yield StreamEvent("started", {"message": "Starting dashboard generation..."})

        # Plan
        yield StreamEvent("planning", {"message": "Planning dashboard layout..."})
        plan = await self.planner.plan_dashboard(
            user_request=request.request,
            db_connection_id=request.db_connection_id,
            llm_config=llm_config,
        )
        yield StreamEvent(
            "planned",
            {
                "message": f"Planned {len(plan.widgets)} widgets",
                "widget_count": len(plan.widgets),
            },
        )

        # Convert and layout
        widgets = self.planner.plan_to_widgets(plan)
        widgets = self.layout_service.auto_layout(widgets)

        # Create dashboard
        dashboard = Dashboard(
            name=request.name or plan.dashboard_name,
            description=plan.description,
            db_connection_id=request.db_connection_id,
            layout=DashboardLayout(widgets=widgets),
            theme=request.theme,
        )

        # Get database connection for SQL validation
        db_connection = self.db_conn_repo.find_by_id(request.db_connection_id)
        database = None
        if db_connection:
            database = SQLDatabase.get_sql_engine(db_connection)

        # Generate and validate queries
        for i, widget in enumerate(dashboard.layout.widgets):
            yield StreamEvent(
                "widget_query",
                {
                    "message": f"Generating query for {widget.name}",
                    "widget_index": i,
                    "widget_name": widget.name,
                },
            )

            if widget.query_description and not widget.query:
                try:
                    if database:
                        # Use validation with auto-fix
                        sql, error = await self.widget_service.generate_and_validate_query(
                            widget=widget,
                            db_connection_id=request.db_connection_id,
                            database=database,
                            llm_config=llm_config,
                            max_retries=3,
                        )
                        widget.query = sql
                        if error:
                            yield StreamEvent(
                                "widget_error",
                                {
                                    "message": f"SQL validation failed for {widget.name}",
                                    "widget_name": widget.name,
                                    "error": error,
                                },
                            )
                    else:
                        # Fallback: generate without validation
                        widget.query = await self.widget_service.generate_widget_query(
                            widget=widget,
                            db_connection_id=request.db_connection_id,
                            llm_config=llm_config,
                        )
                except Exception as e:
                    logger.warning(f"Query generation failed: {e}")

        # Save
        dashboard = self.repository.create(dashboard)

        yield StreamEvent(
            "completed",
            {
                "message": "Dashboard created successfully",
                "dashboard_id": dashboard.id,
                "dashboard_name": dashboard.name,
            },
        )

    def get(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get dashboard by ID."""
        return self.repository.get(dashboard_id)

    def list_by_connection(self, db_connection_id: str) -> list[DashboardSummary]:
        """List dashboards for a database connection."""
        dashboards = self.repository.list_by_connection(db_connection_id)
        return [
            DashboardSummary(
                id=d.id,
                name=d.name,
                description=d.description,
                widget_count=len(d.layout.widgets),
                created_at=d.created_at,
                updated_at=d.updated_at,
                is_public=d.is_public,
            )
            for d in dashboards
        ]

    def update(
        self, dashboard_id: str, request: UpdateDashboardRequest
    ) -> Optional[Dashboard]:
        """Update dashboard metadata."""
        dashboard = self.repository.get(dashboard_id)
        if not dashboard:
            return None

        if request.name is not None:
            dashboard.name = request.name
        if request.description is not None:
            dashboard.description = request.description
        if request.theme is not None:
            dashboard.theme = request.theme
        if request.refresh_interval is not None:
            dashboard.refresh_interval = request.refresh_interval
        if request.is_public is not None:
            dashboard.is_public = request.is_public

        return self.repository.update(dashboard)

    def delete(self, dashboard_id: str) -> bool:
        """Delete a dashboard."""
        return self.repository.delete(dashboard_id)

    # =========================================================================
    # Dashboard Execution
    # =========================================================================

    async def execute(
        self,
        dashboard_id: str,
    ) -> DashboardRun:
        """
        Execute all widgets in a dashboard.

        Args:
            dashboard_id: Dashboard ID to execute

        Returns:
            DashboardRun with results
        """
        dashboard = self.repository.get(dashboard_id)
        if not dashboard:
            raise DashboardNotFoundError(f"Dashboard not found: {dashboard_id}")

        start_time = time.time()

        run = DashboardRun(
            dashboard_id=dashboard_id,
            status="running",
        )

        try:
            # Get database connection
            db_connection = self.db_conn_repo.find_by_id(dashboard.db_connection_id)
            if not db_connection:
                raise DashboardExecutionError(
                    f"Database connection not found: {dashboard.db_connection_id}"
                )

            # Create SQLDatabase instance
            database = SQLDatabase.get_sql_engine(db_connection)

            # Execute each widget
            for widget in dashboard.layout.widgets:
                try:
                    result = await self.widget_service.execute_widget(
                        widget=widget,
                        db_connection_id=dashboard.db_connection_id,
                        database=database,
                        theme=dashboard.theme,
                    )
                    run.widget_results[widget.id] = result
                except Exception as e:
                    logger.error(f"Widget {widget.name} execution failed: {e}")
                    run.widget_results[widget.id] = WidgetResult(
                        widget_id=widget.id,
                        status="failed",
                        error=str(e),
                    )

            run.status = "completed"

        except Exception as e:
            logger.error(f"Dashboard execution failed: {e}")
            run.status = "failed"
            run.error = str(e)

        run.total_execution_time_ms = int((time.time() - start_time) * 1000)
        return run

    async def execute_stream(
        self,
        dashboard_id: str,
    ) -> AsyncIterator[StreamEvent]:
        """
        Execute dashboard with streaming progress.

        Yields:
            StreamEvent for each widget execution
        """
        dashboard = self.repository.get(dashboard_id)
        if not dashboard:
            yield StreamEvent("error", {"message": f"Dashboard not found: {dashboard_id}"})
            return

        yield StreamEvent("started", {"message": "Starting execution..."})

        # Get database
        db_connection = self.db_conn_repo.find_by_id(dashboard.db_connection_id)
        if not db_connection:
            yield StreamEvent("error", {"message": "Database connection not found"})
            return

        database = SQLDatabase.get_sql_engine(db_connection)

        widget_results = {}
        total_widgets = len(dashboard.layout.widgets)

        for i, widget in enumerate(dashboard.layout.widgets):
            yield StreamEvent(
                "widget_executing",
                {
                    "widget_id": widget.id,
                    "widget_name": widget.name,
                    "progress": i / total_widgets,
                },
            )

            try:
                result = await self.widget_service.execute_widget(
                    widget=widget,
                    db_connection_id=dashboard.db_connection_id,
                    database=database,
                    theme=dashboard.theme,
                )
                widget_results[widget.id] = result

                yield StreamEvent(
                    "widget_completed",
                    {
                        "widget_id": widget.id,
                        "widget_name": widget.name,
                        "status": result.status,
                        "row_count": result.row_count,
                    },
                )
            except Exception as e:
                yield StreamEvent(
                    "widget_failed",
                    {
                        "widget_id": widget.id,
                        "widget_name": widget.name,
                        "error": str(e),
                    },
                )

        yield StreamEvent(
            "completed",
            {
                "message": "Dashboard execution completed",
                "widget_results": {k: v.status for k, v in widget_results.items()},
            },
        )

    # =========================================================================
    # Dashboard Rendering
    # =========================================================================

    async def render(
        self,
        dashboard_id: str,
        format: str = "html",
        execute: bool = True,
    ) -> str | dict:
        """
        Render dashboard to specified format.

        Args:
            dashboard_id: Dashboard ID
            format: Output format (html, json)
            execute: Whether to execute widgets first

        Returns:
            Rendered output (HTML string or JSON dict)
        """
        dashboard = self.repository.get(dashboard_id)
        if not dashboard:
            raise DashboardNotFoundError(f"Dashboard not found: {dashboard_id}")

        try:
            # Execute if needed
            if execute:
                run = await self.execute(dashboard_id)
                widget_results = run.widget_results
            else:
                widget_results = {}

            # Render
            if format == "json":
                return await self.renderer.render_to_json(dashboard, widget_results)
            else:
                return await self.renderer.render_to_html(dashboard, widget_results)
        except DashboardNotFoundError:
            raise
        except Exception as e:
            raise DashboardRenderError(f"Failed to render dashboard: {e}") from e

    # =========================================================================
    # Widget Management
    # =========================================================================

    def add_widget(self, dashboard_id: str, widget: Widget) -> Optional[Dashboard]:
        """Add a widget to a dashboard."""
        dashboard = self.repository.get(dashboard_id)
        if not dashboard:
            return None

        dashboard.layout = self.layout_service.add_widget_to_layout(
            dashboard.layout, widget
        )
        return self.repository.update(dashboard)

    def update_widget(
        self, dashboard_id: str, widget_id: str, widget: Widget
    ) -> Optional[Dashboard]:
        """Update a widget in a dashboard."""
        dashboard = self.repository.get(dashboard_id)
        if not dashboard:
            return None

        # Find and replace widget
        for i, w in enumerate(dashboard.layout.widgets):
            if w.id == widget_id:
                widget.id = widget_id  # Preserve ID
                dashboard.layout.widgets[i] = widget
                break

        return self.repository.update(dashboard)

    def remove_widget(
        self, dashboard_id: str, widget_id: str
    ) -> Optional[Dashboard]:
        """Remove a widget from a dashboard."""
        dashboard = self.repository.get(dashboard_id)
        if not dashboard:
            return None

        dashboard.layout = self.layout_service.remove_widget_from_layout(
            dashboard.layout, widget_id, reflow=True
        )
        return self.repository.update(dashboard)

    # =========================================================================
    # Sharing
    # =========================================================================

    def share(self, dashboard_id: str, base_url: str = "") -> Optional[ShareResponse]:
        """Generate a shareable link for a dashboard."""
        try:
            token = self.repository.generate_share_token(dashboard_id)
            if not token:
                return None

            share_url = f"{base_url}/dashboards/shared/{token}"

            return ShareResponse(
                share_url=share_url,
                share_token=token,
            )
        except Exception as e:
            raise ShareTokenError(f"Failed to generate share token: {e}") from e

    def get_by_share_token(self, token: str) -> Optional[Dashboard]:
        """Get a dashboard by its share token."""
        try:
            return self.repository.get_by_share_token(token)
        except Exception as e:
            raise ShareTokenError(f"Failed to retrieve dashboard by share token: {e}") from e

    def revoke_share(self, dashboard_id: str) -> bool:
        """Revoke sharing for a dashboard."""
        try:
            return self.repository.revoke_share(dashboard_id)
        except Exception as e:
            raise ShareTokenError(f"Failed to revoke share token: {e}") from e

    # =========================================================================
    # Refinement
    # =========================================================================

    async def refine(
        self,
        dashboard_id: str,
        request: RefineDashboardRequest,
        llm_config: Optional[LLMConfig] = None,
    ) -> Optional[Dashboard]:
        """
        Refine a dashboard using natural language.

        Args:
            dashboard_id: Dashboard to refine
            request: RefineDashboardRequest with NL instruction
            llm_config: Optional LLM configuration

        Returns:
            Updated Dashboard
        """
        dashboard = self.repository.get(dashboard_id)
        if not dashboard:
            return None

        # Get refined plan
        current_config = {
            "dashboard_name": dashboard.name,
            "description": dashboard.description,
            "widgets": [
                {
                    "name": w.name,
                    "widget_type": w.widget_type.value,
                    "size": w.size.value,
                    "query": w.query,
                    "query_description": w.query_description,
                }
                for w in dashboard.layout.widgets
            ],
        }

        plan = await self.planner.refine_dashboard(
            current_dashboard=current_config,
            refinement_request=request.refinement,
            db_connection_id=dashboard.db_connection_id,
            llm_config=llm_config,
        )

        # Update dashboard with refined plan
        dashboard.name = plan.dashboard_name
        dashboard.description = plan.description

        # Convert and layout new widgets
        widgets = self.planner.plan_to_widgets(plan)
        widgets = self.layout_service.auto_layout(widgets)
        dashboard.layout = DashboardLayout(widgets=widgets)

        # Generate queries for new widgets
        for widget in dashboard.layout.widgets:
            if widget.query_description and not widget.query:
                try:
                    widget.query = await self.widget_service.generate_widget_query(
                        widget=widget,
                        db_connection_id=dashboard.db_connection_id,
                        llm_config=llm_config,
                    )
                except Exception as e:
                    logger.warning(f"Query generation failed: {e}")

        return self.repository.update(dashboard)


__all__ = ["DashboardService", "StreamEvent"]
