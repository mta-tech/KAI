---
title: KAI Tutorial Documentation - Comprehensive Learning Path
type: docs
date: 2026-02-27
status: complete
---

# Brainstorm: KAI Tutorial Documentation

## What We're Building

A comprehensive, progressive tutorial for KAI (Knowledge Agent for Intelligence Query) that teaches analytics engineers and business analysts how to use all KAI capabilities — from first database connection to advanced analytics workflows.

**Format:** Signal-style learning path with 6 sequential parts, each building on the previous. Each part includes time estimates, checkpoint validations, expected output blocks, and "What Could Go Wrong?" troubleshooting sections.

**Primary interface:** CLI-first (`kai` commands), with REST API references as supplementary.

**Sample dataset:** Ships with a built-in sample database (e-commerce or similar) so users can follow along with exact, reproducible outputs.

## Why This Approach

### Signal-Style Learning Path chosen over alternatives:

1. **Narrative Walkthrough** (rejected) — Engaging but hard to use as reference; users can't skip ahead easily
2. **Quick-Start + Deep Dives** (rejected) — Fast time-to-value but loses progressive learning benefit; less cohesive

### Signal-style advantages:
- Proven writing pattern from Signal's getting-started docs
- Scannable — users can stop at any part and have a working setup
- Checkpoints prevent users from getting lost
- "What Could Go Wrong?" blocks reduce support burden
- Time estimates set expectations for both personas (analytics engineers move faster, business analysts appreciate knowing the commitment)

## Key Decisions

### 1. Tutorial Structure — 6 Progressive Parts

| Part | Title | Time | What Users Learn |
|------|-------|------|-----------------|
| 1 | Setup & First Query | ~15 min | Install KAI, connect sample DB, run first NL query |
| 2 | Building Knowledge | ~20 min | Add glossary terms, SQL instructions, reusable skills |
| 3 | Interactive Sessions & Memory | ~15 min | Multi-turn conversations, agent memory, context |
| 4 | Advanced Analytics & Visualization | ~20 min | Statistical analysis, forecasting, chart generation |
| 5 | Dashboards & Reports | ~15 min | NL dashboard creation, Excel/notebook export |
| 6 | Automation & Context Platform | ~20 min | Context sync, benchmarks, feedback loops, Temporal workers |

### 2. Target Audience — Dual Persona

- **Analytics Engineers**: Comfortable with SQL, care about accuracy, want to understand how KAI generates SQL and how to tune it via instructions/skills
- **Business Analysts**: Less SQL experience, care about asking questions in plain English, want dashboards and reports

Both personas follow the same path but Signal-style callout boxes highlight persona-specific tips (e.g., "Analytics Engineers: You can inspect the generated SQL with `--verbose`").

### 3. Sample Dataset

A built-in sample database that:
- Has enough complexity to demonstrate all features (multiple tables, joins, aggregations)
- Represents a domain both personas understand (e-commerce: orders, products, customers, regions)
- Can be loaded via a single CLI command (`kai sample load` or Docker compose)
- Includes pre-built glossary terms and instructions for the sample domain

### 4. Writing Style (Signal-Inspired)

- **Direct, practitioner voice** — "Run this command" not "You may want to consider running"
- **Checkpoint blocks** — After each major step, verify success with expected output
- **Expected output blocks** — Show exact terminal output users should see
- **"What Could Go Wrong?" sections** — Common errors with fixes
- **Time estimates per part** — Set expectations upfront
- **Progressive complexity** — Each part builds on the previous, no jumping ahead required

### 5. CLI-First with API Supplementary

Each operation shown as:
1. CLI command (primary)
2. Equivalent REST API call (in collapsible/aside block)
3. Python SDK snippet where applicable

### 6. Capabilities Coverage Map

All KAI capabilities to demonstrate across the 6 parts:

**Part 1 — Setup & First Query:**
- `kai config` — Environment configuration
- `kai connection create` — Database connection with encryption
- `kai table scan-all` — Schema scanning with AI descriptions
- `kai query run` — One-shot NL-to-SQL query

**Part 2 — Building Knowledge:**
- `kai knowledge glossary` — Business term definitions
- `kai knowledge instruction` — SQL generation rules
- `kai knowledge skill` — Reusable analysis patterns (markdown templates)
- `kai mdl generate` — MDL documentation generation

**Part 3 — Interactive Sessions & Memory:**
- `kai query interactive` — Multi-turn conversational mode
- `kai session` — Session management (list, resume, delete)
- `kai knowledge memory` — Long-term memory management
- Agent tools: memory_tools, context_store_tools

**Part 4 — Advanced Analytics & Visualization:**
- Statistical analysis (trend detection, forecasting, anomaly detection)
- Chart generation with theming
- Agent tools: analysis_tools, chart_tools, sql_tools
- `--verbose` flag for SQL inspection

**Part 5 — Dashboards & Reports:**
- `kai dashboard` — NL dashboard creation
- Excel export, notebook generation
- Agent tools: report_tools, excel_tools, notebook_tools

**Part 6 — Automation & Context Platform:**
- `kai context sync` — File-based context materialization
- `kai benchmark` — Quality benchmarking
- Context platform tools: search_context_files, read_context_file
- Temporal worker mode overview
- Feedback and telemetry

## Open Questions

_None — all key decisions resolved during brainstorming._

## Implementation Notes

### File Structure

```
docs/tutorials/getting-started/
  index.md              # Overview + prerequisites
  part-1-setup.md       # Setup & First Query
  part-2-knowledge.md   # Building Knowledge
  part-3-sessions.md    # Interactive Sessions & Memory
  part-4-analytics.md   # Advanced Analytics & Visualization
  part-5-dashboards.md  # Dashboards & Reports
  part-6-automation.md  # Automation & Context Platform
```

### Sample Dataset Requirements

- PostgreSQL-compatible (users can use local Docker or cloud)
- ~5-7 tables with realistic e-commerce data
- Pre-built seed script or SQL dump
- Matching glossary terms and instructions for the domain

### Per-Part Template

Each part follows this structure:

```markdown
# Part N: Title

> **Time:** ~XX minutes
> **Prerequisites:** Parts 1 through N-1 completed
> **What you'll learn:** [bullet list]

## Introduction
[Brief context for what this part covers and why it matters]

## Step 1: [Action]
[Instructions with CLI commands]

### Expected Output
```
[Exact terminal output]
```

### Checkpoint
[Verification command and expected result]

## Step 2: [Action]
...

## What Could Go Wrong?

### Problem: [Common error]
**Symptom:** [What the user sees]
**Fix:** [How to resolve]

## Summary
[What was accomplished, what's next]

## Next: Part N+1
[Teaser for next part]
```
