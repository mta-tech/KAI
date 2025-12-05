---
name: Data Quality Assessment
description: Use when checking data quality, finding anomalies, or validating data integrity. Provides patterns for identifying data issues.
category: analysis
tags:
  - data-quality
  - validation
  - anomalies
  - integrity
---

# Data Quality Assessment Skill

This skill provides guidance for assessing data quality and identifying data issues.

## When to Use

Load this skill when the user asks about:
- Data quality checks or validation
- Finding missing or NULL values
- Detecting duplicates
- Identifying anomalies or outliers
- Data completeness assessment
- Referential integrity checks

## Standard Quality Checks

### Completeness Check
```sql
SELECT
  COUNT(*) as total_rows,
  SUM(CASE WHEN column_name IS NULL THEN 1 ELSE 0 END) as null_count,
  ROUND(SUM(CASE WHEN column_name IS NULL THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) as null_percentage
FROM table_name
```

### Duplicate Detection
```sql
SELECT
  column1, column2,  -- key columns
  COUNT(*) as duplicate_count
FROM table_name
GROUP BY column1, column2
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC
```

### Orphan Records (Referential Integrity)
```sql
SELECT c.*
FROM child_table c
LEFT JOIN parent_table p ON c.parent_id = p.id
WHERE p.id IS NULL
```

### Outlier Detection (IQR Method)
```sql
WITH stats AS (
  SELECT
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY value) as q1,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY value) as q3
  FROM table_name
)
SELECT t.*
FROM table_name t, stats s
WHERE t.value < s.q1 - 1.5 * (s.q3 - s.q1)
   OR t.value > s.q3 + 1.5 * (s.q3 - s.q1)
```

### Date Validity Check
```sql
SELECT *
FROM table_name
WHERE date_column > CURRENT_DATE  -- future dates
   OR date_column < '1900-01-01'  -- unreasonably old
   OR date_column IS NULL
```

## Data Quality Dimensions

1. **Completeness** - Are all required values present?
2. **Accuracy** - Do values represent reality correctly?
3. **Consistency** - Is data consistent across sources/tables?
4. **Timeliness** - Is data up to date?
5. **Uniqueness** - Are there unwanted duplicates?
6. **Validity** - Do values follow expected formats/ranges?

## Workflow

1. **Profile the data** - Get basic statistics (count, nulls, unique values)
2. **Check primary keys** - Verify uniqueness constraints
3. **Validate foreign keys** - Check referential integrity
4. **Assess completeness** - Identify NULL/missing patterns
5. **Find outliers** - Statistical anomaly detection
6. **Report findings** - Summarize issues with severity levels

## Best Practices

- Always provide counts AND percentages for issues
- Categorize issues by severity (critical, warning, info)
- Sample problematic records for review
- Check data at different time granularities
- Compare expected vs actual row counts
- Document data quality rules/expectations
