# Context Platform Path

**Duration:** ~60 minutes | **Format:** CLI & REST API | **Prerequisites:** KAI installed, Typesense running

Build a production-grade knowledge management system for your analytics workflows, from domain assets to quality benchmarks and feedback loops.

---

## What You'll Learn

The Context Platform path teaches you to manage domain knowledge as first-class assets in KAI. You'll learn to:

1. **Manage Context Assets** - Create, version, and promote domain knowledge through lifecycle states
2. **Run Quality Benchmarks** - Validate asset quality with test suites and track pass rates
3. **Close the Feedback Loop** - Submit feedback, track reuse metrics, and improve asset quality over time

---

## Prerequisites

Before starting this path, ensure you have:

- **KAI installed** with `uv sync` completed
- **Typesense running** via `docker compose up typesense -d`
- **A database connection** created (`kai connection create`)
- Basic familiarity with KAI CLI commands

---

## Chapters

### Chapter 1: Context Asset Lifecycle (~20 minutes)

Learn to create and manage domain knowledge as versioned assets:

```
Create (Draft) → Verify → Publish → Reuse
                              ↓
                          Deprecate
```

**You'll build:**
- Context assets for table descriptions, glossaries, instructions, and skills
- Lifecycle transitions from draft through published
- Version history and audit trail
- Search and discovery across your knowledge base

**[Start Chapter 1 →](1-context-assets.md)**

---

### Chapter 2: Quality Benchmarks (~25 minutes)

Validate your context assets with automated test suites:

```
Define Cases → Create Suite → Run Benchmark → Review Results
                                    ↓
                              Export (JSON/JUnit)
```

**You'll build:**
- Benchmark suites with tagged test cases
- Automated quality scoring with pass/fail results
- CI-friendly exports in JSON and JUnit XML formats
- Historical run comparison for drift detection

**[Start Chapter 2 →](2-benchmarks.md)**

---

### Chapter 3: Feedback and Telemetry (~15 minutes)

Close the loop between asset usage and quality improvement:

```
Use Asset → Submit Feedback → Review → Improve Asset
                ↓
          Track Reuse Metrics
```

**You'll learn:**
- Submitting structured feedback on assets and benchmark cases
- Tracking asset reuse across missions
- Measuring ROI on knowledge management effort
- Dashboard metrics for team-wide visibility

**[Start Chapter 3 →](3-feedback-telemetry.md)**

---

## What You'll Build

By the end of this path, you'll have a complete knowledge management system:

| Component | Surface | Purpose |
|-----------|---------|---------|
| **Context Assets** | CLI + API | Versioned domain knowledge |
| **Lifecycle Governance** | CLI + API | Draft → Verified → Published |
| **Benchmark Suites** | CLI + API | Automated quality validation |
| **Feedback System** | API | Structured quality improvement |
| **Telemetry** | API | Reuse tracking and ROI metrics |

---

## Key Commands You'll Learn

```bash
# Context assets
kai context create --db mydb --type instruction --key my_key --name "My Rule"
kai context list --db mydb --state published
kai context promote asset_id verified --by "analyst@team.com"
kai context search --db mydb --query "revenue calculation"

# Benchmarks
kai benchmark list --db mydb
kai benchmark run suite_id --db mydb --tags smoke,critical
kai benchmark results run_id --failed-only

# API endpoints
curl -X POST localhost:8015/api/v1/context-assets
curl -X POST localhost:8015/api/v1/benchmark/suites/{id}/run
curl -X POST localhost:8015/api/v1/feedback
```

---

## Resources

### Reference
- [Context Platform API Reference](../../apis/context-platform-api.md) - All endpoints and schemas
- [Context Platform User Guide](../../user-guide/context-platform.md) - Complete feature reference
- [CLI Reference](../../README.md) - All KAI CLI commands

### Related
- [MDL Semantic Layer Tutorial](../mdl-semantic-layer.md) - Build semantic models
- [Koperasi Analysis Tutorial](../koperasi-analysis-tutorial.md) - End-to-end analysis workflow

---

## Getting Help

If you get stuck:
1. Run `kai context --help` or `kai benchmark --help` for command-specific help
2. Check the [Context Platform API docs](../../apis/context-platform-api.md)
3. Review the [Troubleshooting Guide](../../TROUBLESHOOTING.md)
