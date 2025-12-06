"""MDL API endpoints."""
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.modules.mdl.models import (
    MDLManifest,
    MDLModel,
    MDLColumn,
    MDLRelationship,
    JoinType,
)
from app.modules.mdl.services import MDLService


# Request/Response models
class CreateManifestRequest(BaseModel):
    """Request to create a new MDL manifest."""

    db_connection_id: str
    name: str
    catalog: str
    schema: str
    data_source: str | None = None


class BuildManifestRequest(BaseModel):
    """Request to build MDL manifest from database."""

    db_connection_id: str
    name: str
    catalog: str
    schema: str
    data_source: str | None = None
    infer_relationships: bool = True


class AddModelRequest(BaseModel):
    """Request to add a model to manifest."""

    name: str
    columns: list[dict]
    table_reference: dict | None = None
    ref_sql: str | None = None
    primary_key: str | None = None
    cached: bool = False
    refresh_time: str | None = None
    properties: dict | None = None


class AddRelationshipRequest(BaseModel):
    """Request to add a relationship."""

    name: str
    models: list[str]
    join_type: str
    condition: str
    properties: dict | None = None


class ManifestResponse(BaseModel):
    """Response with manifest ID."""

    id: str


class ManifestDetailResponse(BaseModel):
    """Response with full manifest details."""

    id: str | None
    db_connection_id: str | None
    name: str | None
    catalog: str
    schema: str
    data_source: str | None
    models: list[dict]
    relationships: list[dict]
    metrics: list[dict]
    views: list[dict]
    created_at: str | None
    updated_at: str | None


def create_mdl_router(service: MDLService) -> APIRouter:
    """
    Create FastAPI router for MDL endpoints.

    Args:
        service: MDL service instance

    Returns:
        Configured APIRouter
    """
    router = APIRouter(prefix="/api/v1/mdl", tags=["MDL Semantic Layer"])

    @router.post("/manifests", status_code=201, response_model=ManifestResponse)
    async def create_manifest(request: CreateManifestRequest):
        """Create a new MDL manifest."""
        manifest_id = await service.create_manifest(
            db_connection_id=request.db_connection_id,
            name=request.name,
            catalog=request.catalog,
            schema=request.schema,
            data_source=request.data_source,
        )
        return ManifestResponse(id=manifest_id)

    @router.get("/manifests", response_model=list[ManifestDetailResponse])
    async def list_manifests(
        db_connection_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ):
        """List all MDL manifests."""
        manifests = await service.list_manifests(
            db_connection_id=db_connection_id,
            limit=limit,
            offset=offset,
        )
        return [_manifest_to_response(m) for m in manifests]

    @router.get("/manifests/{manifest_id}", response_model=ManifestDetailResponse)
    async def get_manifest(manifest_id: str):
        """Get MDL manifest by ID."""
        manifest = await service.get_manifest(manifest_id)
        if not manifest:
            raise HTTPException(status_code=404, detail="Manifest not found")
        return _manifest_to_response(manifest)

    @router.delete("/manifests/{manifest_id}", status_code=204)
    async def delete_manifest(manifest_id: str):
        """Delete an MDL manifest."""
        await service.delete_manifest(manifest_id)

    @router.post("/manifests/build", status_code=201, response_model=ManifestResponse)
    async def build_from_database(request: BuildManifestRequest):
        """Build MDL manifest from database table descriptions."""
        manifest_id = await service.build_from_database(
            db_connection_id=request.db_connection_id,
            name=request.name,
            catalog=request.catalog,
            schema=request.schema,
            data_source=request.data_source,
            infer_relationships=request.infer_relationships,
        )
        return ManifestResponse(id=manifest_id)

    @router.get("/manifests/{manifest_id}/export")
    async def export_mdl_json(manifest_id: str):
        """Export manifest as WrenAI-compatible MDL JSON."""
        manifest = await service.get_manifest(manifest_id)
        if not manifest:
            raise HTTPException(status_code=404, detail="Manifest not found")
        return await service.export_mdl_json(manifest_id)

    @router.post("/manifests/{manifest_id}/models", status_code=201)
    async def add_model(manifest_id: str, request: AddModelRequest):
        """Add a model to the manifest."""
        manifest = await service.get_manifest(manifest_id)
        if not manifest:
            raise HTTPException(status_code=404, detail="Manifest not found")

        columns = [
            MDLColumn(
                name=c["name"],
                type=c["type"],
                not_null=c.get("not_null", False),
                is_calculated=c.get("is_calculated", False),
                expression=c.get("expression"),
                relationship=c.get("relationship"),
                is_hidden=c.get("is_hidden", False),
                properties=c.get("properties"),
            )
            for c in request.columns
        ]

        model = MDLModel(
            name=request.name,
            table_reference=request.table_reference,
            ref_sql=request.ref_sql,
            columns=columns,
            primary_key=request.primary_key,
            cached=request.cached,
            refresh_time=request.refresh_time,
            properties=request.properties,
        )

        await service.add_model(manifest_id, model)
        return {"status": "created"}

    @router.delete("/manifests/{manifest_id}/models/{model_name}", status_code=204)
    async def remove_model(manifest_id: str, model_name: str):
        """Remove a model from the manifest."""
        manifest = await service.get_manifest(manifest_id)
        if not manifest:
            raise HTTPException(status_code=404, detail="Manifest not found")
        await service.remove_model(manifest_id, model_name)

    @router.post("/manifests/{manifest_id}/relationships", status_code=201)
    async def add_relationship(manifest_id: str, request: AddRelationshipRequest):
        """Add a relationship to the manifest."""
        manifest = await service.get_manifest(manifest_id)
        if not manifest:
            raise HTTPException(status_code=404, detail="Manifest not found")

        relationship = MDLRelationship(
            name=request.name,
            models=request.models,
            join_type=JoinType(request.join_type),
            condition=request.condition,
            properties=request.properties,
        )

        await service.add_relationship(manifest_id, relationship)
        return {"status": "created"}

    @router.delete(
        "/manifests/{manifest_id}/relationships/{relationship_name}", status_code=204
    )
    async def remove_relationship(manifest_id: str, relationship_name: str):
        """Remove a relationship from the manifest."""
        manifest = await service.get_manifest(manifest_id)
        if not manifest:
            raise HTTPException(status_code=404, detail="Manifest not found")
        await service.remove_relationship(manifest_id, relationship_name)

    return router


def _manifest_to_response(manifest: MDLManifest) -> ManifestDetailResponse:
    """Convert MDLManifest to response model."""
    return ManifestDetailResponse(
        id=manifest.id,
        db_connection_id=manifest.db_connection_id,
        name=manifest.name,
        catalog=manifest.catalog,
        schema=manifest.schema,
        data_source=manifest.data_source,
        models=[
            {
                "name": m.name,
                "columns": [
                    {"name": c.name, "type": c.type} for c in m.columns
                ],
                "primary_key": m.primary_key,
            }
            for m in manifest.models
        ],
        relationships=[
            {
                "name": r.name,
                "models": r.models,
                "join_type": r.join_type.value,
                "condition": r.condition,
            }
            for r in manifest.relationships
        ],
        metrics=[
            {"name": m.name, "base_object": m.base_object}
            for m in manifest.metrics
        ],
        views=[
            {"name": v.name, "statement": v.statement}
            for v in manifest.views
        ],
        created_at=manifest.created_at,
        updated_at=manifest.updated_at,
    )


__all__ = ["create_mdl_router"]
