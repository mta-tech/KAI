# MDL CLI Commands Brainstorm

**Date:** 2026-01-28
**Status:** Draft
**Related Issue:** TBD

---

## What We're Building

Add CLI commands to view and manage MDL (semantic layer) manifests for database connections.

**Goal:** Enable users to verify MDL generation and understand the semantic layer structure through the CLI.

## Why This Approach

**User Requirements:**
- Primary use case: Verification and understanding
- Scope: Core commands (not full management suite)
- Detail level: Summary with drill-down capability
- Output: Default terminal view + export options

**Chosen Approach:** Grouped MDL subcommand structure

This approach groups all MDL-related commands under a single `mdl` subcommand, which:
- Keeps the CLI namespace organized
- Makes it easy to extend with more MDL operations later
- Follows patterns used by other modern CLIs (git, docker, kubectl)
- Separates MDL concerns from other KAI features

## Key Decisions

### 1. Command Structure

```bash
kai mdl list [--db <connection_id>]    # List MDL manifests
kai mdl show <manifest_id>              # Show manifest summary
kai mdl show <manifest_id> --models     # Show with model details
kai mdl show <manifest_id> --relationships  # Show with relationships
kai mdl export <manifest_id> -f json -o file.md  # Export manifest
```

**Rationale:** Groups MDL operations together while maintaining discoverability.

### 2. Display Philosophy

Based on WrenAI MDL specification, the MDL provides semantic layer context that improves KAI's reasoning capabilities.

**Default (`show`):** Summary view with:
- Manifest metadata (name, catalog, schema, created date)
- Model count and relationship count
- List of model names (compact)
- **NEW:** LLM context summary (properties that aid reasoning)

**With flags:** Drill-down into details:
- `--models`: Show all models with columns, types, primary keys, and calculated fields
- `--relationships`: Show relationship topology (tree/graph view)
- `--metrics`: Show business metrics if defined
- `--lineage`: Show calculated field dependencies through relationships

**Rationale:** Balances quick verification with ability to dive deeper when needed. Shows information that matters for LLM reasoning.

### 3. Output Formats

- **Default:** Rich terminal output with colors and tables (for human consumption)
- **`--json`:** Machine-readable JSON (for scripting, APIs)
- **`-f markdown -o file.md`:** Export as Markdown (for documentation)

**Rationale:** Supports both interactive use and automation/sharing workflows.

### 4. Integration with Existing Patterns

- Follow existing KAI CLI patterns (list-connections, show-connection, list-tables)
- Use Rich library for terminal formatting (tables, panels, colors)
- Leverage existing `MDLRepository` and `MDLService` classes

### 5. Identifier Resolution (NEW)

**Support both UUID and database alias:**
- `kai mdl show 4f8d0993...` - Use specific manifest ID
- `kai mdl show koperasi` - Use database alias (shows latest MDL for that connection)
- Resolution order: Try alias first, then UUID (same as `interactive` command)

**Partial ID matching with confirmation:**
- `kai mdl show 4f8d0` matches `4f8d0993-96d6-4608-ac01-1df26af106ef`
- If ambiguous: Show options and let user choose
- If unique: Auto-match without prompting
- Pattern: Similar to `git` SHA matching

**Rationale:** Balances usability (shorter IDs) with safety (confirmation when ambiguous).

### 6. WrenAI-Based Display Patterns (UPDATED)

**Model Display (--models):**
Following WrenAI structure, each model should show:
- Model name and reference type (refSql vs tableReference)
- Primary key
- Columns with: name, type, nullable, isCalculated, relationship (if applicable)
- Properties/metadata (for LLM context)

Example output:
```
Model: Orders (refSql: select * from tpch.orders)
  Primary Key: orderkey
  Columns:
    orderkey         INTEGER      NOT NULL
    custkey          INTEGER
    customer         Customer     → relationship: CustomerOrders
    customer_name    VARCHAR      CALCULATED: customer.name
    total_amount     NUMERIC      CALCULATED: SUM(amount)
```

**Relationship Display (--relationships):**
Tree/graph view showing model connections:
```
Relationships (3):

  CustomerOrders (MANY_TO_ONE)
    Orders.custkey = Customer.custkey

  OrderItems (ONE_TO_MANY)
    Orders.orderkey = Items.orderkey

  [Visual tree]
  Customer (1) ───< (M) Orders (1) ───< (M) Items
```

