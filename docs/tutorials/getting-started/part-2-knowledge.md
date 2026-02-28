# Part 2: Building Knowledge

> **Time:** ~20 minutes
> **Prerequisites:** [Part 1](part-1-setup.md) completed (database connected, tables scanned)
> **What you'll learn:**
> - Define business glossary terms so KAI speaks your domain language
> - Add SQL instructions to enforce query rules
> - Load reusable analysis skills from markdown files
> - Generate an MDL (Model Definition Language) semantic layer

---

## Introduction

In Part 1, KAI answered your question correctly — but it relied entirely on column names and AI-generated descriptions. In production, column names are often cryptic and business rules are non-obvious. This part teaches you how to give KAI domain knowledge so it generates better, more accurate SQL.

---

## Step 1: Add a Business Glossary Term

A glossary defines what business metrics mean in SQL. Tell KAI what "total registered cooperatives" means:

```bash
uv run kai knowledge glossary add $KAI_DB \
  -m "total registered cooperatives" \
  -s "SUM(\"TotalKoperasiTerdaftar\") FROM fact_kpi"
```

### Expected Output

```
Glossary entry created successfully!

  ID:     <generated-id>
  Metric: total registered cooperatives
  SQL:    SUM("TotalKoperasiTerdaftar") FROM fact_kpi
```

Add a few more terms:

```bash
# Total members
uv run kai knowledge glossary add $KAI_DB \
  -m "total cooperative members" \
  -s "SUM(\"TotalAnggota\") FROM fact_kpi"

# Total assets
uv run kai knowledge glossary add $KAI_DB \
  -m "total cooperative assets" \
  -s "SUM(\"TotalAset\") FROM fact_kpi"
```

### Checkpoint

List all glossary entries:

```bash
uv run kai knowledge glossary list $KAI_DB
```

You should see 3 entries for `total registered cooperatives`, `total cooperative members`, and `total cooperative assets`.

<details>
<summary>REST API equivalent</summary>

```bash
curl -X POST http://localhost:8015/api/v1/business_glossaries \
  -H "Content-Type: application/json" \
  -d '{
    "db_connection_id": "<connection-id>",
    "metric": "total registered cooperatives",
    "sql": "SUM(\"TotalKoperasiTerdaftar\") FROM fact_kpi"
  }'
```

</details>

> **Analytics Engineer Tip:** Glossary entries act as a semantic cache — when KAI sees "total registered cooperatives" in a question, it maps directly to the SQL expression you defined rather than guessing from column names.

---

## Step 2: Add SQL Instructions

Instructions are rules that guide how KAI generates SQL. Add a PostgreSQL-specific rule:

```bash
uv run kai knowledge instruction add $KAI_DB \
  --category "sql_rules" \
  --rule "Always quote mixed-case columns" \
  -i "In PostgreSQL, always wrap mixed-case column names in double quotes. For example: \"TotalKoperasiTerdaftar\", \"TotalAnggota\", \"TotalAset\". Lowercase-only columns like geography_id do not need quotes."
```

### Expected Output

```
Instruction created successfully!

  ID:       <generated-id>
  Category: sql_rules
  Rule:     Always quote mixed-case columns
```

Add another instruction for the koperasi domain:

```bash
uv run kai knowledge instruction add $KAI_DB \
  --category "domain" \
  --rule "Province grouping" \
  -i "When grouping by province, always join fact_kpi with dim_geography on geography_id = id and use province_name for display. Use island_group for regional grouping."
```

### Checkpoint

List instructions:

```bash
uv run kai knowledge instruction list $KAI_DB
```

You should see 2 instructions: `Always quote mixed-case columns` and `Province grouping`.

> **Business Analyst Tip:** Instructions are like guardrails — they prevent KAI from making common mistakes. You don't need to understand SQL to add them; your analytics engineer can define the rules.

---

## Step 3: Test the Improvement

Run the same query from Part 1, but now with glossary and instructions in place:

```bash
uv run kai query run \
  "What are the total registered cooperatives by island group?" \
  --db $KAI_DB
```

### Expected Output

```
🤖 KAI Agent

Mission: What are the total registered cooperatives by island group?

📋 Plan:
  ✓ Look up glossary for "registered cooperatives"
  ✓ Apply instruction: Province grouping
  ✓ Write and execute SQL query

💡 Generated SQL:
  SELECT
    g.island_group,
    SUM(f."TotalKoperasiTerdaftar") as total_registered
  FROM fact_kpi f
  JOIN dim_geography g ON f.geography_id = g.id
  GROUP BY g.island_group
  ORDER BY total_registered DESC

📊 Result:
  ┌─────────────────────┬──────────────────┐
  │ island_group        │ total_registered │
  ├─────────────────────┼──────────────────┤
  │ Java                │ 91               │
  │ Sumatra             │ 51               │
  │ Kalimantan          │ 19               │
  │ Bali-Nusa Tenggara  │ 16               │
  │ Sulawesi            │ 13               │
  └─────────────────────┴──────────────────┘
```

