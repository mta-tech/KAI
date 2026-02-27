"""Context Asset Repository.

Provides CRUD operations for context assets with versioning support.
Integrates with Typesense storage for persistence.
"""

import json
from datetime import datetime, timezone

from app.data.db.storage import Storage
from app.modules.context_platform.models.asset import (
    ContextAsset,
    ContextAssetSearchResult,
    ContextAssetTag,
    ContextAssetType,
    ContextAssetVersion,
    LifecycleState,
)

# Collection names in Typesense
ASSET_COLLECTION = "kai_context_assets"
VERSION_COLLECTION = "kai_context_asset_versions"
TAG_COLLECTION = "kai_context_asset_tags"


class ContextAssetRepository:
    """Repository for managing context assets in Typesense storage.

    Provides:
    - CRUD operations for context assets
    - Version tracking with immutable versions
    - Tag management
    - Indexed queries on db_connection_id, asset_type, lifecycle_state
    """

    def __init__(self, storage: Storage):
        self.storage = storage

    # ===== Context Asset CRUD =====

    def insert(self, asset: ContextAsset) -> ContextAsset:
        """Insert a new context asset."""
        asset_dict = asset.model_dump(exclude={"id"}, mode="json")
        # Serialize enums to strings and content dict to JSON
        asset_dict["asset_type"] = asset.asset_type.value
        asset_dict["lifecycle_state"] = asset.lifecycle_state.value
        asset_dict["content"] = json.dumps(asset_dict["content"])

        asset.id = str(self.storage.insert_one(ASSET_COLLECTION, asset_dict))
        return asset

    def find_by_id(self, id: str) -> ContextAsset | None:
        """Find an asset by its Typesense ID."""
        row = self.storage.find_one(ASSET_COLLECTION, {"id": id})
        if not row:
            return None
        return self._deserialize_asset(row)

    def find_by_key(
        self,
        db_connection_id: str,
        asset_type: ContextAssetType,
        canonical_key: str,
        version: str = "1.0.0",
    ) -> ContextAsset | None:
        """Find an asset by its unique key.

        Args:
            db_connection_id: Database connection ID.
            asset_type: Type of asset.
            canonical_key: Unique key for the asset.
            version: Version string (defaults to "1.0.0").

        Returns:
            The asset if found, None otherwise.
        """
        row = self.storage.find_one(
            ASSET_COLLECTION,
            {
                "db_connection_id": db_connection_id,
                "asset_type": asset_type.value,
                "canonical_key": canonical_key,
                "version": version,
            },
        )
        if not row:
            return None
        return self._deserialize_asset(row)

    def find_latest_version(
        self,
        db_connection_id: str,
        asset_type: ContextAssetType,
        canonical_key: str,
    ) -> ContextAsset | None:
        """Find the latest version of an asset by key.

        Returns the asset with the highest version number.
        """
        assets = self.find_by(
            {
                "db_connection_id": db_connection_id,
                "asset_type": asset_type.value,
                "canonical_key": canonical_key,
            },
            sort=["version:desc"],
            limit=1,
        )
        return assets[0] if assets else None

    def find_by(
        self,
        filter: dict,
        sort: list | None = None,
        page: int = 0,
        limit: int = 0,
    ) -> list[ContextAsset]:
        """Find assets matching a filter.

        Args:
            filter: Dictionary of field=value pairs.
            sort: Optional sort criteria (e.g., ["updated_at:desc"]).
            page: Page number for pagination.
            limit: Max results per page (0 = no limit).

        Returns:
            List of matching assets.
        """
        rows = self.storage.find(
            ASSET_COLLECTION,
            filter,
            sort=sort,
            page=page,
            limit=limit,
        )
        return [self._deserialize_asset(row) for row in rows]

    def find_by_connection(
        self,
        db_connection_id: str,
        asset_type: ContextAssetType | None = None,
        lifecycle_state: LifecycleState | None = None,
        limit: int = 100,
    ) -> list[ContextAsset]:
        """Find all assets for a database connection.

        Args:
            db_connection_id: Database connection ID.
            asset_type: Optional filter by asset type.
            lifecycle_state: Optional filter by lifecycle state.
            limit: Maximum results.

        Returns:
            List of matching assets.
        """
        filter_dict = {"db_connection_id": db_connection_id}
        if asset_type:
            filter_dict["asset_type"] = asset_type.value
        if lifecycle_state:
            filter_dict["lifecycle_state"] = lifecycle_state.value

        return self.find_by(filter_dict, limit=limit)

    def find_by_type(
        self,
        db_connection_id: str,
        asset_type: ContextAssetType,
        lifecycle_state: LifecycleState | None = None,
        limit: int = 100,
    ) -> list[ContextAsset]:
        """Find all assets of a specific type.

        Indexed query on (db_connection_id, asset_type).
        """
        return self.find_by_connection(
            db_connection_id,
            asset_type=asset_type,
            lifecycle_state=lifecycle_state,
            limit=limit,
        )

    def find_by_state(
        self,
        db_connection_id: str,
        lifecycle_state: LifecycleState,
        limit: int = 100,
    ) -> list[ContextAsset]:
        """Find all assets in a specific lifecycle state.

        Indexed query on (db_connection_id, lifecycle_state).
        """
        return self.find_by_connection(
            db_connection_id,
            lifecycle_state=lifecycle_state,
            limit=limit,
        )

    def search(
        self,
        db_connection_id: str,
        query: str,
        asset_type: ContextAssetType | None = None,
        lifecycle_state: LifecycleState | None = None,
        limit: int = 10,
    ) -> list[ContextAssetSearchResult]:
        """Search assets by text query.

        Args:
            db_connection_id: Database connection ID.
            query: Search query text.
            asset_type: Optional filter by asset type.
            lifecycle_state: Optional filter by lifecycle state.
            limit: Maximum results.

        Returns:
            List of search results with relevance scores.
        """
        filter_by = f"db_connection_id:={db_connection_id}"
        if asset_type:
            filter_by += f"&&asset_type:={asset_type.value}"
        if lifecycle_state:
            filter_by += f"&&lifecycle_state:={lifecycle_state.value}"

        rows = self.storage.full_text_search(
            ASSET_COLLECTION,
            query,
            columns=["name", "content_text", "canonical_key"],
            filter_by=filter_by,
            limit=limit,
        )

        results = []
        for row in rows:
            asset = self._deserialize_asset(row)
            score = row.get("score", 0.5)
            results.append(
                ContextAssetSearchResult(
                    asset=asset,
                    score=score,
                    match_type="keyword",
                )
            )
        return results

    def update(self, asset: ContextAsset) -> ContextAsset:
        """Update an existing asset.

        Note: This creates a new version in the version history.
        """
        asset.updated_at = datetime.now(timezone.utc).isoformat()
        update_data = asset.model_dump(exclude={"id"}, mode="json")
        update_data["asset_type"] = asset.asset_type.value
        update_data["lifecycle_state"] = asset.lifecycle_state.value
        update_data["content"] = json.dumps(update_data["content"])

        self.storage.update_or_create(
            ASSET_COLLECTION,
            {"id": asset.id},
            update_data,
        )
        return asset

    def delete(self, id: str) -> int:
        """Delete an asset by ID."""
        return self.storage.delete_by_id(ASSET_COLLECTION, id)

    def delete_by_key(
        self,
        db_connection_id: str,
        asset_type: ContextAssetType,
        canonical_key: str,
        version: str | None = None,
    ) -> bool:
        """Delete an asset by its unique key.

        If version is None, deletes all versions of the asset.
        """
        if version:
            asset = self.find_by_key(db_connection_id, asset_type, canonical_key, version)
            if asset and asset.id:
                return self.delete(asset.id) > 0
            return False
        else:
            # Delete all versions
            return (
                self.storage.delete_by_filter(
                    ASSET_COLLECTION,
                    {
                        "db_connection_id": db_connection_id,
                        "asset_type": asset_type.value,
                        "canonical_key": canonical_key,
                    },
                )
                > 0
            )

    # ===== Version Management =====

    def create_version(
        self,
        asset: ContextAsset,
        change_summary: str | None = None,
    ) -> ContextAssetVersion:
        """Create an immutable version snapshot for an asset.

        Args:
            asset: The asset to version.
            change_summary: Optional description of changes.

        Returns:
            The created version record.
        """
        version = ContextAssetVersion(
            asset_id=asset.id,
            version=asset.version,
            name=asset.name,
            description=asset.description,
            content=asset.content,
            content_text=asset.content_text,
            lifecycle_state=asset.lifecycle_state,
            author=asset.author,
            change_summary=change_summary,
        )

        version_dict = version.model_dump(exclude={"id"}, mode="json")
        version_dict["lifecycle_state"] = version.lifecycle_state.value
        version_dict["content"] = json.dumps(version_dict["content"])

        version.id = str(
            self.storage.insert_one(VERSION_COLLECTION, version_dict)
        )
        return version

    def find_versions(self, asset_id: str) -> list[ContextAssetVersion]:
        """Find all versions for an asset.

        Returns versions in descending order (newest first).
        """
        rows = self.storage.find(
            VERSION_COLLECTION,
            {"asset_id": asset_id},
            sort=["version:desc"],
        )
        return [self._deserialize_version(row) for row in rows]

    def find_version(
        self, asset_id: str, version: str
    ) -> ContextAssetVersion | None:
        """Find a specific version of an asset."""
        row = self.storage.find_one(
            VERSION_COLLECTION,
            {"asset_id": asset_id, "version": version},
        )
        if not row:
            return None
        return self._deserialize_version(row)

    # ===== Tag Management =====

    def create_tag(
        self,
        name: str,
        category: str | None = None,
        description: str | None = None,
    ) -> ContextAssetTag:
        """Create a new tag."""
        tag = ContextAssetTag(
            name=name,
            category=category,
            description=description,
        )
        tag_dict = tag.model_dump(exclude={"id"}, mode="json")
        tag.id = str(self.storage.insert_one(TAG_COLLECTION, tag_dict))
        return tag

    def find_tag(self, name: str) -> ContextAssetTag | None:
        """Find a tag by name."""
        row = self.storage.find_one(TAG_COLLECTION, {"name": name})
        if not row:
            return None
        return ContextAssetTag(**row)

    def find_all_tags(self, limit: int = 100) -> list[ContextAssetTag]:
        """Find all tags, ordered by usage count."""
        rows = self.storage.find(
            TAG_COLLECTION,
            {},
            sort=["usage_count:desc"],
            limit=limit,
        )
        return [ContextAssetTag(**row) for row in rows]

    def find_tags_by_category(self, category: str) -> list[ContextAssetTag]:
        """Find all tags in a specific category."""
        rows = self.storage.find(TAG_COLLECTION, {"category": category})
        return [ContextAssetTag(**row) for row in rows]

    def update_tag_usage(self, tag_name: str) -> ContextAssetTag | None:
        """Increment the usage count for a tag."""
        tag = self.find_tag(tag_name)
        if not tag:
            return None

        tag.usage_count += 1
        tag.last_used_at = datetime.now(timezone.utc).isoformat()

        self.storage.update_or_create(
            TAG_COLLECTION,
            {"id": tag.id},
            tag.model_dump(exclude={"id"}, mode="json"),
        )
        return tag

    # ===== Helper Methods =====

    def _deserialize_asset(self, row: dict) -> ContextAsset:
        """Deserialize a row from Typesense to ContextAsset."""
        if isinstance(row.get("content"), str):
            row["content"] = json.loads(row["content"])
        # Ensure enum values are properly typed
        if "asset_type" in row and isinstance(row["asset_type"], str):
            row["asset_type"] = ContextAssetType(row["asset_type"])
        if "lifecycle_state" in row and isinstance(row["lifecycle_state"], str):
            row["lifecycle_state"] = LifecycleState(row["lifecycle_state"])
        return ContextAsset(**row)

    def _deserialize_version(self, row: dict) -> ContextAssetVersion:
        """Deserialize a row from Typesense to ContextAssetVersion."""
        if isinstance(row.get("content"), str):
            row["content"] = json.loads(row["content"])
        if "lifecycle_state" in row and isinstance(row["lifecycle_state"], str):
            row["lifecycle_state"] = LifecycleState(row["lifecycle_state"])
        return ContextAssetVersion(**row)