**Lineage Display (--lineage):**
Show calculated field dependencies:
```
Calculated Field Lineage:

  Orders.customer_name
    └─ depends on: Customer.name
       └─ via: CustomerOrders relationship

  Orders.total_amount
    └─ aggregates: Items.amount
       └─ via: OrderItems relationship
```

**Rationale:** These patterns follow WrenAI's MDL structure and highlight the semantic layer information that improves KAI's reasoning about data relationships.

**Rationale:** These patterns follow WrenAI's MDL structure and highlight the semantic layer information that improves KAI's reasoning about data relationships.

### 7. How MDL Improves KAI Reasoning (NEW)

The MDL semantic layer provides several benefits for KAI's query generation and reasoning:

1. **Business Terminology**: Models and columns can have `properties` with business-friendly descriptions that guide LLM understanding

2. **Relationship Awareness**: Pre-defined relationships prevent KAI from guessing joins incorrectly
   - Knows cardinality (ONE_TO_MANY, MANY_TO_ONE)
   - Has explicit join conditions
   - Can traverse relationships for multi-hop queries

3. **Calculated Fields**: Reusable business logic that KAI can reference instead of re-implementing
   - `customer_name` instead of complex joins
   - `total_amount` instead of aggregation logic
   - Consistent calculations across queries

4. **Topology Awareness**: Understanding the DAG of model dependencies helps KAI:
   - Choose optimal query paths
   - Avoid circular dependencies
   - Identify aggregation opportunities

**CLI Display Implications:**
The CLI should highlight these reasoning-augmenting features:
- Mark relationship columns prominently (→ relationship_name)
- Show calculated field expressions
- Display join conditions clearly
- Visualize the dependency graph

This is why `--models`, `--relationships`, and `--lineage` flags are important - they let users verify that KAI will have the right semantic context.

## Open Questions

1. **Should we add validation command?**
   - `kai mdl validate <id>` to check manifest integrity
   - Could detect issues like orphaned relationships or missing models

2. **Should we add diff command?**
   - `kai mdl diff <id1> <id2>` to compare two manifests
   - Useful for understanding what changed after re-scanning

3. **Should `list` support filtering by date?**
   - `kai mdl list --created-after 2026-01-01`
   - Useful for finding recent MDL generations

4. **Should we add lineage command?**
   - `kai mdl lineage <id> --field Orders.customer_name`
   - Trace calculated field dependencies through relationships
   - Could be part of `show --lineage` instead

5. **Should we add topology command?**
   - `kai mdl topology <id>` to show just the dependency graph
   - Useful for understanding the overall schema structure

## Decided During Brainstorm

- ✅ Command structure: Grouped under `mdl` subcommand (Click Group in main CLI)
- ✅ File location: Add to `app/modules/autonomous_agent/cli.py` (not a new module)
- ✅ Formatting: Rich Tables for lists, Panels for details, Tree for relationships
- ✅ Identifier resolution: Support both UUID and alias with partial matching
- ✅ Display formats: Default terminal + export options (JSON/Markdown)
- ✅ Model display: WrenAI-style with columns, types, calculated fields, relationships
- ✅ Relationship display: Tree/graph view showing model connections
- ✅ Lineage tracking: Show calculated field dependencies
- ✅ LLM context properties: Highlight business terminology in MDL

## Implementation Notes

**Files to modify:**
- `app/modules/autonomous_agent/cli.py` - Add MDL commands to main CLI (already 4000+ lines)
- Use Click `Group` for `mdl` subcommand to keep commands organized
- No new files needed

**Re-use existing:**
- `MDLRepository` - Already has `find_all()`, `find_by_id()`
- `MDLService` - Already has business logic
- `MDLManifest`, `MDLModel`, `MDLRelationship`, etc. - Data models already defined

**CLI patterns to follow:**
- `list-connections` - Simple Rich Table format
- `show-connection` - Panel-based detail view
- Rich library - Tables for lists, Panels for details
- For relationships: Consider using `rich.tree.Tree` for visual graph

## Examples

