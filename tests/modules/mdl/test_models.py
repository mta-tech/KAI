"""Tests for MDL Pydantic models."""
import pytest
from datetime import datetime

from app.modules.mdl.models import (
    MDLColumn,
    MDLModel,
    MDLRelationship,
    MDLMetric,
    MDLView,
    MDLTimeGrain,
    MDLManifest,
    JoinType,
    DatePart,
)


class TestMDLColumn:
    """Tests for MDLColumn model."""

    def test_minimal_column(self):
        """Test creating a column with minimal required fields."""
        col = MDLColumn(name="id", type="INTEGER")
        assert col.name == "id"
        assert col.type == "INTEGER"
        assert col.not_null is False
        assert col.is_calculated is False
        assert col.is_hidden is False

    def test_column_with_expression(self):
        """Test creating a calculated column with expression."""
        col = MDLColumn(
            name="full_name",
            type="VARCHAR",
            is_calculated=True,
            expression="first_name || ' ' || last_name",
        )
        assert col.is_calculated is True
        assert col.expression == "first_name || ' ' || last_name"

    def test_column_with_relationship(self):
        """Test column referencing a relationship."""
        col = MDLColumn(
            name="customer_name",
            type="VARCHAR",
            relationship="orders_customers",
        )
        assert col.relationship == "orders_customers"


class TestMDLModel:
    """Tests for MDLModel model."""

    def test_minimal_model(self):
        """Test creating a model with minimal fields."""
        model = MDLModel(
            name="users",
            columns=[MDLColumn(name="id", type="INTEGER")],
        )
        assert model.name == "users"
        assert len(model.columns) == 1
        assert model.cached is False

    def test_model_with_table_reference(self):
        """Test model with explicit table reference."""
        model = MDLModel(
            name="users",
            table_reference={"catalog": "prod", "schema": "public", "table": "users"},
            columns=[
                MDLColumn(name="id", type="INTEGER"),
                MDLColumn(name="email", type="VARCHAR"),
            ],
            primary_key="id",
        )
        assert model.table_reference["table"] == "users"
        assert model.primary_key == "id"

    def test_model_with_ref_sql(self):
        """Test model defined by SQL query."""
        model = MDLModel(
            name="active_users",
            ref_sql="SELECT * FROM users WHERE status = 'active'",
            columns=[MDLColumn(name="id", type="INTEGER")],
        )
        assert model.ref_sql == "SELECT * FROM users WHERE status = 'active'"


class TestMDLRelationship:
    """Tests for MDLRelationship model."""

    def test_one_to_many_relationship(self):
        """Test creating a one-to-many relationship."""
        rel = MDLRelationship(
            name="orders_customers",
            models=["orders", "customers"],
            join_type=JoinType.MANY_TO_ONE,
            condition="orders.customer_id = customers.id",
        )
        assert rel.name == "orders_customers"
        assert rel.join_type == JoinType.MANY_TO_ONE
        assert len(rel.models) == 2

    def test_join_type_enum(self):
        """Test all join type enum values."""
        assert JoinType.ONE_TO_ONE.value == "ONE_TO_ONE"
        assert JoinType.ONE_TO_MANY.value == "ONE_TO_MANY"
        assert JoinType.MANY_TO_ONE.value == "MANY_TO_ONE"
        assert JoinType.MANY_TO_MANY.value == "MANY_TO_MANY"


class TestMDLMetric:
    """Tests for MDLMetric model."""

    def test_metric_with_measure(self):
        """Test creating a metric with measure."""
        metric = MDLMetric(
            name="total_revenue",
            base_object="orders",
            measure=[
                MDLColumn(
                    name="revenue",
                    type="DECIMAL",
                    is_calculated=True,
                    expression="SUM(amount)",
                )
            ],
        )
        assert metric.name == "total_revenue"
        assert metric.base_object == "orders"
        assert len(metric.measure) == 1

    def test_metric_with_dimension_and_time_grain(self):
        """Test metric with dimensions and time grain."""
        metric = MDLMetric(
            name="monthly_sales",
            base_object="orders",
            dimension=[MDLColumn(name="category", type="VARCHAR")],
            measure=[
                MDLColumn(
                    name="total",
                    type="DECIMAL",
                    is_calculated=True,
                    expression="SUM(amount)",
                )
            ],
            time_grain=[
                MDLTimeGrain(
                    name="order_date",
                    ref_column="created_at",
                    date_parts=[DatePart.YEAR, DatePart.MONTH],
                )
            ],
        )
        assert len(metric.dimension) == 1
        assert len(metric.time_grain) == 1
        assert DatePart.MONTH in metric.time_grain[0].date_parts


