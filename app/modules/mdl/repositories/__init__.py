"""MDL repository for Typesense storage."""
import uuid
from datetime import datetime
from typing import Any, Optional

from app.modules.mdl.models import (
    MDLManifest,
    MDLModel,
    MDLRelationship,
    MDLMetric,
    MDLView,
)

MDL_COLLECTION_NAME = "mdl_manifests"


class MDLRepository:
    """
    Repository for MDL manifest CRUD operations.

    Uses Typesense as the storage backend.
    """

    def __init__(self, storage: Any):
        """
        Initialize repository with storage.

        Args:
            storage: Typesense storage instance
        """
        self.storage = storage
        self.collection = MDL_COLLECTION_NAME

    async def create(
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
            data_source: Type of data source (postgresql, mysql, etc.)
            models: List of model definitions
            relationships: List of relationship definitions
            metrics: List of metric definitions
            views: List of view definitions
            metadata: Optional custom metadata

        Returns:
            Created manifest ID
        """
        manifest_id = f"mdl_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()

        manifest = MDLManifest(
            id=manifest_id,
            db_connection_id=db_connection_id,
            name=name,
            catalog=catalog,
            schema=schema,
            data_source=data_source,
            models=models or [],
            relationships=relationships or [],
            metrics=metrics or [],
            views=views or [],
            metadata=metadata,
            created_at=now,
        )

        manifest_data = self._manifest_to_doc(manifest)
        # Storage.insert_one generates its own ID, so use the returned ID
        created_id = self.storage.insert_one(self.collection, manifest_data)
        return created_id

    async def get(self, manifest_id: str) -> Optional[MDLManifest]:
        """
        Get manifest by ID.

        Args:
            manifest_id: Manifest ID to retrieve

        Returns:
            MDLManifest if found, None otherwise
        """
        doc = self.storage.find_by_id(self.collection, manifest_id)

        if not doc:
            return None

        return self._doc_to_manifest(doc)

    async def get_by_db_connection(self, db_connection_id: str) -> Optional[MDLManifest]:
        """
        Get manifest by database connection ID.

        Args:
            db_connection_id: Database connection ID

        Returns:
            MDLManifest if found, None otherwise
        """
        docs = self.storage.find(
            self.collection,
            filter={"db_connection_id": db_connection_id},
            limit=1,
        )

        if not docs:
            return None

        return self._doc_to_manifest(docs[0])

    async def list(
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
            List of matching manifests
        """
        filters = {}
        if db_connection_id:
            filters["db_connection_id"] = db_connection_id

        docs = self.storage.find(
            self.collection,
            filter=filters if filters else None,
            limit=limit,
            page=offset // limit if limit > 0 else 0,
        )

        return [self._doc_to_manifest(doc) for doc in docs]

    async def update(self, manifest: MDLManifest) -> None:
        """
        Update an existing manifest.

        Args:
            manifest: Manifest with updated data
        """
        manifest.updated_at = datetime.now().isoformat()
        manifest_data = self._manifest_to_doc(manifest)

        self.storage.update_or_create(
            self.collection,
            {"id": manifest.id},
            manifest_data,
        )

    async def delete(self, manifest_id: str) -> None:
        """
        Delete a manifest.

        Args:
            manifest_id: Manifest ID to delete
        """
        self.storage.delete_by_id(self.collection, manifest_id)

    def _manifest_to_doc(self, manifest: MDLManifest) -> dict:
        """
        Convert MDLManifest to Typesense document.

        Args:
            manifest: Manifest to convert

        Returns:
            Dictionary for Typesense storage
        """
        return {
            "id": manifest.id,
            "db_connection_id": manifest.db_connection_id,
            "name": manifest.name,
            "catalog": manifest.catalog,
            "schema": manifest.schema_name,
            "data_source": manifest.data_source,
            "models": [self._model_to_doc(m) for m in manifest.models],
            "relationships": [self._relationship_to_doc(r) for r in manifest.relationships],
            "metrics": [self._metric_to_doc(m) for m in manifest.metrics],
            "views": [self._view_to_doc(v) for v in manifest.views],
            "enum_definitions": [
                {"name": e.name, "values": [{"name": v.name, "value": v.value} for v in e.values]}
                for e in manifest.enum_definitions
            ],
            "version": manifest.version,
            "metadata": manifest.metadata,
            "created_at": manifest.created_at,
            "updated_at": manifest.updated_at,
        }

    def _model_to_doc(self, model: MDLModel) -> dict:
        """Convert MDLModel to document."""
        return {
            "name": model.name,
            "tableReference": model.table_reference,
            "refSql": model.ref_sql,
            "columns": [
                {
                    "name": c.name,
                    "type": c.type,
                    "notNull": c.not_null,
                    "isCalculated": c.is_calculated,
                    "expression": c.expression,
                    "relationship": c.relationship,
                    "isHidden": c.is_hidden,
                    "properties": c.properties,
                }
                for c in model.columns
            ],
            "primaryKey": model.primary_key,
            "cached": model.cached,
            "refreshTime": model.refresh_time,
            "properties": model.properties,
        }

    def _relationship_to_doc(self, rel: MDLRelationship) -> dict:
        """Convert MDLRelationship to document."""
        return {
            "name": rel.name,
            "models": rel.models,
            "joinType": rel.join_type.value,
            "condition": rel.condition,
            "properties": rel.properties,
        }

    def _metric_to_doc(self, metric: MDLMetric) -> dict:
        """Convert MDLMetric to document."""
        return {
            "name": metric.name,
            "baseObject": metric.base_object,
            "dimension": [
                {"name": c.name, "type": c.type, "expression": c.expression}
                for c in (metric.dimension or [])
            ],
            "measure": [
                {"name": c.name, "type": c.type, "expression": c.expression, "isCalculated": c.is_calculated}
                for c in (metric.measure or [])
            ],
            "timeGrain": [
                {"name": t.name, "refColumn": t.ref_column, "dateParts": [dp.value for dp in t.date_parts]}
                for t in (metric.time_grain or [])
            ],
            "cached": metric.cached,
            "refreshTime": metric.refresh_time,
            "properties": metric.properties,
        }

    def _view_to_doc(self, view: MDLView) -> dict:
        """Convert MDLView to document."""
        return {
            "name": view.name,
            "statement": view.statement,
            "properties": view.properties,
        }

    def _doc_to_manifest(self, doc: dict) -> MDLManifest:
        """
        Convert Typesense document to MDLManifest.

        Args:
            doc: Raw document from Typesense

        Returns:
            MDLManifest instance
        """
        # Build the dict in a format MDLManifest.from_dict expects
        data = {
            "id": doc.get("id"),
            "db_connection_id": doc.get("db_connection_id"),
            "name": doc.get("name"),
            "catalog": doc.get("catalog"),
            "schema": doc.get("schema"),
            "data_source": doc.get("data_source"),
            "models": doc.get("models", []),
            "relationships": doc.get("relationships", []),
            "metrics": doc.get("metrics", []),
            "views": doc.get("views", []),
            "enumDefinitions": doc.get("enum_definitions", []),
            "version": doc.get("version"),
            "metadata": doc.get("metadata"),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
        }

        return MDLManifest.from_dict(data)


__all__ = ["MDLRepository", "MDL_COLLECTION_NAME"]
