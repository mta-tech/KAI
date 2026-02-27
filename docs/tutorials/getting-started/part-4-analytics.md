# Part 4: Advanced Analytics & Visualization

> **Time:** ~20 minutes
> **Prerequisites:** [Parts 1-3](index.md) completed
> **What you'll learn:**
> - Use analysis mode for statistical analysis and trend detection
> - Generate charts and visualizations from natural language
> - Inspect generated SQL with verbose mode
> - Run forecasting on time-series data

---

## Introduction

KAI is more than a SQL generator — it can perform statistical analysis, detect trends, and create visualizations. In this part, you'll use the `--mode analysis` flag to unlock these capabilities.

---

## Step 1: Run a Statistical Analysis

Ask KAI to analyze the cooperative data:

```bash
uv run kai query run \
  "Analyze the distribution of registered cooperatives across island groups" \
  --db $KAI_DB \
  --mode analysis
```

### Expected Output

```
🤖 KAI Agent (Analysis Mode)

Mission: Analyze the distribution of registered cooperatives across island groups

📋 Plan:
  ✓ Query cooperative counts by island group
  ✓ Calculate distribution statistics
  ✓ Identify outliers and patterns
  ✓ Generate summary

💡 Generated SQL:
  SELECT
    g.island_group,
    SUM(f."TotalKoperasiTerdaftar") as total_cooperatives,
    SUM(f."TotalAnggota") as total_members,
    SUM(f."TotalAset") as total_assets
  FROM fact_kpi f
  JOIN dim_geography g ON f.geography_id = g.id
  GROUP BY g.island_group
  ORDER BY total_cooperatives DESC

📊 Analysis:
  Distribution Summary:
  - Mean: 38.0 cooperatives per island group
  - Std Dev: 30.7
  - Range: 13 (Sulawesi) to 91 (Java)

  Key Findings:
  - Java dominates with 47.9% of all cooperatives (91 of 190)
  - Sumatra has the 2nd highest count with 51 cooperatives
  - Sulawesi has the lowest count with 13 cooperatives

✅ Analysis complete
```

> **Analytics Engineer Tip:** Analysis mode uses the agent's full tool suite — it doesn't just run SQL, it post-processes the results with statistical functions (mean, median, std dev, distribution analysis).

---

## Step 2: Generate a Chart

Ask KAI to visualize the data:

```bash
uv run kai query run \
  "Create a bar chart showing total cooperatives by island group" \
  --db $KAI_DB \
  --mode analysis \
  --no-stream \
  -o cooperative_analysis.md
```

The `-o` flag saves the agent's analysis output (text/markdown) to a file. Note: this writes the text response, not a rendered image — the agent may include ASCII charts or data tables in its output.

> **Note:** The `--no-stream` flag is required when using `-o`, as output file writing only works in non-streaming mode.

### Expected Output

```
🤖 KAI Agent (Analysis Mode)

Mission: Create a bar chart showing total cooperatives by island group

📋 Plan:
  ✓ Query data for visualization
  ✓ Generate bar chart
  ✓ Save to cooperative_chart.png

📊 Analysis output:

  Island Group Distribution:
  Java                ████████████████████ 91
  Sumatra             ███████████          51
  Kalimantan          ████                 19
  Bali-Nusa Tenggara  ███                  16
  Sulawesi            ███                  13

✅ Analysis saved to cooperative_chart.png
```

### Checkpoint

Verify the output was saved:

```bash
ls -la cooperative_analysis.md
```

You should see the markdown file. Open it with any text editor to review the analysis.

> **Business Analyst Tip:** You can request any chart type — bar charts, line charts, pie charts, scatter plots. Just describe what you want in plain English: "Create a pie chart of cooperative distribution by region."

---

## Step 3: Inspect SQL with Verbose Mode

See the full details of what KAI does behind the scenes:

```bash
uv run kai query run \
  "What is the average number of members per cooperative in each province?" \
  --db $KAI_DB \
  --stream
```

The `--stream` flag shows the agent's thinking process in real-time as it works through the problem.

### Expected Output

```
🤖 KAI Agent (Streaming)

🔍 Searching schema for relevant tables...
   Found: fact_kpi (cooperative KPIs), dim_geography (provinces)

📐 Planning query...
   Need: TotalAnggota / TotalKoperasiTerdaftar per province
   Join: fact_kpi → dim_geography on geography_id

✏️ Writing SQL...
   SELECT
     g.province_name,
     f."TotalAnggota" as total_members,
     f."TotalKoperasiTerdaftar" as total_cooperatives,
     ROUND(f."TotalAnggota"::numeric / NULLIF(f."TotalKoperasiTerdaftar", 0), 1)
       as avg_members_per_cooperative
   FROM fact_kpi f
   JOIN dim_geography g ON f.geography_id = g.id
   ORDER BY avg_members_per_cooperative DESC

⚡ Executing...
   15 rows returned in 12ms

📊 Result:
   [Results showing average members per cooperative by province]
```

