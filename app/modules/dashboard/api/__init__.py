"""Dashboard API endpoints."""
from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse

from app.modules.dashboard.models import (
    CreateDashboardRequest,
    Dashboard,
    DashboardSummary,
    RefineDashboardRequest,
    ShareResponse,
    UpdateDashboardRequest,
    Widget,
)
from app.modules.dashboard.services import DashboardService


def create_dashboard_router(service: DashboardService) -> APIRouter:
    """Create FastAPI router for dashboard endpoints."""

    router = APIRouter(prefix="/api/v2/dashboards", tags=["Dashboards"])

    # =========================================================================
    # Dashboard CRUD
    # =========================================================================

    @router.post("/", response_model=Dashboard)
    async def create_dashboard(request: CreateDashboardRequest):
        """
        Create a dashboard from natural language request.

        The LLM will:
        1. Analyze the database schema
        2. Plan appropriate widgets (KPIs, charts, tables)
        3. Generate SQL queries for each widget
        4. Auto-layout the dashboard

        Example requests:
        - "Sales dashboard with revenue trends and top products"
        - "Customer analytics with segmentation and churn metrics"
        - "Executive dashboard showing key KPIs"
        """
        try:
            dashboard = await service.create_from_nl(request)
            return dashboard
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/generate/stream")
    async def create_dashboard_stream(request: CreateDashboardRequest):
        """
        Create dashboard with streaming progress updates.

        Returns Server-Sent Events (SSE) with progress:
        - planning: Dashboard layout being planned
        - widget_query: Query being generated for a widget
        - completed: Dashboard creation finished
        """

        async def event_generator():
            async for event in service.create_from_nl_stream(request):
                yield f"event: {event.type}\n"
                yield f"data: {json.dumps(event.data)}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
        )

    @router.get("/", response_model=list[DashboardSummary])
    async def list_dashboards(
        db_connection_id: str = Query(..., description="Database connection ID"),
    ):
        """List all dashboards for a database connection."""
        return service.list_by_connection(db_connection_id)

    @router.get("/{dashboard_id}", response_model=Dashboard)
    async def get_dashboard(dashboard_id: str):
        """Get dashboard definition by ID."""
        dashboard = service.get(dashboard_id)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        return dashboard

    @router.put("/{dashboard_id}", response_model=Dashboard)
    async def update_dashboard(dashboard_id: str, request: UpdateDashboardRequest):
        """Update dashboard metadata (name, description, theme, etc.)."""
        dashboard = service.update(dashboard_id, request)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        return dashboard

    @router.delete("/{dashboard_id}")
    async def delete_dashboard(dashboard_id: str):
        """Delete a dashboard."""
        if not service.delete(dashboard_id):
            raise HTTPException(status_code=404, detail="Dashboard not found")
        return {"message": "Dashboard deleted successfully"}

    # =========================================================================
    # Dashboard Execution & Rendering
    # =========================================================================

    @router.post("/{dashboard_id}/execute")
    async def execute_dashboard(dashboard_id: str):
        """
        Execute all widgets in a dashboard.

        Returns execution results for each widget including:
        - Query results data
        - KPI values and changes
        - Rendered chart HTML
        - Execution time
        """
        try:
            run = await service.execute(dashboard_id)
            return {
                "run_id": run.id,
                "status": run.status,
                "total_execution_time_ms": run.total_execution_time_ms,
                "widget_results": {
                    widget_id: {
                        "status": result.status,
                        "row_count": result.row_count,
                        "execution_time_ms": result.execution_time_ms,
                        "error": result.error,
                    }
                    for widget_id, result in run.widget_results.items()
                },
            }
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/{dashboard_id}/execute/stream")
    async def execute_dashboard_stream(dashboard_id: str):
        """
        Execute dashboard with streaming progress.

        Returns SSE events for each widget execution.
        """

        async def event_generator():
            async for event in service.execute_stream(dashboard_id):
                yield f"event: {event.type}\n"
                yield f"data: {json.dumps(event.data)}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
        )

    @router.get("/{dashboard_id}/render")
    async def render_dashboard(
        dashboard_id: str,
        format: str = Query(default="html", enum=["html", "json"]),
        execute: bool = Query(default=True, description="Execute widgets before rendering"),
    ):
        """
        Render dashboard to specified format.

        - html: Returns complete interactive HTML page
        - json: Returns JSON spec for frontend rendering
        """
        try:
            result = await service.render(dashboard_id, format=format, execute=execute)

            if format == "html":
                return HTMLResponse(content=result)
            else:
                return result
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # =========================================================================
    # Widget Management
    # =========================================================================

    @router.post("/{dashboard_id}/widgets", response_model=Dashboard)
    async def add_widget(dashboard_id: str, widget: Widget):
        """Add a widget to a dashboard."""
        dashboard = service.add_widget(dashboard_id, widget)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        return dashboard

    @router.put("/{dashboard_id}/widgets/{widget_id}", response_model=Dashboard)
    async def update_widget(dashboard_id: str, widget_id: str, widget: Widget):
        """Update a widget in a dashboard."""
        dashboard = service.update_widget(dashboard_id, widget_id, widget)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        return dashboard

    @router.delete("/{dashboard_id}/widgets/{widget_id}", response_model=Dashboard)
    async def remove_widget(dashboard_id: str, widget_id: str):
        """Remove a widget from a dashboard."""
        dashboard = service.remove_widget(dashboard_id, widget_id)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        return dashboard

    # =========================================================================
    # Sharing
    # =========================================================================

    @router.post("/{dashboard_id}/share", response_model=ShareResponse)
    async def share_dashboard(dashboard_id: str, request: Request):
        """
        Generate a shareable link for a dashboard.

        The dashboard will be marked as public and accessible via the share token.
        """
        base_url = str(request.base_url).rstrip("/")
        response = service.share(dashboard_id, base_url=base_url)
        if not response:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        return response

    @router.delete("/{dashboard_id}/share")
    async def revoke_share(dashboard_id: str):
        """Revoke sharing for a dashboard."""
        if not service.revoke_share(dashboard_id):
            raise HTTPException(status_code=404, detail="Dashboard not found")
        return {"message": "Share link revoked"}

    @router.get("/shared/{share_token}")
    async def get_shared_dashboard(share_token: str):
        """
        Access a shared dashboard (public endpoint).

        Returns rendered HTML dashboard.
        """
        dashboard = service.get_by_share_token(share_token)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found or not shared")

        # Render the dashboard
        try:
            html = await service.render(dashboard.id, format="html", execute=True)
            return HTMLResponse(content=html)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # =========================================================================
    # Refinement
    # =========================================================================

    @router.post("/{dashboard_id}/refine", response_model=Dashboard)
    async def refine_dashboard(dashboard_id: str, request: RefineDashboardRequest):
        """
        Refine a dashboard using natural language.

        Examples:
        - "Add a pie chart for sales by category"
        - "Remove the table and add more KPIs"
        - "Change the theme to dark mode"
        - "Add filtering by date range"
        """
        try:
            dashboard = await service.refine(dashboard_id, request)
            if not dashboard:
                raise HTTPException(status_code=404, detail="Dashboard not found")
            return dashboard
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # =========================================================================
    # Themes
    # =========================================================================

    @router.get("/meta/themes")
    async def list_themes():
        """List available dashboard themes."""
        return service.renderer.get_available_themes()

    return router


__all__ = ["create_dashboard_router"]
