"""Tests for MDL validators."""
import pytest
from app.modules.mdl.validators import MDLValidator


class TestMDLValidator:
    """Test MDL validation functionality."""

    def test_validate_valid_minimal_manifest(self):
        """Test validation of a minimal valid manifest."""
        manifest = {
            "catalog": "test_catalog",
            "schema": "test_schema",
            "models": [],
            "relationships": [],
            "metrics": [],
            "views": [],
        }
        is_valid, errors = MDLValidator.validate(manifest)
        assert is_valid is True
        assert errors == []

    def test_validate_valid_manifest_with_model(self):
        """Test validation of a manifest with a model."""
        manifest = {
            "catalog": "test_catalog",
            "schema": "test_schema",
            "models": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "INTEGER"},
                        {"name": "name", "type": "VARCHAR"},
                    ],
                    "primaryKey": "id",
                }
            ],
            "relationships": [],
        }
        is_valid, errors = MDLValidator.validate(manifest)
        assert is_valid is True
        assert errors == []

    def test_validate_invalid_missing_catalog(self):
        """Test validation fails when catalog is missing."""
        manifest = {
            "schema": "test_schema",
            "models": [],
        }
        is_valid, errors = MDLValidator.validate(manifest)
        assert is_valid is False
        assert len(errors) > 0
        assert any("catalog" in err.lower() for err in errors)

    def test_validate_invalid_relationship_join_type(self):
        """Test validation fails for invalid join type."""
        manifest = {
            "catalog": "test_catalog",
            "schema": "test_schema",
            "models": [],
            "relationships": [
                {
                    "name": "invalid_rel",
                    "models": ["a", "b"],
                    "joinType": "INVALID_TYPE",
                    "condition": "a.id = b.a_id",
                }
            ],
        }
        is_valid, errors = MDLValidator.validate(manifest)
        assert is_valid is False
        assert len(errors) > 0

    def test_validate_or_raise_valid(self):
        """Test validate_or_raise doesn't raise for valid manifest."""
        manifest = {
            "catalog": "test_catalog",
            "schema": "test_schema",
        }
        # Should not raise
        MDLValidator.validate_or_raise(manifest)

    def test_validate_or_raise_invalid(self):
        """Test validate_or_raise raises for invalid manifest."""
        manifest = {"models": []}  # Missing required fields
        with pytest.raises(Exception) as exc_info:
            MDLValidator.validate_or_raise(manifest)
        assert "validation failed" in str(exc_info.value).lower()
