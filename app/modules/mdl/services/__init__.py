"""MDL business logic services."""
from typing import Any, Optional

from app.modules.mdl.models import (
    MDLManifest,
    MDLModel,
    MDLRelationship,
    MDLMetric,
    MDLView,
)
from app.modules.mdl.repositories import MDLRepository
from app.modules.mdl.services.builder import MDLBuilder
from app.modules.mdl.validators import MDLValidator
from app.modules.table_description.models import (
    TableDescription,
    ColumnDescription,
    ForeignKeyDetail,
)


class MDLService:
    """
    Service for managing MDL semantic layer manifests.

    Orchestrates:
    - CRUD operations via repository
    - Building manifests from database metadata
    - Validation against JSON schema
    - Export to WrenAI format
    """

    def __init__(
        self,
        repository: MDLRepository,
        table_description_repo: Any = None,
    ):
        """
        Initialize MDL service.

        Args:
            repository: MDL repository for storage operations
            table_description_repo: Optional TableDescription repository for building from DB
        """
        self.repository = repository
        self.table_description_repo = table_description_repo

    async def create_manifest(
        self,
        db_connection_id: str,
        name: str,
        catalog: str,
        schema: str,
        data_source: str | None = None,
        models: list[MDLModel] | None = None,
        relationships: list[MDLRelationship] | None = None,
        metrics: list[MDLMetric] | None = None,
        views: list[MDLView] | None = None,
        metadata: dict | None = None,
    ) -> str:
        """
        Create a new MDL manifest.

        Args:
            db_connection_id: Database connection ID
            name: Manifest name
            catalog: Database catalog
            schema: Database schema
            data_source: Data source type
            models: Initial models
            relationships: Initial relationships
            metrics: Initial metrics
            views: Initial views
            metadata: Custom metadata

        Returns:
            Created manifest ID
        """
        return await self.repository.create(
            db_connection_id=db_connection_id,
            name=name,
            catalog=catalog,
            schema=schema,
            data_source=data_source,
            models=models,
            relationships=relationships,
            metrics=metrics,
            views=views,
            metadata=metadata,
        )

    async def get_manifest(self, manifest_id: str) -> Optional[MDLManifest]:
        """
        Get manifest by ID.

        Args:
            manifest_id: Manifest ID

        Returns:
            MDLManifest if found, None otherwise
        """
        return await self.repository.get(manifest_id)

    async def get_manifest_by_db_connection(
        self, db_connection_id: str
    ) -> Optional[MDLManifest]:
        """
        Get manifest by database connection ID.

        Args:
            db_connection_id: Database connection ID

        Returns:
            MDLManifest if found, None otherwise
        """
        return await self.repository.get_by_db_connection(db_connection_id)

    async def list_manifests(
        self,
        db_connection_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MDLManifest]:
        """
        List manifests with optional filters.

        Args:
            db_connection_id: Filter by database connection
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of manifests
        """
        return await self.repository.list(
            db_connection_id=db_connection_id,
            limit=limit,
            offset=offset,
        )

    async def update_manifest(self, manifest: MDLManifest) -> None:
        """
        Update an existing manifest.

        Args:
            manifest: Manifest with updated data
        """
        await self.repository.update(manifest)

    async def delete_manifest(self, manifest_id: str) -> None:
        """
        Delete a manifest.

        Args:
            manifest_id: Manifest ID to delete
        """
        await self.repository.delete(manifest_id)

    async def build_from_database(
        self,
        db_connection_id: str,
        name: str,
        catalog: str,
        schema: str,
        data_source: str | None = None,
        infer_relationships: bool = True,
    ) -> str:
        """
        Build MDL manifest from database table descriptions.

        Args:
            db_connection_id: Database connection ID
            name: Manifest name
            catalog: Database catalog
            schema: Database schema
            data_source: Data source type
            infer_relationships: Whether to auto-infer relationships

        Returns:
            Created manifest ID
        """
        if not self.table_description_repo:
            raise ValueError("TableDescription repository not configured")

        # Fetch table descriptions for this connection
        docs = self.table_description_repo.find(
            "table_descriptions",
            filter={"db_connection_id": db_connection_id},
        )

        # Convert docs to TableDescription objects
        table_descriptions = []
        for doc in docs:
            columns = [
                ColumnDescription(
                    name=c["name"],
                    data_type=c.get("data_type", "VARCHAR"),
                    description=c.get("description"),
                    is_primary_key=c.get("is_primary_key", False),
                    low_cardinality=c.get("low_cardinality", False),
                    categories=c.get("categories"),
                    foreign_key=(
                        ForeignKeyDetail(
                            field_name=c["foreign_key"]["field_name"],
                            reference_table=c["foreign_key"]["reference_table"],
                        )
                        if c.get("foreign_key")
                        else None
                    ),
                )
                for c in doc.get("columns", [])
            ]

            table_descriptions.append(
                TableDescription(
                    id=doc.get("id"),
                    db_connection_id=doc["db_connection_id"],
                    db_schema=doc.get("db_schema", schema),
                    table_name=doc["table_name"],
                    columns=columns,
                    table_description=doc.get("table_description"),
                )
            )

        # Build manifest using builder
        manifest = MDLBuilder.from_table_descriptions(
            db_connection_id=db_connection_id,
            catalog=catalog,
            schema=schema,
            table_descriptions=table_descriptions,
            name=name,
            data_source=data_source,
        )

        # Optionally infer additional relationships
        if infer_relationships:
            manifest = MDLBuilder.infer_relationships(manifest)

        # Save to repository
        return await self.repository.create(
            db_connection_id=db_connection_id,
            name=name,
            catalog=catalog,
            schema=schema,
            data_source=data_source,
            models=manifest.models,
            relationships=manifest.relationships,
            metrics=manifest.metrics,
            views=manifest.views,
        )

    async def add_model(self, manifest_id: str, model: MDLModel) -> None:
        """
        Add a model to an existing manifest.

        Args:
            manifest_id: Manifest ID
            model: Model to add
        """
        manifest = await self.repository.get(manifest_id)
        if not manifest:
            raise ValueError(f"Manifest {manifest_id} not found")

        updated = MDLBuilder.add_model(manifest, model)
        await self.repository.update(updated)

    async def remove_model(self, manifest_id: str, model_name: str) -> None:
        """
        Remove a model from a manifest.

        Args:
            manifest_id: Manifest ID
            model_name: Name of model to remove
        """
        manifest = await self.repository.get(manifest_id)
        if not manifest:
            raise ValueError(f"Manifest {manifest_id} not found")

        updated = MDLBuilder.remove_model(manifest, model_name)
        await self.repository.update(updated)

    async def add_relationship(
        self, manifest_id: str, relationship: MDLRelationship
    ) -> None:
        """
        Add a relationship to a manifest.

        Args:
            manifest_id: Manifest ID
            relationship: Relationship to add
        """
        manifest = await self.repository.get(manifest_id)
        if not manifest:
            raise ValueError(f"Manifest {manifest_id} not found")

        updated = MDLBuilder.add_relationship(manifest, relationship)
        await self.repository.update(updated)

    async def remove_relationship(
        self, manifest_id: str, relationship_name: str
    ) -> None:
        """
        Remove a relationship from a manifest.

        Args:
            manifest_id: Manifest ID
            relationship_name: Name of relationship to remove
        """
        manifest = await self.repository.get(manifest_id)
        if not manifest:
            raise ValueError(f"Manifest {manifest_id} not found")

        updated = MDLBuilder.remove_relationship(manifest, relationship_name)
        await self.repository.update(updated)

    async def export_mdl_json(self, manifest_id: str) -> dict:
        """
        Export manifest as WrenAI-compatible JSON.

        Args:
            manifest_id: Manifest ID

        Returns:
            MDL JSON dictionary

        Raises:
            ValueError: If manifest not found
        """
        manifest = await self.repository.get(manifest_id)
        if not manifest:
            raise ValueError(f"Manifest {manifest_id} not found")

        return manifest.to_mdl_json()

    async def validate_manifest(
        self, manifest: MDLManifest
    ) -> tuple[bool, list[str]]:
        """
        Validate manifest against MDL JSON schema.

        Args:
            manifest: Manifest to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        mdl_json = manifest.to_mdl_json()
        return MDLValidator.validate(mdl_json)


__all__ = ["MDLService"]