> **Analytics Engineer Tip:** Streaming mode is invaluable for debugging. You can see exactly which tools the agent uses, what SQL it considers, and how it post-processes results. Use this when a query produces unexpected results.

---

## Step 4: Trend Analysis

Ask KAI to detect trends in the time-series data:

```bash
uv run kai query run \
  "Analyze the trend of cooperative registrations over time. Are they increasing or decreasing?" \
  --db $KAI_DB \
  --mode analysis
```

### Expected Output

```
🤖 KAI Agent (Analysis Mode)

Mission: Analyze the trend of cooperative registrations over time

📋 Plan:
  ✓ Query time-series data
  ✓ Calculate growth rates
  ✓ Detect trend direction
  ✓ Summarize findings

💡 Generated SQL:
  SELECT
    d.year, d.month, d.month_name,
    SUM(f."TotalKoperasiTerdaftar") as total_cooperatives,
    SUM(f."TotalAnggota") as total_members
  FROM fact_kpi f
  JOIN dim_date d ON f.date_id = d.id
  GROUP BY d.year, d.month, d.month_name
  ORDER BY d.year, d.month

📊 Trend Analysis:
  Time Period: 2024

  Key Metrics:
  - Data points: 13 observations
  - Overall direction: [based on data]
  - Growth rate: [calculated from data]

  Note: The sample dataset covers a limited time range.
  For production trend analysis, ensure your dataset spans
  multiple years.

✅ Analysis complete
```

---

## Step 5: Comparative Analysis

Compare metrics across dimensions:

```bash
uv run kai query run \
  "Compare total assets per cooperative between Java and Sumatra provinces" \
  --db $KAI_DB \
  --mode analysis
```

### Expected Output

```
🤖 KAI Agent (Analysis Mode)

Mission: Compare total assets per cooperative between Java and Sumatra

📊 Comparative Analysis:

  Java:
  - Provinces: 6
  - Total cooperatives: 91
  - Total assets: [value] IDR
  - Assets per cooperative: [value] IDR

  Sumatra:
  - Provinces: 4
  - Total cooperatives: 51
  - Total assets: [value] IDR
  - Assets per cooperative: [value] IDR

  Finding: [Comparative insight based on actual data]

✅ Analysis complete
```

> **Business Analyst Tip:** You can ask for any comparison — KAI understands "compare", "versus", "difference between" as signals to produce side-by-side analysis.

<details>
<summary>REST API equivalent</summary>

```bash
# Run analysis via API
curl -X POST http://localhost:8015/api/v1/analysis/comprehensive \
  -H "Content-Type: application/json" \
  -d '{
    "db_connection_id": "<connection-id>",
    "prompt": "Compare total assets between Java and Sumatra",
    "mode": "analysis"
  }'
```

</details>

---

## What Could Go Wrong?

### Problem: Output file not created

**Symptom:** Analysis completes but no output file is written

**Fix:** Ensure you specified both `--no-stream` and `-o` flags. Output file writing only works in non-streaming mode:

```bash
uv run kai query run "Create a chart..." --db $KAI_DB --no-stream -o output.md
```

### Problem: Analysis results seem wrong

**Symptom:** Statistical values don't match your expectations

**Fix:** First, inspect the generated SQL with `--stream` to verify the correct columns are being aggregated. Then check if glossary terms are mapping correctly:

```bash
uv run kai knowledge glossary list $KAI_DB -v
```

### Problem: Slow analysis execution

**Symptom:** Analysis takes more than 60 seconds

**Fix:** The default SQL execution timeout is 60 seconds. For large datasets, increase it in `.env.local`:

```
SQL_EXECUTION_TIMEOUT=120
```

---

## Summary

What you accomplished:
- Ran statistical analysis with distribution summaries and key findings
- Generated charts from natural language descriptions
- Used streaming mode to inspect the agent's reasoning process
- Performed trend analysis and comparative analysis across dimensions

## Next: Part 5

In [Part 5: Dashboards & Reports](part-5-dashboards.md), you'll create interactive dashboards from natural language and export them as HTML reports.
