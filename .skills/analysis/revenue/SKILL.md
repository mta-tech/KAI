---
name: Revenue Analysis
description: Use when analyzing revenue, sales, or financial performance. Provides standard approaches for calculating and comparing revenue metrics.
category: analysis
tags:
  - revenue
  - financial
  - sales
  - metrics
---

# Revenue Analysis Skill

This skill provides guidance for performing revenue and financial analysis.

## When to Use

Load this skill when the user asks about:
- Revenue trends or comparisons
- Sales performance analysis
- Financial metrics (ARR, MRR, etc.)
- Period-over-period comparisons
- Revenue breakdowns by segment

## Standard Metrics

### Gross Revenue
```sql
SELECT SUM(amount) as gross_revenue
FROM orders
WHERE status = 'completed'
  AND order_date BETWEEN :start_date AND :end_date
```

### Net Revenue (after refunds)
```sql
SELECT
  SUM(CASE WHEN type = 'order' THEN amount ELSE -amount END) as net_revenue
FROM transactions
WHERE transaction_date BETWEEN :start_date AND :end_date
```

### Period Comparison Template
```sql
WITH current_period AS (
  SELECT SUM(amount) as revenue
  FROM orders
  WHERE order_date BETWEEN :current_start AND :current_end
),
previous_period AS (
  SELECT SUM(amount) as revenue
  FROM orders
  WHERE order_date BETWEEN :previous_start AND :previous_end
)
SELECT
  c.revenue as current_revenue,
  p.revenue as previous_revenue,
  ROUND((c.revenue - p.revenue) / p.revenue * 100, 2) as growth_rate
FROM current_period c, previous_period p
```

## Analysis Workflow

1. **Clarify the time period** - Always confirm the date range
2. **Check for currency/region** - Ask if segmentation is needed
3. **Identify the revenue type** - Gross, net, recognized, etc.
4. **Consider filters** - Product line, customer segment, channel
5. **Calculate baseline** - Compute the main metric first
6. **Add comparisons** - Period-over-period, vs target, vs peers

## Best Practices

- Always exclude cancelled/refunded orders unless specifically asked
- Use consistent date boundaries (start of day to end of day)
- Round financial figures appropriately (2 decimal places for currency)
- Consider timezone implications for date filtering
- Group by business-relevant dimensions (not just technical IDs)

## Common Pitfalls

- Including pending/draft orders in completed revenue
- Double-counting from joined tables
- Missing NULL handling in aggregations
- Not accounting for currency conversion
