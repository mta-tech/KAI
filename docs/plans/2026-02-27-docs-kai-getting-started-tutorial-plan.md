---
title: "docs: KAI Getting Started Tutorial — Comprehensive Learning Path"
type: docs
status: completed
date: 2026-02-27
origin: docs/brainstorms/2026-02-27-kai-tutorial-documentation-brainstorm.md
---

# docs: KAI Getting Started Tutorial — Comprehensive Learning Path

## Overview

Create a 6-part progressive tutorial that teaches analytics engineers and business analysts how to use all KAI capabilities — from connecting a database to running autonomous analytics workflows. The tutorial follows Signal's getting-started writing style with time estimates, checkpoints, expected output blocks, and "What Could Go Wrong?" troubleshooting sections.

## Problem Statement / Motivation

KAI has 86+ CLI subcommands, 86 REST API routes, and 40+ agent tools, but the documentation is fragmented across API reference docs, scattered tutorials, and brainstorm documents. New users have no clear path from "I installed KAI" to "I'm running production analytics." The existing `koperasi-analysis-tutorial.md` covers only basic querying — it misses knowledge management, dashboards, sessions, memory, context platform, and benchmarks.

**Target audience:**
- **Analytics Engineers** — SQL-comfortable, want to understand SQL generation quality, tuning via instructions/skills
- **Business Analysts** — Less SQL experience, want plain-English queries, dashboards, and reports

## Proposed Solution

A Signal-style progressive learning path: 6 markdown files under `docs/tutorials/getting-started/`, each building on the previous. Reuses the existing `koperasi-sample-data/` dataset (PostgreSQL with cooperative KPI data).

**Key design decisions** (see brainstorm: docs/brainstorms/2026-02-27-kai-tutorial-documentation-brainstorm.md):
- Signal-style chosen over Narrative Walkthrough (too linear, poor reference) and Quick-Start + Deep Dives (loses progressive benefit)
- CLI-first (`uv run kai ...`) with REST API in collapsible `<details>` blocks
- Built-in sample dataset for reproducible outputs
- Dual-persona callout boxes for analytics engineers vs business analysts

## Technical Considerations

- **No code changes required** — this is pure documentation
- **Sample dataset already exists** at `docs/tutorials/koperasi-sample-data/` with DDL, CSVs, and README
- **MkDocs** is configured (`mkdocs.yml`) — new pages need to be registered in nav
- **Existing tutorial** `koperasi-analysis-tutorial.md` can be referenced but NOT replaced (it serves a different purpose as a focused beginner tutorial)
- **CLI commands verified** against actual source in `app/modules/autonomous_agent/cli/` — all commands documented here are real and tested

## Acceptance Criteria

### Content Requirements

- [x] 7 markdown files created under `docs/tutorials/getting-started/`
- [x] `index.md` — Overview with prerequisites, learning path map, time estimates
- [x] `part-1-setup.md` — Setup & First Query (~15 min)
- [x] `part-2-knowledge.md` — Building Knowledge (~20 min)
- [x] `part-3-sessions.md` — Interactive Sessions & Memory (~15 min)
- [x] `part-4-analytics.md` — Advanced Analytics & Visualization (~20 min)
- [x] `part-5-dashboards.md` — Dashboards & Reports (~15 min)
- [x] `part-6-automation.md` — Automation & Context Platform (~20 min)

### Per-Part Quality Requirements

- [x] Each part has: time estimate, prerequisites, learning outcomes
- [x] Each major step has: CLI command, expected output block, checkpoint validation
- [x] Each part has: "What Could Go Wrong?" section with 2-3 common errors + fixes
- [x] Each part has: Summary + teaser for next part
- [x] REST API equivalents shown in `<details>` blocks where applicable
- [x] Persona callout boxes for analytics engineer vs business analyst tips

### Coverage Requirements

- [x] All 10 CLI command groups demonstrated: config, connection, table, query, session, dashboard, knowledge (glossary, instruction, skill, memory), mdl, context, benchmark
- [x] Key agent capabilities shown: NL-to-SQL, statistical analysis, chart generation, forecasting
- [x] Knowledge management lifecycle: add glossary → add instructions → create skills → observe improvement
- [x] Context platform lifecycle: create assets → promote → search → sync to files
- [x] Dashboard workflow: create → execute → render → refine

### Technical Accuracy

