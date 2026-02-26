# Chapter 3: Feedback and Telemetry

> **Duration:** 15 minutes | **Difficulty:** Intermediate | **Format:** REST API

Learn to submit structured feedback on context assets, track reuse metrics, and measure the ROI of your knowledge management effort.

---

## What You'll Build

A closed-loop system that connects asset usage to quality improvement:

```
Analyst Uses Asset → Tracks Reuse Event → Submits Feedback
                                               ↓
                                     Review → Improve Asset
```

**After this chapter, you'll have:**
- Structured feedback linked to specific assets and benchmark cases
- Reuse metrics showing which assets deliver the most value
- Dashboard-ready KPI data for team visibility
- A foundation for continuous knowledge improvement

---

## Prerequisites

Before starting, ensure you've completed:

- [ ] [Chapter 1: Context Asset Lifecycle](1-context-assets.md) - Context assets created
- [ ] [Chapter 2: Quality Benchmarks](2-benchmarks.md) - Benchmark suites configured
- [ ] KAI server running (`uv run python -m app.main`)

---

## Part 1: Submit Feedback (5 minutes)

### Understanding Feedback Types

Feedback targets specific entities in the context platform:

| Target Type | Use Case |
|-------------|----------|
| `context_asset` | Feedback on an instruction, glossary, or skill |
| `benchmark_case` | Feedback on a test case definition |
| `mission_run` | Feedback on an autonomous mission output |

| Feedback Type | Meaning |
|---------------|---------|
| `correction` | The asset contains an error |
| `improvement` | The asset works but could be better |
| `confirmation` | The asset is correct and valuable |
| `other` | General feedback |

### Submit Feedback on an Asset

When an analyst notices an instruction produces incorrect SQL:

```bash
curl -X POST http://localhost:8015/api/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "feedback_type": "correction",
    "target_type": "context_asset",
    "target_id": "ctx_f7g8h9i0j1k2",
    "title": "Revenue calculation misses subscription discounts",
    "description": "The revenue calculation rule uses (amount - refund_amount) but does not account for subscription discounts stored in the discounts table. Should be (amount - COALESCE(refund_amount, 0) - COALESCE(discount_amount, 0)).",
    "severity": "high",
    "tags": ["revenue", "accuracy", "subscription"]
  }'
```

**Expected response:**
```json
{
  "id": "feedback_x1y2z3",
  "status": "pending",
  "message": "Feedback submitted successfully",
  "created_at": "2026-02-26T11:00:00Z"
}
```

### Submit Positive Feedback

When an asset works well, confirm it:

```bash
curl -X POST http://localhost:8015/api/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "feedback_type": "confirmation",
    "target_type": "context_asset",
    "target_id": "ctx_m3n4o5p6q7r8",
    "title": "MRR definition is accurate",
    "description": "Used in Q4 reporting - matches finance team calculations exactly.",
    "severity": "low",
    "tags": ["finance", "confirmed"]
  }'
```

### Validation Limits

The API enforces quality gates on feedback:
- **Title**: Maximum 200 characters
- **Description**: Maximum 5,000 characters

Exceeding these limits returns a `400 Bad Request`.

---

## Part 2: Manage Feedback (5 minutes)

### List All Feedback

```bash
curl "http://localhost:8015/api/v1/feedback"
```

### Filter by Target

View feedback for a specific asset:

```bash
curl "http://localhost:8015/api/v1/feedback?target_type=context_asset&target_id=ctx_f7g8h9i0j1k2"
```

### Filter by Status

```bash
curl "http://localhost:8015/api/v1/feedback?status=pending"
```

### View Feedback Details

```bash
curl "http://localhost:8015/api/v1/feedback/feedback_x1y2z3"
```

**Expected response:**
```json
{
  "id": "feedback_x1y2z3",
  "feedback_type": "correction",
  "target_type": "context_asset",
  "target_id": "ctx_f7g8h9i0j1k2",
  "title": "Revenue calculation misses subscription discounts",
  "description": "The revenue calculation rule uses...",
  "severity": "high",
  "status": "pending",
  "tags": ["revenue", "accuracy", "subscription"],
  "created_at": "2026-02-26T11:00:00Z"
}
```

### Update Feedback Status

As a lead reviews feedback, update its status:

```bash
curl -X PATCH "http://localhost:8015/api/v1/feedback/feedback_x1y2z3/status?status=reviewed&review_notes=Confirmed%20-%20updating%20asset"
```

**Status transitions:**
```
pending → reviewed → addressed
                  → dismissed
```

| Status | Meaning |
|--------|---------|
| `pending` | Newly submitted, awaiting review |
| `reviewed` | Lead has acknowledged and evaluated |
| `addressed` | Action taken — asset updated |
| `dismissed` | Not actionable or out of scope |

---

## Part 3: Track Reuse with Telemetry (5 minutes)

### How Telemetry Works

The `TelemetryService` automatically tracks three event types:

| Event | Trigger | What It Records |
|-------|---------|-----------------|
| `asset_reuse` | Asset used in a mission or benchmark | asset_id, reuse_type, context |
| `asset_creation` | New asset created | asset_id, asset_type, author |
| `asset_promotion` | Asset promoted to new state | asset_id, from_state, to_state |

### Telemetry API (Programmatic)

The telemetry service is used internally by KAI. For custom integrations, you can call it from Python:

