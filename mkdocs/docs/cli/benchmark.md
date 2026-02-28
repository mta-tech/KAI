# Benchmark CLI

Run benchmarks to evaluate context asset quality and SQL generation performance.

## Commands

### Run Benchmark

```bash
kai benchmark run <suite_id> --db <connection_id> [--asset-ids <ids>]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--db` | Database connection ID (required) |
| `--asset-ids` | Comma-separated list of context asset IDs to test |

**Example:**

```bash
kai benchmark run suite_123 --db sales
```

### List Benchmark Suites

```bash
kai benchmark list [--db <connection_id>]
```

### Show Suite Details

```bash
kai benchmark info <suite_id>
```

### Show Benchmark Results

```bash
kai benchmark results <run_id> [--format <format>]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--format` | Output format: `table` (default), `json`, `junit` |

**Example:**

```bash
kai benchmark results run_456 --format json
```

## Scoring

Benchmarks use severity-weighted scoring:

| Severity | Weight | Description |
|----------|--------|-------------|
| LOW | 0.5x | Basic functionality |
| MEDIUM | 1.0x | Standard importance |
| HIGH | 1.5x | Critical path |
| CRITICAL | 2.0x | Must pass |

## Example Output

```
Benchmark Run: run_456
Suite: Sales Analytics Suite
Status: completed
Score: 87.5/100

Cases:
  ✅ case_001: Total revenue query (HIGH) - 0.95
  ✅ case_002: Monthly breakdown (MEDIUM) - 1.00
  ❌ case_003: YoY comparison (CRITICAL) - 0.60

Summary:
  Passed: 2/3 (66.7%)
  Weighted Score: 87.5%
  Execution Time: 2.3s
```
