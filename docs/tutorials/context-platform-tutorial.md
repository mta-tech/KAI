# Tutorial: Context Platform for Domain Knowledge Management

This tutorial introduces KAI's **Context Platform** - a powerful system for managing, versioning, and sharing domain knowledge across your analytics projects. You'll learn how to create, manage, and promote context assets through their lifecycle.

**What you'll learn:**
- What Context Assets are and the four types available
- How to create and manage assets through their lifecycle
- How to use benchmarks to validate asset quality
- How to track asset reuse with telemetry
- Best practices for building a knowledge repository

**Time:** 25-30 minutes  
**Difficulty:** Intermediate  
**Prerequisites:** Basic familiarity with KAI and database connections

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Introduction to Context Assets](#introduction-to-context-assets)
3. [Context Asset Lifecycle](#context-asset-lifecycle)
4. [Creating Your First Asset](#creating-your-first-asset)
5. [Managing Assets](#managing-assets)
6. [Search and Discovery](#search-and-discovery)
7. [Benchmarking Assets](#benchmarking-assets)
8. [Tracking Reuse with Telemetry](#tracking-reuse-with-telemetry)
9. [Best Practices](#best-practices)

---

## Prerequisites

Before starting, ensure you have:

- **KAI installed** with dependencies synced
- **Typesense running** for storage backend
- **A database connection** created in KAI
- **Google API Key** or OpenAI key configured

```bash
# Verify Typesense is running
docker compose ps typesense

# List your available connections
uv run kai connection list

# If Typesense is not running
docker compose up typesense -d
```

---

## Introduction to Context Assets

**Context Assets** are reusable domain knowledge artifacts that improve KAI's query accuracy and analysis quality. Unlike ephemeral skills or instructions, context assets are:

- **Versioned**: Track changes over time with semantic versioning
- **Shareable**: Promote through lifecycle states for team reuse
- **Searchable**: Find assets by semantic search across content
- **Measured**: Track reuse metrics and effectiveness with benchmarks

### Four Types of Context Assets

| Type | Purpose | Example |
|------|---------|---------|
| **table_description** | Descriptive metadata about database tables | "fact_sales contains transaction records with..." |
| **glossary** | Business terminology and metric definitions | "Active Users = users who logged in within 30 days" |
| **instruction** | Domain-specific analysis rules | "When analyzing YTD, always use fiscal year start date" |
| **skill** | Reusable analysis patterns and templates | SQL patterns for cohort analysis |

### When to Use Context Platform vs. Skills/Instructions

| Feature | Context Platform | Legacy Skills/Instructions |
|----------|-----------------|---------------------------|
| **Versioning** | Full semantic versioning | No versioning |
| **Lifecycle** | draft → verified → published → deprecated | None |
| **Sharing** | Promote for team-wide reuse | Local to connection |
| **Search** | Semantic search across all assets | Limited discovery |
| **Telemetry** | Track reuse and effectiveness | No metrics |
| **Use Case** | Production knowledge management | Quick experimentation |

---

## Context Asset Lifecycle

Context assets progress through four lifecycle states:

```
┌─────────┐     ┌──────────┐     ┌───────────┐     ┌────────────┐
│  draft   │────►│ verified  │────►│ published  │────►│ deprecated │
└─────────┘     └──────────┘     └───────────┘     └────────────┘
                  ▲                   │
                  │                   │
                  └───────────────────┘ (can return for revision)
```

### Lifecycle States

1. **draft**: Initial creation state. Asset is visible only to creator, not yet validated.

2. **verified**: Asset has been reviewed by a domain expert. Ready for team use but not yet broadly promoted.

3. **published**: Asset approved for reuse across missions and connections. The "gold standard" state.

4. **deprecated**: Asset superseded or no longer relevant. Still exists but marked for replacement.

### Lifecycle Promotion

```bash
# Promote to verified
kai context promote <asset_id> verified --by "Jane Doe"

# Promote to published
kai context promote <asset_id> published --by "Jane Doe" --note "Approved for production"

# Deprecate (from any state)
kai context deprecate <asset_id> --by "Jane Doe" --reason "Replaced by v2.0"
```

---

## Creating Your First Asset

Let's create a **glossary** asset defining business metrics.

### Step 1: Prepare the Content

Create a JSON file with your asset content:

```json
{
  "metrics": [
    {
      "name": "Gross Margin",
      "definition": "Revenue minus Cost of Goods Sold, divided by Revenue",
      "sql_template": "SELECT SUM(revenue - cost) / SUM(revenue) FROM sales"
    },
    {
      "name": "YTD Sales",
      "definition": "Year-to-Date sales from fiscal year start",
      "sql_template": "SELECT SUM(amount) WHERE date >= fiscal_year_start"
    }
  ]
}
```

Save this as `glossary_content.json`.

### Step 2: Create the Asset

```bash
kai context create \
  --db mydb \
  --type glossary \
  --key financial_metrics \
  --name "Financial Metrics Glossary" \
  --description "Standard financial metric definitions for sales analysis" \
  --content-file glossary_content.json \
  --tags "finance,sales,metrics" \
  --author "your-name"
```

**Expected output:**
```
✔ Context asset created
ID: glossary_abc123...
Name: Financial Metrics Glossary
Type: glossary
Key: financial_metrics
State: draft
```

### Step 3: Verify Creation

```bash
kai context list --db mydb --type glossary
```

---

## Managing Assets

### Listing Assets

```bash
# List all assets for a database
kai context list --db mydb

# Filter by type
kai context list --db mydb --type instruction

# Filter by lifecycle state
kai context list --db mydb --state published

# Combine filters
kai context list --db mydb --type skill --state verified --limit 20
```

**Output columns:**
- **Type**: Asset type (table_description, glossary, instruction, skill)
- **Key**: Canonical key (unique identifier)
- **Name**: Human-readable name
- **State**: Current lifecycle state
- **Version**: Semantic version
- **Updated**: Last modification date

### Viewing Asset Details

```bash
kai context show <asset_id>
```

Shows complete asset information:
- Identity fields (ID, type, key, database)
- Lifecycle state and version
- Full content (formatted JSON)
- Tags and metadata
- Timestamps

### Updating Assets

```bash
# Update name only
kai context update <asset_id> --name "Updated Name"

# Update content from file
kai context update <asset_id> --content-file new_content.json

# Update content inline
kai context update <asset_id> --content '{"new": "value"}'

# Replace tags
kai context update <asset_id> --tags "finance,v2.0"
```

**Note**: Updates preserve the asset ID but increment `updated_at` timestamp.

### Deleting Assets

```bash
# Delete latest version
kai context delete mydb instruction sales_analysis

# Delete specific version
kai context delete mydb instruction sales_analysis --version 1.0.0

# Skip confirmation
kai context delete mydb instruction sales_analysis --force
```

---

## Search and Discovery

### Semantic Search

Find assets by meaning, not just keywords:

```bash
kai context search --db mydb --query "sales analysis patterns"
kai context search --db mydb --query "financial metrics" --limit 20
```

Search uses **hybrid approach**:
- **Semantic search**: Finds related concepts (e.g., "revenue" → "income")
- **Keyword search**: Exact matches for specific terms
- Results ranked by combined relevance score

**Output columns:**
- **Type**: Asset type
- **Key**: Canonical key
- **Name**: Asset name
- **Score**: Relevance score (0.0 to 1.0)

### Tag-Based Discovery

```bash
# List all tags
kai context tags

# Filter by category
kai context tags --category domain
```

Shows:
- **Tag**: Tag name
- **Category**: Optional category grouping
- **Usage**: Number of assets with this tag

---

## Benchmarking Assets

Benchmarks validate context asset quality by testing SQL generation against known-good queries.

### What is a Benchmark Suite?

A **benchmark suite** contains test cases that:
- Define expected SQL for specific queries
- Tag cases by severity (smoke, critical, regression)
- Measure execution performance
- Track pass/fail rates

### Running a Benchmark

```bash
# Run all cases in a suite
kai benchmark run suite_123 --db mydb

# Filter by tags
kai benchmark run suite_123 --db mydb --tags smoke,critical

# Export results
kai benchmark run suite_123 --db mydb --export results.json
kai benchmark run suite_123 --db mydb --export report.xml --format junit
```

**Expected output:**
```
Running Benchmark Suite: Sales Analysis Validation
Database: mydb
Cases to run: 15

Executing benchmarks...

Benchmark Results:
Status: COMPLETED
Score: 87.3%
Pass Rate: 13/15 (86.7%)
Execution Time: 2250ms

Severity Breakdown:
┌───────────┬──────┬───────┬──────────┐
│ Severity   │ Pass │ Fail  │ % Pass   │
├───────────┼──────┼───────┼──────────┤
│ smoke      │ 5    │ 0     │ 100.0%   │
│ critical   │ 8    │ 2     │ 80.0%    │
│ regression │ 0    │ 0     │ -         │
└───────────┴──────┴───────┴──────────┘
```

### Viewing Benchmark Information

```bash
# List available suites
kai benchmark list

# View suite details
kai benchmark info suite_123

# View results from a run
kai benchmark results <run_id>
```

### Interpreting Results

- **Score**: Weighted pass rate (critical cases weigh more)
- **Pass Rate**: Simple percentage of passed cases
- **Execution Time**: Total milliseconds for suite completion
- **Severity**: Classification of test importance

Use benchmarks to:
- Validate assets before promotion to published
- Catch regressions when updating assets
- Compare asset quality across versions

---

## Tracking Reuse with Telemetry

The Context Platform automatically tracks how assets are used, providing insights into effectiveness and ROI.

### What Gets Tracked

**Reuse Events**: Each time an asset is used in:
- **mission**: Regular analysis queries
- **benchmark**: Validation test runs
- **validation**: Manual verification workflows

**Metrics Tracked**:
- `reuse_count`: Total times asset was used
- `last_reused_at`: Most recent usage timestamp
- `reuse_by_type`: Breakdown by context (mission, benchmark, etc.)

### Viewing Asset KPIs

```bash
# View KPIs for a specific asset
kai context show <asset_id>

# The output includes telemetry metrics:
# - Reuse count
# - Last used timestamp
# - Usage by type
```

### Organization-Level Metrics

Telemetry enables team-wide insights:
- **Top reused assets**: Find most valuable knowledge
- **Underutilized assets**: Identify needs for deprecation
- **ROI analysis**: Assets reused ≥5 times are "high ROI"

---

## Best Practices

### 1. Start Draft, Verify Before Publishing

Always create assets in `draft` state:
1. Create and test locally
2. Verify with domain experts
3. Promote to `verified` for team use
4. Promote to `published` for broader adoption

```bash
# Create
kai context create --db mydb --type instruction --key revenue_rule --content-file rule.json

# After review
kai context promote <asset_id> verified --by "Domain Expert" --note "Reviewed and validated"

# After team approval
kai context promote <asset_id> published --by "Tech Lead" --note "Approved for production"
```

### 2. Use Semantic Versioning

When updating assets, increment version meaningfully:
- **Major (1.0.0 → 2.0.0)**: Breaking changes, incompatible updates
- **Minor (1.0.0 → 1.1.0)**: Backward-compatible additions
- **Patch (1.0.0 → 1.0.1)**: Bug fixes, minor improvements

### 3. Tag Thoughtfully

Use consistent tag conventions:
- **Domain**: `finance`, `sales`, `operations`
- **Use case**: `reporting`, `ad-hoc`, `automation`
- **Status**: `experimental`, `stable`, `deprecated`

```bash
kai context create ... --tags "finance,reporting,stable"
```

### 4. Benchmark Before Publishing

Run benchmarks to validate quality:
```bash
# Create benchmark suite
kai benchmark create --db mydb --name "Financial Analysis Validation"

# Add test cases
kai benchmark add-case <suite_id> --name "Gross Margin Calculation" \
  --query "Calculate gross margin" \
  --expected "SELECT SUM(revenue - cost) / SUM(revenue) FROM sales"

# Run validation
kai benchmark run <suite_id> --db mydb

# Only promote if passing
kai context promote <asset_id> verified --by "QA Lead"
```

### 5. Deprecate Responsibly

When deprecating assets:
1. **Add replacement reference**: Note what replaces it
2. **Provide migration path**: How to update dependent assets
3. **Wait for adoption**: Allow time for teams to transition

```bash
kai context deprecate <asset_id> \
  --by "Tech Lead" \
  --reason "Superseded by financial_metrics_v2. Use key: financial_metrics_v2"
```

### 6. Search Before Creating

Avoid duplicate assets by searching first:
```bash
# Check if similar asset exists
kai context search --db mydb --query "gross margin calculation"

# If found, consider:
# - Can you use existing asset?
# - Should you update existing instead of creating new?
# - Is your use case different enough to warrant new asset?
```

---

## Next Steps

Now that you understand the Context Platform, explore:

1. **Context Platform User Guide**: Comprehensive reference for all features
2. **API Documentation**: REST endpoints for programmatic access
3. **Architecture Docs**: Deep dive into implementation details

### Quick Reference

```bash
# Asset lifecycle
kai context create --db <db> --type <type> --key <key> --name "<name>"
kai context list --db <db> [--type <type>] [--state <state>]
kai context show <asset_id>
kai context update <asset_id> [--name "<name>"] [--content-file <file>]
kai context promote <asset_id> <target_state> --by "<who>"
kai context deprecate <asset_id> --by "<who>" --reason "<why>"
kai context delete <db> <type> <key>

# Search and discovery
kai context search --db <db> --query "<query>"
kai context tags [--category <category>]

# Benchmarking
kai benchmark run <suite_id> --db <db>
kai benchmark list
kai benchmark info <suite_id>
kai benchmark results <run_id>
```

---

## Troubleshooting

### "No context assets found"

- Verify database connection: `kai connection list`
- Check Typesense is running: `docker compose ps typesense`
- Confirm assets exist: `kai context list --db <db>`

### "Asset not found"

- Use exact asset ID from `kai context list`
- For delete command, use `db_connection_id asset_type canonical_key` format

### "Promotion failed"

- Verify current state: `kai context show <asset_id>`
- Check promotion order: `draft → verified → published`
- Ensure you have permissions (in multi-user setups)

### "Benchmark failed"

- Verify database connection is valid
- Check expected SQL syntax
- Ensure test cases have proper tags
- Review individual case failures with `kai benchmark results <run_id>`

---

*Happy knowledge building with KAI Context Platform!*
