# Chapter 1: Context Asset Lifecycle

> **Duration:** 20 minutes | **Difficulty:** Intermediate | **Format:** CLI + REST API

Learn to create, version, and promote domain knowledge as first-class assets in KAI.

---

## What You'll Build

A complete asset lifecycle for an e-commerce analytics domain:

```
Instruction (Draft) → Verify → Publish → Reuse in missions
Glossary (Draft) → Verify → Publish → Reuse in missions
```

**After this chapter, you'll have:**
- Domain instructions that guide KAI's SQL generation
- Business glossary terms with precise definitions
- Assets promoted through the full lifecycle
- Searchable knowledge base across your database

---

## Prerequisites

Before starting, ensure you've completed:

- [ ] [Context Platform Path Overview](index.md)
- [ ] KAI installed and `uv sync` completed
- [ ] Typesense running (`docker compose up typesense -d`)
- [ ] A database connection created

If you don't have a connection yet:

```bash
# Create a sample connection (PostgreSQL example)
uv run kai connection create "postgresql://user:pass@localhost:5432/ecommerce" -a ecommerce
```

---

## Part 1: Create Your First Context Asset (5 minutes)

### Understanding Asset Types

KAI supports four context asset types:

| Type | Purpose | Example |
|------|---------|---------|
| `table_description` | Describe what a table contains | "orders table stores all customer purchases" |
| `glossary` | Define business terms | "MRR = Monthly Recurring Revenue" |
| `instruction` | Rules for query generation | "Always filter deleted_at IS NULL" |
| `skill` | Reusable analysis patterns | "Revenue trend analysis template" |

### Create an Instruction Asset

Instructions tell KAI how to generate SQL for your specific database. Create one via CLI:

```bash
uv run kai context create \
  --db ecommerce \
  --type instruction \
  --key soft_delete_filter \
  --name "Soft Delete Filter Rule"
```

**Expected output:**
```
Created context asset:
  ID:    ctx_a1b2c3d4e5f6
  Type:  instruction
  Key:   soft_delete_filter
  Name:  Soft Delete Filter Rule
  State: draft
```

### Create via REST API

You can also create assets via the API:

```bash
curl -X POST http://localhost:8015/api/v1/context-assets \
  -H "Content-Type: application/json" \
  -d '{
    "db_connection_id": "ecommerce",
    "asset_type": "instruction",
    "canonical_key": "revenue_calculation",
    "name": "Revenue Calculation Rule",
    "content": {
      "rule": "Always use net_revenue (after refunds) unless explicitly asked for gross revenue",
      "sql_hint": "Use (amount - COALESCE(refund_amount, 0)) AS net_revenue"
    },
    "content_text": "Always use net_revenue (after refunds) unless explicitly asked for gross revenue. Use (amount - COALESCE(refund_amount, 0)) AS net_revenue.",
    "description": "Ensures consistent revenue calculations across all queries",
    "author": "analyst@team.com",
    "tags": ["revenue", "finance", "core-rule"]
  }'
```

**Expected response:**
```json
{
  "id": "ctx_f7g8h9i0j1k2",
  "db_connection_id": "ecommerce",
  "asset_type": "instruction",
  "canonical_key": "revenue_calculation",
  "version": 1,
  "name": "Revenue Calculation Rule",
  "lifecycle_state": "draft",
  "author": "analyst@team.com",
  "tags": ["revenue", "finance", "core-rule"]
}
```

### Create a Glossary Term

```bash
uv run kai context create \
  --db ecommerce \
  --type glossary \
  --key mrr \
  --name "MRR - Monthly Recurring Revenue"
```

---

## Part 2: Manage the Asset Lifecycle (8 minutes)

### Understanding Lifecycle States

Every asset moves through four states:

```
draft → verified → published → deprecated
```

| State | Meaning | Who Can Transition |
|-------|---------|-------------------|
| `draft` | Work in progress, editable | Any analyst |
| `verified` | Reviewed by domain expert | Analyst/lead |
| `published` | Ready for production use | Maintainer/lead |
| `deprecated` | Superseded or obsolete | Maintainer/lead |

### List Your Assets

```bash
uv run kai context list --db ecommerce
```

**Expected output:**
```
Context Assets (ecommerce):
  ID                  Type          Key                  State    Name
  ctx_a1b2c3d4e5f6    instruction   soft_delete_filter   draft    Soft Delete Filter Rule
  ctx_f7g8h9i0j1k2    instruction   revenue_calculation  draft    Revenue Calculation Rule
  ctx_m3n4o5p6q7r8    glossary      mrr                  draft    MRR - Monthly Recurring Revenue
```

### Filter by State

```bash
# Show only published assets
uv run kai context list --db ecommerce --state published

# Show only instructions
uv run kai context list --db ecommerce --type instruction
```

### Promote to Verified

When a domain expert reviews an asset and confirms its accuracy:

