"""Context asset models for lifecycle management.

Context assets are reusable domain knowledge artifacts that can be versioned,
tagged, and shared across missions and database connections.

Asset Types:
- table_description: Descriptive metadata about database tables
- glossary: Business terminology and definitions
- instruction: Domain-specific analysis instructions
- skill: Reusable analysis patterns and templates

Lifecycle States:
- draft: Initial creation, not yet verified
- verified: Validated by domain expert
- published: Approved for reuse across missions
- deprecated: Superseded or no longer relevant
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class LifecycleState(str, Enum):
    """Lifecycle state of a context asset.

    Transitions:
    - draft -> verified: After domain expert review
    - verified -> published: After approval for reuse
    - published -> deprecated: When superseded or obsolete
    - Any state -> draft: For revision cycles
    """

    DRAFT = "draft"
    VERIFIED = "verified"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"


class ContextAssetType(str, Enum):
    """Type of context asset."""

    TABLE_DESCRIPTION = "table_description"
    GLOSSARY = "glossary"
    INSTRUCTION = "instruction"
    SKILL = "skill"


class ContextAsset(BaseModel):
    """A reusable context asset.

    Assets are uniquely identified by the combination of:
    - db_connection_id: The database connection this asset belongs to
    - asset_type: The type of asset (table_description, glossary, etc.)
    - canonical_key: Unique key for this asset within the db/type
    - version: Version string (semver like "1.0.0")

    The (db_connection_id, asset_type, canonical_key, version) tuple must
    be unique for each asset.
    """

    # System fields
    id: str | None = None  # Typesense document ID
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    # Identity fields (uniqueness constraint)
    db_connection_id: str = Field(
        description="ID of the database connection this asset belongs to"
    )
    asset_type: ContextAssetType = Field(description="Type of context asset")
    canonical_key: str = Field(
        description="Unique key for this asset within db_connection_id and asset_type"
    )
    version: str = Field(
        default="1.0.0",
        description="Version following semver (major.minor.patch)",
    )

    # Content fields
    name: str = Field(description="Human-readable name for this asset")
    description: str | None = Field(
        default=None, description="Optional detailed description"
    )
    content: dict[str, Any] = Field(
        description="Asset content (structure varies by asset_type)"
    )
    content_text: str = Field(
        description="Searchable text representation of the content"
    )

    # Lifecycle fields
    lifecycle_state: LifecycleState = Field(
        default=LifecycleState.DRAFT, description="Current lifecycle state"
    )

    # Metadata
    tags: list[str] = Field(default_factory=list, description="User-defined tags")
    author: str | None = Field(default=None, description="Creator identifier")
    parent_asset_id: str | None = Field(
        default=None,
        description="ID of the previous version this asset derives from",
    )

    class Config:
        # For uniqueness, Typesense will use a composite index
        # on (db_connection_id, asset_type, canonical_key, version)
        use_enum_values = True


class ContextAssetVersion(BaseModel):
    """Version history entry for a context asset.

    Tracks the evolution of an asset across its lifecycle.
    """

    id: str | None = None  # Typesense document ID
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    asset_id: str = Field(description="ID of the ContextAsset this version belongs to")
    version: str = Field(description="Version string (e.g., '1.0.0', '1.1.0')")

    # Snapshot of asset state at this version
    name: str
    description: str | None = None
    content: dict[str, Any]
    content_text: str

    # Version metadata
    lifecycle_state: LifecycleState = Field(
        default=LifecycleState.DRAFT, description="Lifecycle state at this version"
    )
    author: str | None = None
    change_summary: str | None = Field(
        default=None, description="Human-readable description of changes"
    )

    class Config:
        use_enum_values = True


class ContextAssetTag(BaseModel):
    """A tag that can be applied to context assets.

    Tags provide flexible categorization and discovery of assets.
    """

    id: str | None = None  # Typesense document ID
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    name: str = Field(description="Tag name (unique)")
    category: str | None = Field(
        default=None,
        description="Optional category grouping (e.g., 'domain', 'use_case')",
    )
    description: str | None = Field(default=None, description="Tag description")

    # Tag usage tracking
    usage_count: int = Field(default=0, description="Number of assets with this tag")
    last_used_at: str | None = Field(default=None, description="Last application time")


class ContextAssetSearchResult(BaseModel):
    """Result from context asset search."""

    asset: ContextAsset
    score: float = Field(description="Relevance score (0-1)")
    match_type: str = Field(default="hybrid", description="'semantic', 'keyword', or 'hybrid'")
