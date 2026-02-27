# Context Platform User Guide

The **Context Platform** is KAI's knowledge management system for creating, versioning, and sharing domain knowledge assets. This guide provides comprehensive reference for all features.

**Contents:**
- [Overview](#overview)
- [Asset Types](#asset-types)
- [CLI Reference](#cli-reference)
- [Lifecycle Management](#lifecycle-management)
- [Search and Discovery](#search-and-discovery)
- [Benchmarking](#benchmarking)
- [Telemetry and KPIs](#telemetry-and-kpis)
- [REST API](#rest-api)

---

## Overview

### What are Context Assets?

Context Assets are reusable domain knowledge artifacts that improve KAI's query accuracy and analysis quality. Unlike ephemeral configurations, context assets are:

- **Versioned**: Full semantic versioning with change history
- **Shareable**: Lifecycle states (draft → verified → published → deprecated)
- **Searchable**: Semantic search across all asset content
- **Measured**: Track reuse metrics and effectiveness

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Canonical Key** | Unique identifier for asset within database+type |
| **Lifecycle State** | Current state: draft, verified, published, deprecated |
| **Version** | Semantic version string (e.g., "1.2.3") |
| **Tags** | User-defined labels for categorization and discovery |
| **Telemetry** | Automatic tracking of reuse and effectiveness |

---

## Asset Types

### table_description

Descriptive metadata about database tables and their relationships.

**Use Case:** Document table semantics beyond column names.

**Content Structure:**
```json
{
  "table_name": "fact_sales",
  "description": "Transactional sales records with product and customer dimensions",
  "columns": {
    "revenue": "Total sales amount in USD",
    "cost": "Cost of goods sold",
    "quantity": "Units sold"
  },
  "relationships": [
    "JOIN dim_product ON product_id",
    "JOIN dim_customer ON customer_id"
  ]
}
```

**Example:**
```bash
kai context create \
  --db mydb \
  --type table_description \
  --key fact_sales \
  --name "Sales Fact Table" \
  --content-file sales_table.json
```

### glossary

Business terminology, metric definitions, and domain-specific vocabulary.

**Use Case:** Define business terms and calculation methods.

**Content Structure:**
```json
{
  "terms": [
    {
      "name": "Active User",
      "definition": "User who logged in within last 30 days",
      "sql": "user WHERE last_login >= NOW() - INTERVAL 30 DAY"
    },
    {
      "name": "Gross Margin",
      "definition": "Revenue minus COGS, divided by revenue",
      "sql": "SUM(revenue - cost) / SUM(revenue)"
    }
  ]
}
```

**Example:**
```bash
kai context create \
  --db mydb \
  --type glossary \
  --key business_metrics \
  --name "Business Metrics Glossary" \
  --content-file glossary.json
```

### instruction

Domain-specific analysis rules and conditional behaviors.

**Use Case:** Enforce business rules and handle edge cases.

**Content Structure:**
```json
{
  "condition": "When user asks about YTD",
  "rules": [
    "Always use fiscal_year_start from config table",
    "Filter by date >= fiscal_year_start",
    "Never use calendar year boundaries"
  ],
  "examples": [
    {
      "query": "YTD sales",
      "expected_behavior": "Use fiscal year start date"
    }
  ]
}
```

**Example:**
```bash
kai context create \
  --db mydb \
  --type instruction \
  --key ytd_rules \
  --name "YTD Analysis Rules" \
  --content-file ytd_rules.json
```

### skill

Reusable analysis patterns, SQL templates, and multi-step workflows.

**Use Case:** Document analysis patterns for complex queries.

**Content Structure:**
```json
{
  "name": "Cohort Analysis",
  "description": "Perform cohort retention analysis",
  "steps": [
    {
      "step": 1,
      "action": "Calculate cohort dates",
      "sql": "SELECT user_id, MIN(order_date) as cohort_date FROM orders GROUP BY user_id"
    },
    {
      "step": 2,
      "action": "Calculate retention by period",
      "sql": "SELECT cohort_date, DATE_DIFF(order_date, cohort_date) as period, COUNT(DISTINCT user_id)"
    }
  ],
  "patterns": [
    "Always group by cohort_date",
    "Use DATE_DIFF for period calculation"
  ]
}
```

**Example:**
```bash
kai context create \
  --db mydb \
  --type skill \
  --key cohort_analysis \
  --name "Cohort Retention Analysis" \
  --content-file cohort_skill.json
```

---

## CLI Reference

### context create

Create a new context asset.

```bash
kai context create \
  --db <db_connection_id_or_alias> \
  --type <asset_type> \
  --key <canonical_key> \
  --name "<name>" \
  [--description "<description>"] \
  [--content-file <path>] \
  [--content <json_string>] \
  [--tags <comma_separated>] \
  [--author <name>]
```

**Parameters:**
- `--db, -d`: Database connection ID or alias (required)
- `--type`: Asset type - table_description, glossary, instruction, skill (required)
- `--key`: Unique canonical key for this asset (required)
- `--name`: Human-readable name (required)
- `--description`: Optional detailed description
- `--content-file`: Path to JSON file with content
- `--content`: JSON string with content (alternative to file)
- `--tags`: Comma-separated tag list
- `--author`: Creator name or identifier

**Examples:**
```bash
# Create from file
kai context create \
  --db mydb \
  --type glossary \
  --key financial_metrics \
  --name "Financial Metrics" \
  --content-file metrics.json \
  --author "Jane Doe"

# Create with inline content
kai context create \
  --db mydb \
  --type instruction \
  --key java_regions \
  --name "Java Provinces" \
  --content '{"condition": "When asked about Java", "rules": ["Include Jakarta, Banten, Yogyakarta"]}'
```

### context list

List context assets with filtering.

```bash
kai context list \
  --db <db_connection_id_or_alias> \
  [--type <asset_type>] \
  [--state <lifecycle_state>] \
  [--limit <n>]
```

**Parameters:**
- `--db, -d`: Database connection ID or alias (required)
- `--type`: Filter by asset type
- `--state`: Filter by lifecycle state (draft, verified, published, deprecated)
- `--limit`: Maximum results (default: 50)

**Examples:**
```bash
# All assets
kai context list --db mydb

# Published skills only
kai context list --db mydb --type skill --state published

# First 20 verified assets
kai context list --db mydb --state verified --limit 20
```

### context show

Display detailed asset information.

```bash
kai context show <asset_id>
```

**Output:**
- Identity (ID, type, key, database)
- Lifecycle (state, version)
- Full content (formatted JSON)
- Tags and metadata
- Timestamps

### context update

Update an existing asset.

```bash
kai context update <asset_id> \
  [--name "<new_name>"] \
  [--description "<new_description>"] \
  [--content-file <path>] \
  [--content <json_string>] \
  [--tags <comma_separated>]
```

**Behavior:**
- Updates only specified fields
- Preserves asset ID
- Increments `updated_at` timestamp
- Replaces tags entirely when `--tags` is provided

### context promote

Promote asset to next lifecycle state.

```bash
kai context promote <asset_id> <target_state> \
  --by <promoter_name> \
  [--note <change_note>]
```

**Parameters:**
- `asset_id`: Asset to promote
- `target_state`: Target state - verified or published
- `--by`: Name of person promoting (required)
- `--note`: Optional reason for promotion

**Promotion Rules:**
- draft → verified: Domain expert review
- verified → published: Final approval for reuse
- Cannot promote to deprecated (use `deprecate`)

**Examples:**
```bash
kai context promote asset_123 verified --by "Domain Expert"
kai context promote asset_123 published --by "Tech Lead" --note "Approved for production"
```

### context deprecate

Mark asset as deprecated.

```bash
kai context deprecate <asset_id> \
  --by <deprecator_name> \
  --reason <reason>
```

**Behavior:**
- Can be called from any state
- Marks asset as deprecated
- Should include replacement reference in reason

**Example:**
```bash
kai context deprecate asset_123 \
  --by "Tech Lead" \
  --reason "Superseded by financial_metrics_v2"
```

### context delete

Delete an asset.

```bash
kai context delete <db_connection_id> <asset_type> <canonical_key> \
  [--version <version>] \
  [--force]
```

**Parameters:**
- `db_connection_id`: Database connection
- `asset_type`: Type of asset
- `canonical_key`: Asset key
- `--version, -v`: Version to delete (default: latest)
- `--force`: Skip confirmation prompt

**Example:**
```bash
kai context delete mydb instruction sales_analysis
kai context delete mydb instruction sales_analysis --version 1.0.0 --force
```

### context search

Search assets by semantic query.

```bash
kai context search \
  --db <db_connection_id_or_alias> \
  --query <search_query> \
  [--limit <n>]
```

**Parameters:**
- `--db, -d`: Database connection (required)
- `--query, -q`: Search query (required)
- `--limit`: Maximum results (default: 10)

**Search Type:** Hybrid (semantic + keyword)

**Examples:**
```bash
kai context search --db mydb --query "sales analysis patterns"
kai context search --db mydb --query "financial metrics" --limit 20
```

### context tags

List all asset tags.

```bash
kai context tags [--category <category>]
```

**Output:**
- Tag name
- Category (optional)
- Usage count

---

## Lifecycle Management

### Lifecycle States

```
┌─────────┐     ┌──────────┐     ┌───────────┐     ┌────────────┐
│  draft   │────►│ verified  │────►│ published  │────►│ deprecated │
└─────────┘     └──────────┘     └───────────┘     └────────────┘
                  ▲                   │
                  │                   │
                  └───────────────────┘ (can return for revision)
```

| State | Description | Visibility | Typical Actions |
|-------|-------------|-------------|-----------------|
| **draft** | Initial creation, under development | Creator only | Edit, test, verify |
| **verified** | Reviewed by domain expert | Team | Use in missions, publish |
| **published** | Approved for broad reuse | All connections | Use as reference, copy |
| **deprecated** | Superseded or obsolete | All (marked) | Migrate away, delete |

### Promotion Workflow

**Recommended Process:**

1. **Create** as draft
2. **Test** with realistic queries
3. **Verify** with domain expert
4. **Publish** for team reuse
5. **Deprecate** when superseded

```bash
# 1. Create
ASSET_ID=$(kai context create ... --output json | jq -r '.id')

# 2. Test (manually or via benchmarks)
kai benchmark run validation_suite --db mydb

# 3. Verify
kai context promote $ASSET_ID verified --by "Domain Expert" --note "Reviewed and validated"

# 4. Publish
kai context promote $ASSET_ID published --by "Tech Lead" --note "Approved for production"
```

### Lifecycle Policy

The system enforces promotion rules:
- **draft → verified**: Requires domain expert review
- **verified → published**: Requires approval for reuse
- **Any state → deprecated**: Always allowed
- **No reverse promotion**: Must create new version for downgrades

---

## Search and Discovery

### Semantic Search

Find assets by meaning, not just keywords.

```bash
kai context search --db mydb --query "sales revenue"
```

**How it works:**
1. Analyzes query for semantic meaning
2. Searches asset content using embeddings
3. Falls back to keyword matching
4. Ranks by combined relevance score

**Search result columns:**
- Type: Asset type
- Key: Canonical key
- Name: Asset name
- Score: Relevance (0.0 - 1.0)

### Tag-Based Discovery

Browse assets by category.

```bash
# List all tags
kai context tags

# Filter by category
kai context tags --category domain
```

**Tag categories:**
- **domain**: Business domain (finance, sales, operations)
- **use_case**: Intended use (reporting, ad-hoc, automation)
- **status**: Maturity (experimental, stable, deprecated)

### Search Best Practices

1. **Be specific**: "gross margin calculation" not "math"
2. **Use domain language**: Terms your team uses
3. **Check existing before creating**: Avoid duplicates
4. **Refine with tags**: Combine search with tag filtering

---

## Benchmarking

Benchmarks validate asset quality by testing SQL generation against known-good queries.

### Benchmark Concepts

| Term | Definition |
|------|------------|
| **Suite** | Collection of test cases for validation |
| **Case** | Single test with query and expected SQL |
| **Run** | Execution of a suite against a database |
| **Severity** | Case importance (smoke, critical, regression) |

### benchmark run

Execute a benchmark suite.

```bash
kai benchmark run <suite_id> \
  --db <db_connection_id_or_alias> \
  [--tags <comma_separated>] \
  [--export <file_path>] \
  [--format <export_format>]
```

**Parameters:**
- `suite_id`: Suite to run
- `--db, -d`: Database connection (required)
- `--tags, -t`: Filter cases by tags
- `--export, -e`: Export results to file
- `--format`: Export format - json (default), junit

**Output:**
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

### benchmark list

List available benchmark suites.

```bash
kai benchmark list
```

### benchmark info

View suite details.

```bash
kai benchmark info <suite_id>
```

Shows:
- Suite name and description
- Total case count
- Case breakdown by severity

### benchmark results

View results from a specific run.

```bash
kai benchmark results <run_id>
```

### Using Benchmarks

**Before Promotion:**
```bash
# Run validation suite
kai benchmark run asset_validation --db mydb --tags smoke,critical

# Only promote if passing
if [ $? -eq 0 ]; then
  kai context promote $ASSET_ID verified --by "QA Lead"
fi
```

**Continuous Integration:**
```bash
# Export for CI systems
kai benchmark run suite_123 --db mydb \
  --export report.xml --format junit
```

---

## Telemetry and KPIs

The Context Platform automatically tracks asset usage.

### Tracked Metrics

| Metric | Description | Source |
|--------|-------------|--------|
| **reuse_count** | Total times asset used | All contexts |
| **last_reused_at** | Most recent usage | Timestamp |
| **reuse_by_type** | Breakdown by context | mission, benchmark, validation |

### Viewing KPIs

```bash
kai context show <asset_id>
```

Output includes telemetry metrics:
```
ID: glossary_abc123
Name: Financial Metrics
...

Telemetry:
  Reuse Count: 23
  Last Used: 2025-02-14T10:30:00
  Reuse by Type:
    mission: 18
    benchmark: 5
```

### Organization Metrics

**Top Reused Assets:**
Find most valuable knowledge assets by reuse count.

**High ROI Assets:**
Assets with reuse_count ≥ 5 are considered high ROI.

**Underutilized Assets:**
Identify assets that may need deprecation or promotion.

### Telemetry Events

Events are automatically tracked when:
- Asset is used in mission query
- Asset is used in benchmark execution
- Asset is validated
- Asset is created, updated, or promoted

---

## REST API

All Context Platform features are available via REST API.

### Base URL

```
http://localhost:8015/api
```

### Authentication

Include API key in header:
```
Authorization: Bearer <your_api_key>
```

### Endpoints

#### List Context Assets

```
GET /context/assets
```

**Query Parameters:**
- `db_connection_id`: Database connection (required)
- `asset_type`: Filter by type
- `lifecycle_state`: Filter by state
- `limit`: Max results (default: 50)

**Response:**
```json
{
  "assets": [
    {
      "id": "asset_123",
      "asset_type": "glossary",
      "canonical_key": "financial_metrics",
      "name": "Financial Metrics",
      "lifecycle_state": "published",
      "version": "1.2.0",
      "created_at": "2025-01-15T10:00:00",
      "updated_at": "2025-02-01T14:30:00"
    }
  ]
}
```

#### Get Context Asset

```
GET /context/assets/{asset_id}
```

**Response:** Full asset with content

#### Create Context Asset

```
POST /context/assets
```

**Request Body:**
```json
{
  "db_connection_id": "conn_123",
  "asset_type": "glossary",
  "canonical_key": "financial_metrics",
  "name": "Financial Metrics",
  "description": "Business metric definitions",
  "content": {
    "terms": [...]
  },
  "tags": ["finance", "metrics"],
  "author": "Jane Doe"
}
```

**Response:** Created asset with ID

#### Update Context Asset

```
PATCH /context/assets/{asset_id}
```

**Request Body:** Partial update of fields

**Response:** Updated asset

#### Promote Context Asset

```
POST /context/assets/{asset_id}/promote
```

**Request Body:**
```json
{
  "target_state": "verified",
  "promoted_by": "Jane Doe",
  "change_note": "Reviewed and validated"
}
```

**Response:** Updated asset with new state

#### Deprecate Context Asset

```
POST /context/assets/{asset_id}/deprecate
```

**Request Body:**
```json
{
  "deprecated_by": "Jane Doe",
  "reason": "Superseded by v2.0"
}
```

#### Search Context Assets

```
POST /context/assets/search
```

**Request Body:**
```json
{
  "db_connection_id": "conn_123",
  "query": "sales analysis",
  "limit": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "asset": {...},
      "score": 0.92,
      "match_type": "semantic"
    }
  ]
}
```

#### Delete Context Asset

```
DELETE /context/assets/{db_connection_id}/{asset_type}/{canonical_key}
```

**Query Parameters:**
- `version`: Version to delete (default: latest)

#### List Tags

```
GET /context/tags
```

**Query Parameters:**
- `category`: Filter by category

**Response:**
```json
{
  "tags": [
    {
      "name": "finance",
      "category": "domain",
      "usage_count": 15
    }
  ]
}
```

### Benchmark Endpoints

#### Run Benchmark

```
POST /benchmarks/{suite_id}/run
```

**Request Body:**
```json
{
  "db_connection_id": "conn_123",
  "tags": ["smoke", "critical"]
}
```

**Response:**
```json
{
  "run_id": "run_abc123",
  "status": "running",
  "suite_id": "suite_123"
}
```

#### Get Benchmark Results

```
GET /benchmarks/runs/{run_id}
```

**Response:** Full run results with case details

---

## Troubleshooting

### "No context assets found"

**Symptoms:** Empty list when running `kai context list`

**Solutions:**
1. Verify database connection: `kai connection list`
2. Check Typesense is running: `docker compose ps typesense`
3. Confirm filter parameters: Try without `--type` or `--state`
4. Check connection has assets: `kai context list --db <db>`

### "Asset not found"

**Symptoms:** Error when showing or updating asset

**Solutions:**
1. Verify asset ID from `kai context list`
2. For delete, use full format: `kai context delete <db> <type> <key>`
3. Check asset belongs to specified database

### "Promotion failed"

**Symptoms:** Error when promoting asset

**Solutions:**
1. Verify current state: `kai context show <asset_id>`
2. Check promotion order: draft → verified → published
3. Ensure `--by` parameter is provided
4. Verify you have permissions (multi-user setups)

### "Benchmark failed"

**Symptoms:** Benchmark execution errors

**Solutions:**
1. Verify database connection: `kai connection show <db>`
2. Check expected SQL syntax in test cases
3. Ensure test data exists in database
4. Review specific case failures: `kai benchmark results <run_id>`

### "Search returns no results"

**Symptoms:** Empty search results

**Solutions:**
1. Try broader query terms
2. Remove database filter to search all
3. Check assets exist: `kai context list --db <db>`
4. Try keyword search instead of semantic

---

## Appendix

### Versioning Strategy

**Semantic Versioning:**
- **Major (X.0.0)**: Breaking changes
- **Minor (0.X.0)**: Backward-compatible additions
- **Patch (0.0.X)**: Bug fixes

**When to Bump:**
- Major: Structure changes, incompatible updates
- Minor: New fields, extended functionality
- Patch: Corrections, clarifications

### Tag Conventions

**Category: domain**
- `finance`, `sales`, `operations`, `hr`

**Category: use_case**
- `reporting`, `ad-hoc`, `automation`, `validation`

**Category: status**
- `experimental`, `stable`, `deprecated`

**Example:**
```bash
--tags "finance,reporting,stable"
```

### Export Formats

**JSON:**
```bash
kai benchmark run suite_123 --db mydb --export results.json
```
Machine-readable, suitable for CI/CD integration.

**JUnit XML:**
```bash
kai benchmark run suite_123 --db mydb --export report.xml --format junit
```
Standard test report format for CI systems.

---

*For tutorial-style introduction, see [Context Platform Tutorial](./tutorials/context-platform-tutorial.md)*