"""MDL (Model Definition Language) module for semantic layer management.

This module provides tools for defining and managing semantic layers using
the Model Definition Language (MDL) format, compatible with WrenAI.

Components:
- models: Pydantic models for MDL entities (models, columns, relationships, metrics)
- repositories: Typesense storage for MDL manifests
- services: Business logic for managing semantic layers
- validators: JSON Schema validation for MDL manifests
- api: REST API endpoints for MDL operations
"""

from app.modules.mdl.models import (
    MDLColumn,
    MDLModel,
    MDLRelationship,
    MDLMetric,
    MDLTimeGrain,
    MDLView,
    MDLManifest,
    JoinType,
    DatePart,
)
from app.modules.mdl.repositories import MDLRepository
from app.modules.mdl.services import MDLService
from app.modules.mdl.services.builder import MDLBuilder
from app.modules.mdl.validators import MDLValidator
from app.modules.mdl.api import create_mdl_router

__all__ = [
    # Models
    "MDLColumn",
    "MDLModel",
    "MDLRelationship",
    "MDLMetric",
    "MDLTimeGrain",
    "MDLView",
    "MDLManifest",
    "JoinType",
    "DatePart",
    # Services
    "MDLService",
    "MDLBuilder",
    "MDLRepository",
    "MDLValidator",
    # API
    "create_mdl_router",
]
