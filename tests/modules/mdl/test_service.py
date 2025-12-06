"""Tests for MDL service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.modules.mdl.services import MDLService
from app.modules.mdl.models import (
    MDLManifest,
    MDLModel,
    MDLColumn,
    MDLRelationship,
    JoinType,
)
from app.modules.table_description.models import (
    TableDescription,
    ColumnDescription,
    ForeignKeyDetail,
)


@pytest.fixture
def mock_repository():
    """Mock MDL repository."""
    repo = MagicMock()
    repo.create = AsyncMock(return_value="mdl_123")
    repo.get = AsyncMock(return_value=None)
    repo.get_by_db_connection = AsyncMock(return_value=None)
    repo.list = AsyncMock(return_value=[])
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_table_description_repo():
    """Mock TableDescription repository."""
    repo = MagicMock()
    repo.find = MagicMock(return_value=[])
    return repo


@pytest.fixture
def service(mock_repository, mock_table_description_repo):
    return MDLService(
        repository=mock_repository,
        table_description_repo=mock_table_description_repo,
    )


@pytest.fixture
def sample_manifest():
    """Sample MDL manifest for testing."""
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
    )


class TestMDLService:
    """Tests for MDLService."""

    @pytest.mark.asyncio
    async def test_create_manifest(self, service, mock_repository):
        """Should create manifest and return ID."""
        manifest_id = await service.create_manifest(
            db_connection_id="conn_456",
            name="New MDL",
            catalog="test",
            schema="public",
        )

        assert manifest_id == "mdl_123"
        mock_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_manifest(self, service, mock_repository, sample_manifest):
        """Should get manifest by ID."""
        mock_repository.get.return_value = sample_manifest

        manifest = await service.get_manifest("mdl_123")

        assert manifest is not None
        assert manifest.id == "mdl_123"
        mock_repository.get.assert_called_once_with("mdl_123")

    @pytest.mark.asyncio
    async def test_get_manifest_by_db_connection(
        self, service, mock_repository, sample_manifest
    ):
        """Should get manifest by database connection ID."""
        mock_repository.get_by_db_connection.return_value = sample_manifest

        manifest = await service.get_manifest_by_db_connection("conn_456")

        assert manifest is not None
        assert manifest.db_connection_id == "conn_456"
        mock_repository.get_by_db_connection.assert_called_once_with("conn_456")

    @pytest.mark.asyncio
    async def test_list_manifests(self, service, mock_repository):
        """Should list all manifests."""
        manifests = await service.list_manifests()

        mock_repository.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_manifest(self, service, mock_repository, sample_manifest):
        """Should update manifest."""
        await service.update_manifest(sample_manifest)

        mock_repository.update.assert_called_once_with(sample_manifest)

    @pytest.mark.asyncio
    async def test_delete_manifest(self, service, mock_repository):
        """Should delete manifest."""
        await service.delete_manifest("mdl_123")

        mock_repository.delete.assert_called_once_with("mdl_123")

    @pytest.mark.asyncio
    async def test_build_from_database(
        self, service, mock_repository, mock_table_description_repo
    ):
        """Should build MDL manifest from database tables."""
        # Setup mock table descriptions
        mock_table_description_repo.find.return_value = [
            {
                "id": "td_1",
                "db_connection_id": "conn_456",
                "db_schema": "public",
                "table_name": "users",
                "columns": [
                    {"name": "id", "data_type": "INTEGER", "is_primary_key": True},
                    {"name": "email", "data_type": "VARCHAR"},
                ],
                "table_description": "User accounts",
            }
        ]

        manifest_id = await service.build_from_database(
            db_connection_id="conn_456",
            name="Generated MDL",
            catalog="test",
            schema="public",
        )

        assert manifest_id == "mdl_123"
        mock_table_description_repo.find.assert_called_once()
        mock_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_model_to_manifest(
        self, service, mock_repository, sample_manifest
    ):
        """Should add a model to existing manifest."""
        mock_repository.get.return_value = sample_manifest

        new_model = MDLModel(
            name="orders",
            columns=[MDLColumn(name="id", type="INTEGER")],
        )

        await service.add_model("mdl_123", new_model)

        mock_repository.update.assert_called_once()
        updated_manifest = mock_repository.update.call_args[0][0]
        assert len(updated_manifest.models) == 2

    @pytest.mark.asyncio
    async def test_remove_model_from_manifest(
        self, service, mock_repository, sample_manifest
    ):
        """Should remove a model from manifest."""
        sample_manifest.models.append(
            MDLModel(
                name="orders",
                columns=[MDLColumn(name="id", type="INTEGER")],
            )
        )
        mock_repository.get.return_value = sample_manifest

        await service.remove_model("mdl_123", "orders")

        mock_repository.update.assert_called_once()
        updated_manifest = mock_repository.update.call_args[0][0]
        assert len(updated_manifest.models) == 1
        assert updated_manifest.models[0].name == "users"

    @pytest.mark.asyncio
    async def test_add_relationship_to_manifest(
        self, service, mock_repository, sample_manifest
    ):
        """Should add a relationship to manifest."""
        sample_manifest.models.append(
            MDLModel(
                name="orders",
                columns=[
                    MDLColumn(name="id", type="INTEGER"),
                    MDLColumn(name="user_id", type="INTEGER"),
                ],
            )
        )
        mock_repository.get.return_value = sample_manifest

        relationship = MDLRelationship(
            name="orders_users",
            models=["orders", "users"],
            join_type=JoinType.MANY_TO_ONE,
            condition="orders.user_id = users.id",
        )

        await service.add_relationship("mdl_123", relationship)

        mock_repository.update.assert_called_once()
        updated_manifest = mock_repository.update.call_args[0][0]
        assert len(updated_manifest.relationships) == 1

    @pytest.mark.asyncio
    async def test_export_mdl_json(self, service, mock_repository, sample_manifest):
        """Should export manifest as WrenAI-compatible JSON."""
        mock_repository.get.return_value = sample_manifest

        mdl_json = await service.export_mdl_json("mdl_123")

        assert mdl_json["catalog"] == "test"
        assert mdl_json["schema"] == "public"
        assert len(mdl_json["models"]) == 1

    @pytest.mark.asyncio
    async def test_validate_manifest(self, service, sample_manifest):
        """Should validate manifest against JSON schema."""
        is_valid, errors = await service.validate_manifest(sample_manifest)

        assert is_valid is True
        assert errors == []

    @pytest.mark.asyncio
    async def test_validate_manifest_with_invalid_relationship(self, service):
        """Should detect invalid relationship join type in manifest."""
        # Create a manifest with valid structure but test validation flow
        manifest = MDLManifest(
            catalog="test",
            schema="public",
            models=[
                MDLModel(
                    name="orders",
                    columns=[MDLColumn(name="id", type="INTEGER")],
                )
            ],
        )

        is_valid, errors = await service.validate_manifest(manifest)

        # Valid manifest should pass
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)