Notice how KAI:
1. Used the glossary to map "registered cooperatives" to `SUM("TotalKoperasiTerdaftar")`
2. Applied the province grouping instruction to join with `dim_geography`
3. Correctly quoted mixed-case column names

> **Analytics Engineer Tip:** Compare the SQL from Part 1 with this version. The glossary eliminated guesswork and the instructions enforced correct join patterns.

---

## Step 4: Create a Reusable Skill

Skills are markdown templates that define reusable analysis patterns. Create a skill file:

```bash
mkdir -p skills
cat > skills/koperasi-overview.md << 'EOF'
---
name: Koperasi Overview
description: Comprehensive overview of cooperative statistics by region
category: analysis
---

# Koperasi Overview Analysis

When asked for an overview of cooperatives or a regional summary:

1. Join `fact_kpi` with `dim_geography` on `geography_id = id`
2. Group by `island_group` and `province_name`
3. Calculate:
   - Total registered cooperatives: `SUM("TotalKoperasiTerdaftar")`
   - Total members: `SUM("TotalAnggota")`
   - Total assets: `SUM("TotalAset")`
4. Order by total cooperatives descending
5. Include both island-level and province-level breakdowns
EOF
```

Load the skill into KAI:

```bash
uv run kai knowledge skill discover $KAI_DB --path ./skills
```

### Expected Output

```
Discovering skills in ./skills...
  Found: koperasi-overview.md

Syncing to storage...
  ✓ koperasi-overview (analysis) — synced

1 skill discovered and synced
```

### Checkpoint

Verify the skill is loaded:

```bash
uv run kai knowledge skill list $KAI_DB
```

You should see `Koperasi Overview` in the skill list with category `analysis`.

---

## Step 5: Generate MDL Documentation

MDL (Model Definition Language) captures your entire data model — tables, relationships, and business context — in a single document:

```bash
uv run kai table scan-all $KAI_DB -d -m --mdl-name "Koperasi Data Model"
```

The `-m` flag generates an MDL manifest alongside the table scan.

### Expected Output

```
Refreshing tables from database... ✓
Found 3 tables in 1 schema(s)

Scanning tables...
  [1/3] public.dim_geography    ✓
  [2/3] public.dim_date         ✓
  [3/3] public.fact_kpi         ✓

Generating MDL manifest: Koperasi Data Model... ✓

Scan complete: 3 tables, MDL generated
```

View the generated MDL:

```bash
uv run kai mdl list $KAI_DB
```

### Checkpoint

```bash
uv run kai mdl show kemenkop --summary
```

The `mdl show` command accepts the connection alias, connection ID, or MDL manifest ID. You should see a summary of the data model including all 3 tables and their relationships.

> **Analytics Engineer Tip:** MDL documents are semantic layer definitions. They capture table relationships, column meanings, and business rules in a machine-readable format that KAI uses to generate more accurate SQL.

> **Business Analyst Tip:** Think of MDL as a "data dictionary" — it documents what every table and column means so KAI understands your data the same way your team does.

> **Note:** MDL management is currently available via CLI only — there are no REST API endpoints for MDL.

---

## What Could Go Wrong?

### Problem: Glossary entry not found during query

**Symptom:** KAI generates SQL without using the glossary term you defined

**Fix:** Check the glossary entry exists and the metric name matches what you used in the question:

```bash
uv run kai knowledge glossary list $KAI_DB -v
```

Glossary matching is semantic — "total registered cooperatives" will match "how many cooperatives are registered" — but very different phrasing may not match.

### Problem: Skills not syncing

**Symptom:** `skill discover` shows 0 skills found

**Fix:** Ensure the skill file has valid YAML frontmatter with `name`, `description`, and `category` fields. The `---` delimiters must be on their own lines.

### Problem: MDL generation fails

**Symptom:** Error during MDL generation step

**Fix:** MDL requires tables to be scanned first. Run `table scan-all $KAI_DB -d` before generating MDL.

---

## Summary

What you accomplished:
- Added 3 business glossary terms that map business language to SQL
- Created 2 SQL instructions that enforce query rules
- Loaded a reusable analysis skill from a markdown template
- Generated an MDL semantic layer document

Your KAI instance now has domain knowledge specific to the koperasi dataset. Queries will be more accurate and consistent.

## Next: Part 3

In [Part 3: Interactive Sessions & Memory](part-3-sessions.md), you'll have multi-turn conversations with KAI and teach it to remember facts across sessions.
