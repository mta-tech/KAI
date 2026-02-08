# Creating Knowledge Base Entries

**Build a reusable library of queries, domain knowledge, and analysis patterns.** The Knowledge Base is your team's shared intelligence.

---

## Overview

The Knowledge Base stores:
- **Queries**: Reusable SQL queries with descriptions
- **Glossaries**: Domain-specific terminology and definitions
- **Skills**: Pre-built analysis patterns and workflows
- **Memory**: Long-term context about your database and business

**Benefits:**
- Share knowledge across your team
- Standardize query patterns
- Onboard new team members faster
- Improve AI query accuracy with domain context

**Navigation:** Click **Knowledge Base** in sidebar or press `Cmd/Ctrl + 2`

---

## Creating Queries

### What are Queries?

Queries are reusable SQL statements stored with:
- Descriptive title
- Natural language explanation
- Parameter definitions
- Tags for organization

### Create a New Query

1. Navigate to **Knowledge Base** → **Queries**
2. Click **New Query** or press `n`
3. Fill in the form:
   - **Title**: "Monthly Recurring Revenue by Plan"
   - **Description**: "Calculates MRR broken down by subscription plan"
   - **SQL**: Enter your SQL query
   - **Parameters**: Define variables (e.g., `@start_date`, `@end_date`)
   - **Tags**: Add tags (e.g., "revenue", "subscription", "monthly")
4. Click **Save**

### Query Parameters

Define parameters to make queries reusable:

```sql
SELECT
    plan_type,
    SUM(amount) AS mrr
FROM subscriptions
WHERE created_at BETWEEN @start_date AND @end_date
    AND status = 'active'
GROUP BY plan_type
```

**Parameter Definitions:**
- `@start_date`: Start date for calculation
- `@end_date`: End date for calculation

When running the query, KAI prompts for parameter values.

### Using Saved Queries

1. Navigate to **Knowledge Base** → **Queries**
2. Browse or search for your query
3. Click to open
4. Review SQL and description
5. Enter parameter values (if any)
6. Click **Run Query**

### Sharing Queries

**With Your Team:**
1. Open query
2. Click **Share**
3. Copy link or invite team members
4. Recipients can view and run

**Public Link:**
- Anyone with link can view
- Useful for documentation
- No login required

---

## Creating Glossaries

### What are Glossaries?

Glossaries define domain-specific terminology:
- Business metrics (e.g., "MRR", "ARPU")
- Abbreviations (e.g., "LTV" = "Lifetime Value")
- Column explanations (e.g., "status_code meanings")

**Why Use Glossaries?**
- Teach KAI your business terminology
- Standardize definitions across team
- Improve query accuracy with context

### Create a Glossary Entry

1. Navigate to **Knowledge Base** → **Glossaries**
2. Click **New Glossary Entry**
3. Fill in the form:
   - **Term**: "MRR"
   - **Definition**: "Monthly Recurring Revenue - normalized revenue from subscription contracts"
   - **Formula**: "SUM of monthly subscription amounts for active subscribers"
   - **Related Tables**: "subscriptions", "plans"
   - **Example Query**: Reference to MRR calculation
4. Click **Save**

### Glossary Use Cases

**Business Metrics:**
```
Term: ARPU
Definition: Average Revenue Per User
Formula: Total Revenue / Active User Count
Context: Calculated monthly
```

**Status Codes:**
```
Term: Order Status
Definition: Current state of an order
Values:
  - pending: Order created, awaiting payment
  - processing: Payment received, preparing fulfillment
  - shipped: Order dispatched
  - delivered: Order received by customer
  - cancelled: Order cancelled
```

**Data Dictionary:**
```
Term: user_id
Definition: Unique identifier for users
Table: users, orders, subscriptions
Type: UUID
Notes: Foreign key to users.id in all user-related tables
```

---

## Creating Skills

### What are Skills?

Skills are reusable analysis patterns:
- Pre-built query templates
- Multi-step analysis workflows
- Common reporting patterns
- Domain-specific calculations

**Benefits:**
- Execute complex analyses with one command
- Standardize analytical approaches
- Share best practices across team

### Create a Skill

1. Navigate to **Knowledge Base** → **Skills**
2. Click **New Skill**
3. Fill in the form:
   - **Name**: "Cohort Analysis"
   - **Description**: "Analyze user retention by signup cohort"
   - **Steps**: Define the workflow
   - **Queries**: Add relevant SQL queries
   - **Parameters**: Define variables
4. Click **Save**

### Skill Example: Cohort Analysis

**Skill Name:** Cohort Retention Analysis

**Description:** Analyze user retention by signup cohort to understand user engagement over time.

**Steps:**
1. Select user signup date range
2. Calculate user activity by period
3. Group users by signup month (cohort)
4. Calculate retention rate for each period

