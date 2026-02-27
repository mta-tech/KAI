# Part 1: Setup & First Query

> **Time:** ~15 minutes
> **Prerequisites:** None — this is where you start
> **What you'll learn:**
> - Start the required services (Typesense, PostgreSQL)
> - Connect KAI to a database
> - Scan tables with AI-generated descriptions
> - Run your first natural language query

---

## Introduction

KAI turns natural language questions into SQL queries and analysis. In this part, you'll set up a sample database, connect KAI to it, and ask your first question.

---

## Step 1: Start Typesense

KAI uses Typesense for storing metadata, instructions, and embeddings. Start it with Docker:

```bash
docker compose up typesense -d
```

### Expected Output

```
[+] Running 1/1
 ✔ Container kai-typesense-1  Started
```

### Checkpoint

Verify Typesense is running:

```bash
curl -s http://localhost:8108/health | python3 -m json.tool
```

You should see:

```json
{
    "ok": true
}
```

---

## Step 2: Set Up the Sample Database

Start a PostgreSQL container and load the koperasi sample data:

```bash
# Start PostgreSQL
docker run -d \
  --name postgres_koperasi \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=koperasi_demo \
  -p 5432:5432 \
  postgres:15

# Wait for PostgreSQL to start
sleep 5
```

Copy data files and create tables:

```bash
# Navigate to sample data directory
cd docs/tutorials/koperasi-sample-data

# Copy CSV files to container
docker cp dim_geography.csv postgres_koperasi:/tmp/
docker cp dim_date.csv postgres_koperasi:/tmp/
docker cp fact_kpi.csv postgres_koperasi:/tmp/

# Create tables and load data
docker exec -i postgres_koperasi psql -U postgres -d koperasi_demo < setup_database.sql

# Return to project root
cd ../../..
```

### Checkpoint

Verify the data loaded:

```bash
docker exec postgres_koperasi psql -U postgres -d koperasi_demo \
  -c "SELECT COUNT(*) as provinces FROM dim_geography; SELECT COUNT(*) as kpi_records FROM fact_kpi;"
```

You should see:

```
 provinces
-----------
        15

 kpi_records
-------------
          15
```

---

## Step 3: Configure KAI

Make sure your environment is set up. Create or edit `.env.local`:

```bash
# Required: LLM provider
GOOGLE_API_KEY=your-api-key-here
CHAT_FAMILY=google
CHAT_MODEL=gemini-2.0-flash

# Required: Embedding model
EMBEDDING_FAMILY=google
EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_DIMENSIONS=768

# Required: Encryption key (generate one and paste the result here)
# Run this command separately in your terminal to generate the key:
#   uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPT_KEY=your-generated-key-here
```

Verify your configuration:

```bash
uv run kai config show
```

### Expected Output

```
╭─── KAI Configuration ───╮
│ App: KAI API v1.0.0      │
│ Environment: development  │
│                           │
│ Chat: google/gemini-2.0-flash │
│ Embedding: google/gemini-embedding-001 (768d) │
│                           │
│ Storage: typesense        │
│ Typesense: localhost:8108 │
╰───────────────────────────╯
```

> **Analytics Engineer Tip:** Run `uv run kai config check` for a deeper validation that tests API key connectivity and Typesense health.

---

## Step 4: Connect to the Database

Register the sample database with KAI:

```bash
uv run kai connection create \
  "postgresql://postgres:postgres@localhost:5432/koperasi_demo" \
  -a kemenkop
```

### Expected Output

```
Testing connection... ✓
Connection created successfully!

  ID:    <generated-uuid>
  Alias: kemenkop
  URI:   postgresql://***@localhost:5432/koperasi_demo
```

**Important:** Copy the `ID` value (a UUID like `a1b2c3d4-e5f6-...`). Most CLI commands need this connection ID. For convenience, save it as a variable:

```bash
export KAI_DB=<paste-your-connection-id-here>
```

Throughout the rest of this tutorial, we use `$KAI_DB` wherever a connection ID is needed. If you start a new terminal, run `uv run kai connection list` to find the ID again.

### Checkpoint

Verify the connection is saved:

