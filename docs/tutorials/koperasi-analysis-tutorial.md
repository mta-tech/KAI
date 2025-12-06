# Tutorial: Teaching KAI-Agent Domain Knowledge

This tutorial walks you through KAI-Agent's learning capabilities using a real-world example: analyzing Indonesian cooperative (koperasi) data. You'll learn how to:

- Connect to a database
- Scan and describe tables with AI
- Run natural language queries
- Teach domain knowledge using **Skills**
- Add business rules using **Instructions**

By the end, you'll understand how KAI-Agent learns from your guidance to deliver accurate, context-aware analysis.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Connect to the Database](#connect-to-the-database)
4. [Scan Tables with AI Descriptions](#scan-tables-with-ai-descriptions)
5. [First Analysis Attempt](#first-analysis-attempt)
6. [Teaching with Skills](#teaching-with-skills)
7. [Refining with Instructions](#refining-with-instructions)
8. [Final Results](#final-results)
9. [Key Takeaways](#key-takeaways)

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.11+** installed
- **[uv](https://docs.astral.sh/uv/)** package manager
- **Docker** running (for Typesense)
- **Google API Key** (for Gemini models)

```bash
# Clone and enter the project
git clone <repo-url> && cd KAI

# Install dependencies
uv sync

# Start Typesense (required for storage)
docker compose up typesense -d
```

---

## Environment Setup

Create a `.env` file in the project root with the following configuration:

```bash
# LLM Configuration
GOOGLE_API_KEY=your_google_api_key_here
CHAT_FAMILY=google
CHAT_MODEL=gemini-2.0-flash
EMBEDDING_FAMILY=google
EMBEDDING_MODEL=text-embedding-004
EMBEDDING_DIMENSIONS=768

# Typesense Configuration
TYPESENSE_API_KEY=kai_typesense
TYPESENSE_HOST=localhost
TYPESENSE_PORT=8108
TYPESENSE_PROTOCOL=HTTP

# Generate and add encryption key
# Run this command and paste the output into .env:
# uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPT_KEY=your_generated_key_here

# Agent Configuration
AGENT_LANGUAGE=en
AGENT_MAX_ITERATIONS=20
```

> 💡 **Tip**: Generate the encryption key by running:
> ```bash
> uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
> ```

---

## Connect to the Database

For this tutorial, we'll use a sample database containing Indonesian cooperative (koperasi) data hosted on Neon PostgreSQL.

### Create the Connection

```bash
uv run kai-agent create-connection \
  "postgresql://neondb_owner:npg_Pb6dIxMEVW8L@ep-damp-smoke-a15l6d4g-pooler.ap-southeast-1.aws.neon.tech/kemenkop?sslmode=require&channel_binding=require" \
  -a koperasi \
  -s public
```

**Parameters explained:**
- `-a koperasi` — Sets a friendly alias for the connection
- `-s public` — Limits scanning to the `public` schema

**Expected output:**
```
✔ Connection created successfully
  ID: abc123-def456-...
  Alias: koperasi
  Database: kemenkop
  Schemas: ['public']
```

> 📝 **Note**: Save the connection ID (e.g., `abc123-def456-...`). You'll need it for subsequent commands.

### Verify the Connection

```bash
uv run kai-agent list-connections
```

---

## Scan Tables with AI Descriptions

Now let's scan the database schema and generate AI-powered descriptions for each table and column:

```bash
uv run kai-agent scan-all <connection_id> -d
```

Replace `<connection_id>` with your actual connection ID.

**What this does:**
1. Discovers all tables in the specified schema
2. Analyzes table structures and sample data
3. Generates human-readable descriptions using AI
4. Stores metadata for semantic search

**Expected output:**
```
Scanning database schema...
✔ Found 5 tables in schema 'public'

Generating AI descriptions...
  ✔ dim_geography: Geographic dimension table with provinces and regions
  ✔ dim_date: Date dimension for time-based analysis
  ✔ fact_kpi: Key performance indicators for cooperatives
  ...

✔ Scan complete: 5 tables, 45 columns described
```

---

## First Analysis Attempt

Let's try asking KAI-Agent a business question:

```bash
uv run kai-agent interactive --db <connection_id>
```

Once in the interactive session, type:

```
how many total koperasi in java
```

### The Problem

KAI-Agent will likely return an **incorrect result** or an error. Why?

The agent doesn't yet know:
1. **Which column** contains the koperasi count (`TotalKoperasiTerdaftar`)
2. **How to join** fact and dimension tables
3. **Which provinces** are part of Java

This is expected! KAI-Agent needs domain knowledge to answer correctly.

Type `exit` to leave the interactive session.

---

## Teaching with Skills

**Skills** are reusable analysis patterns that teach KAI-Agent domain-specific knowledge. They're written in Markdown with YAML frontmatter.

### Create the Skills Directory

```bash
mkdir -p .skills/koperasi-analysis
```

### Create the Skill File

Create `.skills/koperasi-analysis/SKILL.md`:

```markdown
---
name: Total Number Koperasi / Cooperatives Analysis
description: Use when analyzing registered number of koperasi. Provides standard approaches for calculating and comparing koperasi count in different areas.
category: analysis
tags:
  - koperasi
  - metrics
  - cooperative
---

# Total Number Koperasi Analysis Skill

This skill provides guidance for performing total number koperasi analysis.

## When to Use

Load this skill when the user asks about:
- Total koperasi analysis
- Koperasi count by region
- Cooperative statistics comparisons

## Analysis Workflow

### Step 1: Use the Correct Metric Column

Always use the `TotalKoperasiTerdaftar` column from `fact_kpi` table for koperasi counts.

```sql
SELECT SUM(TotalKoperasiTerdaftar) as total_koperasi
FROM fact_kpi
```

### Step 2: Join Geography for Regional Analysis

When asked about provinces or regions, join with `dim_geography`:

```sql
SELECT 
    g.province_name,
    SUM(f.TotalKoperasiTerdaftar) as total_koperasi
FROM fact_kpi f
JOIN dim_geography g ON f.geography_id = g.id
GROUP BY g.province_name
```

### Step 3: Filter by Province Name

**Important**: Use explicit equality filters for province names. DO NOT use LIKE or pattern matching.

```sql
-- ✅ Correct
WHERE g.province_name = 'Jawa Barat'

-- ❌ Incorrect
WHERE g.province_name LIKE '%Jawa%'
```

## Example Queries

**Total koperasi nationwide:**
```sql
SELECT SUM(TotalKoperasiTerdaftar) as total_koperasi
FROM fact_kpi
```

**Total koperasi by province:**
```sql
SELECT 
    g.province_name,
    SUM(f.TotalKoperasiTerdaftar) as total_koperasi
FROM fact_kpi f
JOIN dim_geography g ON f.geography_id = g.id
GROUP BY g.province_name
ORDER BY total_koperasi DESC
```
```

### Discover and Register the Skill

```bash
uv run kai-agent discover-skills <connection_id>
```

**Expected output:**
```
Discovering skills in: /path/to/KAI/.skills
Sync to storage: Yes

✔ Discovered 1 skill(s)
  • koperasi-analysis (Total Number Koperasi / Cooperatives Analysis) active
    Use when analyzing registered number of koperasi...
```

### Verify the Skill

```bash
uv run kai-agent list-skills <connection_id>
```

---

## Test with the Skill

Now let's run the analysis again. Start a new interactive session:

```bash
uv run kai-agent interactive --db <connection_id>
```

Ask the question with skill context:

```
how many total koperasi in java
```

### Progress!

This time, KAI-Agent should:
- ✅ Use the correct column (`TotalKoperasiTerdaftar`)
- ✅ Join with geography dimension
- ✅ Filter by provinces

**But there's still an issue**: The result might be **incomplete** because "Java" includes provinces that don't have "Jawa" in their name:
- **Jawa Barat** ✅
- **Jawa Tengah** ✅
- **Jawa Timur** ✅
- **DKI Jakarta** ❌ (missed!)
- **Banten** ❌ (missed!)
- **DI Yogyakarta** ❌ (missed!)

Type `exit` to leave the session.

---

## Refining with Instructions

**Instructions** are conditional rules that tell KAI-Agent how to handle specific scenarios. Unlike skills (which provide analysis patterns), instructions enforce business rules.

### Add the Instruction

```bash
uv run kai-agent add-instruction <connection_id> \
  -c "When asked about Java" \
  -r "Always include Jakarta (DKI Jakarta), Banten, and Yogyakarta (DI Yogyakarta) in addition to Jawa Barat, Jawa Tengah, and Jawa Timur"
```

**Parameters explained:**
- `-c` — **Condition**: When this instruction applies
- `-r` — **Rules**: What the agent should do

**Expected output:**
```
✔ Instruction added successfully
  ID: instr_abc123
  Condition: When asked about Java
  Rules: Always include Jakarta (DKI Jakarta), Banten, and Yogyakarta...
```

### Verify the Instruction

```bash
uv run kai-agent list-instructions <connection_id>
```

---

## Final Results

Now let's run the complete analysis with both the skill and instruction:

```bash
uv run kai-agent interactive --db <connection_id>
```

Ask the question:

```
how many total koperasi in java
```

### The Correct Answer

KAI-Agent should now:

1. ✅ Load the koperasi analysis skill
2. ✅ Use `TotalKoperasiTerdaftar` column
3. ✅ Apply the Java instruction (include all 6 provinces)
4. ✅ Return the correct total: **91** koperasi

**Sample output:**
```
Based on my analysis of the database, the total number of registered 
cooperatives (koperasi) in Java is 91.

This includes all provinces in the Java region:
- Jawa Barat
- Jawa Tengah  
- Jawa Timur
- DKI Jakarta
- Banten
- DI Yogyakarta
```

---

## Key Takeaways

### Skills vs Instructions

| Aspect | Skills | Instructions |
|--------|--------|--------------|
| **Purpose** | Teach analysis patterns | Enforce business rules |
| **Format** | Markdown with YAML | Condition + Rules |
| **Scope** | Reusable templates | Context-specific rules |
| **Examples** | SQL patterns, workflows | "When X, always do Y" |

### When to Use Each

**Use Skills when:**
- Teaching general analysis patterns
- Documenting SQL templates
- Defining metric calculations
- Creating reusable knowledge

**Use Instructions when:**
- Adding business-specific rules
- Handling edge cases
- Defining terminology mappings
- Enforcing conventions

### The Learning Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   First Query   │────►│  Identify Gap   │────►│   Add Skill/    │
│   (May Fail)    │     │  (Missing Info) │     │   Instruction   │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                        ┌─────────────────┐              │
                        │  Accurate       │◄─────────────┘
                        │  Results!       │
                        └─────────────────┘
```

---

## Next Steps

Now that you understand the basics, try:

1. **Add more skills** for different analysis types
2. **Create default instructions** that always apply (`--default` flag)
3. **Export sessions** to share analysis with colleagues
4. **Add a business glossary** for metric definitions

```bash
# Add a default instruction
uv run kai-agent add-instruction <connection_id> \
  -c "Always" \
  -r "Format numbers with thousand separators" \
  --default

# Add a glossary entry
uv run kai-agent add-glossary <connection_id> \
  --metric "Active Koperasi" \
  --sql "SELECT COUNT(*) FROM fact_kpi WHERE status = 'active'"
```

---

## Troubleshooting

### "No skills found"

Ensure your skill file is named `SKILL.md` (case-sensitive) and is in a subdirectory of `.skills/`:

```
.skills/
└── koperasi-analysis/
    └── SKILL.md  ✅
```

### "Database connection not found"

Run `uv run kai-agent list-connections` to verify the connection ID.

### Skill not being used

Check if the skill is active:

```bash
uv run kai-agent list-skills <connection_id>
```

If inactive, try rediscovering:

```bash
uv run kai-agent discover-skills <connection_id>
```

---

## Full Command Reference

```bash
# Connection management
uv run kai-agent create-connection "<uri>" -a <alias> -s <schema>
uv run kai-agent list-connections
uv run kai-agent show-connection <connection_id>

# Schema scanning
uv run kai-agent scan-all <connection_id> -d

# Interactive analysis
uv run kai-agent interactive --db <connection_id>

# Skills management
uv run kai-agent discover-skills <connection_id>
uv run kai-agent list-skills <connection_id>
uv run kai-agent search-skills <connection_id> "query"

# Instructions management
uv run kai-agent add-instruction <connection_id> -c "condition" -r "rules"
uv run kai-agent list-instructions <connection_id>

# Session management
uv run kai-agent list-sessions
uv run kai-agent export-session <session_id> -f markdown
```

---

*Happy analyzing with KAI-Agent! 🚀*

