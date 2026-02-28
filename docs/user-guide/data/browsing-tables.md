# Browsing Tables & Schema

**Explore your database without writing SQL.** KAI's Data Explorer provides a visual interface for understanding your database structure.

---

## Overview

The Data Explorer lets you:
- Browse all tables in your database
- View column names, types, and relationships
- Read AI-generated descriptions
- Preview sample data
- Scan tables with AI for automated documentation

**Navigation:** Click **Data** in sidebar or press `Cmd/Ctrl + 3`

---

## Tables List

### Viewing All Tables

1. Navigate to **Data** → **Tables**
2. See all tables in your connected database
3. Each table shows:
   - Table name
   - Row count (when available)
   - AI description (if scanned)

### Table List Actions

| Action | Shortcut | Description |
|--------|----------|-------------|
| Open Table | `Enter` | View table details and columns |
| Select Table | `Space` | Select for batch operations |
| Scan Table | `a` | Initiate AI table scan |
| Preview Data | `p` | Show first 100 rows |
| Filter | `f` | Filter table list |

---

## Table Details

### Opening a Table

1. Click on any table name
2. View detailed information:
   - **Columns**: All column names and types
   - **Indexes**: Indexes on the table
   - **Foreign Keys**: Relationships to other tables
   - **Sample Data**: First 10 rows
   - **AI Description**: Natural language summary

### Column Information

Each column shows:
- **Name**: Column name
- **Type**: Data type (varchar, int, timestamp, etc.)
- **Nullable**: Whether column allows NULL values
- **Default**: Default value (if any)
- **Description**: AI-generated explanation

### Understanding Relationships

KAI automatically detects and displays:

**Foreign Keys:**
```
orders.customer_id → customers.id
This represents a many-to-one relationship:
Many orders can belong to one customer
```

**Use Cases:**
- Understand joins before querying
- Discover related tables
- Plan multi-table queries

---

## AI Table Scanning

### What is Table Scanning?

KAI can analyze your table schema and sample data to generate:
- Natural language table descriptions
- Column-by-column explanations
- Business context insights
- Relationship detection

### Running a Scan

1. Navigate to **Data** → **Tables**
2. Select a table
3. Click **Scan** or press `a`
4. KAI analyzes:
   - Column names and types
   - Sample data patterns
   - Relationships
5. Results saved to table metadata

### Scan Benefits

**Better Queries:**
- KAI understands your schema better
- More accurate SQL generation
- Smarter query suggestions

**Team Knowledge:**
- Document your database automatically
- Onboard new team members faster
- Share domain knowledge

**Discovery:**
- Find relevant tables quickly
- Understand unfamiliar schemas
- Discover relationships you missed

---

## Schema View

### Visual Schema Browser

1. Navigate to **Data** → **Schema**
2. See visual representation of your database
3. Shows:
   - All tables as boxes
   - Relationships as lines
   - Table sizes (row counts)

### Schema Actions

| Action | Description |
|--------|-------------|
| Zoom In/Out | `+` / `-` keys or mouse wheel |
| Pan | Arrow keys or drag |
| Focus Table | Click table name to center |
| Export Schema | Save as PNG or SVG |

---

## Sample Data Preview

### Viewing Sample Data

1. Open any table
2. Click **Preview** tab
3. See first 100 rows
4. Columns are sortable

### Sample Data Uses

- **Understand Data Format:** See actual values, not just types
- **Verify Queries:** Check if expected data exists
- **Data Quality:** Spot issues or patterns
- **Test Queries:** Try queries against real data

---

## Keyboard Shortcuts

### Data Navigation

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + 3` | Go to Data section |
| `t` | Go to Tables |
| `s` | Go to Schema |
| `c` | Go to Columns |
| `p` | Preview Data |

### Table List

| Shortcut | Action |
|----------|--------|
| `j` / `k` | Navigate up/down |
| `Enter` | Open table |
| `a` | Scan table |
| `Space` | Select table |
| `f` | Focus filter |

---

## Best Practices

### 1. Scan Your Tables

After connecting a database:
1. Navigate to Data → Tables
2. Scan important tables first
3. Build comprehensive schema understanding

**Why:** Better queries, faster onboarding

### 2. Use AI Descriptions

Read AI-generated descriptions to:
- Learn what each table contains
- Understand business context
- Discover relationships

**Why:** Avoid confusion, query the right tables

### 3. Explore Relationships

Check foreign keys and joins to:
- Plan multi-table queries
- Understand data flow
- Discover related data

**Why:** Build more complex, useful queries

### 4. Preview Data

Always preview before querying to:
- Verify data exists
- Check data quality
- Understand value formats

**Why:** Avoid surprises in query results

---

## Troubleshooting

### "No tables found"

**Cause:** No database connected or connection failed

**Solution:**
1. Check Settings → Connections
2. Test connection
3. Verify database has tables

### "Scan failed"

**Cause:** Insufficient permissions or LLM error

**Solution:**
1. Check database user has SELECT privileges
2. Verify LLM API key is valid
3. Try scanning a smaller table

### "No sample data"

**Cause:** Table is empty or query timeout

**Solution:**
1. Verify table has data
2. Check connection is working
3. Try a smaller table

---

## Examples

### Finding Relevant Tables

**Goal:** Find user-related tables

**Steps:**
1. Navigate to Data → Tables
2. Type "user" in filter
3. Review filtered results
4. Open tables with AI descriptions mentioning "user"

### Understanding a New Schema

**Goal:** Understand unfamiliar database

**Steps:**
1. Navigate to Data → Schema
2. Review visual schema
3. Identify main tables (most connections)
4. Scan main tables for AI descriptions
5. Preview sample data

### Preparing for a Query

**Goal:** Query sales data

**Steps:**
1. Navigate to Data → Tables
2. Find "sales" or "orders" table
3. Review columns and types
4. Check foreign keys (e.g., customers, products)
5. Preview sample data
6. Build query with confidence

---

## Next Steps

- Learn about [Managing Connections](../settings/connection-settings.md)
- Explore [Knowledge Base](../knowledge-base/creating-entries.md)
- Return to [Chat](../chat/natural-language-queries.md)

---

**Explore your data with confidence!** 🗄️
