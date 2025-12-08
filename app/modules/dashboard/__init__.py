"""Dashboard module for BI dashboard generation from natural language."""
from app.modules.dashboard.models import (
    AggregationType,
    ChartType,
    ChartWidgetConfig,
    CreateDashboardRequest,
    Dashboard,
    DashboardLayout,
    DashboardPlan,
    DashboardRun,
    DashboardSummary,
    DashboardTheme,
    FilterWidgetConfig,
    KPIWidgetConfig,
    RefineDashboardRequest,
    ShareResponse,
    TableWidgetConfig,
    TextWidgetConfig,
    UpdateDashboardRequest,
    Widget,
    WidgetResult,
    WidgetSize,
    WidgetType,
)
from app.modules.dashboard.repositories import DashboardRepository
from app.modules.dashboard.services import (
    DashboardPlannerService,
    DashboardRendererService,
    DashboardService,
    LayoutService,
    StreamEvent,
    THEMES,
    WidgetService,
)
from app.modules.dashboard.api import create_dashboard_router

__all__ = [
    # Models
    "AggregationType",
    "ChartType",
    "ChartWidgetConfig",
    "CreateDashboardRequest",
    "Dashboard",
    "DashboardLayout",
    "DashboardPlan",
    "DashboardRun",
    "DashboardSummary",
    "DashboardTheme",
    "FilterWidgetConfig",
    "KPIWidgetConfig",
    "RefineDashboardRequest",
    "ShareResponse",
    "TableWidgetConfig",
    "TextWidgetConfig",
    "UpdateDashboardRequest",
    "Widget",
    "WidgetResult",
    "WidgetSize",
    "WidgetType",
    # Repository
    "DashboardRepository",
    # Services
    "DashboardPlannerService",
    "DashboardRendererService",
    "DashboardService",
    "LayoutService",
    "StreamEvent",
    "THEMES",
    "WidgetService",
    # API
    "create_dashboard_router",
]
