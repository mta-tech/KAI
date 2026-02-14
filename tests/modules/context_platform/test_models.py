# tests/modules/context_platform/test_models.py
"""Tests for Context Platform Models."""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.modules.context_platform.models.asset import (
    ContextAsset,
    ContextAssetVersion,
    ContextAssetTag,
    LifecycleState,
    ContextAssetType,
    ContextAssetSearchResult,
)


class TestContextAsset:
    """Tests for ContextAsset model."""

    def test_create_context_asset_with_required_fields(self):
        """Should create ContextAsset with required fields."""
        asset = ContextAsset(
            db_connection_id="db_456",
            asset_type=ContextAssetType.TABLE_DESCRIPTION,
            canonical_key="sales_table",
            name="Sales Table",
            content={"columns": ["id", "name", "amount"]},
            content_text="Sales table with id, name, and amount columns",
        )
        assert asset.db_connection_id == "db_456"
        assert asset.asset_type == ContextAssetType.TABLE_DESCRIPTION
        assert asset.lifecycle_state == LifecycleState.DRAFT

    def test_validate_asset_type_enum(self):
        """Should validate asset_type is valid enum value."""
        with pytest.raises(ValidationError):
            ContextAsset(
                db_connection_id="db_456",
                asset_type="invalid_type",  # type: ignore
                canonical_key="test",
                name="Test",
                content={},
                content_text="test",
            )


class TestContextAssetVersion:
    """Tests for ContextAssetVersion model."""

    def test_create_version_with_required_fields(self):
        """Should create ContextAssetVersion with required fields."""
        version = ContextAssetVersion(
            asset_id="asset_123",
            version="1.0.0",
            name="Sales Table",
            content={"columns": ["id", "name"]},
            content_text="Sales table",
        )
        assert version.asset_id == "asset_123"
        assert version.version == "1.0.0"


class TestContextAssetTag:
    """Tests for ContextAssetTag model."""

    def test_create_tag_with_name(self):
        """Should create tag with name."""
        tag = ContextAssetTag(name="sales")
        assert tag.name == "sales"


class TestLifecycleState:
    """Tests for LifecycleState enum."""

    def test_have_all_required_states(self):
        """Should have all required lifecycle states."""
        assert LifecycleState.DRAFT.value == "draft"
        assert LifecycleState.VERIFIED.value == "verified"
        assert LifecycleState.PUBLISHED.value == "published"
        assert LifecycleState.DEPRECATED.value == "deprecated"


class TestContextAssetType:
    """Tests for ContextAssetType enum."""

    def test_have_all_required_types(self):
        """Should have all required asset types."""
        assert ContextAssetType.TABLE_DESCRIPTION.value == "table_description"
        assert ContextAssetType.GLOSSARY.value == "glossary"
        assert ContextAssetType.INSTRUCTION.value == "instruction"
        assert ContextAssetType.SKILL.value == "skill"


class TestContextAssetSearchResult:
    """Tests for ContextAssetSearchResult model."""

    def test_create_search_result(self):
        """Should create search result with asset and score."""
        asset = ContextAsset(
            db_connection_id="db_456",
            asset_type=ContextAssetType.GLOSSARY,
            canonical_key="test",
            name="Test",
            content={},
            content_text="test",
        )
        result = ContextAssetSearchResult(asset=asset, score=0.85)
        assert result.asset == asset
        assert result.score == 0.85
