"""Tests for MDL Semantic Lookup tool."""
import pytest

from app.modules.mdl.models import (
    MDLManifest,
    MDLModel,
    MDLColumn,
    MDLRelationship,
    MDLMetric,
    MDLTimeGrain,
    JoinType,
    DatePart,
)
from app.utils.sql_tools.mdl_semantic_lookup import (
    MDLSemanticLookupTool,
    create_mdl_semantic_tool,
    get_mdl_context_prompt,
)


@pytest.fixture
def sample_manifest():
    """Create a sample MDL manifest for testing."""
    return MDLManifest(
        catalog="analytics",
        schema="public",
        models=[
            MDLModel(
                name="customers",
                columns=[
                    MDLColumn(name="id", type="INTEGER"),
                    MDLColumn(
                        name="name",
                        type="VARCHAR",
                        properties={"description": "Customer full name"},
                    ),
                    MDLColumn(name="tier", type="VARCHAR"),
                    MDLColumn(name="created_at", type="TIMESTAMP"),
                ],
                primary_key="id",
                properties={"description": "Customer master data"},
            ),
            MDLModel(
                name="orders",
                columns=[
                    MDLColumn(name="id", type="INTEGER"),
                    MDLColumn(name="customer_id", type="INTEGER"),
                    MDLColumn(name="product_id", type="INTEGER"),
                    MDLColumn(name="quantity", type="INTEGER"),
                    MDLColumn(name="unit_price", type="DECIMAL"),
                    MDLColumn(
                        name="total_amount",
                        type="DECIMAL",
                        is_calculated=True,
                        expression="quantity * unit_price",
                        properties={"description": "Line item total"},
                    ),
                    MDLColumn(name="created_at", type="TIMESTAMP"),
                ],
                primary_key="id",
                properties={"description": "Customer orders"},
            ),
            MDLModel(
                name="products",
                columns=[
                    MDLColumn(name="id", type="INTEGER"),
                    MDLColumn(name="name", type="VARCHAR"),
                    MDLColumn(name="category", type="VARCHAR"),
                    MDLColumn(name="price", type="DECIMAL"),
                ],
                primary_key="id",
            ),
        ],
        relationships=[
            MDLRelationship(
                name="orders_customers",
                models=["orders", "customers"],
                join_type=JoinType.MANY_TO_ONE,
                condition="orders.customer_id = customers.id",
            ),
            MDLRelationship(
                name="orders_products",
                models=["orders", "products"],
                join_type=JoinType.MANY_TO_ONE,
                condition="orders.product_id = products.id",
            ),
        ],
        metrics=[
            MDLMetric(
                name="total_revenue",
                base_object="orders",
                dimension=[
                    MDLColumn(name="customer_tier", type="VARCHAR"),
                ],
                measure=[
                    MDLColumn(
                        name="revenue",
                        type="DECIMAL",
                        is_calculated=True,
                        expression="SUM(total_amount)",
                    ),
                    MDLColumn(
                        name="order_count",
                        type="INTEGER",
                        is_calculated=True,
                        expression="COUNT(*)",
                    ),
                ],
                time_grain=[
                    MDLTimeGrain(
                        name="order_date",
                        ref_column="created_at",
                        date_parts=[DatePart.YEAR, DatePart.MONTH],
                    )
                ],
                properties={"description": "Total revenue metric"},
            ),
        ],
    )


class TestMDLSemanticLookupTool:
    """Tests for MDLSemanticLookupTool."""

    def test_create_tool(self, sample_manifest):
        """Should create tool from manifest."""
        tool = create_mdl_semantic_tool(sample_manifest)
        assert tool.name == "mdl_semantic_lookup"
        assert tool.mdl_manifest == sample_manifest

    def test_search_models_by_name(self, sample_manifest):
        """Should find models by name."""
        tool = create_mdl_semantic_tool(sample_manifest)
        result = tool._run("customers")

        assert "customers" in result.lower()
        assert "Customer master data" in result

    def test_search_models_by_description(self, sample_manifest):
        """Should find models by description."""
        tool = create_mdl_semantic_tool(sample_manifest)
        result = tool._run("master data")

        assert "customers" in result.lower()

    def test_search_columns(self, sample_manifest):
        """Should find columns by name."""
        tool = create_mdl_semantic_tool(sample_manifest)
        result = tool._run("quantity")

        assert "orders" in result.lower()
        assert "quantity" in result.lower()

    def test_search_relationships(self, sample_manifest):
        """Should find relationships."""
        tool = create_mdl_semantic_tool(sample_manifest)
        result = tool._run("orders")

        assert "orders_customers" in result.lower() or "JOIN" in result
        assert "customer_id = customers.id" in result

    def test_search_metrics(self, sample_manifest):
        """Should find metrics by name."""
        tool = create_mdl_semantic_tool(sample_manifest)
        result = tool._run("revenue")

        assert "total_revenue" in result.lower()
        assert "SUM(total_amount)" in result

    def test_search_calculated_columns(self, sample_manifest):
        """Should find calculated columns."""
        tool = create_mdl_semantic_tool(sample_manifest)
        result = tool._run("total_amount")

        assert "CALCULATED" in result or "quantity * unit_price" in result

    def test_no_results(self, sample_manifest):
        """Should return message when no matches found."""
        tool = create_mdl_semantic_tool(sample_manifest)
        result = tool._run("nonexistent_xyz_term")

        assert "No semantic definitions found" in result

    def test_relationship_formatting(self, sample_manifest):
        """Should format relationships with join type."""
        tool = create_mdl_semantic_tool(sample_manifest)
        result = tool._run("products")

        # Check that join type is shown
        assert "N:1" in result or "MANY_TO_ONE" in result


class TestGetMDLContextPrompt:
    """Tests for get_mdl_context_prompt function."""

    def test_generates_context(self, sample_manifest):
        """Should generate context prompt."""
        prompt = get_mdl_context_prompt(sample_manifest)

        assert "Semantic Layer" in prompt
        assert "customers" in prompt
        assert "orders" in prompt
        assert "products" in prompt

    def test_includes_relationships(self, sample_manifest):
        """Should include relationship info."""
        prompt = get_mdl_context_prompt(sample_manifest)

        assert "Relationships" in prompt or "JOINs" in prompt
        assert "customer_id = customers.id" in prompt

    def test_includes_metrics(self, sample_manifest):
        """Should include metric formulas."""
        prompt = get_mdl_context_prompt(sample_manifest)

        assert "Metrics" in prompt
        assert "SUM(total_amount)" in prompt

    def test_empty_manifest(self):
        """Should handle empty manifest."""
        manifest = MDLManifest(catalog="test", schema="public")
        prompt = get_mdl_context_prompt(manifest)

        assert "Semantic Layer" in prompt
        # Should not crash on empty lists


class TestToolIntegration:
    """Integration tests for MDL tool with KaiToolContext."""

    def test_tool_can_be_invoked(self, sample_manifest):
        """Should be able to invoke tool like LangChain tool."""
        tool = create_mdl_semantic_tool(sample_manifest)

        # Simulate LangChain-style invocation
        result = tool.invoke("customer orders")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_async_invocation(self, sample_manifest):
        """Should support async invocation."""
        tool = create_mdl_semantic_tool(sample_manifest)
        result = await tool._arun("revenue metrics")

        assert isinstance(result, str)
        assert "revenue" in result.lower()
