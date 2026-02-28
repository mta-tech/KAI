# Part 6: Automation & Context Platform

> **Time:** ~20 minutes
> **Prerequisites:** [Parts 1-5](index.md) completed
> **What you'll learn:**
> - Sync context assets to files for version control and search
> - Manage context asset lifecycle (draft → verified → published)
> - Run benchmarks to measure query quality
> - Understand how KAI runs as a Temporal worker for production workflows

---

## Introduction

So far, you've worked interactively — adding knowledge, running queries, creating dashboards. In production, you need:

1. **Version control** — track changes to business rules, glossary, and instructions over time
2. **Quality assurance** — measure whether KAI's SQL generation is accurate
3. **Automation** — run KAI as a background worker that processes analysis requests

This part covers all three.

---

## Step 1: Sync Context to Files

KAI can materialize all context assets (glossary terms, instructions, table descriptions) as markdown files on disk. This makes them searchable, git-versionable, and readable.

```bash
uv run kai context sync -d kemenkop --output-dir ./context
```

The `--include-preview` flag is enabled by default, generating sample data previews for each table.

### Expected Output

```
Syncing context for kemenkop...

  Tables:
    ✓ context/kemenkop/tables/dim_geography/columns.md
    ✓ context/kemenkop/tables/dim_geography/preview.md
    ✓ context/kemenkop/tables/dim_date/columns.md
    ✓ context/kemenkop/tables/dim_date/preview.md
    ✓ context/kemenkop/tables/fact_kpi/columns.md
    ✓ context/kemenkop/tables/fact_kpi/preview.md

  Glossary:
    ✓ context/kemenkop/glossary/total-registered-cooperatives.md
    ✓ context/kemenkop/glossary/total-cooperative-members.md
    ✓ context/kemenkop/glossary/total-cooperative-assets.md

  Instructions:
    ✓ context/kemenkop/instructions/always-quote-mixed-case-columns.md
    ✓ context/kemenkop/instructions/province-grouping.md

Sync complete: 11 files written
```

### Checkpoint

Browse the generated files:

```bash
find ./context -name "*.md" | head -20
```

View a table's column documentation:

```bash
cat ./context/kemenkop/tables/fact_kpi/columns.md
```

You should see a markdown file with the table schema, column types, and AI-generated descriptions.

> **Analytics Engineer Tip:** Commit the `context/` directory to git. This creates a versioned history of your data model documentation — you can track when glossary terms changed, instructions were added, or table schemas evolved.

> **Business Analyst Tip:** The synced files are plain markdown — you can read them in any text editor or IDE. They serve as a data dictionary for your team.

---

## Step 2: Create Context Assets via the Platform

The Context Platform provides a lifecycle for managing context assets (beyond the glossary and instructions you created in Part 2):

```bash
# Create a context asset
uv run kai context create \
  -d kemenkop \
  --type glossary \
  --key "cooperative-density" \
  --name "Cooperative Density" \
  --description "Number of cooperatives per 1000 population in a province" \
  --content '{"text": "Calculate as: TotalKoperasiTerdaftar / (estimated_population / 1000). Population data not in current dataset."}' \
  --tags "analysis,density" \
  --author "tutorial-user"
```

### Expected Output

```
Context asset created!

  ID:      <asset-id>
  Type:    glossary
  Key:     cooperative-density
  State:   draft
  Version: 1
  Author:  tutorial-user
```

Notice the state is `draft` — all new assets start here.

---

## Step 3: Promote Context Assets Through Lifecycle

Assets move through a lifecycle: **draft → verified → published → deprecated**.

Promote the asset to `verified`:

```bash
uv run kai context promote <asset-id> verified \
  --by "tutorial-reviewer" \
  --note "Reviewed formula and description for accuracy"
```

### Expected Output

```
Asset promoted: draft → verified

  ID:      <asset-id>
  State:   verified
  Note:    Reviewed formula and description for accuracy
  By:      tutorial-reviewer
```

Promote to `published` (making it active for the agent):

```bash
uv run kai context promote <asset-id> published \
  --by "tutorial-reviewer" \
  --note "Approved for production use"
```

### Checkpoint

List all context assets:

```bash
uv run kai context list -d kemenkop --state published
```

You should see the `cooperative-density` asset in `published` state.

<details>
<summary>REST API equivalent</summary>

```bash
# Create asset
curl -X POST http://localhost:8015/api/v1/context-assets \
  -H "Content-Type: application/json" \
  -d '{
    "db_connection_id": "<connection-id>",
    "asset_type": "glossary",
    "canonical_key": "cooperative-density",
    "name": "Cooperative Density",
    "description": "Number of cooperatives per 1000 population",
    "content": {"text": "Calculate as: TotalKoperasiTerdaftar / (population / 1000)"},
    "content_text": "Calculate as: TotalKoperasiTerdaftar / (population / 1000)",
    "tags": ["analysis", "density"],
    "author": "tutorial-user"
  }'

# Promote asset
curl -X POST http://localhost:8015/api/v1/context-assets/<asset-id>/promote/verified \
  -H "Content-Type: application/json" \
  -d '{"promoted_by": "tutorial-reviewer", "change_note": "Approved"}'
```

</details>

---

## Step 4: Search Context Assets

Search across all context assets semantically:

```bash
uv run kai context search -d kemenkop -q "how to count cooperatives"
```

### Expected Output