```bash
uv run kai connection list
```

You should see `kemenkop` in the list with its UUID.

<details>
<summary>REST API equivalent</summary>

```bash
curl -X POST http://localhost:8015/api/v1/database-connections \
  -H "Content-Type: application/json" \
  -d '{
    "connection_uri": "postgresql://postgres:postgres@localhost:5432/koperasi_demo",
    "alias": "kemenkop"
  }'
```

</details>

---

## Step 5: Scan Tables

Scan all tables and generate AI descriptions of each column:

```bash
uv run kai table scan-all $KAI_DB -d
```

The `-d` flag tells KAI to use the LLM to generate human-readable descriptions for each column.

### Expected Output

```
Refreshing tables from database... ✓
Found 3 tables in 1 schema(s)

Scanning tables...
  [1/3] public.dim_geography    ✓ (5 columns)
  [2/3] public.dim_date         ✓ (8 columns)
  [3/3] public.fact_kpi         ✓ (7 columns)

Scan complete: 3 tables, 20 columns described
```

### Checkpoint

View the scanned tables:

```bash
uv run kai table list $KAI_DB -c
```

You should see all 3 tables with their column counts and descriptions.

> **Business Analyst Tip:** The `-d` flag is important — it tells KAI what each column means in plain English. Without it, KAI only sees column names like `TotalKoperasiTerdaftar` without understanding the context.

<details>
<summary>REST API equivalent</summary>

```bash
# Sync schemas
curl -X POST http://localhost:8015/api/v1/table-descriptions/sync-schemas \
  -H "Content-Type: application/json" \
  -d '{"db_connection_id": "<connection-id>"}'

# Scan with descriptions
curl -X POST http://localhost:8015/api/v1/table-descriptions/refresh \
  -H "Content-Type: application/json" \
  -d '{"db_connection_id": "<connection-id>", "with_descriptions": true}'
```

</details>

---

## Step 6: Run Your First Query

Ask KAI a question in plain English:

```bash
uv run kai query run \
  "How many cooperatives are registered in total?" \
  --db $KAI_DB
```

### Expected Output

```
🤖 KAI Agent

Mission: How many cooperatives are registered in total?

📋 Plan:
  ✓ Understand the database schema
  ✓ Write SQL query to count total registered cooperatives
  ✓ Execute query and present results

💡 Generated SQL:
  SELECT SUM("TotalKoperasiTerdaftar") as total_registered
  FROM fact_kpi

📊 Result:
  ┌──────────────────────┐
  │ total_registered     │
  ├──────────────────────┤
  │ 190                  │
  └──────────────────────┘

✅ Analysis complete
```

You just asked a question in English and got a SQL-backed answer.

> **Analytics Engineer Tip:** Notice that KAI correctly quoted `"TotalKoperasiTerdaftar"` with double quotes — PostgreSQL requires this for mixed-case column names. KAI handles this automatically.

> **Business Analyst Tip:** You don't need to know any SQL. Just type your question and KAI figures out which tables and columns to use.

---

## What Could Go Wrong?

### Problem: Typesense connection refused

**Symptom:** `ConnectionError: Could not connect to Typesense at localhost:8108`

**Fix:** Start Typesense:

```bash
docker compose up typesense -d
```

### Problem: Database connection fails

**Symptom:** `OperationalError: could not connect to server`

**Fix:** Check PostgreSQL is running:

```bash
docker ps | grep postgres_koperasi
```

If not running, restart it:

```bash
docker start postgres_koperasi
```

### Problem: Embedding model not found

**Symptom:** `404 models/text-embedding-004 is not found`

**Fix:** Update your `.env.local` to use the correct model:

```bash
EMBEDDING_MODEL=gemini-embedding-001
```

---

## Summary

What you accomplished:
- Started Typesense and PostgreSQL with sample data
- Connected KAI to the koperasi database
- Scanned 3 tables with AI-generated column descriptions
- Ran your first natural language query and got a SQL-backed answer

## Next: Part 2

In [Part 2: Building Knowledge](part-2-knowledge.md), you'll teach KAI domain-specific terms and rules to improve query accuracy.
