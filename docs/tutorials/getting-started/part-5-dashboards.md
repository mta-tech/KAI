# Part 5: Dashboards & Reports

> **Time:** ~15 minutes
> **Prerequisites:** [Parts 1-4](index.md) completed
> **What you'll learn:**
> - Create dashboards from natural language descriptions
> - Execute dashboard widgets and view results
> - Render dashboards as HTML reports
> - Refine dashboards with natural language

---

## Introduction

Individual queries are useful, but stakeholders want dashboards — multiple views of the same data, organized on a single page. KAI generates entire dashboards from a plain-English description, including the layout, widget queries, and visualizations.

---

## Step 1: Create a Dashboard

Describe the dashboard you want:

```bash
uv run kai dashboard create \
  "Cooperative overview dashboard with: total cooperatives by island group, member distribution, asset comparison across provinces, and a trend line" \
  --db $KAI_DB \
  --name "Koperasi Overview" \
  --theme default
```

### Expected Output

```
Dashboard created successfully!

  ID:      <dashboard-id>
  Name:    Koperasi Overview
  Theme:   default
  Widgets: 4

  Widget Layout:
  ┌─────────────────────────┬─────────────────────────┐
  │ Total by Island Group   │ Member Distribution      │
  │ (bar chart)             │ (pie chart)              │
  ├─────────────────────────┼─────────────────────────┤
  │ Asset Comparison        │ Trend Line               │
  │ (horizontal bar)        │ (line chart)             │
  └─────────────────────────┴─────────────────────────┘
```

KAI designed 4 widgets, each with its own SQL query and chart type, arranged in a 2x2 grid.

### Checkpoint

Verify the dashboard exists:

```bash
uv run kai dashboard list --db $KAI_DB
```

You should see "Koperasi Overview" in the list.

> **Business Analyst Tip:** Just describe what you want to see on the dashboard. You don't need to specify chart types or SQL — KAI picks the best visualization for each metric.

> **Note:** Dashboard management is currently available via CLI only — there are no direct REST API endpoints for dashboards.

---

## Step 2: View Dashboard Details

Inspect the dashboard structure:

```bash
uv run kai dashboard show <dashboard-id>
```

### Expected Output

```
Dashboard: Koperasi Overview
Theme: default
Widgets: 4

  1. Total Cooperatives by Island Group
     Type: bar_chart
     SQL: SELECT g.island_group, SUM(f."TotalKoperasiTerdaftar")...

  2. Member Distribution
     Type: pie_chart
     SQL: SELECT g.island_group, SUM(f."TotalAnggota")...

  3. Asset Comparison by Province
     Type: horizontal_bar
     SQL: SELECT g.province_name, SUM(f."TotalAset")...

  4. Registration Trend
     Type: line_chart
     SQL: SELECT d.month_name, SUM(f."TotalKoperasiTerdaftar")...
```

> **Analytics Engineer Tip:** Review the generated SQL for each widget. If a query isn't optimal, you can refine it in Step 4 using natural language.

---

## Step 3: Execute Dashboard Queries

Run all widget queries and see the results:

```bash
uv run kai dashboard execute <dashboard-id>
```

### Expected Output

```
Executing dashboard: Koperasi Overview

  [1/4] Total by Island Group     ✓ (5 rows, 8ms)
  [2/4] Member Distribution       ✓ (5 rows, 6ms)
  [3/4] Asset Comparison          ✓ (15 rows, 11ms)
  [4/4] Registration Trend        ✓ (13 rows, 9ms)

All widgets executed successfully
```

Save the execution results:

```bash
uv run kai dashboard execute <dashboard-id> -s --output-format markdown
```

The `-s` flag saves results so they persist between executions.

---

## Step 4: Render as HTML

Generate a standalone HTML report:

```bash
uv run kai dashboard render <dashboard-id> \
  -f html \
  -o dashboard.html \
  --execute
```

The `--execute` flag runs all queries before rendering, ensuring fresh data.

### Expected Output

```
Executing widgets... ✓ (4/4)
Rendering HTML... ✓

Dashboard rendered to dashboard.html
  Size: 128 KB
  Widgets: 4
  Charts: 4
```

### Checkpoint

Open the HTML file:

```bash
open dashboard.html  # macOS
# or: xdg-open dashboard.html  # Linux
```

You should see a styled dashboard page with 4 interactive charts.

> **Business Analyst Tip:** Share the HTML file directly with stakeholders — it's self-contained with no dependencies. They can open it in any browser.

---

## Step 5: Refine the Dashboard

Modify the dashboard using natural language:

```bash
uv run kai dashboard refine <dashboard-id> \
  "Add a widget showing the top 5 provinces by total assets, and change the trend chart to show quarterly data instead of monthly"
```

### Expected Output

```
Dashboard refined!

Changes:
  + Added widget: Top 5 Provinces by Total Assets (bar_chart)
  ~ Modified widget: Registration Trend (grouped by quarter)

Widgets: 4 → 5
```

### Checkpoint

Verify the changes:

```bash
uv run kai dashboard show <dashboard-id>
```

You should see 5 widgets, including the new "Top 5 Provinces by Total Assets" widget.

Re-render the updated dashboard:

```bash
uv run kai dashboard render <dashboard-id> -f html -o dashboard_v2.html --execute
```

---

## Step 6: Export as JSON

Export the dashboard definition for version control or sharing:

```bash
uv run kai dashboard render <dashboard-id> -f json -o dashboard.json
```

### Expected Output

```
Dashboard exported to dashboard.json
```

The JSON export includes widget definitions, SQL queries, and layout configuration — useful for programmatic dashboard management.

> **Note:** Dashboard rendering is CLI-only. Use `kai dashboard render` for HTML/JSON export.

---

## What Could Go Wrong?

### Problem: Widget query fails

**Symptom:** One or more widgets show `Error: query execution failed`

**Fix:** The generated SQL may have issues. View the failed widget's SQL:

```bash
uv run kai dashboard show <dashboard-id>
```

Then refine the dashboard to fix the query:

```bash
uv run kai dashboard refine <dashboard-id> \
  "Fix the failing widget — use correct column names"
```

### Problem: HTML render is blank

**Symptom:** HTML file opens but charts are empty

**Fix:** Run `--execute` to populate data before rendering:

```bash
uv run kai dashboard render <dashboard-id> -f html -o dashboard.html --execute
```

### Problem: Theme not applied

**Symptom:** Dashboard renders without styling

**Fix:** Specify a theme during creation or update. Available themes: `default`, `light`, `dark`, `ocean`, `sunset`, `forest`.

---

## Summary

What you accomplished:
- Created a multi-widget dashboard from a natural language description
- Executed all widget queries and viewed results
- Rendered the dashboard as a standalone HTML report
- Refined the dashboard with natural language to add widgets and modify charts
- Exported the dashboard definition as JSON

## Next: Part 6

In [Part 6: Automation & Context Platform](part-6-automation.md), you'll learn how to sync context to files, run benchmarks for quality assurance, and set up feedback loops.