```
Search results for "how to count cooperatives":

  1. total-registered-cooperatives (glossary, published)
     Score: 0.92
     SQL: SUM("TotalKoperasiTerdaftar") FROM fact_kpi

  2. cooperative-density (glossary, published)
     Score: 0.78
     Calculate as: TotalKoperasiTerdaftar / (population / 1000)

  3. always-quote-mixed-case-columns (instruction, published)
     Score: 0.45
     Always wrap mixed-case column names in double quotes
```

Browse available tags:

```bash
uv run kai context tags
```

> **Analytics Engineer Tip:** Context search is semantic — it understands meaning, not just keywords. "How to count cooperatives" matches "total registered cooperatives" even though the words don't overlap exactly.

---

## Step 5: Run Quality Benchmarks

Benchmarks measure how accurately KAI generates SQL for known questions. First, view available benchmark suites:

```bash
uv run kai benchmark list -d kemenkop
```

If no suites exist, create one through the API. For this tutorial, let's run a benchmark if one exists:

```bash
uv run kai benchmark run <suite-id> -d kemenkop
```

### Expected Output

```
Running benchmark suite: <suite-name>

  [1/5] "Total cooperatives"           ✓ PASS (SQL match, correct result)
  [2/5] "Cooperatives by province"     ✓ PASS (SQL match, correct result)
  [3/5] "Top 3 provinces by assets"    ✓ PASS (correct result, different SQL)
  [4/5] "Average members per coop"     ✓ PASS (correct result)
  [5/5] "Year-over-year growth"        ⚠ PARTIAL (correct approach, edge case)

Results: 4/5 passed, 1 partial
Score: 90%
```

View detailed results:

```bash
uv run kai benchmark results <run-id>
```

### Checkpoint

Check that the benchmark run completed:

```bash
uv run kai benchmark results <run-id> --failed-only
```

Review any failures to understand where KAI's SQL generation needs improvement.

> **Analytics Engineer Tip:** Benchmark suites are your regression tests for SQL generation. When you add new glossary terms or instructions, re-run benchmarks to verify the changes didn't break existing queries.

> **Business Analyst Tip:** Benchmark scores give you confidence in KAI's accuracy. A score of 90%+ means KAI reliably understands your domain.

<details>
<summary>REST API equivalent</summary>

```bash
# Run benchmark
curl -X POST http://localhost:8015/api/v1/benchmark/suites/<suite-id>/run \
  -H "Content-Type: application/json" \
  -d '{"db_connection_id": "<connection-id>"}'

# Get results
curl http://localhost:8015/api/v1/benchmark/runs/<run-id>/results
```

</details>

---

## Step 6: Temporal Workers (Conceptual Overview)

For production deployments, KAI can run as a **Temporal worker** — a background process that handles analysis requests from other systems.

```bash
# Start KAI as a Temporal worker
uv run kai config worker
```

In worker mode, KAI:
- Listens on a Temporal task queue for analysis requests
- Processes natural language queries autonomously
- Returns structured results to the calling workflow
- Supports multi-tenant deployments with per-organization task queues

This is how you integrate KAI into larger data pipelines — a scheduler triggers an analysis, KAI processes it, and the result flows to a dashboard or report.

> **Analytics Engineer Tip:** Temporal workers are ideal for scheduled reports, automated data quality checks, and pipeline-triggered analysis. See `docs/DEPLOYMENT.md` for production deployment patterns.

---

## What Could Go Wrong?

### Problem: Context sync produces empty files

**Symptom:** Files are created but contain no content

**Fix:** Ensure tables have been scanned with descriptions first (Part 1, Step 5). Context sync requires existing metadata:

```bash
uv run kai table scan-all $KAI_DB -d
```

Then retry the sync.

### Problem: Benchmark suite not found

**Symptom:** `Error: No benchmark suites found for this connection`

**Fix:** Benchmark suites must be created first. Use the REST API to create a suite with test cases:

```bash
curl -X POST http://localhost:8015/api/v1/benchmark/suites \
  -H "Content-Type: application/json" \
  -d '{
    "db_connection_id": "<connection-id>",
    "name": "Koperasi Basic Suite",
    "test_cases": [
      {"question": "Total cooperatives", "expected_sql": "SELECT SUM(\"TotalKoperasiTerdaftar\") FROM fact_kpi"}
    ]
  }'
```

### Problem: Context promote fails

**Symptom:** `Error: Invalid state transition`

**Fix:** Assets must follow the lifecycle order: `draft → verified → published`. You can't skip steps (e.g., promote directly from `draft` to `published`).

---

## Summary

What you accomplished:
- Synced context assets to markdown files for version control
- Created and promoted context assets through the draft → verified → published lifecycle
- Searched context semantically across all asset types
- Ran quality benchmarks to measure SQL generation accuracy
- Learned how KAI runs as a Temporal worker for production automation

---

## Congratulations!

You've completed the KAI Getting Started tutorial. Here's a recap of everything you've learned:

| Part | What You Built |
|------|---------------|
| 1 | Connected to a database and ran your first NL query |
| 2 | Added glossary terms, instructions, skills, and MDL |
| 3 | Had multi-turn conversations with session memory |
| 4 | Ran statistical analysis and generated charts |
| 5 | Created, refined, and rendered dashboards |
| 6 | Synced context, ran benchmarks, and learned about automation |

### Where to Go Next

- **API Reference**: See `docs/apis/` for all 86 REST API endpoints
- **Existing Tutorial**: `docs/tutorials/koperasi-analysis-tutorial.md` for a focused beginner walkthrough
- **Deployment**: `docs/DEPLOYMENT.md` for production setup with LangGraph and Temporal
- **Architecture**: `ARCHITECTURE.md` for system design and module structure
- **CLI Reference**: Run `uv run kai --help` for the complete command reference
