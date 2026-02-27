"""Context Asset Service.

Provides business logic for context asset lifecycle management with
policy enforcement, promotion tracking, and integration with KAI's
verified SQL and memory tools.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from app.data.db.storage import Storage
from app.modules.context_platform.models.asset import (
    ContextAsset,
    ContextAssetSearchResult,
    ContextAssetTag,
    ContextAssetType,
    ContextAssetVersion,
    LifecycleState,
)
from app.modules.context_platform.repositories.asset_repository import (
    ContextAssetRepository,
)

logger = logging.getLogger(__name__)


class LifecyclePolicyError(Exception):
    """Raised when a lifecycle transition violates policy."""

    pass


class ContextAssetService:
    """Service for managing context asset lifecycle with policy enforcement.

    Enforces lifecycle transitions:
    - draft -> verified: Requires domain expert approval
    - verified -> published: Requires final approval
    - published -> deprecated: Requires deprecation reason
    - Any state -> draft: For revision cycles

    Tracks promotion metadata (promoted_by, promoted_at, change_note).
    """

    def __init__(self, storage: Storage, repository: ContextAssetRepository | None = None):
        """Initialize the service.

        Args:
            storage: Typesense storage instance.
            repository: Optional repository instance (for testing).
        """
        self.storage = storage
        self.repository = repository or ContextAssetRepository(storage)

    # ===== CRUD Operations =====

    def create_asset(
        self,
        db_connection_id: str,
        asset_type: ContextAssetType,
        canonical_key: str,
        name: str,
        content: dict[str, Any],
        content_text: str,
        description: str | None = None,
        author: str | None = None,
        tags: list[str] | None = None,
    ) -> ContextAsset:
        """Create a new context asset in DRAFT state.

        Args:
            db_connection_id: Database connection ID.
            asset_type: Type of asset.
            canonical_key: Unique key for the asset.
            name: Human-readable name.
            content: Asset content (structure varies by type).
            content_text: Searchable text representation.
            description: Optional detailed description.
            author: Optional creator identifier.
            tags: Optional user-defined tags.

        Returns:
            The created asset.
        """
        # Check if an asset with this key already exists
        existing = self.repository.find_by_key(
            db_connection_id, asset_type, canonical_key
        )
        if existing:
            raise ValueError(f"Asset with key '{canonical_key}' already exists")

        asset = ContextAsset(
            db_connection_id=db_connection_id,
            asset_type=asset_type,
            canonical_key=canonical_key,
            name=name,
            description=description,
            content=content,
            content_text=content_text,
            lifecycle_state=LifecycleState.DRAFT,
            author=author,
            tags=tags or [],
        )

        created = self.repository.insert(asset)

        # Update tag usage counts
        for tag in tags or []:
            self._update_tag_usage(tag)

        logger.info(
            f"Created context asset: {asset_type.value}/{canonical_key} "
            f"(id={created.id}, author={author})"
        )
        return created

    def get_asset(
        self,
        db_connection_id: str,
        asset_type: ContextAssetType,
        canonical_key: str,
        version: str = "latest",
    ) -> ContextAsset | None:
        """Get an asset by key.

        Args:
            db_connection_id: Database connection ID.
            asset_type: Type of asset.
            canonical_key: Unique key for the asset.
            version: Version string or "latest" for the newest version.

        Returns:
            The asset if found, None otherwise.
        """
        if version == "latest":
            return self.repository.find_latest_version(
                db_connection_id, asset_type, canonical_key
            )
        return self.repository.find_by_key(
            db_connection_id, asset_type, canonical_key, version
        )

    def list_assets(
        self,
        db_connection_id: str,
        asset_type: ContextAssetType | None = None,
        lifecycle_state: LifecycleState | None = None,
        limit: int = 100,
    ) -> list[ContextAsset]:
        """List assets with optional filtering.

        Args:
            db_connection_id: Database connection ID.
            asset_type: Optional filter by asset type.
            lifecycle_state: Optional filter by lifecycle state.
            limit: Maximum results.

        Returns:
            List of matching assets.
        """
        return self.repository.find_by_connection(
            db_connection_id,
            asset_type=asset_type,
            lifecycle_state=lifecycle_state,
            limit=limit,
        )

    def search_assets(
        self,
        db_connection_id: str,
        query: str,
        asset_type: ContextAssetType | None = None,
        lifecycle_state: LifecycleState | None = None,
        limit: int = 10,
    ) -> list[ContextAssetSearchResult]:
        """Search assets by text query.

        Only searches published assets by default for reuse.
        """
        search_state = lifecycle_state or LifecycleState.PUBLISHED
        return self.repository.search(
            db_connection_id=db_connection_id,
            query=query,
            asset_type=asset_type,
            lifecycle_state=search_state,
            limit=limit,
        )

    def update_asset(
        self,
        asset_id: str,
        name: str | None = None,
        description: str | None = None,
        content: dict[str, Any] | None = None,
        content_text: str | None = None,
        tags: list[str] | None = None,
    ) -> ContextAsset | None:
        """Update an asset's content.

        Only DRAFT assets can be updated directly.
        For other states, use create_draft_revision().

        Args:
            asset_id: ID of the asset to update.
            name: Optional new name.
            description: Optional new description.
            content: Optional new content.
            content_text: Optional new content text.
            tags: Optional new tags.

        Returns:
            The updated asset, or None if not found.
        """
        asset = self.repository.find_by_id(asset_id)
        if not asset:
            return None

        if asset.lifecycle_state != LifecycleState.DRAFT:
            raise LifecyclePolicyError(
                f"Cannot update {asset.lifecycle_state.value} asset directly. "
                f"Use create_draft_revision() instead."
            )

        if name is not None:
            asset.name = name
        if description is not None:
            asset.description = description
        if content is not None:
            asset.content = content
        if content_text is not None:
            asset.content_text = content_text
        if tags is not None:
            asset.tags = tags

        updated = self.repository.update(asset)

        # Update tag usage counts
        for tag in tags or []:
            self._update_tag_usage(tag)

        logger.info(f"Updated context asset: {asset.id}")
        return updated

    def delete_asset(
        self,
        db_connection_id: str,
        asset_type: ContextAssetType,
        canonical_key: str,
        version: str | None = None,
    ) -> bool:
        """Delete an asset.

        Only DRAFT assets can be deleted. Other states must be deprecated first.

        Args:
            db_connection_id: Database connection ID.
            asset_type: Type of asset.
            canonical_key: Unique key for the asset.
            version: Optional version (if None, deletes all versions).

        Returns:
            True if deleted, False otherwise.
        """
        if version:
            asset = self.repository.find_by_key(
                db_connection_id, asset_type, canonical_key, version
            )
            if asset and asset.lifecycle_state != LifecycleState.DRAFT:
                raise LifecyclePolicyError(
                    f"Cannot delete {asset.lifecycle_state.value} asset. "
                    f"Deprecate it first."
                )

        return self.repository.delete_by_key(
            db_connection_id, asset_type, canonical_key, version
        )

    # ===== Lifecycle Transitions =====

    def promote_to_verified(
        self,
        asset_id: str,
        promoted_by: str,
        change_note: str | None = None,
    ) -> ContextAsset | None:
        """Promote an asset from DRAFT to VERIFIED.

        Requires domain expert approval.

        Args:
            asset_id: ID of the asset to promote.
            promoted_by: Identifier of the approver.
            change_note: Optional note about the approval.

        Returns:
            The promoted asset, or None if not found.
        """
        asset = self.repository.find_by_id(asset_id)
        if not asset:
            return None

        self._validate_transition(
            asset.lifecycle_state, LifecycleState.VERIFIED
        )

        # Create version snapshot before promotion
        self.repository.create_version(asset, change_note or "Verified by domain expert")

        # Update lifecycle state
        asset.lifecycle_state = LifecycleState.VERIFIED
        self._add_promotion_metadata(asset, promoted_by, change_note)

        updated = self.repository.update(asset)
        logger.info(
            f"Promoted asset to VERIFIED: {asset.id} (by={promoted_by})"
        )
        return updated

    def promote_to_published(
        self,
        asset_id: str,
        promoted_by: str,
        change_note: str | None = None,
    ) -> ContextAsset | None:
        """Promote an asset from VERIFIED to PUBLISHED.

        Requires final approval for reuse across missions.

        Args:
            asset_id: ID of the asset to promote.
            promoted_by: Identifier of the approver.
            change_note: Optional note about the approval.

        Returns:
            The promoted asset, or None if not found.
        """
        asset = self.repository.find_by_id(asset_id)
        if not asset:
            return None

        self._validate_transition(
            asset.lifecycle_state, LifecycleState.PUBLISHED
        )

        # Create version snapshot
        self.repository.create_version(asset, change_note or "Published for reuse")

        # Update lifecycle state
        asset.lifecycle_state = LifecycleState.PUBLISHED
        self._add_promotion_metadata(asset, promoted_by, change_note)

        updated = self.repository.update(asset)
        logger.info(
            f"Promoted asset to PUBLISHED: {asset.id} (by={promoted_by})"
        )
        return updated

    def deprecate_asset(
        self,
        asset_id: str,
        promoted_by: str,
        reason: str,
    ) -> ContextAsset | None:
        """Deprecate a published asset.

        Args:
            asset_id: ID of the asset to deprecate.
            promoted_by: Identifier of the approver.
            reason: Reason for deprecation.

        Returns:
            The deprecated asset, or None if not found.
        """
        asset = self.repository.find_by_id(asset_id)
        if not asset:
            return None

        self._validate_transition(
            asset.lifecycle_state, LifecycleState.DEPRECATED
        )

        # Create version snapshot with reason
        self.repository.create_version(asset, f"Deprecated: {reason}")

        # Update lifecycle state
        asset.lifecycle_state = LifecycleState.DEPRECATED
        self._add_promotion_metadata(asset, promoted_by, f"Deprecated: {reason}")

        updated = self.repository.update(asset)
        logger.info(
            f"Deprecated asset: {asset.id} (by={promoted_by}, reason={reason})"
        )
        return updated

    def create_draft_revision(
        self,
        asset_id: str,
        author: str,
    ) -> ContextAsset | None:
        """Create a new DRAFT revision of an existing asset.

        This allows revisiting published or deprecated assets.

        Args:
            asset_id: ID of the asset to revise.
            author: Identifier of the reviser.

        Returns:
            The new draft asset, or None if not found.
        """
        asset = self.repository.find_by_id(asset_id)
        if not asset:
            return None

        # Store parent reference
        parent_id = asset.id

        # Create new draft version with incremented version number
        new_version = self._increment_version(asset.version)
        new_asset = ContextAsset(
            db_connection_id=asset.db_connection_id,
            asset_type=asset.asset_type,
            canonical_key=f"{asset.canonical_key}_rev_{new_version.replace('.', '_')}",
            version=new_version,
            name=asset.name,
            description=asset.description,
            content=asset.content.copy(),
            content_text=asset.content_text,
            lifecycle_state=LifecycleState.DRAFT,
            author=author,
            parent_asset_id=parent_id,
            tags=asset.tags.copy(),
        )

        created = self.repository.insert(new_asset)
        logger.info(
            f"Created draft revision of asset: {parent_id} -> {created.id}"
        )
        return created

    # ===== Version History =====

    def get_version_history(self, asset_id: str) -> list[ContextAssetVersion]:
        """Get the version history for an asset.

        Args:
            asset_id: ID of the asset.

        Returns:
            List of versions in descending order (newest first).
        """
        return self.repository.find_versions(asset_id)

    # ===== Tag Management =====

    def get_tags(self, category: str | None = None) -> list[ContextAssetTag]:
        """Get all tags, optionally filtered by category.

        Args:
            category: Optional category filter.

        Returns:
            List of tags.
        """
        if category:
            return self.repository.find_tags_by_category(category)
        return self.repository.find_all_tags()

    # ===== Integration with KAI Tools =====

    def format_for_sql_context(self, db_connection_id: str) -> str:
        """Format published context assets for SQL generation context.

        Includes table descriptions and glossaries that can enhance
        SQL generation accuracy.

        Args:
            db_connection_id: Database connection ID.

        Returns:
            Formatted string for prompt injection.
        """
        parts = []

        # Get table descriptions
        table_descriptions = self.repository.find_by_type(
            db_connection_id,
            ContextAssetType.TABLE_DESCRIPTION,
            LifecycleState.PUBLISHED,
        )
        if table_descriptions:
            parts.append("## Table Descriptions\n")
            for asset in table_descriptions:
                parts.append(f"### {asset.name}")
                if asset.description:
                    parts.append(f"*{asset.description}*")
                parts.append(f"{asset.content_text}\n")

        # Get glossaries
        glossaries = self.repository.find_by_type(
            db_connection_id,
            ContextAssetType.GLOSSARY,
            LifecycleState.PUBLISHED,
        )
        if glossaries:
            parts.append("## Business Glossary\n")
            for asset in glossaries:
                parts.append(f"**{asset.name}**: {asset.content_text}")

        return "\n".join(parts) if parts else ""

    def format_for_memory_context(self, db_connection_id: str) -> str:
        """Format published context assets for memory storage.

        Creates memory entries from published assets for cross-session
        knowledge retention.

        Args:
            db_connection_id: Database connection ID.

        Returns:
            List of (namespace, key, value) tuples for memory storage.
        """
        memories = []

        # Store published assets as memories
        assets = self.repository.find_by_connection(
            db_connection_id,
            lifecycle_state=LifecycleState.PUBLISHED,
        )

        for asset in assets:
            namespace = f"context_{asset.asset_type.value}"
            key = asset.canonical_key
            value = {
                "name": asset.name,
                "description": asset.description,
                "content": asset.content,
                "content_text": asset.content_text,
                "version": asset.version,
                "tags": asset.tags,
            }
            memories.append((namespace, key, value))

        return memories

    # ===== Helper Methods =====

    def _validate_transition(
        self,
        current_state: LifecycleState,
        target_state: LifecycleState,
    ) -> None:
        """Validate that a lifecycle transition is allowed.

        Args:
            current_state: Current lifecycle state.
            target_state: Target lifecycle state.

        Raises:
            LifecyclePolicyError: If transition is not allowed.
        """
        valid_transitions = {
            LifecycleState.DRAFT: [LifecycleState.VERIFIED, LifecycleState.DEPRECATED],
            LifecycleState.VERIFIED: [
                LifecycleState.PUBLISHED,
                LifecycleState.DEPRECATED,
                LifecycleState.DRAFT,  # For revision
            ],
            LifecycleState.PUBLISHED: [
                LifecycleState.DEPRECATED,
                LifecycleState.DRAFT,  # For revision
            ],
            LifecycleState.DEPRECATED: [
                LifecycleState.DRAFT,  # For revival
            ],
        }

        allowed = valid_transitions.get(current_state, [])
        if target_state not in allowed:
            raise LifecyclePolicyError(
                f"Invalid lifecycle transition: {current_state.value} -> {target_state.value}. "
                f"Allowed transitions from {current_state.value}: {[s.value for s in allowed]}"
            )

    def _add_promotion_metadata(
        self,
        asset: ContextAsset,
        promoted_by: str,
        change_note: str | None,
    ) -> None:
        """Add promotion metadata to an asset.

        Stores promotion information in the content dict for tracking.

        Args:
            asset: The asset to update.
            promoted_by: Identifier of the approver.
            change_note: Optional note about the promotion.
        """
        now = datetime.now(timezone.utc).isoformat()

        # Initialize promotion metadata in content if not present
        if "promotion_history" not in asset.content:
            asset.content["promotion_history"] = []

        asset.content["promotion_history"].append({
            "to_state": asset.lifecycle_state.value,
            "promoted_by": promoted_by,
            "promoted_at": now,
            "change_note": change_note,
        })

        # Update direct references for quick access
        asset.content["promoted_by"] = promoted_by
        asset.content["promoted_at"] = now
        if change_note:
            asset.content["change_note"] = change_note

    def _increment_version(self, version: str) -> str:
        """Increment a version string.

        Uses semver rules: bumps patch version by default.

        Args:
            version: Current version string (e.g., "1.0.0").

        Returns:
            Incremented version string.
        """
        try:
            parts = version.split(".")
            if len(parts) != 3:
                # If not valid semver, append .1
                return f"{version}.1"

            major, minor, patch = parts
            new_patch = int(patch) + 1
            return f"{major}.{minor}.{new_patch}"
        except (ValueError, AttributeError):
            return f"{version}.1"

    def _update_tag_usage(self, tag_name: str) -> None:
        """Increment usage count for a tag.

        Args:
            tag_name: Name of the tag.
        """
        try:
            self.repository.update_tag_usage(tag_name)
        except Exception:
            # Tag update is not critical, log and continue
            logger.debug(f"Failed to update tag usage for: {tag_name}")