```python
from app.modules.context_platform.services.telemetry_service import TelemetryService
from app.data.db.storage import Storage
from app.server.config import Settings

storage = Storage(Settings())
telemetry = TelemetryService(storage)

# Track an asset reuse event
event_id = telemetry.track_asset_reuse(
    asset_id="ctx_f7g8h9i0j1k2",
    asset_type="instruction",
    reuse_type="mission",
    context={"mission_id": "mission_abc123", "question": "What is our MRR?"},
    user_id="analyst@team.com",
)
print(f"Tracked reuse event: {event_id}")
```

### Get Reuse Count for an Asset

```python
count = telemetry.get_reuse_count(
    asset_id="ctx_f7g8h9i0j1k2",
    time_window_days=30,
)
print(f"Reused {count} times in last 30 days")
```

### Get Top Reused Assets

```python
metrics = telemetry.get_reuse_metrics(
    asset_type="instruction",
    time_window_days=30,
    limit=10,
)

for asset in metrics:
    print(f"  {asset['asset_id']}: {asset['reuse_count']} reuses ({asset['reuse_types']})")
```

**Example output:**
```
  ctx_f7g8h9i0j1k2: 47 reuses (['mission', 'benchmark'])
  ctx_a1b2c3d4e5f6: 23 reuses (['mission'])
  ctx_m3n4o5p6q7r8: 15 reuses (['mission', 'validation'])
```

### Get Asset KPIs

```python
kpi = telemetry.get_asset_kpi(
    asset_id="ctx_f7g8h9i0j1k2",
    time_window_days=30,
)

print(f"Asset KPI:")
print(f"  Total events:  {kpi['total_events']}")
print(f"  Reuse count:   {kpi['reuse_count']}")
print(f"  Promotions:    {kpi['promotion_count']}")
print(f"  Reuse by type: {kpi['reuse_by_type']}")
```

### Get Dashboard Metrics

```python
dashboard = telemetry.get_dashboard_metrics(time_window_days=30)

print(f"Dashboard (last 30 days):")
print(f"  Total events:       {dashboard['total_events']}")
print(f"  Unique assets:      {dashboard['total_unique_assets']}")
print(f"  Events by type:     {dashboard['events_by_type']}")
print(f"  Assets by type:     {dashboard['assets_by_type']}")
print(f"  Top reused assets:  {dashboard['top_reused_assets'][:3]}")
```

### Find High-ROI Assets

Identify assets that deliver the most value:

```python
high_roi = telemetry.get_reuse_roi(
    asset_type="instruction",
    min_reuse_count=5,
    time_window_days=30,
)

print(f"High-ROI instructions ({len(high_roi)} assets):")
for asset in high_roi:
    print(f"  {asset['asset_id']}: {asset['reuse_count']} reuses")
```

---

## What Could Go Wrong?

**1. Feedback rejected with "Title too long"**

- Symptom: `400 Title too long (max 200 characters)`
- Fix: Keep titles concise. Move details to the description field.

**2. Invalid feedback status transition**

- Symptom: `400 Invalid status`
- Fix: Use one of: `pending`, `reviewed`, `addressed`, `dismissed`

**3. Empty telemetry metrics**

- Symptom: All counts return 0
- Fix: Telemetry events are created when assets are used in missions. Run some queries first, or track events manually via the Python API.

---

## Summary

In this chapter, you learned:

- [x] **Feedback Types** - correction, improvement, confirmation, other
- [x] **Target Types** - context_asset, benchmark_case, mission_run
- [x] **Feedback Lifecycle** - pending → reviewed → addressed/dismissed
- [x] **Telemetry Events** - asset_reuse, asset_creation, asset_promotion
- [x] **Metrics** - Reuse counts, asset KPIs, dashboard aggregates, ROI analysis

**Key API Endpoints:**
```
POST   /api/v1/feedback                    # Submit feedback
GET    /api/v1/feedback                    # List feedback (with filters)
GET    /api/v1/feedback/{id}               # Get feedback details
PATCH  /api/v1/feedback/{id}/status        # Update status
```

**Key Telemetry Methods:**
```python
telemetry.track_asset_reuse(...)           # Record reuse event
telemetry.get_reuse_count(asset_id)        # Count for one asset
telemetry.get_reuse_metrics(asset_type)    # Top reused assets
telemetry.get_asset_kpi(asset_id)          # Full KPI for one asset
telemetry.get_dashboard_metrics()          # Aggregate dashboard data
telemetry.get_reuse_roi(min_reuse_count)   # High-value assets
```

---

## Path Complete

You've completed the Context Platform Path. Here's what you built:

| Chapter | What You Learned |
|---------|-----------------|
| **1. Context Assets** | Create, version, and promote domain knowledge |
| **2. Benchmarks** | Validate quality with automated test suites |
| **3. Feedback & Telemetry** | Close the loop with feedback and reuse tracking |

### Key KPIs to Track

| KPI | Target | How to Measure |
|-----|--------|----------------|
| **Benchmark pass rate** | >=90% | `kai benchmark results <run_id>` |
| **Asset reuse rate** | >=70% | `telemetry.get_reuse_metrics()` |
| **Feedback resolution time** | <48 hours | Filter feedback by status and timestamps |

---

## See Also

- [Context Platform API Reference](../../apis/context-platform-api.md) - All endpoints and schemas
- [Context Platform User Guide](../../user-guide/context-platform.md) - Complete feature reference
- [MDL Semantic Layer Tutorial](../mdl-semantic-layer.md) - Build semantic models