class TestMDLTimeGrain:
    """Tests for MDLTimeGrain model."""

    def test_time_grain_creation(self):
        """Test creating a time grain."""
        tg = MDLTimeGrain(
            name="created_date",
            ref_column="created_at",
            date_parts=[DatePart.YEAR, DatePart.QUARTER, DatePart.MONTH],
        )
        assert tg.name == "created_date"
        assert tg.ref_column == "created_at"
        assert len(tg.date_parts) == 3

    def test_date_part_enum(self):
        """Test all date part enum values."""
        assert DatePart.YEAR.value == "YEAR"
        assert DatePart.QUARTER.value == "QUARTER"
        assert DatePart.MONTH.value == "MONTH"
        assert DatePart.WEEK.value == "WEEK"
        assert DatePart.DAY.value == "DAY"
        assert DatePart.HOUR.value == "HOUR"
        assert DatePart.MINUTE.value == "MINUTE"


class TestMDLView:
    """Tests for MDLView model."""

    def test_view_creation(self):
        """Test creating a view."""
        view = MDLView(
            name="active_customers",
            statement="SELECT * FROM customers WHERE status = 'active'",
        )
        assert view.name == "active_customers"
        assert "SELECT" in view.statement

    def test_view_with_properties(self):
        """Test view with description."""
        view = MDLView(
            name="vip_customers",
            statement="SELECT * FROM customers WHERE tier = 'vip'",
            properties={"description": "VIP tier customers only"},
        )
        assert view.properties["description"] == "VIP tier customers only"


class TestMDLManifest:
    """Tests for MDLManifest model."""

    def test_minimal_manifest(self):
        """Test creating a minimal manifest."""
        manifest = MDLManifest(
            catalog="analytics",
            schema="public",
        )
        assert manifest.catalog == "analytics"
        assert manifest.schema == "public"
        assert manifest.models == []
        assert manifest.relationships == []

    def test_full_manifest(self):
        """Test creating a full manifest with all components."""
        manifest = MDLManifest(
            id="mdl_123",
            db_connection_id="conn_456",
            name="Sales Analytics",
            catalog="analytics",
            schema="public",
            data_source="postgresql",
            models=[
                MDLModel(
                    name="orders",
                    columns=[
                        MDLColumn(name="id", type="INTEGER"),
                        MDLColumn(name="customer_id", type="INTEGER"),
                        MDLColumn(name="amount", type="DECIMAL"),
                    ],
                    primary_key="id",
                )
            ],
            relationships=[
                MDLRelationship(
                    name="orders_customers",
                    models=["orders", "customers"],
                    join_type=JoinType.MANY_TO_ONE,
                    condition="orders.customer_id = customers.id",
                )
            ],
            metrics=[
                MDLMetric(
                    name="total_revenue",
                    base_object="orders",
                    measure=[
                        MDLColumn(
                            name="revenue",
                            type="DECIMAL",
                            is_calculated=True,
                            expression="SUM(amount)",
                        )
                    ],
                )
            ],
            views=[
                MDLView(
                    name="recent_orders",
                    statement="SELECT * FROM orders WHERE created_at > NOW() - INTERVAL '30 days'",
                )
            ],
        )
        assert manifest.name == "Sales Analytics"
        assert len(manifest.models) == 1
        assert len(manifest.relationships) == 1
        assert len(manifest.metrics) == 1
        assert len(manifest.views) == 1

    def test_manifest_to_dict(self):
        """Test converting manifest to dictionary."""
        manifest = MDLManifest(
            id="mdl_123",
            db_connection_id="conn_456",
            name="Test MDL",
            catalog="test",
            schema="public",
            models=[
                MDLModel(
                    name="users",
                    columns=[MDLColumn(name="id", type="INTEGER")],
                )
            ],
        )
        d = manifest.to_dict()
        assert d["id"] == "mdl_123"
        assert d["catalog"] == "test"
        assert len(d["models"]) == 1
        assert d["models"][0]["name"] == "users"

    def test_manifest_from_dict(self):
        """Test creating manifest from dictionary."""
        data = {
            "id": "mdl_789",
            "db_connection_id": "conn_111",
            "name": "Loaded MDL",
            "catalog": "loaded",
            "schema": "main",
            "models": [
                {
                    "name": "products",
                    "columns": [{"name": "id", "type": "INTEGER"}],
                }
            ],
            "relationships": [],
            "created_at": "2024-01-01T12:00:00",
        }
        manifest = MDLManifest.from_dict(data)
        assert manifest.id == "mdl_789"
        assert manifest.name == "Loaded MDL"
        assert len(manifest.models) == 1
        assert manifest.models[0].name == "products"

    def test_manifest_to_mdl_json(self):
        """Test exporting manifest to MDL JSON format (WrenAI compatible)."""
        manifest = MDLManifest(
            catalog="analytics",
            schema="public",
            models=[
                MDLModel(
                    name="orders",
                    columns=[MDLColumn(name="id", type="INTEGER")],
                    primary_key="id",
                )
            ],
        )
        mdl_json = manifest.to_mdl_json()
        assert mdl_json["catalog"] == "analytics"
        assert mdl_json["schema"] == "public"
        assert len(mdl_json["models"]) == 1
        assert mdl_json["models"][0]["primaryKey"] == "id"
