# Natural Language Queries

**KAI's core feature:** Transform natural language questions into SQL queries. No SQL knowledge required.

---

## Overview

KAI uses Large Language Models (LLMs) to understand your questions and generate optimized SQL queries. Simply describe what you want to know in plain English, and KAI handles the rest.

**How It Works:**
1. You type a question in natural language
2. KAI analyzes your database schema
3. KAI generates SQL query
4. KAI executes the query
5. Results are displayed in a clean table

---

## Getting Started

### Your First Query

1. Navigate to **Chat** (`Cmd/Ctrl + 1`)
2. Click **New Chat** or press `Cmd/Ctrl + N`
3. Type your question:
   ```
   What are the top 10 products by revenue?
   ```
4. Press **Enter**
5. KAI generates SQL and displays results

### View the Generated SQL

KAI shows you the SQL it generated:

1. Click the **SQL** tab above results
2. Review the query
3. Copy or modify as needed

**Why show SQL?**
- Learn SQL by example
- Verify correctness
- Customize complex queries
- Build reusable patterns

---

## Query Patterns

### Basic Queries

**Count records:**
```
How many users do we have?
What's the total number of orders?
Count all products in inventory
```

**Filter data:**
```
Show me users from the United States
Orders placed in the last 30 days
Products with price greater than $100
```

**Sort and limit:**
```
Top 10 customers by lifetime value
Bottom 5 performing products
First 100 orders sorted by date
```

### Aggregation Queries

**Sum and averages:**
```
Total revenue this month
Average order value
Sum of all refunds processed
```

**Grouping:**
```
Revenue by country
Sales by product category
Orders by day of week
```

**Multiple aggregations:**
```
Show me revenue, profit, and margin by product
Count of users and avg session duration by country
```

### Time-Based Queries

**Date ranges:**
```
Sales this week
Orders in Q1 2024
Activity from January to March
```

**Time periods:**
```
Daily revenue for the past 30 days
Monthly active users for the last year
Hourly traffic patterns
```

**Date comparisons:**
```
Revenue growth month over month
Year over year comparison
This week vs last week
```

### Join Queries

**Related tables:**
```
Show customer names with their orders
Product categories and their products
Users and their subscription plans
```

**Complex joins:**
```
Orders with customer details and product info
Users with their latest subscription status
Transactions with payment methods
```

### Subquery Queries

**Nested queries:**
```
Products with above-average prices
Users who made more than 5 purchases
Orders larger than the average order
```

### Conditional Queries

**Case statements:**
```
Categorize users by activity level
Group orders into size buckets
Classify revenue as high/medium/low
```

---

## Refinement & Iteration

KAI maintains context across messages. Refine your query through follow-up questions:

### Example Conversation

```
You: Show me sales by region
KAI: [Displays results: North, South, East, West]

You: Just for North America
KAI: [Filters to North America regions]

You: Group by state instead
KAI: [Groups results by state]

You: Add monthly breakdown
KAI: [Adds month column to grouping]

You: Sort by highest revenue first
Kai: [Sorts results descending by revenue]
```

**Context Retention:**
- Table names persist across messages
- Previous filters remembered
- Sort preferences carry over

### Common Refinements

**Narrow results:**
```
"Just for..."
"Only show..."
"Exclude..."
```

**Change grouping:**
```
"Group by..."
"Break down by..."
"Show per..."
```

**Add calculations:**
```
"Also include..."
"Add..."
"Calculate..."
```

**Change sort order:**
```
"Sort by..."
"Order by..."
"Put... first"
```

---

## Advanced Techniques

### Domain Knowledge

Teach KAI your business terminology:

1. Open **Knowledge Base** (`Cmd/Ctrl + 2`)
2. Navigate to **Glossaries**
3. Click **New Glossary Entry**
4. Add terms:
   - **Term:** "MRR"
   - **Definition:** "Monthly Recurring Revenue from subscriptions table"
5. Use in queries:
   ```
   Show MRR by plan type
   ```

### Skills (Reusable Patterns)

Create analysis patterns for complex queries:

1. Open **Knowledge Base**
2. Navigate to **Skills**
3. Click **New Skill**
4. Name your skill (e.g., "Cohort Analysis")
5. Define the pattern
6. Use anytime:
   ```
   Run cohort analysis on user signups
   ```

### SQL Hints

Guide KAI when needed:

```
Use the orders table
Join with customers
Include all columns
Limit to 1000 rows
Use INDEX hint on user_id
```

---

## Best Practices

### Be Specific

**Good:**
```
What's the average order value for customers in California
who placed orders in Q1 2024?
```

**Less Good:**
```
Show me orders
```

### Use Column Names

If you know your schema, reference columns:

```
SELECT price, quantity FROM order_items WHERE created_at > '2024-01-01'
```

KAI will incorporate your hints into the generated query.

### Iterate

Start simple, refine gradually:

1. ```
   Show me sales
   ```
2. ```
   Just for this month
   ```
3. ```
   Group by product
   ```
4. ```
   Add profit margin
   ```

### Check the SQL

Always review the generated SQL:

- **Verify filters** match your intent
- **Check joins** are correct
- **Ensure aggregations** are accurate
- **Confirm no data leakage** (unintended rows)

---

## Troubleshooting

### "No results found"

**Possible causes:**
- Filter too restrictive
- Table is empty
- Column name mismatch

**Solutions:**
- Widen your filters
- Check table has data
- Verify column names

### "Query took too long"

**Possible causes:**
- Querying too much data
- Missing indexes
- Complex joins

**Solutions:**
- Add date filters
- Limit result set
- Ask DBA about indexes

### "SQL syntax error"

**Possible causes:**
- KAI misunderstood your intent
- Complex query structure
- Database-specific syntax

**Solutions:**
- Rephrase your question
- Break into multiple queries
- Manually edit the SQL

---

## Examples by Use Case

### E-commerce Analytics

```
What are our best-selling products?
Which customers have the highest lifetime value?
Cart abandonment rate by traffic source
Products frequently bought together
```

### Product Analytics

```
Daily active users for the past 30 days
Retention rate by cohort
Feature usage patterns
User funnel conversion rates
```

### Financial Analysis

```
Revenue breakdown by product line
Profit margin by product
Accounts receivable aging
Cash flow trends
```

### Marketing Analytics

```
Campaign performance by channel
Lead conversion rate by source
Customer acquisition cost by campaign
Email engagement metrics
```

---

## Keyboard Shortcuts for Chat

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + N` | New chat |
| `Enter` | Send message |
| `Shift + Enter` | New line |
| `Cmd/Ctrl + ↑` | Previous message |
| `Cmd/Ctrl + ↓` | Next message |
| `Cmd/Ctrl + Shift + C` | Copy SQL |
| `Cmd/Ctrl + Shift + R` | Rerun query |
| `Cmd/Ctrl + Shift + E` | Export results |

---

## Next Steps

- Learn [Understanding Results](understanding-results.md)
- Explore [Exporting Data](exporting-data.md)
- Build [Knowledge Base Entries](../knowledge-base/creating-entries.md)

---

**Happy querying!** 🎯
