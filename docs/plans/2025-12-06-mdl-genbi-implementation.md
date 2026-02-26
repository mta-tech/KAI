# MDL & GENBI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement MDL (Model Definition Language) semantic layer and GENBI (Generative Business Intelligence) capabilities in KAI, enabling unified schema management, chart generation, and narrative SQL answers.

**Architecture:** Build MDL as a new module following KAI's existing patterns (models/repositories/services). MDL will consolidate existing TableDescription, BusinessGlossary, and relationship data into a unified semantic manifest. GENBI adds chart generation (Vega-Lite) and SQL narrative answers as new modules.

**Tech Stack:** Python 3.11+, Pydantic, FastAPI, Typesense, jsonschema for validation, LangChain for LLM interactions.

---

## Phase 0: Alignment & Tooling

### Task 0.1: Create MDL Module Directory Structure

**Files:**
- Create: `app/modules/mdl/__init__.py`
- Create: `app/modules/mdl/models/__init__.py`
- Create: `app/modules/mdl/repositories/__init__.py`
- Create: `app/modules/mdl/services/__init__.py`
- Create: `app/modules/mdl/validators/__init__.py`
- Create: `app/modules/mdl/schema/`

**Step 1: Create the module directories**

```bash
mkdir -p app/modules/mdl/models
mkdir -p app/modules/mdl/repositories
mkdir -p app/modules/mdl/services
mkdir -p app/modules/mdl/validators
mkdir -p app/modules/mdl/schema
```

**Step 2: Create empty __init__.py files**

Create `app/modules/mdl/__init__.py`:
```python
"""MDL (Model Definition Language) module for semantic layer management."""
```

Create `app/modules/mdl/models/__init__.py`:
```python
"""MDL Pydantic models."""
```

Create `app/modules/mdl/repositories/__init__.py`:
```python
"""MDL data access layer."""
```

Create `app/modules/mdl/services/__init__.py`:
```python
"""MDL business logic services."""
```

Create `app/modules/mdl/validators/__init__.py`:
```python
"""MDL validation utilities."""
```

**Step 3: Commit**

```bash
git add app/modules/mdl/
git commit -m "feat(mdl): create MDL module directory structure"
```

---

### Task 0.2: Add jsonschema Dependency

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add the dependency to pyproject.toml**

Add to the dependencies section:
```toml
"jsonschema>=4.20.0",
```

**Step 2: Install the dependency**

Run: `uv sync`
Expected: Dependency installed successfully

**Step 3: Verify installation**

Run: `uv run python -c "import jsonschema; print(jsonschema.__version__)"`
Expected: Version number printed (e.g., 4.20.0)

**Step 4: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add jsonschema dependency for MDL validation"
```

---

### Task 0.3: Create MDL JSON Schema File

**Files:**
- Create: `app/modules/mdl/schema/mdl.schema.json`

**Step 1: Create the JSON Schema file**

Create `app/modules/mdl/schema/mdl.schema.json`:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://kai.dev/mdl.schema.json",
  "title": "KAI MDL Manifest Schema",
  "type": "object",
  "properties": {
    "catalog": {
      "type": "string",
      "description": "Database catalog name"
    },
    "schema": {
      "type": "string",
      "description": "Database schema name"
    },
    "dataSource": {
      "type": "string",
      "enum": ["postgresql", "mysql", "bigquery", "duckdb", "sqlite", "snowflake", "clickhouse"],
      "description": "Type of data source"
    },
    "models": {
      "type": "array",
      "items": { "$ref": "#/$defs/model" },
      "description": "Array of data models (tables)"
    },
    "relationships": {
      "type": "array",
      "items": { "$ref": "#/$defs/relationship" },
      "description": "Array of relationships between models"
    },
    "metrics": {
      "type": "array",
      "items": { "$ref": "#/$defs/metric" },
      "description": "Array of business metrics"
    },
    "views": {
      "type": "array",
      "items": { "$ref": "#/$defs/view" },
      "description": "Array of saved views"
    },
    "enumDefinitions": {
      "type": "array",
      "items": { "$ref": "#/$defs/enumDefinition" },
      "description": "Array of enum definitions"
    }
  },
  "required": ["catalog", "schema"],
  "$defs": {
    "model": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "tableReference": { "$ref": "#/$defs/tableReference" },
        "refSql": { "type": "string" },
        "columns": {
          "type": "array",
          "items": { "$ref": "#/$defs/column" }
        },
        "primaryKey": { "type": "string" },
        "cached": { "type": "boolean", "default": false },
        "refreshTime": { "type": "string" },
        "properties": { "$ref": "#/$defs/properties" }
      },
      "required": ["name", "columns"]
    },
    "tableReference": {
      "type": "object",
      "properties": {
        "catalog": { "type": "string" },
        "schema": { "type": "string" },
        "table": { "type": "string" }
      },
      "required": ["table"]
    },
    "column": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "type": { "type": "string" },
        "notNull": { "type": "boolean", "default": false },
        "isCalculated": { "type": "boolean", "default": false },
        "expression": { "type": "string" },
        "relationship": { "type": "string" },
        "isHidden": { "type": "boolean", "default": false },
        "properties": { "$ref": "#/$defs/properties" }
      },
      "required": ["name", "type"]
    },
    "relationship": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "models": {
          "type": "array",
          "items": { "type": "string" },
          "minItems": 2,
          "maxItems": 2
        },
        "joinType": {
          "type": "string",
          "enum": ["ONE_TO_ONE", "ONE_TO_MANY", "MANY_TO_ONE", "MANY_TO_MANY"]
        },
        "condition": { "type": "string" },
        "properties": { "$ref": "#/$defs/properties" }
      },
      "required": ["name", "models", "joinType", "condition"]
    },
    "metric": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "baseObject": { "type": "string" },
        "dimension": {
          "type": "array",
          "items": { "$ref": "#/$defs/column" }
        },
        "measure": {
          "type": "array",
          "items": { "$ref": "#/$defs/column" }
        },
        "timeGrain": {
          "type": "array",
          "items": { "$ref": "#/$defs/timeGrain" }
        },
        "cached": { "type": "boolean", "default": false },
        "refreshTime": { "type": "string" },
        "properties": { "$ref": "#/$defs/properties" }
      },
      "required": ["name", "baseObject"]
    },
    "timeGrain": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "refColumn": { "type": "string" },
        "dateParts": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": ["YEAR", "QUARTER", "MONTH", "WEEK", "DAY", "HOUR", "MINUTE"]
          }
        }
      },
      "required": ["name", "refColumn", "dateParts"]
    },
    "view": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "statement": { "type": "string" },
        "properties": { "$ref": "#/$defs/properties" }
      },
      "required": ["name", "statement"]
    },
    "enumDefinition": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "values": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "value": { "type": "string" },
              "properties": { "$ref": "#/$defs/properties" }
            },
            "required": ["name"]
          }
        },
        "properties": { "$ref": "#/$defs/properties" }
      },
      "required": ["name", "values"]
    },
    "properties": {
      "type": "object",
      "properties": {
        "description": { "type": "string" },
        "displayName": { "type": "string" }
      },
      "additionalProperties": true
    }
  }
}
```

**Step 2: Commit**

```bash
git add app/modules/mdl/schema/mdl.schema.json
git commit -m "feat(mdl): add MDL JSON Schema definition"
```

---

### Task 0.4: Create MDL Validator Test

**Files:**
- Create: `tests/modules/mdl/__init__.py`
- Create: `tests/modules/mdl/test_validators.py`

**Step 1: Create test directory**

```bash
mkdir -p tests/modules/mdl
touch tests/modules/mdl/__init__.py
```

**Step 2: Write the failing test**

Create `tests/modules/mdl/test_validators.py`:
```python
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
```

**Step 3: Run test to verify it fails**