```bash
# List all MDL manifests
$ kai mdl list
MDL Manifests:
  4f8d0993-96d6-4608-ac01-1df26af106ef: koperasi Semantic Layer (5 models, 0 relationships)
  a1b2c3d4-5678-90ab-cdef-123456789012: sales_db Semantic Layer (12 models, 8 relationships)

# List MDLs for a specific connection (by alias)
$ kai mdl list --db koperasi
MDL Manifests for koperasi:
  4f8d0993-96d6-4608-ac01-1df26af106ef: koperasi Semantic Layer (5 models, 0 relationships)

# Show summary using full ID
$ kai mdl show 4f8d0993-96d6-4608-ac01-1df26af106ef
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ┓
┃ MDL Manifest: koperasi Semantic Layer                           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ┩
│ ID:        4f8d0993-96d6-4608-ac01-1df26af106ef                │
│ Catalog:   koperasi                                              │
│ Schema:    public                                                │
│ Created:   2026-01-28T10:30:45Z                                │
│                                                                  │
│ Models:     5                                                    │
│   - fact_kpi, dim_period, dim_management, dim_geography,       │
│     dim_cooperative                                              │
│                                                                  │
│ Relationships: 0                                                 │
└──────────────────────────────────────────────────────────────────┘

# Show using database alias (latest MDL for that connection)
$ kai mdl show koperasi
[Shows same as above - finds latest MDL for koperasi connection]

# Show using partial ID (auto-matches if unique)
$ kai mdl show 4f8d0
[Shows manifest 4f8d0993-96d6-4608-ac01-1df26af106ef]

# Show with model details (WrenAI-style)
$ kai mdl show 4f8d0 --models
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ┓
┃ Model: Orders                                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ┩
│ Reference: refSql                                                 │
│   select * from tpch.orders                                        │
│ Primary Key: orderkey                                             │
│                                                                   │
│ Columns:                                                          │
│   name           type      nullable  calculated  relationship    │
│   ─────────────  ─────────  ────────  ──────────  ──────────────  │
│   orderkey       INTEGER   false     false                        │
│   custkey        INTEGER   true      false                        │
│   customer       Customer  true      false       CustomerOrders  │
│   customer_name  VARCHAR   true      true        customer.name    │
│   total_amount   NUMERIC   true      true        SUM(items.amt)  │
└───────────────────────────────────────────────────────────────────┘

# Show with relationship graph
$ kai mdl show 4f8d0 --relationships
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ┓
┃ Relationship Topology                                             ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ┩
│                                                                   │
│  CustomerOrders (MANY_TO_ONE)                                     │
│    Orders.custkey = Customer.custkey                              │
│                                                                   │
│  OrderItems (ONE_TO_MANY)                                         │
│    Orders.orderkey = Items.orderkey                              │
│                                                                   │
│  [Dependency Graph]                                               │
│                                                                   │
│    Customer (1) ────< (M) Orders (1) ────< (M) Items              │
│                      │                                            │
│                      └──> (calculated fields flow downstream)    │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘

# Show calculated field lineage
$ kai mdl show 4f8d0 --lineage
Calculated Field Dependencies:

  Orders.customer_name
    └─ Customer.name (via CustomerOrders)

  Orders.total_amount
    └─ SUM(Items.amount) (via OrderItems)

# Export as WrenAI-compatible JSON
$ kai mdl export koperasi -f json -o koperasi_mdl.json
Exported to koperasi_mdl.json (WrenAI-compatible format)

# Export as Markdown documentation
$ kai mdl export 4f8d0 -f markdown -o koperasi_mdl.md
Exported to koperasi_mdl.md
```

## Next Steps

1. Implement MVP: `list` and `show` (summary only)
2. Add drill-down flags (`--models`, `--relationships`)
3. Add export functionality
4. Consider additional commands based on user feedback

## References

- Existing CLI: `app/modules/autonomous_agent/cli.py`
- MDL Module: `app/modules/mdl/`
- WrenAI MDL Documentation:
  - [Overview](https://docs.getwren.ai/oss/engine/guide/modeling/overview)
  - [Model](https://docs.getwren.ai/oss/engine/guide/modeling/model)
  - [Relationship](https://docs.getwren.ai/oss/engine/guide/modeling/relation)
  - [Calculated Fields](https://docs.getwren.ai/oss/engine/guide/modeling/calculated)
