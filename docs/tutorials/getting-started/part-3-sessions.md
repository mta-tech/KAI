# Part 3: Interactive Sessions & Memory

> **Time:** ~15 minutes
> **Prerequisites:** [Part 1](part-1-setup.md) and [Part 2](part-2-knowledge.md) completed
> **What you'll learn:**
> - Run multi-turn conversations in interactive mode
> - Manage sessions (list, export, resume)
> - Store and recall persistent memories across sessions

---

## Introduction

So far, you've run one-shot queries — ask a question, get an answer, done. But real analysis is conversational. You ask a question, see the result, then drill deeper. KAI's interactive mode keeps context across turns, so follow-up questions understand what came before.

---

## Step 1: Start an Interactive Session

Launch the REPL (Read-Eval-Print Loop):

```bash
uv run kai query interactive --db kemenkop
```

### Expected Output

```
╭─── KAI Interactive Session ───╮
│ Database: kemenkop              │
│ Session: <session-id>           │
│ Type 'exit' or 'quit' to end   │
╰─────────────────────────────────╯

kai> _
```

You're now in a conversational session. Try a multi-turn conversation:

```
kai> How many cooperatives are registered in Java?
```

Wait for the response, then follow up:

```
kai> Which province in Java has the most?
```

KAI remembers the context — "Java" and "cooperatives" carry over from the first question. The follow-up doesn't need to repeat the full context.

```
kai> Compare that to Sumatra
```

Again, KAI understands "that" refers to cooperative counts and extends the comparison to Sumatra.

Type `exit` to end the session:

```
kai> exit
```

> **Business Analyst Tip:** Interactive mode is the most natural way to explore data. Start with a broad question, then narrow down based on what you see — just like talking to a colleague.

---

## Step 2: View Your Sessions

List all your sessions:

```bash
uv run kai session list
```

### Expected Output

```
Sessions:
  ┌──────────────────────────────┬──────────┬──────────┬──────────────────────┐
  │ ID                           │ Database │ Status   │ Created              │
  ├──────────────────────────────┼──────────┼──────────┼──────────────────────┤
  │ <session-id>                 │ kemenkop │ idle     │ 2026-02-27 14:30:00  │
  └──────────────────────────────┴──────────┴──────────┴──────────────────────┘
```

View the details and message history of a session:

```bash
uv run kai session show <session-id>
```

### Checkpoint

You should see the 3 messages from your interactive session (Java cooperatives, top province, Sumatra comparison) along with KAI's responses.

> **Note:** Session management is CLI-only. Sessions are managed internally via LangGraph — there are no direct REST API endpoints for listing or viewing sessions.

---

## Step 3: Export a Session

Save a session's conversation to a file for sharing or documentation:

```bash
uv run kai session export <session-id> -o session-export.md -f markdown
```

### Expected Output

```
Session exported to session-export.md (markdown format)
```

The exported file contains the full conversation in readable markdown — useful for reports or sharing with colleagues.

> **Analytics Engineer Tip:** Export sessions as JSON (`-f json`) for programmatic processing. The JSON format includes metadata like generated SQL, execution times, and tool usage.

---

## Step 4: Resume a Previous Session

Continue where you left off:

```bash
uv run kai query resume <session-id> \
  "Now show me the trend over time for Jawa Barat" \
  --db $KAI_DB
```

### Expected Output

```
🤖 KAI Agent (Resuming session)

Mission: Now show me the trend over time for Jawa Barat

📋 Plan:
  ✓ Recall context: previous queries about Java cooperatives
  ✓ Query time-series data for Jawa Barat
  ✓ Present trend analysis

💡 Generated SQL:
  SELECT
    d.year, d.month_name,
    f."TotalKoperasiTerdaftar" as registered
  FROM fact_kpi f
  JOIN dim_geography g ON f.geography_id = g.id
  JOIN dim_date d ON f.date_id = d.id
  WHERE g.province_name = 'Jawa Barat'
  ORDER BY d.date

📊 Result:
  [Trend data for Jawa Barat cooperatives over time]
```

KAI remembered the conversation context and knew "Jawa Barat" was a province from the earlier Java discussion.

---

## Step 5: Add Persistent Memory

Memory lets KAI remember facts across sessions. Add a domain-specific fact:

The `memory add` command takes four positional arguments: connection ID, namespace, key, and content.

```bash
uv run kai knowledge memory add $KAI_DB \
  domain_facts \
  fiscal_year \
  "The fiscal year for koperasi reporting runs January to December. Annual reports are due by March 31 of the following year." \
  -i 0.8
```

### Expected Output

```
Memory added successfully!

  ID:         <generated-id>
  Namespace:  domain_facts
  Key:        fiscal_year
  Importance: 0.8
```

Add another memory:

```bash
uv run kai knowledge memory add $KAI_DB \
  domain_facts \
  active_threshold \
  "A cooperative is considered 'active' if it has held at least one annual meeting (RAT) in the current fiscal year and submitted financial reports." \
  -i 0.7
```

### Checkpoint

Search memories to verify:

```bash
uv run kai knowledge memory search "fiscal year" -d $KAI_DB
```

You should see the fiscal year memory entry you just created.

```bash
uv run kai knowledge memory list $KAI_DB --namespace domain_facts
```

You should see 2 entries in the `domain_facts` namespace.

> **Analytics Engineer Tip:** Use namespaces to organize memories by topic (e.g., `domain_facts`, `data_quality`, `business_rules`). The `-i` (importance) parameter ranges from 0.0 to 1.0 — higher values mean higher retrieval priority.

> **Business Analyst Tip:** Memories are like sticky notes for KAI. Write down important facts about your data once, and KAI will recall them whenever relevant.

<details>
<summary>REST API equivalent</summary>

```bash
# Add memory
curl -X POST http://localhost:8015/api/v1/context-stores \
  -H "Content-Type: application/json" \
  -d '{
    "db_connection_id": "<connection-id>",
    "namespace": "domain_facts",
    "key": "fiscal_year",
    "content": "The fiscal year for koperasi reporting runs January to December.",
    "importance": 0.8
  }'

# Search memories
curl "http://localhost:8015/api/v1/context-stores/semantic-search?prompt=fiscal+year&db_connection_id=<connection-id>"
```

</details>

---

## What Could Go Wrong?

### Problem: Session not found when resuming

**Symptom:** `Error: Session <id> not found`

**Fix:** Sessions may have been cleared. List available sessions first:

```bash
uv run kai session list
```

If the session was deleted, start a new interactive session instead.

### Problem: Memory search returns no results

**Symptom:** `No memories found matching "..."` even though you just added one

**Fix:** Memory indexing may take a moment. Wait a few seconds and try again. Also verify the memory was saved:

```bash
uv run kai knowledge memory list $KAI_DB
```

---

## Summary

What you accomplished:
- Had a multi-turn conversation in interactive mode with context retention
- Listed and exported sessions for documentation
- Resumed a previous session with full context recall
- Added persistent memories that KAI recalls across sessions

## Next: Part 4

In [Part 4: Advanced Analytics & Visualization](part-4-analytics.md), you'll use KAI's analysis mode for statistical analysis, trend detection, and chart generation.