- [x] All CLI commands use `uv run kai` prefix
- [x] All expected outputs match actual KAI output format
- [x] Sample data setup instructions are tested and reproducible
- [x] No references to deprecated commands or non-existent features

## Implementation Phases

### Phase 1: Foundation (index + Part 1 + Part 2)

**Files to create:**
- `docs/tutorials/getting-started/index.md`
- `docs/tutorials/getting-started/part-1-setup.md`
- `docs/tutorials/getting-started/part-2-knowledge.md`

**Part 1 — Setup & First Query** covers:
- Prerequisites (Python 3.11+, uv, Docker, API key)
- Starting Typesense via Docker
- `kai config show` — verify configuration
- `kai connection create` — connect to sample koperasi database
- `kai table scan-all -d` — scan tables with AI descriptions
- `kai query run "How many cooperatives are registered?" --db kemenkop` — first NL query
- Checkpoint: verify query returns correct result with generated SQL

**Part 2 — Building Knowledge** covers:
- `kai knowledge glossary add` — define "total cooperatives registered" metric
- `kai knowledge instruction add` — add PostgreSQL quoting rule
- `kai query run` — same query, show improved SQL quality
- `kai knowledge skill discover` — load reusable analysis patterns
- `kai mdl generate` — generate MDL documentation
- Checkpoint: re-run query and compare before/after SQL

### Phase 2: Interactive Features (Part 3 + Part 4)

**Files to create:**
- `docs/tutorials/getting-started/part-3-sessions.md`
- `docs/tutorials/getting-started/part-4-analytics.md`

**Part 3 — Interactive Sessions & Memory** covers:
- `kai query interactive --db kemenkop` — launch REPL
- Multi-turn conversation showing context retention
- `kai session list` — view sessions
- `kai session export` — export conversation
- `kai knowledge memory add` — store persistent facts
- Checkpoint: resume session, verify memory recall

**Part 4 — Advanced Analytics & Visualization** covers:
- `kai query run "Analyze cooperative growth trends" --db kemenkop --mode analysis`
- Statistical analysis output (trend detection, growth rates)
- Chart generation (line charts, bar charts)
- `--verbose` flag for SQL inspection (analytics engineer callout)
- Forecasting capabilities
- Checkpoint: verify chart file generated

### Phase 3: Output & Automation (Part 5 + Part 6)

**Files to create:**
- `docs/tutorials/getting-started/part-5-dashboards.md`
- `docs/tutorials/getting-started/part-6-automation.md`

**Part 5 — Dashboards & Reports** covers:
- `kai dashboard create "Cooperative overview dashboard" --db kemenkop`
- `kai dashboard execute` — run all widgets
- `kai dashboard render -f html -o dashboard.html` — generate HTML
- `kai dashboard refine` — modify via natural language
- Excel/notebook export capabilities
- Checkpoint: open rendered HTML dashboard

**Part 6 — Automation & Context Platform** covers:
- `kai context sync -d kemenkop` — materialize context files
- `kai context list` / `kai context search` — browse context assets
- `kai context promote` — lifecycle management
- `kai benchmark run` — quality benchmarking
- Temporal worker overview (conceptual, not hands-on)
- Checkpoint: verify context files created on disk

## Relevant Files

### Existing Files (Read/Reference)
- `docs/tutorials/koperasi-analysis-tutorial.md` — existing tutorial pattern to follow
- `docs/tutorials/koperasi-sample-data/` — sample dataset (DDL + CSVs)
- `app/modules/autonomous_agent/cli/` — all CLI command definitions
- `app/api/__init__.py` — REST API route registration
- `mkdocs.yml` — MkDocs nav configuration

### New Files to Create
- `docs/tutorials/getting-started/index.md`
- `docs/tutorials/getting-started/part-1-setup.md`
- `docs/tutorials/getting-started/part-2-knowledge.md`
- `docs/tutorials/getting-started/part-3-sessions.md`
- `docs/tutorials/getting-started/part-4-analytics.md`
- `docs/tutorials/getting-started/part-5-dashboards.md`
- `docs/tutorials/getting-started/part-6-automation.md`

## Per-Part Template

Each part follows this Signal-inspired structure:

