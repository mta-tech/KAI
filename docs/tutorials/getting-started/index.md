# Getting Started with KAI

A progressive tutorial that takes you from zero to running autonomous analytics workflows. Each part builds on the previous — follow them in order.

> **Total time:** ~105 minutes across 6 parts
> **Audience:** Analytics engineers and business analysts
> **Sample data:** Indonesian cooperative (koperasi) statistics — included

---

## Prerequisites

Before starting, you need:

- **Python 3.11+** installed
- **[uv](https://docs.astral.sh/uv/)** package manager
- **Docker** running (for Typesense and PostgreSQL)
- **Google API Key** (for Gemini) or **OpenAI API Key**

```bash
# Clone the repository
git clone https://github.com/mta-tech/KAI.git && cd KAI

# Install dependencies
uv sync
```

---

## Learning Path

| Part | Title | Time | What You'll Learn |
|------|-------|------|-------------------|
| 1 | [Setup & First Query](part-1-setup.md) | ~15 min | Connect a database, scan tables, run your first NL query |
| 2 | [Building Knowledge](part-2-knowledge.md) | ~20 min | Add glossary terms, SQL instructions, and reusable skills |
| 3 | [Interactive Sessions & Memory](part-3-sessions.md) | ~15 min | Multi-turn conversations, session management, persistent memory |
| 4 | [Advanced Analytics & Visualization](part-4-analytics.md) | ~20 min | Statistical analysis, trend detection, chart generation |
| 5 | [Dashboards & Reports](part-5-dashboards.md) | ~15 min | Create dashboards from natural language, export to HTML |
| 6 | [Automation & Context Platform](part-6-automation.md) | ~20 min | Context sync, benchmarks, feedback loops |

---

## How This Tutorial Works

Each part follows the same structure:

- **Time estimate** — how long this part takes
- **Prerequisites** — which prior parts you need
- **Step-by-step instructions** — CLI commands with expected output
- **Checkpoints** — verify your setup is correct before continuing
- **What Could Go Wrong?** — common errors and fixes

> **Analytics Engineer Tip:** Look for these callouts — they highlight SQL-level details, query optimization, and tuning opportunities.

> **Business Analyst Tip:** Look for these callouts — they explain concepts without requiring SQL knowledge and show how to get answers in plain English.

---

## Sample Dataset

This tutorial uses a pre-built PostgreSQL database with Indonesian cooperative statistics:

- **3 tables**: `dim_geography` (15 provinces), `dim_date` (13 dates), `fact_kpi` (15 KPI records)
- **Domain**: Cooperative registrations, member counts, and total assets across provinces
- **Setup**: Part 1 walks you through loading this data

All data files are in `docs/tutorials/koperasi-sample-data/`.

---

## Start Here

Ready? Begin with [Part 1: Setup & First Query](part-1-setup.md).
