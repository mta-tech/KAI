"""Tests for MDL API endpoints."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.mdl.api import create_mdl_router
from app.modules.mdl.models import (
    MDLManifest,
    MDLModel,
    MDLColumn,
    MDLRelationship,
    JoinType,
)


@pytest.fixture
def mock_service():
    """Mock MDL service."""
    service = MagicMock()
    service.create_manifest = AsyncMock(return_value="mdl_123")
    service.get_manifest = AsyncMock(return_value=None)
    service.get_manifest_by_db_connection = AsyncMock(return_value=None)
    service.list_manifests = AsyncMock(return_value=[])
    service.update_manifest = AsyncMock()
    service.delete_manifest = AsyncMock()
    service.build_from_database = AsyncMock(return_value="mdl_456")
    service.export_mdl_json = AsyncMock(return_value={"catalog": "test", "schema": "public"})
    service.validate_manifest = AsyncMock(return_value=(True, []))
    service.add_model = AsyncMock()
    service.remove_model = AsyncMock()
    service.add_relationship = AsyncMock()
    service.remove_relationship = AsyncMock()
    return service


@pytest.fixture
def app(mock_service):
    """Create FastAPI app with MDL router."""
    app = FastAPI()
    router = create_mdl_router(mock_service)
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_manifest():
    """Sample manifest for testing."""
    return MDLManifest(
        id="mdl_123",
        db_connection_id="conn_456",
        name="Test MDL",
        catalog="test",
        schema="public",
        models=[
            MDLModel(
                name="users",
                columns=[MDLColumn(name="id", type="INTEGER")],
                primary_key="id",
            )
        ],
        created_at=datetime.now().isoformat(),
    )


class TestMDLAPIEndpoints:
    """Tests for MDL API endpoints."""

    def test_create_manifest(self, client, mock_service):
        """Should create manifest via POST."""
        response = client.post(
            "/api/v1/mdl/manifests",
            json={
                "db_connection_id": "conn_456",
                "name": "New MDL",
                "catalog": "test",
                "schema": "public",
            },
        )

        assert response.status_code == 201
        assert response.json()["id"] == "mdl_123"
        mock_service.create_manifest.assert_called_once()

    def test_get_manifest(self, client, mock_service, sample_manifest):
        """Should get manifest by ID via GET."""
        mock_service.get_manifest.return_value = sample_manifest

        response = client.get("/api/v1/mdl/manifests/mdl_123")

        assert response.status_code == 200
        assert response.json()["id"] == "mdl_123"
        assert response.json()["catalog"] == "test"

    def test_get_manifest_not_found(self, client, mock_service):
        """Should return 404 when manifest not found."""
        mock_service.get_manifest.return_value = None

        response = client.get("/api/v1/mdl/manifests/nonexistent")

        assert response.status_code == 404

    def test_list_manifests(self, client, mock_service, sample_manifest):
        """Should list manifests via GET."""
        mock_service.list_manifests.return_value = [sample_manifest]

        response = client.get("/api/v1/mdl/manifests")

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == "mdl_123"

    def test_list_manifests_by_db_connection(self, client, mock_service, sample_manifest):
        """Should filter manifests by db_connection_id."""
        mock_service.list_manifests.return_value = [sample_manifest]

        response = client.get("/api/v1/mdl/manifests?db_connection_id=conn_456")

        assert response.status_code == 200
        mock_service.list_manifests.assert_called_once()

    def test_delete_manifest(self, client, mock_service):
        """Should delete manifest via DELETE."""
        response = client.delete("/api/v1/mdl/manifests/mdl_123")

        assert response.status_code == 204
        mock_service.delete_manifest.assert_called_once_with("mdl_123")

    def test_build_from_database(self, client, mock_service):
        """Should build manifest from database via POST."""
        response = client.post(
            "/api/v1/mdl/manifests/build",
            json={
                "db_connection_id": "conn_456",
                "name": "Built MDL",
                "catalog": "test",
                "schema": "public",
            },
        )

        assert response.status_code == 201
        assert response.json()["id"] == "mdl_456"
        mock_service.build_from_database.assert_called_once()

    def test_export_mdl_json(self, client, mock_service, sample_manifest):
        """Should export manifest as MDL JSON via GET."""
        mock_service.get_manifest.return_value = sample_manifest

        response = client.get("/api/v1/mdl/manifests/mdl_123/export")

        assert response.status_code == 200
        assert response.json()["catalog"] == "test"
        mock_service.export_mdl_json.assert_called_once_with("mdl_123")

    def test_add_model(self, client, mock_service, sample_manifest):
        """Should add model to manifest via POST."""
        mock_service.get_manifest.return_value = sample_manifest

        response = client.post(
            "/api/v1/mdl/manifests/mdl_123/models",
            json={
                "name": "orders",
                "columns": [{"name": "id", "type": "INTEGER"}],
            },
        )

        assert response.status_code == 201
        mock_service.add_model.assert_called_once()

    def test_remove_model(self, client, mock_service, sample_manifest):
        """Should remove model from manifest via DELETE."""
        mock_service.get_manifest.return_value = sample_manifest

        response = client.delete("/api/v1/mdl/manifests/mdl_123/models/orders")

        assert response.status_code == 204
        mock_service.remove_model.assert_called_once_with("mdl_123", "orders")

    def test_add_relationship(self, client, mock_service, sample_manifest):
        """Should add relationship to manifest via POST."""
        mock_service.get_manifest.return_value = sample_manifest

        response = client.post(
            "/api/v1/mdl/manifests/mdl_123/relationships",
            json={
                "name": "orders_users",
                "models": ["orders", "users"],
                "join_type": "MANY_TO_ONE",
                "condition": "orders.user_id = users.id",
            },
        )

        assert response.status_code == 201
        mock_service.add_relationship.assert_called_once()

    def test_remove_relationship(self, client, mock_service, sample_manifest):
        """Should remove relationship from manifest via DELETE."""
        mock_service.get_manifest.return_value = sample_manifest

        response = client.delete("/api/v1/mdl/manifests/mdl_123/relationships/orders_users")

        assert response.status_code == 204
        mock_service.remove_relationship.assert_called_once_with("mdl_123", "orders_users")