```markdown
# Part N: Title

> **Time:** ~XX minutes
> **Prerequisites:** Parts 1 through N-1 completed
> **What you'll learn:**
> - Bullet 1
> - Bullet 2

## Introduction
Brief context — why this matters for your analytics workflow.

## Step 1: [Action]

Run:
```bash
uv run kai <command> [args]
```

### Expected Output
```
[Exact terminal output users should see]
```

### Checkpoint
Verify success:
```bash
uv run kai <verification-command>
```
You should see: [expected result].

> **Analytics Engineer Tip:** [SQL-focused insight]

> **Business Analyst Tip:** [Plain-language insight]

## Step 2: [Action]
...

<details>
<summary>REST API equivalent</summary>

```bash
curl -X POST http://localhost:8015/api/v1/... \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```
</details>

## What Could Go Wrong?

### Problem: [Common error]
**Symptom:** `[Error message]`
**Fix:** [Resolution steps]

### Problem: [Another error]
**Symptom:** `[Error message]`
**Fix:** [Resolution steps]

## Summary
What you accomplished:
- [Outcome 1]
- [Outcome 2]

## Next: Part N+1
[One-sentence teaser for what's coming next]
```

## Writing Style Guide

Follow these conventions consistently (see brainstorm: docs/brainstorms/2026-02-27-kai-tutorial-documentation-brainstorm.md):

1. **Direct, practitioner voice** — "Run this command" not "You may want to consider running"
2. **Show, don't explain** — lead with the command, follow with context
3. **Expected output blocks** — show exact terminal output after every command
4. **Checkpoints after every major step** — verification command + expected result
5. **"What Could Go Wrong?" sections** — 2-3 common errors per part with symptoms and fixes
6. **Time estimates** — at the top of every part
7. **Persona callouts** — boxquotes for analytics engineer vs business analyst tips
8. **CLI-first** — `uv run kai ...` commands primary, REST API in collapsible blocks
9. **Progressive** — each part explicitly states prerequisites (which prior parts)

## Dependencies & Risks

| Risk | Mitigation |
|------|------------|
| Sample dataset commands may produce different output across KAI versions | Pin expected outputs to current version (1.0.0) |
| Some CLI commands may require Typesense collections that don't exist yet | Part 1 includes prerequisite setup that creates all needed collections |
| Dashboard and analytics features may produce non-deterministic output | Use deterministic queries (counts, sums) for checkpoints; note that AI-generated analysis text may vary |
| Context platform and benchmark features are newest and may have bugs | Test all commands against the sample dataset before publishing |

## Success Metrics

| Metric | Target |
|--------|--------|
| All 10 CLI command groups covered | 100% |
| Parts with working checkpoints | 7/7 |
| "What Could Go Wrong?" entries per part | >= 2 |
| REST API equivalents shown | >= 1 per part |
| Persona callouts per part | >= 1 per part |

## Sources & References

### Origin
- **Brainstorm document:** [docs/brainstorms/2026-02-27-kai-tutorial-documentation-brainstorm.md](docs/brainstorms/2026-02-27-kai-tutorial-documentation-brainstorm.md) — Key decisions: Signal-style learning path, 6 progressive parts, CLI-first, built-in sample dataset, dual persona callouts

### Internal References
- Existing tutorial pattern: `docs/tutorials/koperasi-analysis-tutorial.md`
- Sample dataset: `docs/tutorials/koperasi-sample-data/`
- CLI source: `app/modules/autonomous_agent/cli/`
- API routes: `app/api/__init__.py`
- Signal docs inspiration: `~/project/mta/signal/docs/getting-started/`

### CLI Command Inventory (for reference during writing)

| Group | Subcommands | Key Commands |
|-------|-------------|--------------|
| `config` | show, check, version, worker | `config show`, `config check` |
| `connection` | create, list, show, update, delete, test | `connection create`, `connection list` |
| `table` | list, show, refresh, scan, scan-all, context, search | `table scan-all -d`, `table list` |
| `query` | run, interactive, resume, debug | `query run`, `query interactive` |
| `session` | list, show, export, delete, clear | `session list`, `session export` |
| `dashboard` | create, list, show, execute, render, delete, refine | `dashboard create`, `dashboard render` |
| `knowledge glossary` | add, list, show, update, delete | `glossary add` |
| `knowledge instruction` | add, list, show, update, delete | `instruction add` |
| `knowledge skill` | discover, list, show, search, reload, delete | `skill discover` |
| `knowledge memory` | list, show, search, add, delete, clear, namespaces | `memory add`, `memory search` |
| `mdl` | list, show | `mdl list`, `mdl show` |
| `context` | list, show, create, update, promote, deprecate, delete, search, tags, sync | `context sync`, `context search` |
| `benchmark` | run, list, info, results | `benchmark run` |
