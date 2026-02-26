# Chapter 2: Quality Benchmarks

> **Duration:** 25 minutes | **Difficulty:** Intermediate | **Format:** CLI + REST API

Learn to validate your context assets with automated benchmark suites, track pass rates over time, and export results for CI pipelines.

---

## What You'll Build

A quality assurance pipeline for your analytics domain:

```
Define Cases → Create Suite → Run Benchmark → Review Results → Export
```

**After this chapter, you'll have:**
- Benchmark cases that test specific business questions
- Suites that group cases by domain or severity
- Automated pass/fail scoring with detailed results
- CI-friendly exports in JSON and JUnit XML

---

## Prerequisites

Before starting, ensure you've completed:

- [ ] [Chapter 1: Context Asset Lifecycle](1-context-assets.md) - Context assets created
- [ ] Typesense running (`docker compose up typesense -d`)
- [ ] KAI server running (`uv run python -m app.main`)

---

## Part 1: Understand Benchmark Architecture (3 minutes)

### The Benchmark Model

KAI's benchmark system has four components:

| Component | Purpose | Stored In |
|-----------|---------|-----------|
| **Case** | A single test question with expected behavior | `benchmark_cases` |
| **Suite** | A group of cases to run together | `benchmark_suites` |
| **Run** | One execution of a suite | `benchmark_runs` |
| **Result** | Pass/fail outcome for each case in a run | `benchmark_results` |

### Severity Levels

Each benchmark case has a severity that affects scoring:

| Severity | Weight | Meaning |
|----------|--------|---------|
| `critical` | 3x | Core business logic — must pass |
| `high` | 2x | Important accuracy — should pass |
| `medium` | 1x | Nice to have — acceptable to skip |
| `low` | 0.5x | Informational only |

---

## Part 2: Create Benchmark Suites via CLI (8 minutes)

### List Existing Suites

```bash
uv run kai benchmark list
```

If this is your first time, the list will be empty.

### Create a Suite via API

Create a benchmark suite for your e-commerce analytics domain:

```bash
curl -X POST http://localhost:8015/api/v1/benchmark/suites \
  -H "Content-Type: application/json" \
  -d 'name=Sales%20Analytics%20Suite&db_connection_id=ecommerce&description=Core%20sales%20queries&tags=sales&tags=critical'
```

Or with JSON body using query parameters:

```bash
curl -X POST "http://localhost:8015/api/v1/benchmark/suites?name=Sales+Analytics+Suite&db_connection_id=ecommerce"
```

**Expected response:**
```json
{
  "id": "suite_1740550000.123",
  "name": "Sales Analytics Suite",
  "created_at": "2026-02-26T10:00:00Z"
}
```

### View Suite Details

```bash
uv run kai benchmark info suite_1740550000.123
```

Or via API:

```bash
curl http://localhost:8015/api/v1/benchmark/suites/suite_1740550000.123
```

---

## Part 3: Run Benchmarks (8 minutes)

### Execute a Suite via CLI

Run all cases in a benchmark suite against your database:

```bash
uv run kai benchmark run suite_1740550000.123 --db ecommerce
```

**Expected output:**
```
Running benchmark suite: Sales Analytics Suite
  Database: ecommerce
  Cases: 5

  [1/5] Revenue trend QoQ .................. PASS (0.15s)
  [2/5] Top customers by spend ............. PASS (0.12s)
  [3/5] Monthly active users ............... FAIL (0.18s)
  [4/5] Average order value ................ PASS (0.09s)
  [5/5] Churn rate calculation ............. PASS (0.14s)

Results:
  Pass rate: 80% (4/5)
  Duration:  0.68s
  Run ID:    run_abc123def456
```

### Execute via API

```bash
curl -X POST "http://localhost:8015/api/v1/benchmark/suites/suite_1740550000.123/run?db_connection_id=ecommerce" \
  -H "Content-Type: application/json"
```

### Run with Tag Filters

Execute only a subset of cases by tag:

```bash
uv run kai benchmark run suite_1740550000.123 --db ecommerce --tags smoke,critical
```

### Run with Export

Generate a report file alongside the run:

```bash
uv run kai benchmark run suite_1740550000.123 --db ecommerce --export results.json
```

---

## Part 4: Review and Export Results (6 minutes)