Run: `uv run pytest tests/modules/mdl/test_validators.py -v`
Expected: FAIL with ImportError (MDLValidator doesn't exist yet)

**Step 4: Commit the failing test**

```bash
git add tests/modules/mdl/
git commit -m "test(mdl): add failing tests for MDL validator"
```

---

### Task 0.5: Implement MDL Validator

**Files:**
- Modify: `app/modules/mdl/validators/__init__.py`

**Step 1: Implement the validator**

Update `app/modules/mdl/validators/__init__.py`:
```python
"""MDL validation utilities."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError


class MDLValidator:
    """Validate MDL manifests against JSON Schema."""

    _schema: dict | None = None
    _schema_path = Path(__file__).parent.parent / "schema" / "mdl.schema.json"

    @classmethod
    def get_schema(cls) -> dict:
        """Load and cache the MDL JSON schema."""
        if cls._schema is None:
            with open(cls._schema_path) as f:
                cls._schema = json.load(f)
        return cls._schema

    @classmethod
    def validate(cls, manifest: dict) -> tuple[bool, list[str]]:
        """
        Validate MDL manifest against schema.

        Args:
            manifest: MDL manifest dictionary to validate.

        Returns:
            Tuple of (is_valid, list_of_error_messages).
        """
        schema = cls.get_schema()
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(manifest))

        if errors:
            error_messages = [
                f"{'.'.join(str(p) for p in e.path) or 'root'}: {e.message}"
                for e in errors
            ]
            return False, error_messages

        return True, []

    @classmethod
    def validate_or_raise(cls, manifest: dict) -> None:
        """
        Validate and raise ValidationError if invalid.

        Args:
            manifest: MDL manifest dictionary to validate.

        Raises:
            ValidationError: If the manifest is invalid.
        """
        is_valid, errors = cls.validate(manifest)
        if not is_valid:
            raise ValidationError(f"MDL validation failed: {errors}")
```

**Step 2: Run test to verify it passes**

Run: `uv run pytest tests/modules/mdl/test_validators.py -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add app/modules/mdl/validators/__init__.py
git commit -m "feat(mdl): implement MDL validator with JSON Schema validation"
```

---

### Task 0.6: Create Typesense Schema for MDL Manifests

**Files:**
- Create: `app/data/db/schemas/mdl_manifests.json`

**Step 1: Create the Typesense schema**

Create `app/data/db/schemas/mdl_manifests.json`:
```json
{
    "name": "mdl_manifests",
    "enable_nested_fields": true,
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "db_connection_id", "type": "string", "reference": "database_connections.id"},
        {"name": "catalog", "type": "string"},
        {"name": "schema", "type": "string"},
        {"name": "data_source", "type": "string", "optional": true},
        {"name": "mdl_hash", "type": "string", "optional": true},
        {"name": "manifest_json", "type": "string"},
        {"name": "model_count", "type": "int32", "optional": true},
        {"name": "relationship_count", "type": "int32", "optional": true},
        {"name": "metric_count", "type": "int32", "optional": true},
        {"name": "view_count", "type": "int32", "optional": true},
        {"name": "metadata", "type": "object", "optional": true},
        {"name": "created_at", "type": "string"},
        {"name": "updated_at", "type": "string", "optional": true}
    ]
}
```

**Step 2: Commit**

```bash
git add app/data/db/schemas/mdl_manifests.json
git commit -m "feat(mdl): add Typesense schema for MDL manifests"
```

---

## Phase 1: MDL Schema & Models

### Task 1.1: Create MDL Pydantic Models Test

**Files:**
- Create: `tests/modules/mdl/test_models.py`

**Step 1: Write the failing test**

Create `tests/modules/mdl/test_models.py`:
```python
"""Tests for MDL Pydantic models."""
import pytest
from pydantic import ValidationError


class TestMDLModels:
    """Test MDL model definitions."""

    def test_mdl_column_basic(self):
        """Test basic MDL column creation."""
        from app.modules.mdl.models import MDLColumn

        col = MDLColumn(name="user_id", type="INTEGER")
        assert col.name == "user_id"
        assert col.type == "INTEGER"
        assert col.is_calculated is False
        assert col.not_null is False

    def test_mdl_column_calculated(self):
        """Test calculated column."""
        from app.modules.mdl.models import MDLColumn

        col = MDLColumn(
            name="total_orders",
            type="INTEGER",
            is_calculated=True,
            expression="COUNT(orders.id)",
            relationship="CustomerOrders",
        )
        assert col.is_calculated is True
        assert col.expression == "COUNT(orders.id)"
        assert col.relationship == "CustomerOrders"

    def test_mdl_model_basic(self):
        """Test basic MDL model creation."""
        from app.modules.mdl.models import MDLColumn, MDLModel, TableReference

        model = MDLModel(
            name="users",
            table_reference=TableReference(schema="public", table="users"),
            columns=[
                MDLColumn(name="id", type="INTEGER"),
                MDLColumn(name="name", type="VARCHAR"),
            ],
            primary_key="id",
        )
        assert model.name == "users"
        assert len(model.columns) == 2
        assert model.primary_key == "id"
        assert model.cached is False

    def test_mdl_relationship(self):
        """Test MDL relationship creation."""
        from app.modules.mdl.models import JoinType, MDLRelationship

        rel = MDLRelationship(
            name="CustomerOrders",
            models=["customers", "orders"],
            join_type=JoinType.ONE_TO_MANY,
            condition="customers.id = orders.customer_id",
        )
        assert rel.name == "CustomerOrders"
        assert rel.models == ["customers", "orders"]
        assert rel.join_type == JoinType.ONE_TO_MANY

    def test_mdl_metric(self):
        """Test MDL metric creation."""
        from app.modules.mdl.models import MDLColumn, MDLMetric

        metric = MDLMetric(
            name="revenue_metrics",
            base_object="order_items",
            dimension=[MDLColumn(name="order_date", type="TIMESTAMP")],
            measure=[
                MDLColumn(
                    name="total_revenue",
                    type="DECIMAL",
                    is_calculated=True,
                    expression="SUM(price * quantity)",
                )
            ],
        )
        assert metric.name == "revenue_metrics"
        assert metric.base_object == "order_items"
        assert len(metric.dimension) == 1
        assert len(metric.measure) == 1

    def test_mdl_view(self):
        """Test MDL view creation."""
        from app.modules.mdl.models import MDLView

        view = MDLView(
            name="monthly_revenue",
            statement="SELECT DATE_TRUNC('month', order_date) as month, SUM(revenue) FROM orders GROUP BY 1",
            properties={"question": "What is the monthly revenue?"},
        )
        assert view.name == "monthly_revenue"
        assert "SELECT" in view.statement

    def test_mdl_manifest_creation(self):
        """Test complete MDL manifest creation."""
        from app.modules.mdl.models import (
            JoinType,
            MDLColumn,
            MDLManifest,
            MDLModel,
            MDLRelationship,
            TableReference,
        )

        manifest = MDLManifest(
            db_connection_id="conn-123",
            catalog="my_db",
            schema="public",
            data_source="postgresql",
            models=[
                MDLModel(
                    name="users",
                    table_reference=TableReference(table="users"),
                    columns=[MDLColumn(name="id", type="INTEGER")],
                )
            ],
            relationships=[
                MDLRelationship(
                    name="UserOrders",
                    models=["users", "orders"],
                    join_type=JoinType.ONE_TO_MANY,
                    condition="users.id = orders.user_id",
                )
            ],
        )
        assert manifest.catalog == "my_db"
        assert len(manifest.models) == 1
        assert len(manifest.relationships) == 1
        assert manifest.mdl_hash is None  # Not computed yet

    def test_mdl_manifest_to_dict(self):
        """Test MDL manifest serialization."""
        from app.modules.mdl.models import MDLManifest

        manifest = MDLManifest(
            db_connection_id="conn-123",
            catalog="my_db",
            schema="public",
        )
        data = manifest.model_dump()
        assert data["catalog"] == "my_db"
        assert data["schema"] == "public"
        assert "models" in data
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/modules/mdl/test_models.py -v`
Expected: FAIL with ImportError (models don't exist yet)

**Step 3: Commit the failing test**

```bash
git add tests/modules/mdl/test_models.py
git commit -m "test(mdl): add failing tests for MDL Pydantic models"
```

---

### Task 1.2: Implement MDL Pydantic Models

**Files:**
- Modify: `app/modules/mdl/models/__init__.py`

**Step 1: Implement the models**

Update `app/modules/mdl/models/__init__.py`:
```python
"""MDL Pydantic models for semantic layer definition."""
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class JoinType(str, Enum):
    """Relationship join types."""

    ONE_TO_ONE = "ONE_TO_ONE"
    ONE_TO_MANY = "ONE_TO_MANY"
    MANY_TO_ONE = "MANY_TO_ONE"
    MANY_TO_MANY = "MANY_TO_MANY"


class MDLColumn(BaseModel):
    """Column definition in MDL model."""

    name: str
    type: str
    relationship: str | None = None
    is_calculated: bool = False
    not_null: bool = False
    expression: str | None = None
    is_hidden: bool = False
    properties: dict[str, Any] = Field(default_factory=dict)


class TableReference(BaseModel):
    """Reference to a physical database table."""

    catalog: str | None = None
    schema: str | None = None
    table: str


class MDLModel(BaseModel):
    """Data model (table) definition in MDL."""

    name: str
    table_reference: TableReference | None = None
    ref_sql: str | None = None
    columns: list[MDLColumn] = Field(default_factory=list)
    primary_key: str | None = None
    cached: bool = False
    refresh_time: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)


class MDLRelationship(BaseModel):
    """Relationship between two models."""

    name: str
    models: list[str]  # Exactly 2 models
    join_type: JoinType
    condition: str
    properties: dict[str, Any] = Field(default_factory=dict)


class TimeGrain(BaseModel):
    """Time grain configuration for metrics."""

    name: str
    ref_column: str
    date_parts: list[str]  # YEAR, QUARTER, MONTH, WEEK, DAY, etc.


class MDLMetric(BaseModel):
    """Business metric definition."""

    name: str
    base_object: str  # Reference to model
    dimension: list[MDLColumn] = Field(default_factory=list)
    measure: list[MDLColumn] = Field(default_factory=list)
    time_grain: list[TimeGrain] = Field(default_factory=list)
    cached: bool = False
    refresh_time: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)


class MDLView(BaseModel):
    """Saved SQL view definition."""

    name: str
    statement: str  # SQL statement
    properties: dict[str, Any] = Field(default_factory=dict)


class EnumValue(BaseModel):
    """Single value in an enum definition."""

    name: str
    value: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)


class MDLEnumDefinition(BaseModel):
    """Enum definition for controlled vocabularies."""

    name: str
    values: list[EnumValue]
    properties: dict[str, Any] = Field(default_factory=dict)


class MDLManifest(BaseModel):
    """Complete MDL Manifest for a database connection."""

    id: str | None = None
    db_connection_id: str
    catalog: str
    schema: str
    data_source: str | None = None
    models: list[MDLModel] = Field(default_factory=list)
    relationships: list[MDLRelationship] = Field(default_factory=list)
    metrics: list[MDLMetric] = Field(default_factory=list)
    views: list[MDLView] = Field(default_factory=list)
    enum_definitions: list[MDLEnumDefinition] = Field(default_factory=list)
    mdl_hash: str | None = None  # For caching/versioning
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str | None = None
```

**Step 2: Run test to verify it passes**

Run: `uv run pytest tests/modules/mdl/test_models.py -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add app/modules/mdl/models/__init__.py
git commit -m "feat(mdl): implement MDL Pydantic models"
```

---

### Task 1.3: Create MDL Repository Test

**Files:**
- Create: `tests/modules/mdl/test_repositories.py`

**Step 1: Write the failing test**

Create `tests/modules/mdl/test_repositories.py`:
```python
"""Tests for MDL repository."""
import pytest

from app.data.db.storage import Storage
from app.modules.mdl.models import MDLManifest, MDLModel, MDLColumn, TableReference
from app.modules.mdl.repositories import MDLManifestRepository
from app.server.config import Settings


@pytest.fixture(scope="module")
def storage():
    """Create storage instance for tests."""
    return Storage(Settings())


@pytest.fixture(scope="module")
def repository(storage):
    """Create repository instance for tests."""
    return MDLManifestRepository(storage)


@pytest.fixture
def sample_manifest():
    """Create a sample MDL manifest for testing."""
    return MDLManifest(
        db_connection_id="test-conn-123",
        catalog="test_catalog",
        schema="test_schema",
        data_source="postgresql",
        models=[
            MDLModel(
                name="users",
                table_reference=TableReference(table="users"),
                columns=[
                    MDLColumn(name="id", type="INTEGER"),
                    MDLColumn(name="name", type="VARCHAR"),
                ],
                primary_key="id",
            )
        ],
    )


class TestMDLManifestRepository:
    """Test MDL manifest repository operations."""

    def test_insert_manifest(self, repository, sample_manifest):
        """Test inserting a new manifest."""
        result = repository.insert(sample_manifest)
        assert result.id is not None
        assert result.db_connection_id == "test-conn-123"

        # Cleanup
        repository.delete_by_id(result.id)

    def test_find_by_id(self, repository, sample_manifest):
        """Test finding manifest by ID."""
        inserted = repository.insert(sample_manifest)

        found = repository.find_by_id(inserted.id)
        assert found is not None
        assert found.id == inserted.id
        assert found.catalog == "test_catalog"

        # Cleanup
        repository.delete_by_id(inserted.id)

    def test_find_by_connection(self, repository, sample_manifest):
        """Test finding manifest by database connection ID."""
        inserted = repository.insert(sample_manifest)

        found = repository.get_by_connection(sample_manifest.db_connection_id)
        assert found is not None
        assert found.db_connection_id == sample_manifest.db_connection_id

        # Cleanup
        repository.delete_by_id(inserted.id)

    def test_update_manifest(self, repository, sample_manifest):
        """Test updating an existing manifest."""
        inserted = repository.insert(sample_manifest)
        inserted.catalog = "updated_catalog"

        updated = repository.update(inserted)
        assert updated.catalog == "updated_catalog"

        # Verify persistence
        found = repository.find_by_id(inserted.id)
        assert found.catalog == "updated_catalog"

        # Cleanup
        repository.delete_by_id(inserted.id)

    def test_delete_by_id(self, repository, sample_manifest):
        """Test deleting manifest by ID."""
        inserted = repository.insert(sample_manifest)
        repository.delete_by_id(inserted.id)

        found = repository.find_by_id(inserted.id)
        assert found is None

    def test_find_by_hash(self, repository, sample_manifest):
        """Test finding manifest by MDL hash."""
        sample_manifest.mdl_hash = "abc123hash"
        inserted = repository.insert(sample_manifest)

        found = repository.get_by_hash("abc123hash")
        assert found is not None
        assert found.mdl_hash == "abc123hash"

        # Cleanup
        repository.delete_by_id(inserted.id)
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/modules/mdl/test_repositories.py -v`
Expected: FAIL with ImportError (repository doesn't exist yet)

**Step 3: Commit the failing test**

```bash
git add tests/modules/mdl/test_repositories.py
git commit -m "test(mdl): add failing tests for MDL repository"
```

---

### Task 1.4: Implement MDL Repository

**Files:**
- Modify: `app/modules/mdl/repositories/__init__.py`

**Step 1: Implement the repository**

Update `app/modules/mdl/repositories/__init__.py`:
```python
"""MDL data access layer."""
import json
from datetime import datetime

from app.data.db.storage import Storage
from app.modules.mdl.models import MDLManifest

DB_COLLECTION = "mdl_manifests"


class MDLManifestRepository:
    """Repository for MDL manifest persistence."""

    def __init__(self, storage: Storage):
        self.storage = storage

    def insert(self, manifest: MDLManifest) -> MDLManifest:
        """
        Insert a new MDL manifest.

        Args:
            manifest: MDL manifest to insert.

        Returns:
            The inserted manifest with ID set.
        """
        manifest_dict = manifest.model_dump(exclude={"id"})
        # Store the full manifest as JSON string for complex nested structure
        manifest_dict["manifest_json"] = json.dumps(manifest.model_dump())
        manifest_dict["model_count"] = len(manifest.models)
        manifest_dict["relationship_count"] = len(manifest.relationships)
        manifest_dict["metric_count"] = len(manifest.metrics)
        manifest_dict["view_count"] = len(manifest.views)

        manifest.id = str(self.storage.insert_one(DB_COLLECTION, manifest_dict))
        return manifest

    def find_by_id(self, manifest_id: str) -> MDLManifest | None:
        """
        Find manifest by ID.

        Args:
            manifest_id: The manifest ID.

        Returns:
            The manifest if found, None otherwise.
        """
        row = self.storage.find_one(DB_COLLECTION, {"id": manifest_id})
        if not row:
            return None
        return self._row_to_manifest(row)

    def get_by_connection(self, db_connection_id: str) -> MDLManifest | None:
        """
        Get MDL manifest for a database connection.

        Args:
            db_connection_id: The database connection ID.

        Returns:
            The manifest if found, None otherwise.
        """
        results = self.storage.find(
            DB_COLLECTION,
            {"db_connection_id": db_connection_id},
            limit=1,
        )
        if not results:
            return None
        return self._row_to_manifest(results[0])

    def get_by_hash(self, mdl_hash: str) -> MDLManifest | None:
        """
        Get MDL manifest by hash (for caching).

        Args:
            mdl_hash: The MDL hash.

        Returns:
            The manifest if found, None otherwise.
        """
        results = self.storage.find(
            DB_COLLECTION,
            {"mdl_hash": mdl_hash},
            limit=1,
        )
        if not results:
            return None
        return self._row_to_manifest(results[0])

    def update(self, manifest: MDLManifest) -> MDLManifest:
        """
        Update an existing manifest.

        Args:
            manifest: The manifest to update (must have ID set).

        Returns:
            The updated manifest.
        """
        if not manifest.id:
            raise ValueError("Cannot update manifest without ID")

        manifest.updated_at = datetime.now().isoformat()
        manifest_dict = manifest.model_dump()
        manifest_dict["manifest_json"] = json.dumps(manifest.model_dump())
        manifest_dict["model_count"] = len(manifest.models)
        manifest_dict["relationship_count"] = len(manifest.relationships)
        manifest_dict["metric_count"] = len(manifest.metrics)
        manifest_dict["view_count"] = len(manifest.views)

        self.storage.update_or_create(
            DB_COLLECTION,
            {"id": manifest.id},
            manifest_dict,
        )
        return manifest

    def delete_by_id(self, manifest_id: str) -> None:
        """
        Delete manifest by ID.

        Args:
            manifest_id: The manifest ID to delete.
        """
        self.storage.delete_by_id(DB_COLLECTION, manifest_id)

    def _row_to_manifest(self, row: dict) -> MDLManifest:
        """Convert storage row to MDLManifest."""
        # If we have manifest_json, use it for full fidelity
        if "manifest_json" in row and row["manifest_json"]:
            manifest_data = json.loads(row["manifest_json"])
            manifest_data["id"] = row.get("id")
            return MDLManifest(**manifest_data)
        # Otherwise reconstruct from flat fields
        return MDLManifest(**row)
```

**Step 2: Run test to verify it passes**

Run: `uv run pytest tests/modules/mdl/test_repositories.py -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add app/modules/mdl/repositories/__init__.py
git commit -m "feat(mdl): implement MDL manifest repository"
```

---

### Task 1.5: Create MDL Builder Test

**Files:**
- Create: `tests/modules/mdl/test_mdl_builder.py`

**Step 1: Write the failing test**

Create `tests/modules/mdl/test_mdl_builder.py`:
```python
"""Tests for MDL builder service."""
import pytest

from app.modules.mdl.services.mdl_builder import MDLBuilder
from app.modules.mdl.models import JoinType
from app.modules.table_description.models import (
    ColumnDescription,
    ForeignKeyDetail,
    TableDescription,
)
from app.modules.business_glossary.models import BusinessGlossary
from app.modules.database_connection.models import DatabaseConnection


@pytest.fixture
def sample_table_descriptions():
    """Create sample table descriptions."""
    return [
        TableDescription(
            id="td-1",
            db_connection_id="conn-123",
            db_schema="public",
            table_name="customers",
            columns=[
                ColumnDescription(
                    name="id",
                    data_type="INTEGER",
                    is_primary_key=True,
                    description="Customer ID",
                ),
                ColumnDescription(
                    name="name",
                    data_type="VARCHAR",
                    description="Customer name",
                ),
            ],
            table_description="Customer information",
        ),
        TableDescription(
            id="td-2",
            db_connection_id="conn-123",
            db_schema="public",
            table_name="orders",
            columns=[
                ColumnDescription(
                    name="id",
                    data_type="INTEGER",
                    is_primary_key=True,
                    description="Order ID",
                ),
                ColumnDescription(
                    name="customer_id",
                    data_type="INTEGER",
                    description="Reference to customer",
                    foreign_key=ForeignKeyDetail(
                        reference_table="customers",
                        field_name="id",
                    ),
                ),
                ColumnDescription(
                    name="amount",
                    data_type="DECIMAL",
                    description="Order amount",
                ),
            ],
            table_description="Order records",
        ),
    ]


@pytest.fixture
def sample_glossaries():
    """Create sample business glossaries."""
    return [
        BusinessGlossary(
            id="bg-1",
            db_connection_id="conn-123",
            metric="total_revenue",
            alias=["revenue", "sales"],
            sql="SUM(orders.amount)",
        ),
    ]


@pytest.fixture
def sample_db_connection():
    """Create sample database connection."""
    return DatabaseConnection(
        id="conn-123",
        alias="test_db",
        dialect="postgresql",
        schemas=["public"],
    )


class TestMDLBuilder:
    """Test MDL builder functionality."""

    def test_build_manifest_from_tables(
        self, sample_table_descriptions, sample_glossaries, sample_db_connection
    ):
        """Test building MDL manifest from table descriptions."""
        builder = MDLBuilder(
            table_descriptions=sample_table_descriptions,
            business_glossaries=sample_glossaries,
            db_connection=sample_db_connection,
        )
        manifest = builder.build()

        assert manifest.db_connection_id == "conn-123"
        assert manifest.catalog == "test_db"
        assert manifest.schema == "public"
        assert manifest.data_source == "postgresql"
        assert len(manifest.models) == 2

    def test_build_models_from_tables(
        self, sample_table_descriptions, sample_glossaries, sample_db_connection
    ):
        """Test that models are correctly created from tables."""
        builder = MDLBuilder(
            table_descriptions=sample_table_descriptions,
            business_glossaries=sample_glossaries,
            db_connection=sample_db_connection,
        )
        manifest = builder.build()

        customers_model = next(m for m in manifest.models if m.name == "customers")
        assert customers_model.primary_key == "id"
        assert len(customers_model.columns) == 2
        assert customers_model.properties.get("description") == "Customer information"

    def test_build_relationships_from_fks(
        self, sample_table_descriptions, sample_glossaries, sample_db_connection
    ):
        """Test that relationships are extracted from foreign keys."""
        builder = MDLBuilder(
            table_descriptions=sample_table_descriptions,
            business_glossaries=sample_glossaries,
            db_connection=sample_db_connection,
        )
        manifest = builder.build()

        assert len(manifest.relationships) == 1
        rel = manifest.relationships[0]
        assert "orders" in rel.models
        assert "customers" in rel.models
        assert rel.join_type == JoinType.MANY_TO_ONE

    def test_build_metrics_from_glossary(
        self, sample_table_descriptions, sample_glossaries, sample_db_connection
    ):
        """Test that metrics are created from business glossary."""
        builder = MDLBuilder(
            table_descriptions=sample_table_descriptions,
            business_glossaries=sample_glossaries,
            db_connection=sample_db_connection,
        )
        manifest = builder.build()

        assert len(manifest.metrics) == 1
        metric = manifest.metrics[0]
        assert metric.name == "total_revenue"
        assert len(metric.measure) == 1

    def test_build_computes_hash(
        self, sample_table_descriptions, sample_glossaries, sample_db_connection
    ):
        """Test that MDL hash is computed."""
        builder = MDLBuilder(
            table_descriptions=sample_table_descriptions,
            business_glossaries=sample_glossaries,
            db_connection=sample_db_connection,
        )
        manifest = builder.build()

        assert manifest.mdl_hash is not None
        assert len(manifest.mdl_hash) == 32  # MD5 hex length
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/modules/mdl/test_mdl_builder.py -v`
Expected: FAIL with ImportError (MDLBuilder doesn't exist yet)

**Step 3: Commit the failing test**

```bash
git add tests/modules/mdl/test_mdl_builder.py
git commit -m "test(mdl): add failing tests for MDL builder"
```

---

### Task 1.6: Implement MDL Builder Service

**Files:**
- Create: `app/modules/mdl/services/mdl_builder.py`

**Step 1: Implement the MDL builder**

Create `app/modules/mdl/services/mdl_builder.py`:
```python
"""MDL Builder - Constructs MDL manifests from KAI data structures."""
import hashlib
import re

from app.modules.business_glossary.models import BusinessGlossary
from app.modules.database_connection.models import DatabaseConnection
from app.modules.mdl.models import (
    JoinType,
    MDLColumn,
    MDLManifest,
    MDLMetric,
    MDLModel,
    MDLRelationship,
    TableReference,
)
from app.modules.table_description.models import TableDescription


class MDLBuilder:
    """Build MDL manifest from KAI's existing data structures."""

    def __init__(
        self,
        table_descriptions: list[TableDescription],
        business_glossaries: list[BusinessGlossary],
        db_connection: DatabaseConnection,
    ):
        self.table_descriptions = table_descriptions
        self.business_glossaries = business_glossaries
        self.db_connection = db_connection
        self.manifest = MDLManifest(
            db_connection_id=db_connection.id,
            catalog=db_connection.alias,
            schema=db_connection.schemas[0] if db_connection.schemas else "public",
            data_source=db_connection.dialect,
        )

    def build(self) -> MDLManifest:
        """Build complete MDL manifest."""
        self._add_models()
        self._add_relationships()
        self._add_metrics()
        self._compute_hash()
        return self.manifest

    def _add_models(self) -> None:
        """Convert TableDescriptions to MDL Models."""
        for td in self.table_descriptions:
            model = MDLModel(
                name=td.table_name,
                table_reference=TableReference(
                    schema=td.db_schema,
                    table=td.table_name,
                ),
                columns=[
                    MDLColumn(
                        name=col.name,
                        type=col.data_type,
                        not_null=col.is_primary_key,
                        properties={
                            "description": col.description,
                            "low_cardinality": col.low_cardinality,
                            "categories": col.categories,
                        },
                    )
                    for col in td.columns
                ],
                primary_key=next(
                    (col.name for col in td.columns if col.is_primary_key),
                    None,
                ),
                properties={
                    "description": td.table_description,
                    "displayName": td.table_name,
                },
            )
            self.manifest.models.append(model)

    def _add_relationships(self) -> None:
        """Extract relationships from foreign keys."""
        for td in self.table_descriptions:
            for col in td.columns:
                if col.foreign_key:
                    rel = MDLRelationship(
                        name=f"{td.table_name}_{col.name}_fk",
                        models=[td.table_name, col.foreign_key.reference_table],
                        join_type=JoinType.MANY_TO_ONE,
                        condition=(
                            f'"{td.table_name}".{col.name} = '
                            f'"{col.foreign_key.reference_table}".{col.foreign_key.field_name}'
                        ),
                    )
                    self.manifest.relationships.append(rel)

    def _add_metrics(self) -> None:
        """Convert BusinessGlossary to MDL Metrics."""
        for bg in self.business_glossaries:
            base_table = self._extract_base_table(bg.sql)
            metric = MDLMetric(
                name=bg.metric,
                base_object=base_table,
                measure=[
                    MDLColumn(
                        name=bg.metric,
                        type="DECIMAL",
                        is_calculated=True,
                        expression=bg.sql,
                    )
                ],
                properties={
                    "alias": bg.alias,
                    "sql": bg.sql,
                },
            )
            self.manifest.metrics.append(metric)

    def _extract_base_table(self, sql: str) -> str:
        """Extract base table name from SQL expression."""
        # Simple regex to find table.column pattern
        match = re.search(r"(\w+)\.\w+", sql)
        if match:
            return match.group(1)
        return "unknown"

    def _compute_hash(self) -> None:
        """Compute MD5 hash of manifest for caching."""
        # Exclude id and timestamps from hash computation
        content = self.manifest.model_dump_json(
            exclude={"id", "created_at", "updated_at", "mdl_hash"}
        )
        self.manifest.mdl_hash = hashlib.md5(content.encode()).hexdigest()
```

**Step 2: Run test to verify it passes**

Run: `uv run pytest tests/modules/mdl/test_mdl_builder.py -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add app/modules/mdl/services/mdl_builder.py
git commit -m "feat(mdl): implement MDL builder service"
```

---

### Task 1.7: Create MDL Service Test

**Files:**
- Create: `tests/modules/mdl/test_services.py`

**Step 1: Write the failing test**

Create `tests/modules/mdl/test_services.py`:
```python
"""Tests for MDL service."""
import pytest
from unittest.mock import MagicMock, patch

from app.modules.mdl.services import MDLService
from app.modules.mdl.models import MDLManifest


class TestMDLService:
    """Test MDL service functionality."""

    @pytest.fixture
    def mock_storage(self):
        """Create mock storage."""
        return MagicMock()

    @pytest.fixture
    def mdl_service(self, mock_storage):
        """Create MDL service with mocked dependencies."""
        with patch("app.modules.mdl.services.TableDescriptionRepository") as mock_td_repo, \
             patch("app.modules.mdl.services.BusinessGlossaryRepository") as mock_bg_repo, \
             patch("app.modules.mdl.services.DatabaseConnectionRepository") as mock_db_repo:

            # Setup mock returns
            mock_db_repo.return_value.find_by_id.return_value = MagicMock(
                id="conn-123",
                alias="test_db",
                dialect="postgresql",
                schemas=["public"],
            )
            mock_td_repo.return_value.find_by.return_value = []
            mock_bg_repo.return_value.find_by.return_value = []

            service = MDLService(mock_storage)
            yield service

    def test_build_mdl(self, mdl_service):
        """Test building MDL from existing data."""
        with patch.object(mdl_service, "_build_manifest") as mock_build:
            mock_manifest = MDLManifest(
                db_connection_id="conn-123",
                catalog="test_db",
                schema="public",
            )
            mock_build.return_value = mock_manifest

            result = mdl_service.build_mdl("conn-123")
            assert result.db_connection_id == "conn-123"

    def test_get_mdl_cached(self, mdl_service):
        """Test getting cached MDL."""
        cached_manifest = MDLManifest(
            id="mdl-123",
            db_connection_id="conn-123",
            catalog="test_db",
            schema="public",
        )
        mdl_service.mdl_repo.get_by_connection = MagicMock(return_value=cached_manifest)

        result = mdl_service.get_mdl("conn-123")
        assert result.id == "mdl-123"

    def test_get_mdl_builds_if_not_cached(self, mdl_service):
        """Test that get_mdl builds if no cache exists."""
        mdl_service.mdl_repo.get_by_connection = MagicMock(return_value=None)

        with patch.object(mdl_service, "build_mdl") as mock_build:
            mock_manifest = MDLManifest(
                db_connection_id="conn-123",
                catalog="test_db",
                schema="public",
            )
            mock_build.return_value = mock_manifest

            result = mdl_service.get_mdl("conn-123")
            mock_build.assert_called_once_with("conn-123")

    def test_refresh_mdl(self, mdl_service):
        """Test force refresh of MDL."""
        with patch.object(mdl_service, "build_mdl") as mock_build:
            mock_manifest = MDLManifest(
                db_connection_id="conn-123",
                catalog="test_db",
                schema="public",
            )
            mock_build.return_value = mock_manifest

            result = mdl_service.refresh_mdl("conn-123")
            mock_build.assert_called_once_with("conn-123")

    def test_to_ddl(self, mdl_service):
        """Test converting MDL to DDL string."""
        from app.modules.mdl.models import MDLModel, MDLColumn, TableReference

        manifest = MDLManifest(
            db_connection_id="conn-123",
            catalog="test_db",
            schema="public",
            models=[
                MDLModel(
                    name="users",
                    table_reference=TableReference(table="users"),
                    columns=[
                        MDLColumn(name="id", type="INTEGER"),
                        MDLColumn(name="name", type="VARCHAR"),
                    ],
                    primary_key="id",
                    properties={"description": "User accounts"},
                )
            ],
        )

        ddl = mdl_service.to_ddl(manifest)
        assert "CREATE TABLE users" in ddl
        assert "id INTEGER" in ddl
        assert "name VARCHAR" in ddl
        assert "User accounts" in ddl
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/modules/mdl/test_services.py -v`
Expected: FAIL with ImportError (MDLService doesn't exist yet)

**Step 3: Commit the failing test**

```bash
git add tests/modules/mdl/test_services.py
git commit -m "test(mdl): add failing tests for MDL service"
```

---

### Task 1.8: Implement MDL Service

**Files:**
- Modify: `app/modules/mdl/services/__init__.py`

**Step 1: Implement the service**

Update `app/modules/mdl/services/__init__.py`:
```python
"""MDL business logic services."""
from app.data.db.storage import Storage
from app.modules.business_glossary.repositories import BusinessGlossaryRepository
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.mdl.models import MDLManifest
from app.modules.mdl.repositories import MDLManifestRepository
from app.modules.mdl.services.mdl_builder import MDLBuilder
from app.modules.table_description.repositories import TableDescriptionRepository


class MDLService:
    """Service for managing MDL manifests."""

    def __init__(self, storage: Storage):
        self.storage = storage
        self.mdl_repo = MDLManifestRepository(storage)
        self.table_repo = TableDescriptionRepository(storage)
        self.glossary_repo = BusinessGlossaryRepository(storage)
        self.db_conn_repo = DatabaseConnectionRepository(storage)

    def build_mdl(self, db_connection_id: str) -> MDLManifest:
        """
        Build MDL manifest from existing KAI data.

        Args:
            db_connection_id: The database connection ID.

        Returns:
            The built and saved MDL manifest.
        """
        manifest = self._build_manifest(db_connection_id)
        return self.mdl_repo.insert(manifest)

    def get_mdl(self, db_connection_id: str) -> MDLManifest | None:
        """
        Get cached MDL or build new one.

        Args:
            db_connection_id: The database connection ID.

        Returns:
            The MDL manifest if found or built.
        """
        manifest = self.mdl_repo.get_by_connection(db_connection_id)
        if not manifest:
            manifest = self.build_mdl(db_connection_id)
        return manifest

    def refresh_mdl(self, db_connection_id: str) -> MDLManifest:
        """
        Force rebuild MDL manifest.

        Args:
            db_connection_id: The database connection ID.

        Returns:
            The newly built MDL manifest.
        """
        # Delete existing manifest if any
        existing = self.mdl_repo.get_by_connection(db_connection_id)
        if existing and existing.id:
            self.mdl_repo.delete_by_id(existing.id)

        return self.build_mdl(db_connection_id)

    def to_ddl(self, manifest: MDLManifest) -> str:
        """
        Convert MDL to DDL string for LLM context.

        Args:
            manifest: The MDL manifest.

        Returns:
            DDL string representation.
        """
        ddl_parts = []

        for model in manifest.models:
            columns_str = ", ".join(
                [
                    f"{col.name} {col.type}"
                    + (" PRIMARY KEY" if model.primary_key == col.name else "")
                    + (" NOT NULL" if col.not_null else "")
                    for col in model.columns
                ]
            )
            ddl = f"CREATE TABLE {model.name} ({columns_str});"
            if model.properties.get("description"):
                ddl += f"\n-- {model.properties['description']}"
            ddl_parts.append(ddl)

        for rel in manifest.relationships:
            ddl_parts.append(
                f"-- Relationship: {rel.name} ({rel.join_type.value})\n"
                f"-- {rel.condition}"
            )

        return "\n\n".join(ddl_parts)

    def _build_manifest(self, db_connection_id: str) -> MDLManifest:
        """Internal method to build manifest from data."""
        db_conn = self.db_conn_repo.find_by_id(db_connection_id)
        if not db_conn:
            raise ValueError(f"Database connection {db_connection_id} not found")

        tables = self.table_repo.find_by({"db_connection_id": db_connection_id})
        glossaries = self.glossary_repo.find_by({"db_connection_id": db_connection_id})

        builder = MDLBuilder(
            table_descriptions=tables,
            business_glossaries=glossaries,
            db_connection=db_conn,
        )
        return builder.build()
```

**Step 2: Run test to verify it passes**

Run: `uv run pytest tests/modules/mdl/test_services.py -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add app/modules/mdl/services/__init__.py
git commit -m "feat(mdl): implement MDL service"
```

---

### Task 1.9: Create MDL API Endpoints Test

**Files:**
- Create: `tests/test_integration/test_int_mdl.py`

**Step 1: Write the failing test**

Create `tests/test_integration/test_int_mdl.py`:
```python
"""Integration tests for MDL API endpoints."""
import pytest
from fastapi.testclient import TestClient


class TestMDLAPIEndpoints:
    """Test MDL API endpoints."""

    @pytest.fixture(scope="class")
    def setup_test_data(self, client):
        """Setup test database connection."""
        # Create a test database connection
        response = client.post(
            "/api/v1/database-connections",
            json={
                "alias": "mdl_test_db",
                "dialect": "postgresql",
                "connection_uri": "postgresql://test:test@localhost:5432/test",
            },
        )
        if response.status_code == 201:
            conn_id = response.json()["id"]
            yield conn_id
            # Cleanup
            client.delete(f"/api/v1/database-connections/{conn_id}")
        else:
            yield None

    def test_build_mdl(self, client, setup_test_data):
        """Test building MDL manifest."""
        if not setup_test_data:
            pytest.skip("Test data setup failed")

        response = client.post(f"/api/v1/mdl/build/{setup_test_data}")
        assert response.status_code in [200, 201]
        data = response.json()
        assert "mdl_hash" in data

    def test_get_mdl(self, client, setup_test_data):
        """Test getting MDL manifest."""
        if not setup_test_data:
            pytest.skip("Test data setup failed")

        # First build the MDL
        client.post(f"/api/v1/mdl/build/{setup_test_data}")

        # Then get it
        response = client.get(f"/api/v1/mdl/{setup_test_data}")
        assert response.status_code == 200
        data = response.json()
        assert "catalog" in data
        assert "schema" in data

    def test_refresh_mdl(self, client, setup_test_data):
        """Test refreshing MDL manifest."""
        if not setup_test_data:
            pytest.skip("Test data setup failed")

        # First build the MDL
        client.post(f"/api/v1/mdl/build/{setup_test_data}")

        # Then refresh it
        response = client.post(f"/api/v1/mdl/{setup_test_data}/refresh")
        assert response.status_code == 200
        data = response.json()
        assert "mdl_hash" in data

    def test_get_mdl_not_found(self, client):
        """Test getting non-existent MDL manifest."""
        response = client.get("/api/v1/mdl/nonexistent-id")
        assert response.status_code == 404
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_integration/test_int_mdl.py -v`
Expected: FAIL (endpoints don't exist yet)

**Step 3: Commit the failing test**

```bash
git add tests/test_integration/test_int_mdl.py
git commit -m "test(mdl): add failing integration tests for MDL API"
```

---

### Task 1.10: Implement MDL API Endpoints

**Files:**
- Create: `app/api/routers/mdl.py`
- Modify: `app/api/__init__.py`

**Step 1: Create the MDL router**

Create `app/api/routers/mdl.py`:
```python
"""MDL API endpoints."""
from fastapi import APIRouter, HTTPException

from app.data.db.storage import Storage
from app.modules.mdl.services import MDLService
from app.server.config import Settings

router = APIRouter(prefix="/api/v1/mdl", tags=["MDL"])


def get_mdl_service() -> MDLService:
    """Get MDL service instance."""
    storage = Storage(Settings())
    return MDLService(storage)


@router.post("/build/{db_connection_id}")
async def build_mdl(db_connection_id: str):
    """
    Build MDL manifest from database schema.

    Args:
        db_connection_id: The database connection ID.

    Returns:
        Dict with mdl_hash and manifest.
    """
    try:
        service = get_mdl_service()
        manifest = service.build_mdl(db_connection_id)
        return {"mdl_hash": manifest.mdl_hash, "manifest": manifest.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{db_connection_id}")
async def get_mdl(db_connection_id: str):
    """
    Get MDL manifest for a database connection.

    Args:
        db_connection_id: The database connection ID.

    Returns:
        The MDL manifest.
    """
    service = get_mdl_service()
    manifest = service.mdl_repo.get_by_connection(db_connection_id)
    if not manifest:
        raise HTTPException(status_code=404, detail="MDL not found")
    return manifest.model_dump()


@router.post("/{db_connection_id}/refresh")
async def refresh_mdl(db_connection_id: str):
    """
    Force refresh MDL manifest.

    Args:
        db_connection_id: The database connection ID.

    Returns:
        Dict with mdl_hash.
    """
    try:
        service = get_mdl_service()
        manifest = service.refresh_mdl(db_connection_id)
        return {"mdl_hash": manifest.mdl_hash}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Step 2: Register the router in the API**

In `app/api/__init__.py`, add the import and registration:

Add import at top:
```python
from app.api.routers.mdl import router as mdl_router
```

In `_register_routes` method, add:
```python
self.router.include_router(mdl_router)
```

**Step 3: Run tests to verify they pass**

Run: `uv run pytest tests/test_integration/test_int_mdl.py -v`
Expected: All tests PASS

**Step 4: Commit**

```bash
git add app/api/routers/mdl.py app/api/__init__.py
git commit -m "feat(mdl): implement MDL API endpoints"
```

---

## Phase 2: Enhanced Relationship Management

### Task 2.1: Add Relationship Type to TableDescription Models

**Files:**
- Modify: `app/modules/table_description/models/__init__.py`
- Create: `tests/modules/table_description/test_relationship_models.py`

**Step 1: Write the failing test**

Create `tests/modules/table_description/test_relationship_models.py`:
```python
"""Tests for relationship type models."""
import pytest
from app.modules.table_description.models import RelationshipType, Relationship


class TestRelationshipModels:
    """Test relationship model additions."""

    def test_relationship_type_enum(self):
        """Test RelationshipType enum values."""
        assert RelationshipType.ONE_TO_ONE.value == "ONE_TO_ONE"
        assert RelationshipType.ONE_TO_MANY.value == "ONE_TO_MANY"
        assert RelationshipType.MANY_TO_ONE.value == "MANY_TO_ONE"
        assert RelationshipType.MANY_TO_MANY.value == "MANY_TO_MANY"

    def test_relationship_creation(self):
        """Test Relationship model creation."""
        rel = Relationship(
            name="CustomerOrders",
            from_table="customers",
            from_column="id",
            to_table="orders",
            to_column="customer_id",
            join_type=RelationshipType.ONE_TO_MANY,
        )
        assert rel.name == "CustomerOrders"
        assert rel.join_type == RelationshipType.ONE_TO_MANY
        assert rel.inferred is False

    def test_relationship_with_custom_condition(self):
        """Test Relationship with custom join condition."""
        rel = Relationship(
            name="CustomJoin",
            from_table="a",
            from_column="id",
            to_table="b",
            to_column="a_id",
            join_type=RelationshipType.MANY_TO_MANY,
            condition="a.id = b.a_id AND a.active = true",
            inferred=True,
        )
        assert rel.condition is not None
        assert "active" in rel.condition
        assert rel.inferred is True
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/modules/table_description/test_relationship_models.py -v`
Expected: FAIL with ImportError (RelationshipType, Relationship don't exist)

**Step 3: Implement the models**

Add to `app/modules/table_description/models/__init__.py`:
```python
from enum import Enum

class RelationshipType(str, Enum):
    """Types of table relationships."""
    ONE_TO_ONE = "ONE_TO_ONE"
    ONE_TO_MANY = "ONE_TO_MANY"
    MANY_TO_ONE = "MANY_TO_ONE"
    MANY_TO_MANY = "MANY_TO_MANY"


class Relationship(BaseModel):
    """Explicit relationship between tables."""
    name: str
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    join_type: RelationshipType
    condition: str | None = None  # Custom join condition
    inferred: bool = False  # AI-detected vs user-defined
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/modules/table_description/test_relationship_models.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add app/modules/table_description/models/__init__.py tests/modules/table_description/test_relationship_models.py
git commit -m "feat(table_description): add RelationshipType enum and Relationship model"
```

---

## Phase 3: GENBI - Chart & Narrative Generation

### Task 3.1: Create Chart Module Directory Structure

**Files:**
- Create: `app/modules/chart/__init__.py`
- Create: `app/modules/chart/models/__init__.py`
- Create: `app/modules/chart/services/__init__.py`

**Step 1: Create the module directories**

```bash
mkdir -p app/modules/chart/models
mkdir -p app/modules/chart/services
```

**Step 2: Create empty __init__.py files**

Create `app/modules/chart/__init__.py`:
```python
"""Chart generation module for GENBI."""
```

Create `app/modules/chart/models/__init__.py`:
```python
"""Chart Pydantic models."""
```

Create `app/modules/chart/services/__init__.py`:
```python
"""Chart generation services."""
```

**Step 3: Commit**

```bash
git add app/modules/chart/
git commit -m "feat(chart): create chart module directory structure"
```

---

### Task 3.2: Create Chart Models Test

**Files:**
- Create: `tests/modules/chart/__init__.py`
- Create: `tests/modules/chart/test_models.py`

**Step 1: Write the failing test**

Create `tests/modules/chart/test_models.py`:
```python
"""Tests for chart models."""
import pytest


class TestChartModels:
    """Test chart model definitions."""

    def test_chart_type_enum(self):
        """Test ChartType enum values."""
        from app.modules.chart.models import ChartType

        assert ChartType.LINE.value == "line"
        assert ChartType.BAR.value == "bar"
        assert ChartType.PIE.value == "pie"

    def test_chart_request(self):
        """Test ChartRequest creation."""
        from app.modules.chart.models import ChartRequest

        request = ChartRequest(
            query="Show monthly sales",
            sql="SELECT month, SUM(amount) FROM sales GROUP BY month",
        )
        assert request.query == "Show monthly sales"
        assert request.language == "en"  # default

    def test_chart_request_with_data(self):
        """Test ChartRequest with result data."""
        from app.modules.chart.models import ChartRequest

        request = ChartRequest(
            query="Show monthly sales",
            sql="SELECT month, total FROM sales",
            data=[
                {"month": "Jan", "total": 1000},
                {"month": "Feb", "total": 1500},
            ],
        )
        assert len(request.data) == 2

    def test_chart_result(self):
        """Test ChartResult creation."""
        from app.modules.chart.models import ChartResult, ChartType

        result = ChartResult(
            reasoning="Bar chart is best for comparing categories",
            chart_type=ChartType.BAR,
            chart_schema={
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "mark": "bar",
                "encoding": {
                    "x": {"field": "month", "type": "nominal"},
                    "y": {"field": "total", "type": "quantitative"},
                },
            },
        )
        assert result.chart_type == ChartType.BAR
        assert "mark" in result.chart_schema

    def test_chart_generation(self):
        """Test ChartGeneration model."""
        from app.modules.chart.models import ChartGeneration, ChartRequest

        generation = ChartGeneration(
            sql_generation_id="sql-123",
            request=ChartRequest(query="test", sql="SELECT 1"),
            status="pending",
            created_at="2024-01-01T00:00:00",
        )
        assert generation.status == "pending"
        assert generation.result is None
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/modules/chart/test_models.py -v`
Expected: FAIL with ImportError (models don't exist)

**Step 3: Commit the failing test**

```bash
mkdir -p tests/modules/chart
touch tests/modules/chart/__init__.py
git add tests/modules/chart/
git commit -m "test(chart): add failing tests for chart models"
```

---

### Task 3.3: Implement Chart Models

**Files:**
- Modify: `app/modules/chart/models/__init__.py`

**Step 1: Implement the models**

Update `app/modules/chart/models/__init__.py`:
```python
"""Chart Pydantic models for GENBI visualization."""
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel


class ChartType(str, Enum):
    """Supported chart types."""

    LINE = "line"
    MULTI_LINE = "multi_line"
    BAR = "bar"
    PIE = "pie"
    GROUPED_BAR = "grouped_bar"
    STACKED_BAR = "stacked_bar"
    AREA = "area"
    SCATTER = "scatter"
    HEATMAP = "heatmap"


class ChartRequest(BaseModel):
    """Request for chart generation."""

    query: str  # Original user question
    sql: str  # Generated SQL
    data: list[dict[str, Any]] | None = None  # Query results
    language: str = "en"
    custom_instruction: str | None = None


class ChartResult(BaseModel):
    """Result of chart generation."""

    reasoning: str  # Why this chart type was chosen
    chart_type: ChartType
    chart_schema: dict[str, Any]  # Vega-Lite schema
    data_preview: list[dict[str, Any]] | None = None


class ChartGeneration(BaseModel):
    """Chart generation record."""

    id: str | None = None
    sql_generation_id: str
    request: ChartRequest
    result: ChartResult | None = None
    status: Literal["pending", "processing", "completed", "failed"] = "pending"
    error: str | None = None
    created_at: str
```

**Step 2: Run test to verify it passes**

Run: `uv run pytest tests/modules/chart/test_models.py -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add app/modules/chart/models/__init__.py
git commit -m "feat(chart): implement chart Pydantic models"
```

---

### Task 3.4: Create Chart Generation Service Test

**Files:**
- Create: `tests/modules/chart/test_services.py`

**Step 1: Write the failing test**

Create `tests/modules/chart/test_services.py`:
```python
"""Tests for chart generation service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestChartGenerationService:
    """Test chart generation service."""

    @pytest.fixture
    def mock_llm(self):
        """Create mock LLM adapter."""
        llm = AsyncMock()
        llm.generate = AsyncMock(
            return_value='{"reasoning": "Bar chart for categories", "chart_type": "bar", "chart_schema": {"mark": "bar"}}'
        )
        return llm

    @pytest.fixture
    def mock_database(self):
        """Create mock SQL database."""
        db = MagicMock()
        return db

    @pytest.mark.asyncio
    async def test_generate_chart_with_data(self, mock_llm, mock_database):
        """Test chart generation when data is provided."""
        from app.modules.chart.services import ChartGenerationService
        from app.modules.chart.models import ChartRequest

        service = ChartGenerationService(mock_llm, mock_database)

        request = ChartRequest(
            query="Show sales by category",
            sql="SELECT category, SUM(amount) FROM sales GROUP BY category",
            data=[
                {"category": "A", "amount": 100},
                {"category": "B", "amount": 200},
            ],
        )

        result = await service.generate_chart(request)

        assert result.chart_type.value == "bar"
        assert result.reasoning is not None
        mock_llm.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_preprocess_data_handles_decimals(self, mock_llm, mock_database):
        """Test that decimal values are converted to float."""
        from decimal import Decimal
        from app.modules.chart.services import ChartGenerationService

        service = ChartGenerationService(mock_llm, mock_database)

        data = [{"value": Decimal("123.45"), "name": "test"}]
        processed = service._preprocess_data(data)

        assert isinstance(processed[0]["value"], float)
        assert processed[0]["value"] == 123.45

    @pytest.mark.asyncio
    async def test_preprocess_data_handles_dates(self, mock_llm, mock_database):
        """Test that date values are converted to ISO strings."""
        from datetime import datetime, date
        from app.modules.chart.services import ChartGenerationService

        service = ChartGenerationService(mock_llm, mock_database)

        data = [
            {"date": datetime(2024, 1, 15, 10, 30)},
            {"date": date(2024, 1, 15)},
        ]
        processed = service._preprocess_data(data)

        assert isinstance(processed[0]["date"], str)
        assert "2024-01-15" in processed[0]["date"]

    def test_get_column_samples(self, mock_llm, mock_database):
        """Test column type detection."""
        from app.modules.chart.services import ChartGenerationService

        service = ChartGenerationService(mock_llm, mock_database)

        data = [
            {"amount": 100, "name": "A"},
            {"amount": 200, "name": "B"},
            {"amount": 150, "name": "C"},
        ]
        samples = service._get_column_samples(data)

        assert "amount" in samples
        assert samples["amount"]["type"] == "int"
        assert samples["name"]["type"] == "str"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/modules/chart/test_services.py -v`
Expected: FAIL with ImportError (ChartGenerationService doesn't exist)

**Step 3: Commit the failing test**

```bash
git add tests/modules/chart/test_services.py
git commit -m "test(chart): add failing tests for chart generation service"
```

---

### Task 3.5: Implement Chart Generation Service

**Files:**
- Modify: `app/modules/chart/services/__init__.py`

**Step 1: Implement the service**

Update `app/modules/chart/services/__init__.py`:
```python
"""Chart generation services for GENBI."""
import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from app.modules.chart.models import ChartRequest, ChartResult, ChartType


class ChartGenerationService:
    """Generate Vega-Lite charts from SQL results."""

    SYSTEM_PROMPT = """
    You are a data visualization expert. Given a user's question, SQL query, and data,
    generate an appropriate Vega-Lite chart specification.

    Guidelines:
    - Choose the most appropriate chart type for the data
    - Use clear labels and titles
    - Consider color schemes for accessibility
    - Handle null/missing values gracefully

    Chart type options: line, multi_line, bar, pie, grouped_bar, stacked_bar, area, scatter, heatmap

    Output JSON with exactly these fields:
    - reasoning: string explaining why this chart type was chosen
    - chart_type: one of the chart type options above
    - chart_schema: Vega-Lite specification object (without data)
    """

    def __init__(self, llm_adapter, sql_database):
        self.llm = llm_adapter
        self.database = sql_database

    async def generate_chart(self, request: ChartRequest) -> ChartResult:
        """
        Generate chart from request.

        Args:
            request: Chart generation request.

        Returns:
            ChartResult with Vega-Lite schema.
        """
        # Preprocess data
        if request.data:
            sample_data = self._preprocess_data(request.data)
        else:
            sample_data = []

        sample_columns = self._get_column_samples(sample_data) if sample_data else {}

        prompt = f"""
        Question: {request.query}
        SQL: {request.sql}
        Sample Data: {json.dumps(sample_data[:10])}
        Column Types: {json.dumps(sample_columns)}
        Language: {request.language}
        Custom Instruction: {request.custom_instruction or "None"}

        Generate a Vega-Lite chart specification.
        """

        response = await self.llm.generate(
            self.SYSTEM_PROMPT + "\n\n" + prompt,
        )

        result = json.loads(response)

        # Inject data into schema if available
        chart_schema = result.get("chart_schema", {})
        if sample_data:
            chart_schema["data"] = {"values": sample_data}

        return ChartResult(
            reasoning=result.get("reasoning", ""),
            chart_type=ChartType(result.get("chart_type", "bar")),
            chart_schema=chart_schema,
            data_preview=sample_data[:5] if sample_data else None,
        )

    def _preprocess_data(self, data: list[dict]) -> list[dict]:
        """
        Clean and preprocess data for charting.

        Args:
            data: Raw query result data.

        Returns:
            Cleaned data list.
        """
        if not data:
            return []

        processed = []
        for row in data:
            clean_row = {}
            for k, v in row.items():
                # Handle datetime
                if isinstance(v, (datetime, date)):
                    clean_row[k] = v.isoformat()
                # Handle Decimal
                elif isinstance(v, Decimal):
                    clean_row[k] = float(v)
                else:
                    clean_row[k] = v
            processed.append(clean_row)

        return processed

    def _get_column_samples(self, data: list[dict]) -> dict[str, Any]:
        """
        Extract column type samples for LLM context.

        Args:
            data: Preprocessed data.

        Returns:
            Dict of column metadata.
        """
        if not data:
            return {}

        samples = {}
        for col in data[0].keys():
            values = [row.get(col) for row in data[:10] if row.get(col) is not None]
            if values:
                samples[col] = {
                    "type": type(values[0]).__name__,
                    "samples": values[:3],
                    "unique_count": len(set(str(v) for v in values)),
                }
        return samples
```

**Step 2: Run test to verify it passes**

Run: `uv run pytest tests/modules/chart/test_services.py -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add app/modules/chart/services/__init__.py
git commit -m "feat(chart): implement chart generation service"
```

---

### Task 3.6: Create SQL Answer Module

**Files:**
- Create: `app/modules/sql_answer/__init__.py`
- Create: `app/modules/sql_answer/models/__init__.py`
- Create: `app/modules/sql_answer/services/__init__.py`
- Create: `tests/modules/sql_answer/test_models.py`

**Step 1: Create directory structure**

```bash
mkdir -p app/modules/sql_answer/models
mkdir -p app/modules/sql_answer/services
mkdir -p tests/modules/sql_answer
```

**Step 2: Create module __init__ files**

Create `app/modules/sql_answer/__init__.py`:
```python
"""SQL Answer module for narrative generation from query results."""
```

Create `app/modules/sql_answer/models/__init__.py`:
```python
"""SQL Answer Pydantic models."""
from typing import Any, Literal

from pydantic import BaseModel


class SQLAnswerRequest(BaseModel):
    """Request for SQL answer generation."""

    query: str  # Original user question
    sql: str  # Generated SQL
    data: list[dict[str, Any]]  # Query results
    language: str = "en"
    custom_instruction: str | None = None


class SQLAnswerResult(BaseModel):
    """Result of SQL answer generation."""

    answer: str  # Markdown formatted answer
    key_insights: list[str] = []
    data_summary: dict[str, Any] | None = None


class SQLAnswer(BaseModel):
    """SQL Answer generation record."""

    id: str | None = None
    sql_generation_id: str
    request: SQLAnswerRequest
    result: SQLAnswerResult | None = None
    status: Literal["pending", "processing", "completed", "failed"] = "pending"
    error: str | None = None
    created_at: str
```

**Step 3: Write the test**

Create `tests/modules/sql_answer/__init__.py`:
```python
"""Tests for SQL Answer module."""
```

Create `tests/modules/sql_answer/test_models.py`:
```python
"""Tests for SQL answer models."""
import pytest

from app.modules.sql_answer.models import (
    SQLAnswerRequest,
    SQLAnswerResult,
    SQLAnswer,
)


class TestSQLAnswerModels:
    """Test SQL answer model definitions."""

    def test_sql_answer_request(self):
        """Test SQLAnswerRequest creation."""
        request = SQLAnswerRequest(
            query="What are total sales?",
            sql="SELECT SUM(amount) FROM sales",
            data=[{"sum": 10000}],
        )
        assert request.query == "What are total sales?"
        assert request.language == "en"

    def test_sql_answer_result(self):
        """Test SQLAnswerResult creation."""
        result = SQLAnswerResult(
            answer="The total sales amount is **$10,000**.",
            key_insights=["Sales are up 15% from last month"],
            data_summary={"total_rows": 1, "sum": 10000},
        )
        assert "10,000" in result.answer
        assert len(result.key_insights) == 1

    def test_sql_answer_model(self):
        """Test SQLAnswer model creation."""
        answer = SQLAnswer(
            sql_generation_id="sql-123",
            request=SQLAnswerRequest(
                query="test",
                sql="SELECT 1",
                data=[{"col": 1}],
            ),
            status="pending",
            created_at="2024-01-01T00:00:00",
        )
        assert answer.status == "pending"
        assert answer.result is None
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/modules/sql_answer/test_models.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add app/modules/sql_answer/ tests/modules/sql_answer/
git commit -m "feat(sql_answer): create SQL answer module with models"
```

---

### Task 3.7: Implement SQL Answer Service

**Files:**
- Modify: `app/modules/sql_answer/services/__init__.py`
- Create: `tests/modules/sql_answer/test_services.py`

**Step 1: Write the failing test**

Create `tests/modules/sql_answer/test_services.py`:
```python
"""Tests for SQL answer service."""
import pytest
from unittest.mock import AsyncMock


class TestSQLAnswerService:
    """Test SQL answer service."""

    @pytest.fixture
    def mock_llm(self):
        """Create mock LLM adapter."""
        llm = AsyncMock()
        llm.generate = AsyncMock(
            return_value="The total revenue is **$50,000**.\n\n- Revenue increased 10% month-over-month\n- Top category: Electronics"
        )
        return llm

    @pytest.mark.asyncio
    async def test_generate_answer(self, mock_llm):
        """Test answer generation."""
        from app.modules.sql_answer.services import SQLAnswerService
        from app.modules.sql_answer.models import SQLAnswerRequest

        service = SQLAnswerService(mock_llm)

        request = SQLAnswerRequest(
            query="What is the total revenue?",
            sql="SELECT SUM(amount) as revenue FROM orders",
            data=[{"revenue": 50000}],
        )

        result = await service.generate_answer(request)

        assert "50,000" in result.answer
        assert len(result.key_insights) > 0
        mock_llm.generate.assert_called_once()

    def test_summarize_data(self, mock_llm):
        """Test data summarization."""
        from app.modules.sql_answer.services import SQLAnswerService

        service = SQLAnswerService(mock_llm)

        data = [
            {"amount": 100, "category": "A"},
            {"amount": 200, "category": "B"},
            {"amount": 150, "category": "A"},
        ]

        summary = service._summarize_data(data)

        assert summary["row_count"] == 3
        assert "amount" in summary["columns"]
        assert "amount_stats" in summary
        assert summary["amount_stats"]["min"] == 100
        assert summary["amount_stats"]["max"] == 200

    def test_extract_insights(self, mock_llm):
        """Test insight extraction from response."""
        from app.modules.sql_answer.services import SQLAnswerService

        service = SQLAnswerService(mock_llm)

        response = """
        The answer is here.

        - First insight about data
        - Second insight with numbers
        * Third bullet point
        """

        insights = service._extract_insights(response)

        assert len(insights) == 3
        assert "First insight" in insights[0]
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/modules/sql_answer/test_services.py -v`
Expected: FAIL with ImportError (SQLAnswerService doesn't exist)

**Step 3: Implement the service**

Update `app/modules/sql_answer/services/__init__.py`:
```python
"""SQL Answer generation service for GENBI."""
from typing import Any

from app.modules.sql_answer.models import SQLAnswerRequest, SQLAnswerResult


class SQLAnswerService:
    """Generate natural language answers from SQL results."""

    SYSTEM_PROMPT = """
    You are a data analyst explaining query results to a business user.
    Given a question, SQL query, and data results, provide a clear, concise answer.

    Guidelines:
    - Lead with the direct answer to the question
    - Highlight key insights and notable patterns
    - Use bullet points for multiple findings
    - Include relevant numbers with context
    - Keep language accessible to non-technical users
    - Format output as Markdown

    Structure your response:
    1. Direct Answer (1-2 sentences)
    2. Key Insights (bullet points starting with - or *)
    3. Data Summary (if applicable)
    """

    def __init__(self, llm_adapter):
        self.llm = llm_adapter

    async def generate_answer(
        self,
        request: SQLAnswerRequest,
        stream: bool = False,
    ) -> SQLAnswerResult:
        """
        Generate natural language answer from SQL results.

        Args:
            request: SQL answer request.
            stream: Whether to stream the response.

        Returns:
            SQLAnswerResult with answer and insights.
        """
        # Prepare data summary
        data_summary = self._summarize_data(request.data)

        prompt = f"""
        Question: {request.query}
        SQL: {request.sql}
        Results: {request.data[:20]}
        Total Rows: {len(request.data)}
        Data Summary: {data_summary}
        Language: {request.language}
        Custom Instruction: {request.custom_instruction or "None"}

        Provide a clear, insightful answer.
        """

        response = await self.llm.generate(
            self.SYSTEM_PROMPT + "\n\n" + prompt
        )

        return SQLAnswerResult(
            answer=response,
            key_insights=self._extract_insights(response),
            data_summary=data_summary,
        )

    def _summarize_data(self, data: list[dict]) -> dict[str, Any]:
        """
        Create statistical summary of data.

        Args:
            data: Query result data.

        Returns:
            Summary dictionary.
        """
        if not data:
            return {"row_count": 0}

        summary: dict[str, Any] = {
            "row_count": len(data),
            "columns": list(data[0].keys()) if data else [],
        }

        # Add numeric column stats
        for col in summary["columns"]:
            values = [row.get(col) for row in data if row.get(col) is not None]
            if values and all(isinstance(v, (int, float)) for v in values):
                summary[f"{col}_stats"] = {
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                }

        return summary

    def _extract_insights(self, response: str) -> list[str]:
        """
        Extract bullet point insights from response.

        Args:
            response: LLM response text.

        Returns:
            List of insight strings.
        """
        insights = []
        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                insights.append(line[2:])
        return insights[:5]  # Top 5 insights
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/modules/sql_answer/test_services.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add app/modules/sql_answer/services/__init__.py tests/modules/sql_answer/test_services.py
git commit -m "feat(sql_answer): implement SQL answer generation service"
```

---

## Summary & Next Steps

This plan covers **Phase 0-3** of the MDL & GENBI implementation:

- **Phase 0**: Foundation setup (MDL module structure, JSON schema, validator)
- **Phase 1**: MDL core (models, repository, builder, service, API)
- **Phase 2**: Enhanced relationships (RelationshipType enum, Relationship model)
- **Phase 3**: GENBI (chart models/service, SQL answer models/service)

**Remaining phases** (Phase 4-7) would include:
- ACL module for access control
- Ask pipeline integration
- Semantics preparation service
- Full API endpoint integration

**Run all tests** after completing all tasks:
```bash
uv run pytest tests/modules/mdl/ tests/modules/chart/ tests/modules/sql_answer/ -v
```

---

Plan complete and saved to `docs/plans/2025-12-06-mdl-genbi-implementation.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
