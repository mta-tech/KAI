# MDL Semantic Layer Tutorial

This tutorial covers how to use the MDL (Model Definition Language) module in KAI to create and manage semantic layers for your databases.

## Table of Contents

1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [Getting Started](#getting-started)
4. [Creating MDL Manifests](#creating-mdl-manifests)
5. [Working with Models](#working-with-models)
6. [Defining Relationships](#defining-relationships)
7. [Business Metrics](#business-metrics)
8. [API Reference](#api-reference)
9. [Best Practices](#best-practices)
10. [Integration with Autonomous Agent](#integration-with-autonomous-agent)

---

## Introduction

The MDL module provides a semantic layer abstraction over your database tables. It allows you to:

- Define business-friendly names and descriptions for tables and columns
- Establish relationships between tables
- Create calculated columns and business metrics
- Export to WrenAI-compatible format for advanced analytics

### Why Use a Semantic Layer?

1. **Simplify queries**: Users can query using business terms instead of technical table/column names
2. **Enforce consistency**: Define metrics once, use everywhere
3. **Enable self-service**: Business users can explore data without SQL knowledge
4. **Improve AI accuracy**: LLMs understand your data model better with semantic context

---

## Core Concepts

### MDL Manifest

The top-level container that holds your entire semantic layer definition:

```python
from app.modules.mdl import MDLManifest

manifest = MDLManifest(
    catalog="analytics",      # Database catalog
    schema="public",          # Database schema
    data_source="postgresql", # Database type
    models=[...],             # Table definitions
    relationships=[...],      # Table relationships
    metrics=[...],            # Business metrics
    views=[...],              # Saved queries
)
```

### Models

Models represent database tables with semantic metadata:

```python
from app.modules.mdl import MDLModel, MDLColumn

users_model = MDLModel(
    name="users",
    columns=[
        MDLColumn(name="id", type="INTEGER"),
        MDLColumn(name="email", type="VARCHAR"),
        MDLColumn(name="created_at", type="TIMESTAMP"),
    ],
    primary_key="id",
    properties={"description": "User accounts table"}
)
```

### Relationships

Relationships define how models connect to each other:

```python
from app.modules.mdl import MDLRelationship, JoinType

relationship = MDLRelationship(
    name="orders_users",
    models=["orders", "users"],
    join_type=JoinType.MANY_TO_ONE,
    condition="orders.user_id = users.id"
)
```

### Join Types

| Type | Description | Example |
|------|-------------|---------|
| `ONE_TO_ONE` | Each record in A maps to exactly one in B | user -> user_profile |
| `ONE_TO_MANY` | One record in A maps to many in B | user -> orders |
| `MANY_TO_ONE` | Many records in A map to one in B | orders -> user |
| `MANY_TO_MANY` | Many-to-many relationship | students <-> courses |

---

## Getting Started

### Prerequisites

1. KAI server running with Typesense
2. A database connection configured in KAI
3. Tables scanned via TableDescription

### Installation

The MDL module is included in KAI. No additional installation needed.

### Basic Setup

```python
from app.modules.mdl import (
    MDLService,
    MDLRepository,
    MDLBuilder,
)
from app.data.db.storage import Storage

# Initialize storage and repository
storage = Storage()
repository = MDLRepository(storage=storage)

# Create the service
mdl_service = MDLService(
    repository=repository,
    table_description_repo=storage,  # For auto-generation
)
```

---

## Creating MDL Manifests

### Method 1: Auto-Generate from Database

The easiest way to create an MDL manifest is to generate it from your existing TableDescriptions:

```python
# Auto-generate MDL from scanned tables
manifest_id = await mdl_service.build_from_database(
    db_connection_id="your_connection_id",
    name="Sales Analytics",
    catalog="analytics",
    schema="public",
    data_source="postgresql",
    infer_relationships=True,  # Auto-detect relationships
)

print(f"Created manifest: {manifest_id}")
```

This will:
1. Fetch all TableDescriptions for the connection
2. Convert them to MDL models
3. Infer relationships from foreign keys and column naming conventions
4. Save the manifest to Typesense

### Method 2: Manual Creation

For more control, create manifests manually:

```python
from app.modules.mdl import (
    MDLManifest,
    MDLModel,
    MDLColumn,
    MDLRelationship,
    JoinType,
)

# Define models
customers = MDLModel(
    name="customers",
    columns=[
        MDLColumn(name="id", type="INTEGER"),
        MDLColumn(name="name", type="VARCHAR"),
        MDLColumn(name="email", type="VARCHAR"),
        MDLColumn(name="tier", type="VARCHAR"),
    ],
    primary_key="id",
    properties={"description": "Customer accounts"}
)

orders = MDLModel(
    name="orders",
    columns=[
        MDLColumn(name="id", type="INTEGER"),
        MDLColumn(name="customer_id", type="INTEGER"),
        MDLColumn(name="total_amount", type="DECIMAL"),
        MDLColumn(name="status", type="VARCHAR"),
        MDLColumn(name="created_at", type="TIMESTAMP"),
    ],
    primary_key="id",
    properties={"description": "Customer orders"}
)

# Define relationship
orders_customers = MDLRelationship(
    name="orders_customers",
    models=["orders", "customers"],
    join_type=JoinType.MANY_TO_ONE,
    condition="orders.customer_id = customers.id"
)

# Create manifest
manifest_id = await mdl_service.create_manifest(
    db_connection_id="your_connection_id",
    name="E-Commerce Analytics",
    catalog="ecommerce",
    schema="public",
    data_source="postgresql",
    models=[customers, orders],
    relationships=[orders_customers],
)
```

### Method 3: Using the API

```bash
# Create manifest via REST API
curl -X POST http://localhost:8015/api/v1/mdl/manifests \
  -H "Content-Type: application/json" \
  -d '{
    "db_connection_id": "your_connection_id",
    "name": "Sales Analytics",
    "catalog": "analytics",
    "schema": "public",
    "data_source": "postgresql"
  }'

# Build from database
curl -X POST http://localhost:8015/api/v1/mdl/manifests/build \
  -H "Content-Type: application/json" \
  -d '{
    "db_connection_id": "your_connection_id",
    "name": "Auto-Generated MDL",
    "catalog": "analytics",
    "schema": "public",
    "infer_relationships": true
  }'
```

---

## Working with Models

### Adding Calculated Columns

Calculated columns are derived from expressions:

```python
orders_model = MDLModel(
    name="orders",
    columns=[
        MDLColumn(name="id", type="INTEGER"),
        MDLColumn(name="quantity", type="INTEGER"),
        MDLColumn(name="unit_price", type="DECIMAL"),
        # Calculated column
        MDLColumn(
            name="total_price",
            type="DECIMAL",
            is_calculated=True,
            expression="quantity * unit_price",
            properties={"description": "Total line item price"}
        ),
    ],
    primary_key="id",
)
```

### Adding Models to Existing Manifest

```python
# Via service
new_model = MDLModel(
    name="products",
    columns=[
        MDLColumn(name="id", type="INTEGER"),
        MDLColumn(name="name", type="VARCHAR"),
        MDLColumn(name="price", type="DECIMAL"),
    ],
    primary_key="id",
)

await mdl_service.add_model(manifest_id, new_model)
```

```bash
# Via API
curl -X POST http://localhost:8015/api/v1/mdl/manifests/{manifest_id}/models \
  -H "Content-Type: application/json" \
  -d '{
    "name": "products",
    "columns": [
      {"name": "id", "type": "INTEGER"},
      {"name": "name", "type": "VARCHAR"},
      {"name": "price", "type": "DECIMAL"}
    ],
    "primary_key": "id"
  }'
```

### Removing Models

```python
await mdl_service.remove_model(manifest_id, "products")
```

```bash
curl -X DELETE http://localhost:8015/api/v1/mdl/manifests/{manifest_id}/models/products
```

---

## Defining Relationships

### Relationship Types

#### One-to-Many (Parent to Children)

```python
# One customer has many orders
customer_orders = MDLRelationship(
    name="customer_orders",
    models=["customers", "orders"],
    join_type=JoinType.ONE_TO_MANY,
    condition="customers.id = orders.customer_id"
)
```

#### Many-to-One (Child to Parent)

```python
# Many orders belong to one customer
orders_customer = MDLRelationship(
    name="orders_customer",
    models=["orders", "customers"],
    join_type=JoinType.MANY_TO_ONE,
    condition="orders.customer_id = customers.id"
)
```

### Auto-Inferring Relationships

The MDL Builder can automatically infer relationships based on:

1. **Foreign key constraints** from TableDescriptions
2. **Column naming conventions** (e.g., `customer_id` -> `customers` table)

```python
from app.modules.mdl import MDLBuilder

# Get existing manifest
manifest = await mdl_service.get_manifest(manifest_id)

# Infer additional relationships
updated_manifest = MDLBuilder.infer_relationships(manifest)

# Save the updated manifest
await mdl_service.update_manifest(updated_manifest)
```

### Adding Relationships via API

```bash
curl -X POST http://localhost:8015/api/v1/mdl/manifests/{manifest_id}/relationships \
  -H "Content-Type: application/json" \
  -d '{
    "name": "orders_products",
    "models": ["orders", "products"],
    "join_type": "MANY_TO_ONE",
    "condition": "orders.product_id = products.id"
  }'
```

---

## Business Metrics

Metrics define reusable business calculations:

```python
from app.modules.mdl import MDLMetric, MDLTimeGrain, DatePart

revenue_metric = MDLMetric(
    name="total_revenue",
    base_object="orders",
    dimension=[
        MDLColumn(name="customer_tier", type="VARCHAR"),
        MDLColumn(name="product_category", type="VARCHAR"),
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
            date_parts=[DatePart.YEAR, DatePart.QUARTER, DatePart.MONTH],
        )
    ],
    properties={"description": "Total revenue by customer tier and product category"}
)
```

---

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/mdl/manifests` | Create manifest |
| GET | `/api/v1/mdl/manifests` | List manifests |
| GET | `/api/v1/mdl/manifests/{id}` | Get manifest by ID |
| DELETE | `/api/v1/mdl/manifests/{id}` | Delete manifest |
| POST | `/api/v1/mdl/manifests/build` | Build from database |
| GET | `/api/v1/mdl/manifests/{id}/export` | Export MDL JSON |
| POST | `/api/v1/mdl/manifests/{id}/models` | Add model |
| DELETE | `/api/v1/mdl/manifests/{id}/models/{name}` | Remove model |
| POST | `/api/v1/mdl/manifests/{id}/relationships` | Add relationship |
| DELETE | `/api/v1/mdl/manifests/{id}/relationships/{name}` | Remove relationship |

### Export to WrenAI Format

```python
# Get WrenAI-compatible JSON
mdl_json = await mdl_service.export_mdl_json(manifest_id)
print(json.dumps(mdl_json, indent=2))
```

Output:
```json
{
  "catalog": "analytics",
  "schema": "public",
  "dataSource": "postgresql",
  "models": [
    {
      "name": "customers",
      "columns": [
        {"name": "id", "type": "INTEGER"},
        {"name": "name", "type": "VARCHAR"}
      ],
      "primaryKey": "id"
    }
  ],
  "relationships": [
    {
      "name": "orders_customers",
      "models": ["orders", "customers"],
      "joinType": "MANY_TO_ONE",
      "condition": "orders.customer_id = customers.id"
    }
  ]
}
```

### Validation

Validate manifests against the MDL JSON Schema:

```python
from app.modules.mdl import MDLValidator

# Validate a manifest
is_valid, errors = MDLValidator.validate(mdl_json)

if not is_valid:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
```

---

## Best Practices

### 1. Use Descriptive Names

```python
# Good
MDLModel(name="customer_orders", ...)
MDLRelationship(name="orders_to_customers", ...)

# Avoid
MDLModel(name="tbl_1", ...)
MDLRelationship(name="rel_a_b", ...)
```

### 2. Add Descriptions

```python
MDLColumn(
    name="ltv",
    type="DECIMAL",
    is_calculated=True,
    expression="SUM(order_total)",
    properties={
        "description": "Customer Lifetime Value - total of all orders",
        "displayName": "Lifetime Value"
    }
)
```

### 3. Define Primary Keys

Always specify primary keys for proper relationship handling:

```python
MDLModel(
    name="orders",
    columns=[...],
    primary_key="id",  # Important!
)
```

### 4. Use Consistent Join Types

- Use `MANY_TO_ONE` when the "many" side has the foreign key
- Use `ONE_TO_MANY` when defining from the "one" side's perspective

### 5. Validate Before Deployment

```python
# Always validate before using in production
manifest = await mdl_service.get_manifest(manifest_id)
is_valid, errors = await mdl_service.validate_manifest(manifest)

if not is_valid:
    raise ValueError(f"Invalid manifest: {errors}")
```

### 6. Version Your Manifests

Use the `version` field to track changes:

```python
manifest = MDLManifest(
    catalog="analytics",
    schema="public",
    version="1.2.0",
    ...
)
```

---

## Example: Complete E-Commerce MDL

```python
from app.modules.mdl import (
    MDLManifest,
    MDLModel,
    MDLColumn,
    MDLRelationship,
    MDLMetric,
    MDLTimeGrain,
    JoinType,
    DatePart,
)

# Models
customers = MDLModel(
    name="customers",
    columns=[
        MDLColumn(name="id", type="INTEGER"),
        MDLColumn(name="name", type="VARCHAR"),
        MDLColumn(name="email", type="VARCHAR"),
        MDLColumn(name="tier", type="VARCHAR"),
        MDLColumn(name="created_at", type="TIMESTAMP"),
    ],
    primary_key="id",
    properties={"description": "Customer master data"}
)

products = MDLModel(
    name="products",
    columns=[
        MDLColumn(name="id", type="INTEGER"),
        MDLColumn(name="name", type="VARCHAR"),
        MDLColumn(name="category", type="VARCHAR"),
        MDLColumn(name="price", type="DECIMAL"),
    ],
    primary_key="id",
    properties={"description": "Product catalog"}
)

orders = MDLModel(
    name="orders",
    columns=[
        MDLColumn(name="id", type="INTEGER"),
        MDLColumn(name="customer_id", type="INTEGER"),
        MDLColumn(name="product_id", type="INTEGER"),
        MDLColumn(name="quantity", type="INTEGER"),
        MDLColumn(name="unit_price", type="DECIMAL"),
        MDLColumn(
            name="total",
            type="DECIMAL",
            is_calculated=True,
            expression="quantity * unit_price"
        ),
        MDLColumn(name="status", type="VARCHAR"),
        MDLColumn(name="created_at", type="TIMESTAMP"),
    ],
    primary_key="id",
    properties={"description": "Customer orders"}
)

# Relationships
relationships = [
    MDLRelationship(
        name="orders_customers",
        models=["orders", "customers"],
        join_type=JoinType.MANY_TO_ONE,
        condition="orders.customer_id = customers.id"
    ),
    MDLRelationship(
        name="orders_products",
        models=["orders", "products"],
        join_type=JoinType.MANY_TO_ONE,
        condition="orders.product_id = products.id"
    ),
]

# Metrics
revenue_metric = MDLMetric(
    name="revenue_by_category",
    base_object="orders",
    dimension=[
        MDLColumn(name="category", type="VARCHAR"),
        MDLColumn(name="customer_tier", type="VARCHAR"),
    ],
    measure=[
        MDLColumn(
            name="total_revenue",
            type="DECIMAL",
            is_calculated=True,
            expression="SUM(total)"
        ),
        MDLColumn(
            name="avg_order_value",
            type="DECIMAL",
            is_calculated=True,
            expression="AVG(total)"
        ),
    ],
    time_grain=[
        MDLTimeGrain(
            name="order_date",
            ref_column="created_at",
            date_parts=[DatePart.YEAR, DatePart.MONTH, DatePart.DAY]
        )
    ]
)

# Complete manifest
manifest = MDLManifest(
    name="E-Commerce Analytics",
    catalog="ecommerce",
    schema="public",
    data_source="postgresql",
    models=[customers, products, orders],
    relationships=relationships,
    metrics=[revenue_metric],
    version="1.0.0",
)

# Save to KAI
manifest_id = await mdl_service.create_manifest(
    db_connection_id="your_connection_id",
    name=manifest.name,
    catalog=manifest.catalog,
    schema=manifest.schema,
    data_source=manifest.data_source,
    models=manifest.models,
    relationships=manifest.relationships,
    metrics=manifest.metrics,
)

print(f"Created E-Commerce MDL: {manifest_id}")
```

---

## Integration with Autonomous Agent

The MDL semantic layer integrates with KAI's autonomous SQL generation agent to improve query accuracy by providing:

- **Business term resolution**: Maps user-friendly terms to actual table/column names
- **Metric formulas**: Pre-defined calculations (e.g., "revenue" → `SUM(total_amount)`)
- **Join paths**: Correct relationships between tables
- **Calculated columns**: Derived column expressions

### How It Works

When an MDL manifest is available, the agent receives an additional tool called `mdl_semantic_lookup` that allows it to search the semantic layer for relevant definitions.

```
┌──────────────────────────────────────────────────────────────┐
│                    User Question                              │
│         "Show me total revenue by customer tier"              │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                   MDL Semantic Tool                           │
│   • Searches for "revenue" → Finds metric formula             │
│   • Searches for "customer tier" → Finds column mapping       │
│   • Returns join paths between orders and customers           │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                SQL Generation Agent                           │
│   Uses semantic context to generate accurate SQL:             │
│   SELECT c.tier, SUM(o.total_amount) as revenue               │
│   FROM orders o JOIN customers c ON o.customer_id = c.id      │
│   GROUP BY c.tier                                             │
└──────────────────────────────────────────────────────────────┘
```

### Enabling MDL in Agent Sessions

#### Method 1: Via KaiToolContext (Programmatic)

```python
from app.utils.deep_agent.tools import KaiToolContext, build_tool_specs
from app.modules.mdl import MDLService, MDLRepository
from app.data.db.storage import Storage

# Get the MDL manifest
storage = Storage()
mdl_repo = MDLRepository(storage=storage)
mdl_service = MDLService(repository=mdl_repo)

manifest = await mdl_service.get_manifest(manifest_id)

# Create tool context with MDL
ctx = KaiToolContext(
    database=sql_database,
    db_scan=table_descriptions,
    embedding=embedding_model,
    mdl_manifest=manifest,  # Enable MDL semantic lookup
)

# Build tools - includes mdl_semantic_lookup when manifest is provided
tool_specs = build_tool_specs(ctx)
```

#### Method 2: Via CLI (kai-agent)

```bash
# First, ensure an MDL manifest exists for your database
uv run kai-agent run "Show revenue by customer tier" \
    --db mydb \
    --mdl-manifest-id your_manifest_id
```

### MDL Semantic Lookup Tool

The `mdl_semantic_lookup` tool allows the agent to search semantic definitions:

```python
from app.utils.sql_tools.mdl_semantic_lookup import (
    create_mdl_semantic_tool,
    get_mdl_context_prompt,
)

# Create the tool
tool = create_mdl_semantic_tool(manifest)

# Example searches
print(tool._run("revenue"))
# Output:
# ## Business Metrics:
# **total_revenue** - Total revenue metric
#   Base: orders
#   Dimensions: customer_tier
#   Measure: revenue = SUM(total_amount)
#   Time Grain: order_date on created_at

print(tool._run("customers"))
# Output:
# ## Matching Tables/Models:
# **customers** - Customer master data, PK: id
# Columns:
#   - id: INTEGER
#   - name: VARCHAR (Customer full name)
#   - tier: VARCHAR
#   - created_at: TIMESTAMP
#
# ## Available Joins:
# **orders_customers**: orders N:1 customers
#   JOIN: orders.customer_id = customers.id
```

### System Prompt Context

For enhanced awareness without tool calls, inject MDL context into the agent's system prompt:

```python
from app.utils.sql_tools.mdl_semantic_lookup import get_mdl_context_prompt

# Generate context string for system prompt
mdl_context = get_mdl_context_prompt(manifest)
print(mdl_context)
```

Output:
```
## Semantic Layer (MDL) Context

This database has a semantic layer defined. Use business-friendly names when possible.

### Available Tables:
- **customers** - Customer master data
- **orders** - Customer orders
- **products** - Product catalog

### Table Relationships (use these for JOINs):
- orders → customers: `orders.customer_id = customers.id`
- orders → products: `orders.product_id = products.id`

### Business Metrics (use these formulas):
- **total_revenue.revenue**: `SUM(total_amount)`
- **total_revenue.order_count**: `COUNT(*)`
```

### Agent Behavior with MDL

When the MDL tool is available, the agent will:

1. **Search semantic layer first** before querying raw schema
2. **Use metric formulas** instead of guessing aggregations
3. **Follow defined join paths** for multi-table queries
4. **Map business terms** to actual column/table names

Example agent reasoning:
```
User: "What's our total revenue by product category this month?"

Agent thinking:
1. Search MDL for "revenue" → Found metric with SUM(total_amount) formula
2. Search MDL for "product category" → Found in products.category column
3. Search MDL for "orders" → Found relationship orders_products
4. Generate SQL using the semantic definitions...
```

### Best Practices for Agent Integration

1. **Define all important metrics**: Pre-define common business metrics so the agent uses consistent formulas

2. **Add column descriptions**: Help the agent understand what each column represents
   ```python
   MDLColumn(
       name="ltv",
       type="DECIMAL",
       properties={"description": "Customer Lifetime Value"}
   )
   ```

3. **Name relationships clearly**: Use descriptive names like `orders_customers` instead of `rel_1`

4. **Include time grains**: Define time dimensions for proper date handling
   ```python
   MDLTimeGrain(
       name="order_date",
       ref_column="created_at",
       date_parts=[DatePart.YEAR, DatePart.MONTH, DatePart.DAY]
   )
   ```

5. **Keep manifests updated**: Update the MDL when schema changes to maintain accuracy

---

## Next Steps

- Explore the [MDL JSON Schema](/app/modules/mdl/schema/mdl.schema.json) for the complete specification
- Check out the [test examples](/tests/modules/mdl/) for more usage patterns
- Review the [WrenAI MDL documentation](https://docs.getwren.ai/oss/concept/what-is-mdl) for advanced features

For questions or issues, see the main KAI documentation.