```bash
uv run kai context promote ctx_f7g8h9i0j1k2 verified --by "lead@team.com"
```

**Expected output:**
```
Promoted context asset:
  ID:    ctx_f7g8h9i0j1k2
  Name:  Revenue Calculation Rule
  State: draft → verified
  By:    lead@team.com
```

Via REST API:

```bash
curl -X POST http://localhost:8015/api/v1/context-assets/ctx_f7g8h9i0j1k2/promote/verified \
  -H "Content-Type: application/json" \
  -d '{
    "promoted_by": "lead@team.com",
    "change_note": "Reviewed against finance team definitions"
  }'
```

### Promote to Published

After verification, publish the asset for production use:

```bash
uv run kai context promote ctx_f7g8h9i0j1k2 published --by "lead@team.com"
```

The asset is now available for KAI to use during autonomous missions.

### Deprecate When Replaced

When an asset is superseded by a newer version:

```bash
uv run kai context deprecate ctx_a1b2c3d4e5f6 \
  --by "lead@team.com" \
  --reason "Replaced by comprehensive data quality rule set"
```

---

## Part 3: Search, Update, and Version (7 minutes)

### Search Across Assets

Find assets by content or description:

```bash
uv run kai context search --db ecommerce --query "revenue calculation"
```

Via REST API:

```bash
curl -X POST http://localhost:8015/api/v1/context-assets/search \
  -H "Content-Type: application/json" \
  -d '{
    "db_connection_id": "ecommerce",
    "query": "revenue",
    "limit": 10
  }'
```

### View Asset Details

```bash
uv run kai context show ctx_f7g8h9i0j1k2
```

### Update a Draft Asset

Only draft assets can be edited directly:

```bash
uv run kai context update ctx_m3n4o5p6q7r8 \
  --name "MRR - Monthly Recurring Revenue (Updated)"
```

Via REST API:

```bash
curl -X PUT http://localhost:8015/api/v1/context-assets/ctx_m3n4o5p6q7r8 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MRR - Monthly Recurring Revenue",
    "content": {
      "definition": "Sum of all active subscription revenue in a calendar month",
      "formula": "SUM(subscription_amount) WHERE status = active AND billing_period = month",
      "excludes": ["one-time purchases", "refunds", "credits"]
    },
    "content_text": "MRR is the sum of all active subscription revenue in a calendar month. Excludes one-time purchases, refunds, and credits."
  }'
```

### Browse Tags

Discover assets by category:

```bash
uv run kai context tags --category domain
```

### View Version History

Every promotion creates a new version entry:

```bash
# Via API
curl http://localhost:8015/api/v1/context-assets/ctx_f7g8h9i0j1k2/versions
```

**Expected response:**
```json
[
  {
    "version": 2,
    "lifecycle_state": "published",
    "change_summary": "Reviewed against finance team definitions",
    "created_at": "2026-02-26T10:30:00Z"
  },
  {
    "version": 1,
    "lifecycle_state": "draft",
    "change_summary": "Initial creation",
    "created_at": "2026-02-26T10:00:00Z"
  }
]
```

---

## What Could Go Wrong?

**1. "Asset not found" on promote**

- Symptom: `404 Asset not found`
- Fix: Use `kai context list --db <alias>` to find the correct asset ID

**2. "Cannot update non-draft asset"**

- Symptom: `400 LifecyclePolicyError`
- Fix: Only draft assets can be updated. Create a new draft revision instead:
  ```bash
  curl -X POST http://localhost:8015/api/v1/context-assets/{id}/revision \
    -H "Content-Type: application/json" \
    -d '{"author": "analyst@team.com"}'
  ```

**3. "Typesense connection refused"**

- Symptom: Connection errors during create/list
- Fix: Start Typesense with `docker compose up typesense -d`

---

## Summary

In this chapter, you learned:

- [x] **Asset Types** - table_description, glossary, instruction, skill
- [x] **Lifecycle States** - draft → verified → published → deprecated
- [x] **CLI Commands** - create, list, show, update, promote, deprecate, search, tags
- [x] **REST API** - Full CRUD + lifecycle transitions + version history
- [x] **Governance** - Promotion metadata with `promoted_by` and `change_note`

**Key Commands:**
```bash
kai context create --db <alias> --type <type> --key <key> --name "<name>"
kai context list --db <alias> [--type <type>] [--state <state>]
kai context show <asset_id>
kai context update <asset_id> --name "<new_name>"
kai context promote <asset_id> <target_state> --by "<who>"
kai context deprecate <asset_id> --by "<who>" --reason "<why>"
kai context search --db <alias> --query "<search>"
kai context tags [--category <category>]
```

---

## What's Next?

[Chapter 2: Quality Benchmarks →](2-benchmarks.md)

Validate your context assets with automated test suites, track pass rates, and export results for CI pipelines.
