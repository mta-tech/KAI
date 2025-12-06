"""Tests for MDL repository."""
import pytest
from unittest.mock import MagicMock
from datetime import datetime

from app.modules.mdl.repositories import MDLRepository
from app.modules.mdl.models import (
    MDLManifest,
    MDLModel,
    MDLColumn,
    MDLRelationship,
    JoinType,
)


@pytest.fixture
def mock_storage():
    """Mock storage with sync methods."""
    storage = MagicMock()
    storage.insert_one = MagicMock(return_value="mdl_123")
    storage.find_by_id = MagicMock(return_value=None)
    storage.find = MagicMock(return_value=[])
    storage.update_or_create = MagicMock()
    storage.delete_by_id = MagicMock()
    return storage


@pytest.fixture
def repository(mock_storage):
    return MDLRepository(storage=mock_storage)


@pytest.fixture
def sample_manifest():
    """Sample MDL manifest for testing."""
    return MDLManifest(
        id="mdl_123",
        db_connection_id="conn_456",
        name="Test Analytics",
        catalog="test_catalog",
        schema="public",
        models=[
            MDLModel(
                name="orders",
                columns=[
                    MDLColumn(name="id", type="INTEGER"),
                    MDLColumn(name="customer_id", type="INTEGER"),
                ],
                primary_key="id",
            )
        ],
        relationships=[
            MDLRelationship(
                name="orders_customers",
                models=["orders", "customers"],
                join_type=JoinType.MANY_TO_ONE,
                condition="orders.customer_id = customers.id",
            )
        ],
    )


class TestMDLRepository:
    """Tests for MDLRepository."""

    @pytest.mark.asyncio
    async def test_create_manifest(self, repository, mock_storage):
        """Should create manifest and return ID."""
        manifest_id = await repository.create(
            db_connection_id="conn_456",
            name="New MDL",
            catalog="test",
            schema="public",
        )

        assert manifest_id is not None
        assert manifest_id.startswith("mdl_")
        mock_storage.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_manifest_with_models(self, repository, mock_storage):
        """Should create manifest with models."""
        models = [
            MDLModel(
                name="users",
                columns=[MDLColumn(name="id", type="INTEGER")],
            )
        ]

        manifest_id = await repository.create(
            db_connection_id="conn_456",
            name="With Models",
            catalog="test",
            schema="public",
            models=models,
        )

        assert manifest_id is not None
        call_args = mock_storage.insert_one.call_args
        assert len(call_args[0][1]["models"]) == 1

    @pytest.mark.asyncio
    async def test_get_manifest_returns_none_when_not_found(self, repository, mock_storage):
        """Should return None when manifest doesn't exist."""
        mock_storage.find_by_id.return_value = None

        manifest = await repository.get("nonexistent")

        assert manifest is None

    @pytest.mark.asyncio
    async def test_get_manifest_returns_manifest_when_found(self, repository, mock_storage):
        """Should return MDLManifest when found."""
        mock_storage.find_by_id.return_value = {
            "id": "mdl_123",
            "db_connection_id": "conn_456",
            "name": "Test",
            "catalog": "test",
            "schema": "public",
            "models": [],
            "relationships": [],
            "metrics": [],
            "views": [],
            "enum_definitions": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": None,
        }

        manifest = await repository.get("mdl_123")

        assert manifest is not None
        assert manifest.id == "mdl_123"
        assert manifest.catalog == "test"

    @pytest.mark.asyncio
    async def test_get_manifest_by_db_connection(self, repository, mock_storage):
        """Should get manifest by database connection ID."""
        mock_storage.find.return_value = [
            {
                "id": "mdl_123",
                "db_connection_id": "conn_456",
                "name": "Test",
                "catalog": "test",
                "schema": "public",
                "models": [],
                "relationships": [],
                "metrics": [],
                "views": [],
                "enum_definitions": [],
                "created_at": datetime.now().isoformat(),
            }
        ]

        manifest = await repository.get_by_db_connection("conn_456")

        assert manifest is not None
        assert manifest.db_connection_id == "conn_456"

    @pytest.mark.asyncio
    async def test_list_manifests(self, repository, mock_storage):
        """Should list all manifests."""
        mock_storage.find.return_value = [
            {
                "id": "mdl_1",
                "db_connection_id": "conn_1",
                "name": "MDL 1",
                "catalog": "cat1",
                "schema": "public",
                "models": [],
                "relationships": [],
                "metrics": [],
                "views": [],
                "enum_definitions": [],
                "created_at": datetime.now().isoformat(),
            },
            {
                "id": "mdl_2",
                "db_connection_id": "conn_2",
                "name": "MDL 2",
                "catalog": "cat2",
                "schema": "main",
                "models": [],
                "relationships": [],
                "metrics": [],
                "views": [],
                "enum_definitions": [],
                "created_at": datetime.now().isoformat(),
            },
        ]

        manifests = await repository.list()

        assert len(manifests) == 2
        assert manifests[0].id == "mdl_1"
        assert manifests[1].id == "mdl_2"

    @pytest.mark.asyncio
    async def test_list_manifests_by_db_connection(self, repository, mock_storage):
        """Should list manifests filtered by db_connection_id."""
        mock_storage.find.return_value = [
            {
                "id": "mdl_1",
                "db_connection_id": "conn_456",
                "name": "MDL 1",
                "catalog": "cat1",
                "schema": "public",
                "models": [],
                "relationships": [],
                "metrics": [],
                "views": [],
                "enum_definitions": [],
                "created_at": datetime.now().isoformat(),
            }
        ]

        manifests = await repository.list(db_connection_id="conn_456")

        assert len(manifests) == 1
        assert manifests[0].db_connection_id == "conn_456"
        mock_storage.find.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_manifest(self, repository, mock_storage, sample_manifest):
        """Should update manifest."""
        await repository.update(sample_manifest)

        mock_storage.update_or_create.assert_called_once()
        call_args = mock_storage.update_or_create.call_args
        assert call_args[0][1] == {"id": "mdl_123"}

    @pytest.mark.asyncio
    async def test_delete_manifest(self, repository, mock_storage):
        """Should delete manifest."""
        await repository.delete("mdl_123")

        mock_storage.delete_by_id.assert_called_once()
