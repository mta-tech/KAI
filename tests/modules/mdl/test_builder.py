"""Tests for MDL Builder service."""
import pytest

from app.modules.mdl.services.builder import MDLBuilder
from app.modules.mdl.models import (
    MDLManifest,
    MDLModel,
    MDLColumn,
    MDLRelationship,
    JoinType,
)
from app.modules.table_description.models import (
    TableDescription,
    ColumnDescription,
    ForeignKeyDetail,
)


class TestMDLBuilder:
    """Tests for MDLBuilder service."""

    def test_from_table_descriptions_empty(self):
        """Test building MDL from empty table descriptions."""
        manifest = MDLBuilder.from_table_descriptions(
            db_connection_id="conn_123",
            catalog="test",
            schema="public",
            table_descriptions=[],
        )

        assert manifest.catalog == "test"
        assert manifest.schema == "public"
        assert manifest.db_connection_id == "conn_123"
        assert manifest.models == []
        assert manifest.relationships == []

    def test_from_table_descriptions_single_table(self):
        """Test building MDL from a single table description."""
        table = TableDescription(
            id="td_1",
            db_connection_id="conn_123",
            db_schema="public",
            table_name="users",
            columns=[
                ColumnDescription(
                    name="id",
                    data_type="INTEGER",
                    is_primary_key=True,
                ),
                ColumnDescription(
                    name="email",
                    data_type="VARCHAR",
                    description="User email address",
                ),
            ],
            table_description="User accounts table",
        )

        manifest = MDLBuilder.from_table_descriptions(
            db_connection_id="conn_123",
            catalog="test",
            schema="public",
            table_descriptions=[table],
        )

        assert len(manifest.models) == 1
        model = manifest.models[0]
        assert model.name == "users"
        assert len(model.columns) == 2
        assert model.primary_key == "id"

        # Check column properties
        id_col = next(c for c in model.columns if c.name == "id")
        assert id_col.type == "INTEGER"

        email_col = next(c for c in model.columns if c.name == "email")
        assert email_col.type == "VARCHAR"
        assert email_col.properties["description"] == "User email address"

    def test_from_table_descriptions_with_foreign_keys(self):
        """Test building MDL with foreign key relationships."""
        users_table = TableDescription(
            id="td_1",
            db_connection_id="conn_123",
            db_schema="public",
            table_name="users",
            columns=[
                ColumnDescription(
                    name="id",
                    data_type="INTEGER",
                    is_primary_key=True,
                ),
            ],
        )

        orders_table = TableDescription(
            id="td_2",
            db_connection_id="conn_123",
            db_schema="public",
            table_name="orders",
            columns=[
                ColumnDescription(
                    name="id",
                    data_type="INTEGER",
                    is_primary_key=True,
                ),
                ColumnDescription(
                    name="user_id",
                    data_type="INTEGER",
                    foreign_key=ForeignKeyDetail(
                        field_name="id",
                        reference_table="users",
                    ),
                ),
            ],
        )

        manifest = MDLBuilder.from_table_descriptions(
            db_connection_id="conn_123",
            catalog="test",
            schema="public",
            table_descriptions=[users_table, orders_table],
        )

        assert len(manifest.models) == 2
        assert len(manifest.relationships) == 1

        rel = manifest.relationships[0]
        assert "orders" in rel.models
        assert "users" in rel.models
        assert rel.join_type == JoinType.MANY_TO_ONE
        assert "orders.user_id = users.id" in rel.condition

    def test_from_table_descriptions_with_name(self):
        """Test building MDL with custom name."""
        manifest = MDLBuilder.from_table_descriptions(
            db_connection_id="conn_123",
            catalog="analytics",
            schema="main",
            table_descriptions=[],
            name="Sales Analytics MDL",
        )

        assert manifest.name == "Sales Analytics MDL"

    def test_from_table_descriptions_with_data_source(self):
        """Test building MDL with data source type."""
        manifest = MDLBuilder.from_table_descriptions(
            db_connection_id="conn_123",
            catalog="test",
            schema="public",
            table_descriptions=[],
            data_source="postgresql",
        )

        assert manifest.data_source == "postgresql"

    def test_add_model(self):
        """Test adding a model to existing manifest."""
        manifest = MDLManifest(
            catalog="test",
            schema="public",
        )

        new_model = MDLModel(
            name="products",
            columns=[
                MDLColumn(name="id", type="INTEGER"),
                MDLColumn(name="name", type="VARCHAR"),
            ],
            primary_key="id",
        )

        updated = MDLBuilder.add_model(manifest, new_model)

        assert len(updated.models) == 1
        assert updated.models[0].name == "products"

    def test_add_model_replaces_existing(self):
        """Test adding a model replaces one with same name."""
        manifest = MDLManifest(
            catalog="test",
            schema="public",
            models=[
                MDLModel(
                    name="products",
                    columns=[MDLColumn(name="id", type="INTEGER")],
                )
            ],
        )

        new_model = MDLModel(
            name="products",
            columns=[
                MDLColumn(name="id", type="INTEGER"),
                MDLColumn(name="sku", type="VARCHAR"),
            ],
        )

        updated = MDLBuilder.add_model(manifest, new_model)

        assert len(updated.models) == 1
        assert len(updated.models[0].columns) == 2

    def test_add_relationship(self):
        """Test adding a relationship to manifest."""
        manifest = MDLManifest(
            catalog="test",
            schema="public",
            models=[
                MDLModel(
                    name="orders",
                    columns=[
                        MDLColumn(name="id", type="INTEGER"),
                        MDLColumn(name="customer_id", type="INTEGER"),
                    ],
                ),
                MDLModel(
                    name="customers",
                    columns=[MDLColumn(name="id", type="INTEGER")],
                ),
            ],
        )

        relationship = MDLRelationship(
            name="orders_customers",
            models=["orders", "customers"],
            join_type=JoinType.MANY_TO_ONE,
            condition="orders.customer_id = customers.id",
        )

        updated = MDLBuilder.add_relationship(manifest, relationship)

        assert len(updated.relationships) == 1
        assert updated.relationships[0].name == "orders_customers"

    def test_remove_model(self):
        """Test removing a model from manifest."""
        manifest = MDLManifest(
            catalog="test",
            schema="public",
            models=[
                MDLModel(
                    name="products",
                    columns=[MDLColumn(name="id", type="INTEGER")],
                ),
                MDLModel(
                    name="categories",
                    columns=[MDLColumn(name="id", type="INTEGER")],
                ),
            ],
        )

        updated = MDLBuilder.remove_model(manifest, "products")

        assert len(updated.models) == 1
        assert updated.models[0].name == "categories"

    def test_remove_relationship(self):
        """Test removing a relationship from manifest."""
        manifest = MDLManifest(
            catalog="test",
            schema="public",
            relationships=[
                MDLRelationship(
                    name="rel_1",
                    models=["a", "b"],
                    join_type=JoinType.ONE_TO_MANY,
                    condition="a.b_id = b.id",
                ),
                MDLRelationship(
                    name="rel_2",
                    models=["c", "d"],
                    join_type=JoinType.MANY_TO_ONE,
                    condition="c.d_id = d.id",
                ),
            ],
        )

        updated = MDLBuilder.remove_relationship(manifest, "rel_1")

        assert len(updated.relationships) == 1
        assert updated.relationships[0].name == "rel_2"

    def test_infer_relationships(self):
        """Test inferring relationships from foreign key naming conventions."""
        manifest = MDLManifest(
            catalog="test",
            schema="public",
            models=[
                MDLModel(
                    name="orders",
                    columns=[
                        MDLColumn(name="id", type="INTEGER"),
                        MDLColumn(name="customer_id", type="INTEGER"),
                        MDLColumn(name="product_id", type="INTEGER"),
                    ],
                    primary_key="id",
                ),
                MDLModel(
                    name="customers",
                    columns=[MDLColumn(name="id", type="INTEGER")],
                    primary_key="id",
                ),
                MDLModel(
                    name="products",
                    columns=[MDLColumn(name="id", type="INTEGER")],
                    primary_key="id",
                ),
            ],
        )

        updated = MDLBuilder.infer_relationships(manifest)

        # Should infer orders->customers and orders->products relationships
        assert len(updated.relationships) >= 2
        rel_names = [r.name for r in updated.relationships]
        assert any("customer" in name.lower() for name in rel_names)
        assert any("product" in name.lower() for name in rel_names)