**Queries:**
```sql
-- Step 1: Create cohorts
SELECT
    DATE_TRUNC('month', created_at) AS cohort_month,
    COUNT(*) AS user_count
FROM users
WHERE created_at BETWEEN @start_date AND @end_date
GROUP BY cohort_month;

-- Step 2: Calculate retention
SELECT
    c.cohort_month,
    DATE_TRUNC('month', a.created_at) AS activity_month,
    COUNT(DISTINCT a.user_id) AS active_users,
    c.user_count AS cohort_size,
    COUNT(DISTINCT a.user_id)::FLOAT / c.user_count AS retention_rate
FROM cohorts c
LEFT JOIN activity a ON a.user_id = c.user_id
GROUP BY c.cohort_month, DATE_TRUNC('month', a.created_at), c.user_count;
```

### Using Skills

1. Navigate to **Knowledge Base** → **Skills**
2. Find the skill you want to use
3. Click **Run Skill**
4. Enter parameter values
5. KAI executes the workflow
6. Review results

---

## Best Practices

### 1. Descriptive Titles

**Good:**
```
"Monthly Recurring Revenue by Plan Type"
"User Retention by Signup Cohort"
"Customer Lifetime Value Calculation"
```

**Less Good:**
```
"Revenue Query"
"Retention"
"CLV"
```

### 2. Clear Descriptions

Explain **what** the query does and **why** it's useful:

```
Calculates Monthly Recurring Revenue (MRR) broken down by subscription
plan type. Use this to track revenue distribution and identify which
plans drive the most revenue.

Parameters:
- start_date: First month to include
- end_date: Last month to include

Business Context: MRR is a key SaaS metric that shows predictable
revenue from active subscriptions.
```

### 3. Use Tags Effectively

Add relevant tags:
- **Domain**: "revenue", "users", "subscriptions"
- **Frequency**: "daily", "weekly", "monthly", "quarterly"
- **Purpose**: "reporting", "analysis", "dashboard"
- **Stakeholder**: "executive", "product", "engineering"

### 4. Document Parameters

For each parameter, specify:
- **Name**: Clear, descriptive name
- **Type**: Date, number, string, etc.
- **Required**: Whether value is mandatory
- **Default**: Default value (if any)
- **Description**: What the parameter controls

### 5. Test Queries

Before saving:
1. Run the query with sample parameters
2. Verify results are correct
3. Check for performance issues
4. Test edge cases

### 6. Version Control

For important queries:
1. Copy query before major changes
2. Add version to title (e.g., "MRR Query v2")
3. Keep notes on changes
4. Archive outdated versions

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `n` | New entry (query, glossary, skill) |
| `e` | Edit selected entry |
| `d` | Delete selected entry |
| `f` | Focus search |
| `r` | Run selected query |
| `s` | Save current changes |

### Navigation

| Shortcut | Action |
|----------|--------|
| `g` then `q` | Go to Queries |
| `g` then `l` | Go to Glossaries |
| `g` then `s` | Go to Skills |
| `g` then `m` | Go to Memory |

---

## Organizing Your Knowledge Base

### Folder Structure

Create folders to organize:

```
Queries/
├── Revenue/
│   ├── MRR by Plan
│   ├── ARPU Calculation
│   └── Revenue Forecasts
├── Users/
│   ├── User Signups
│   ├── Active Users
│   └── User Churn
└── Product/
    ├── Feature Usage
    └── Engagement Metrics
```

### Tagging Strategy

**Common Tags:**
- `finance`, `product`, `engineering`
- `daily`, `weekly`, `monthly`, `ad-hoc`
- `dashboard`, `report`, `analysis`
- `public`, `internal`, `confidential`

---

## Examples

### Example 1: E-commerce Metrics

**Query:** "Average Order Value (AOV)"

```sql
SELECT
    AVG(total_amount) AS average_order_value,
    COUNT(*) AS order_count,
    SUM(total_amount) AS total_revenue
FROM orders
WHERE created_at BETWEEN @start_date AND @end_date
    AND status NOT IN ('cancelled', 'refunded')
```

**Parameters:**
- `start_date`: Start date for analysis
- `end_date`: End date for analysis

**Description:** Calculates the average order value for completed orders in the specified date range. Use this to track spending patterns and evaluate pricing strategies.

### Example 2: Product Analytics

**Glossary Entry:** "DAU / MAU Ratio"

**Definition:** Daily Active Users divided by Monthly Active Users

**Formula:** `DAU / MAU`

**Context:** Also called "stickiness ratio". Measures how many monthly users use the product daily. Higher ratios indicate strong engagement.

**Benchmark:**
- Below 10%: Low engagement
- 10-25%: Moderate engagement
- Above 25%: High engagement

### Example 3: SaaS Metrics

**Skill:** "SaaS Revenue Waterfall"

**Description:** Step-by-step revenue analysis showing how revenue changes from start to end of period.

**Steps:**
1. Starting MRR
2. New Business MRR
3. Expansion MRR
4. Churned MRR
5. Ending MRR

**Query:** (Multi-step SQL for each waterfall component)

---

## Next Steps

- Learn [Managing Glossaries](managing-glossaries.md)
- Explore [Using Skills](using-skills.md)
- Return to [Getting Started](../getting-started.md)

---

**Build your team's shared intelligence!** 🧠