### View Run Results

```bash
uv run kai benchmark results run_abc123def456
```

**Expected output:**
```
Benchmark Run: run_abc123def456
  Suite:     Sales Analytics Suite
  Status:    completed
  Pass Rate: 80% (4/5)

  Results:
  ✓ Revenue trend QoQ (critical)     0.15s
  ✓ Top customers by spend (high)    0.12s
  ✗ Monthly active users (medium)    0.18s
    Failure: Empty result set returned when data exists
  ✓ Average order value (medium)     0.09s
  ✓ Churn rate calculation (high)    0.14s
```

### View Only Failures

```bash
uv run kai benchmark results run_abc123def456 --failed-only
```

### List Historical Runs

Track pass rate trends across multiple runs:

```bash
# Via API
curl "http://localhost:8015/api/v1/benchmark/suites/suite_1740550000.123/runs?limit=10"
```

**Expected response:**
```json
[
  {
    "id": "run_abc123def456",
    "status": "completed",
    "pass_rate": 0.8,
    "total_cases": 5,
    "passed": 4,
    "failed": 1,
    "created_at": "2026-02-26T10:30:00Z"
  }
]
```

### Export for CI Systems

**JSON export** for dashboards and internal tools:

```bash
curl "http://localhost:8015/api/v1/benchmark/runs/run_abc123def456/export?format=json"
```

**JUnit XML export** for CI pipelines (GitHub Actions, Jenkins):

```bash
curl "http://localhost:8015/api/v1/benchmark/runs/run_abc123def456/export?format=junit"
```

**Expected JUnit XML:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
  <testsuite name="Sales Analytics Suite" tests="5" failures="1" time="0.68">
    <testcase name="Revenue trend QoQ" time="0.15"/>
    <testcase name="Top customers by spend" time="0.12"/>
    <testcase name="Monthly active users" time="0.18">
      <failure message="Empty result set returned when data exists"/>
    </testcase>
    <testcase name="Average order value" time="0.09"/>
    <testcase name="Churn rate calculation" time="0.14"/>
  </testsuite>
</testsuites>
```

This integrates directly with CI dashboards for automated quality gates.

---

## What Could Go Wrong?

**1. "Suite not found" error**

- Symptom: `404 Suite not found: suite_xxx`
- Fix: Use `kai benchmark list` to find valid suite IDs

**2. Empty benchmark results**

- Symptom: Run completes but shows 0 cases
- Fix: Ensure the suite has cases attached. Check with `kai benchmark info <suite_id>`

**3. Slow benchmark execution**

- Symptom: Individual cases take >5s
- Fix: Check database connection health with `kai connection test <alias>`

**4. Export format error**

- Symptom: `400 Invalid format`
- Fix: Use `format=json` or `format=junit` — no other formats are supported

---

## Summary

In this chapter, you learned:

- [x] **Benchmark Model** - Cases, suites, runs, and results
- [x] **Severity Levels** - critical, high, medium, low with weighted scoring
- [x] **CLI Commands** - list, info, run, results
- [x] **REST API** - Full suite CRUD, run execution, and result export
- [x] **CI Integration** - JSON + JUnit XML exports for automated pipelines

**Key Commands:**
```bash
kai benchmark list [--db <alias>]                    # List suites
kai benchmark info <suite_id>                        # Suite details
kai benchmark run <suite_id> --db <alias>            # Execute suite
kai benchmark results <run_id> [--failed-only]       # View results
```

**Key API Endpoints:**
```
POST   /api/v1/benchmark/suites                     # Create suite
GET    /api/v1/benchmark/suites                     # List suites
GET    /api/v1/benchmark/suites/{id}                # Get suite
POST   /api/v1/benchmark/suites/{id}/run            # Run suite
GET    /api/v1/benchmark/suites/{id}/runs           # List runs
GET    /api/v1/benchmark/runs/{id}                  # Get run
GET    /api/v1/benchmark/runs/{id}/results          # Get results
GET    /api/v1/benchmark/runs/{id}/export           # Export (JSON/JUnit)
```

---

## What's Next?

[Chapter 3: Feedback and Telemetry →](3-feedback-telemetry.md)

Close the loop between asset usage and quality improvement with structured feedback and reuse tracking.
