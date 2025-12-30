"""Integration tests for dashboard API structured error responses.

These tests verify that API endpoints return structured error responses
with correct error codes when module-specific exceptions are raised.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.dashboard.api import create_dashboard_router
from app.modules.dashboard.exceptions import (
    DashboardCreationError,
    DashboardExecutionError,
    DashboardNotFoundError,
    DashboardRenderError,
    ShareTokenError,
)


@pytest.fixture
def mock_service():
    """Create mock dashboard service."""
    service = MagicMock()
    # Set up default successful returns
    service.create_from_nl = AsyncMock()
    service.get = MagicMock(return_value=None)
    service.update = MagicMock(return_value=None)
    service.delete = MagicMock(return_value=False)
    service.list_by_connection = MagicMock(return_value=[])
    service.execute = AsyncMock()
    service.render = AsyncMock()
    service.add_widget = MagicMock(return_value=None)
    service.update_widget = MagicMock(return_value=None)
    service.remove_widget = MagicMock(return_value=None)
    service.share = MagicMock(return_value=None)
    service.revoke_share = MagicMock(return_value=False)
    service.get_by_share_token = MagicMock(return_value=None)
    service.refine = AsyncMock()

    # Mock renderer for theme listing
    service.renderer = MagicMock()
    service.renderer.get_available_themes = MagicMock(return_value=["default", "dark"])

    return service


@pytest.fixture
def app(mock_service):
    """Create FastAPI app with dashboard router."""
    app = FastAPI()
    router = create_dashboard_router(mock_service)
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


class TestCreateDashboardErrors:
    """Tests for POST / (create dashboard) endpoint error responses."""

    def test_dashboard_creation_error_returns_structured_response(
        self, client, mock_service
    ):
        """Should return structured error when DashboardCreationError is raised."""
        mock_service.create_from_nl.side_effect = DashboardCreationError(
            "Failed to create dashboard from request"
        )

        response = client.post(
            "/api/v2/dashboards/",
            json={
                "db_connection_id": "conn_123",
                "request": "Create a sales dashboard",
            },
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_creation_failed"
        assert "Failed to create dashboard" in body["message"]
        assert body["detail"]["request"] == "Create a sales dashboard"

    def test_generic_exception_wrapped_as_creation_error(self, client, mock_service):
        """Should wrap generic exception as DashboardCreationError."""
        mock_service.create_from_nl.side_effect = RuntimeError("Unexpected error")

        response = client.post(
            "/api/v2/dashboards/",
            json={
                "db_connection_id": "conn_123",
                "request": "Create a sales dashboard",
            },
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_creation_failed"
        assert "Dashboard creation failed" in body["message"]


class TestGetDashboardErrors:
    """Tests for GET /{dashboard_id} endpoint error responses."""

    def test_dashboard_not_found_returns_structured_response(
        self, client, mock_service
    ):
        """Should return structured error when dashboard not found."""
        mock_service.get.return_value = None

        response = client.get("/api/v2/dashboards/nonexistent_id")

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_not_found"
        assert "not found" in body["message"].lower()
        assert body["detail"]["dashboard_id"] == "nonexistent_id"


class TestUpdateDashboardErrors:
    """Tests for PUT /{dashboard_id} endpoint error responses."""

    def test_update_not_found_returns_structured_response(self, client, mock_service):
        """Should return structured error when updating non-existent dashboard."""
        mock_service.update.return_value = None

        response = client.put(
            "/api/v2/dashboards/nonexistent_id",
            json={"name": "Updated Name"},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_not_found"
        assert body["detail"]["dashboard_id"] == "nonexistent_id"


class TestDeleteDashboardErrors:
    """Tests for DELETE /{dashboard_id} endpoint error responses."""

    def test_delete_not_found_returns_structured_response(self, client, mock_service):
        """Should return structured error when deleting non-existent dashboard."""
        mock_service.delete.return_value = False

        response = client.delete("/api/v2/dashboards/nonexistent_id")

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_not_found"
        assert body["detail"]["dashboard_id"] == "nonexistent_id"


class TestExecuteDashboardErrors:
    """Tests for POST /{dashboard_id}/execute endpoint error responses."""

    def test_dashboard_not_found_during_execute(self, client, mock_service):
        """Should return structured error when dashboard not found during execute."""
        mock_service.execute.side_effect = ValueError("Dashboard not found")

        response = client.post("/api/v2/dashboards/nonexistent_id/execute")

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_not_found"
        assert body["detail"]["dashboard_id"] == "nonexistent_id"

    def test_dashboard_execution_error_returns_structured_response(
        self, client, mock_service
    ):
        """Should return structured error when DashboardExecutionError is raised."""
        mock_service.execute.side_effect = DashboardExecutionError(
            "No database connection available"
        )

        response = client.post("/api/v2/dashboards/dash_123/execute")

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_execution_failed"
        assert "No database connection" in body["message"]
        assert body["detail"]["dashboard_id"] == "dash_123"

    def test_generic_exception_wrapped_as_execution_error(self, client, mock_service):
        """Should wrap generic exception as DashboardExecutionError."""
        mock_service.execute.side_effect = RuntimeError("Unexpected execution error")

        response = client.post("/api/v2/dashboards/dash_123/execute")

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_execution_failed"
        assert "Dashboard execution failed" in body["message"]


class TestRenderDashboardErrors:
    """Tests for GET /{dashboard_id}/render endpoint error responses."""

    def test_render_not_found_returns_structured_response(self, client, mock_service):
        """Should return structured error when dashboard not found during render."""
        mock_service.render.side_effect = ValueError("Dashboard not found")

        response = client.get("/api/v2/dashboards/nonexistent_id/render")

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_not_found"
        assert body["detail"]["dashboard_id"] == "nonexistent_id"

    def test_dashboard_render_error_returns_structured_response(
        self, client, mock_service
    ):
        """Should return structured error when DashboardRenderError is raised."""
        mock_service.render.side_effect = DashboardRenderError(
            "Failed to render dashboard to HTML"
        )

        response = client.get("/api/v2/dashboards/dash_123/render?format=html")

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_render_failed"
        assert "Failed to render" in body["message"]
        assert body["detail"]["format"] == "html"

    def test_generic_exception_wrapped_as_render_error(self, client, mock_service):
        """Should wrap generic exception as DashboardRenderError."""
        mock_service.render.side_effect = RuntimeError("Unexpected render error")

        response = client.get("/api/v2/dashboards/dash_123/render")

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_render_failed"
        assert "Dashboard render failed" in body["message"]


class TestWidgetErrors:
    """Tests for widget management endpoint error responses."""

    def test_add_widget_not_found_returns_structured_response(
        self, client, mock_service
    ):
        """Should return structured error when adding widget to non-existent dashboard."""
        mock_service.add_widget.return_value = None

        response = client.post(
            "/api/v2/dashboards/nonexistent_id/widgets",
            json={
                "id": "widget_1",
                "type": "kpi",
                "title": "Test Widget",
                "query": "SELECT 1",
                "position": {"x": 0, "y": 0, "w": 4, "h": 2},
            },
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_not_found"
        assert body["detail"]["dashboard_id"] == "nonexistent_id"

    def test_update_widget_not_found_returns_structured_response(
        self, client, mock_service
    ):
        """Should return structured error when updating widget in non-existent dashboard."""
        mock_service.update_widget.return_value = None

        response = client.put(
            "/api/v2/dashboards/nonexistent_id/widgets/widget_1",
            json={
                "id": "widget_1",
                "type": "kpi",
                "title": "Updated Widget",
                "query": "SELECT 1",
                "position": {"x": 0, "y": 0, "w": 4, "h": 2},
            },
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_not_found"
        assert body["detail"]["dashboard_id"] == "nonexistent_id"
        assert body["detail"]["widget_id"] == "widget_1"

    def test_remove_widget_not_found_returns_structured_response(
        self, client, mock_service
    ):
        """Should return structured error when removing widget from non-existent dashboard."""
        mock_service.remove_widget.return_value = None

        response = client.delete("/api/v2/dashboards/nonexistent_id/widgets/widget_1")

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_not_found"
        assert body["detail"]["dashboard_id"] == "nonexistent_id"
        assert body["detail"]["widget_id"] == "widget_1"


class TestShareDashboardErrors:
    """Tests for sharing endpoint error responses."""

    def test_share_not_found_returns_structured_response(self, client, mock_service):
        """Should return structured error when sharing non-existent dashboard."""
        mock_service.share.return_value = None

        response = client.post("/api/v2/dashboards/nonexistent_id/share")

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_not_found"
        assert body["detail"]["dashboard_id"] == "nonexistent_id"

    def test_revoke_share_not_found_returns_structured_response(
        self, client, mock_service
    ):
        """Should return structured error when revoking share for non-existent dashboard."""
        mock_service.revoke_share.return_value = False

        response = client.delete("/api/v2/dashboards/nonexistent_id/share")

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_not_found"
        assert body["detail"]["dashboard_id"] == "nonexistent_id"


class TestSharedDashboardErrors:
    """Tests for /shared/{share_token} endpoint error responses."""

    def test_invalid_share_token_returns_structured_response(
        self, client, mock_service
    ):
        """Should return structured error when share token is invalid."""
        mock_service.get_by_share_token.return_value = None

        response = client.get("/api/v2/dashboards/shared/invalid_token")

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "share_token_error"
        assert "not found or not shared" in body["message"].lower()
        assert body["detail"]["share_token"] == "invalid_token"


class TestRefineDashboardErrors:
    """Tests for POST /{dashboard_id}/refine endpoint error responses."""

    def test_refine_not_found_returns_structured_response(self, client, mock_service):
        """Should return structured error when refining non-existent dashboard."""
        mock_service.refine.return_value = None

        response = client.post(
            "/api/v2/dashboards/nonexistent_id/refine",
            json={"request": "Add a pie chart"},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_not_found"
        assert body["detail"]["dashboard_id"] == "nonexistent_id"

    def test_dashboard_creation_error_during_refine(self, client, mock_service):
        """Should return structured error when DashboardCreationError during refine."""
        mock_service.refine.side_effect = DashboardCreationError(
            "Failed to parse refinement request"
        )

        response = client.post(
            "/api/v2/dashboards/dash_123/refine",
            json={"request": "Add a pie chart"},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_creation_failed"
        assert "Failed to parse" in body["message"]
        assert body["detail"]["request"] == "Add a pie chart"

    def test_generic_exception_wrapped_during_refine(self, client, mock_service):
        """Should wrap generic exception as DashboardCreationError during refine."""
        mock_service.refine.side_effect = RuntimeError("Unexpected error")

        response = client.post(
            "/api/v2/dashboards/dash_123/refine",
            json={"request": "Add a pie chart"},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_creation_failed"
        assert "Dashboard refinement failed" in body["message"]


class TestErrorResponseStructure:
    """Tests verifying the structure of error responses."""

    def test_error_response_has_required_fields(self, client, mock_service):
        """Error responses should have error_code, message, and detail fields."""
        mock_service.get.return_value = None

        response = client.get("/api/v2/dashboards/test_id")

        assert response.status_code == 400
        body = response.json()

        # Verify required fields exist
        assert "error_code" in body
        assert "message" in body
        assert "detail" in body
        assert "description" in body

    def test_error_response_with_description(self, client, mock_service):
        """Error responses should include description when provided."""
        error_with_desc = DashboardExecutionError(
            "Execution failed",
            description="Ensure database connection is active",
        )
        mock_service.execute.side_effect = error_with_desc

        response = client.post("/api/v2/dashboards/dash_123/execute")

        assert response.status_code == 400
        body = response.json()
        assert body["description"] == "Ensure database connection is active"


class TestErrorCodeMapping:
    """Tests verifying error codes match ERROR_MAPPING."""

    def test_dashboard_not_found_error_code(self, client, mock_service):
        """DashboardNotFoundError should map to 'dashboard_not_found'."""
        mock_service.get.return_value = None

        response = client.get("/api/v2/dashboards/test_id")

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_not_found"

    def test_dashboard_creation_error_code(self, client, mock_service):
        """DashboardCreationError should map to 'dashboard_creation_failed'."""
        mock_service.create_from_nl.side_effect = DashboardCreationError("Creation failed")

        response = client.post(
            "/api/v2/dashboards/",
            json={"db_connection_id": "conn_123", "request": "Test"},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_creation_failed"

    def test_dashboard_execution_error_code(self, client, mock_service):
        """DashboardExecutionError should map to 'dashboard_execution_failed'."""
        mock_service.execute.side_effect = DashboardExecutionError("Execution failed")

        response = client.post("/api/v2/dashboards/dash_123/execute")

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_execution_failed"

    def test_dashboard_render_error_code(self, client, mock_service):
        """DashboardRenderError should map to 'dashboard_render_failed'."""
        mock_service.render.side_effect = DashboardRenderError("Render failed")

        response = client.get("/api/v2/dashboards/dash_123/render")

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "dashboard_render_failed"

    def test_share_token_error_code(self, client, mock_service):
        """ShareTokenError should map to 'share_token_error'."""
        mock_service.get_by_share_token.return_value = None

        response = client.get("/api/v2/dashboards/shared/invalid_token")

        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "share_token_error"
