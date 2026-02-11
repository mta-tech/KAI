# Migration Scripts

This directory contains migration scripts for the KAI application.

## Embedding Migration

### Overview

When you change the embedding model configuration (e.g., switching from OpenAI to Google, or changing model dimensions), all stored embeddings need to be recomputed.

### How It Works

#### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      MIGRATION WORKFLOW                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  1. READ NEW CONFIG                                                  │
│     └── Loads EMBEDDING_FAMILY, EMBEDDING_MODEL, EMBEDDING_DIMENSIONS│
│                                                                       │
│  2. FETCH EXISTING RECORDS                                           │
│     └── Queries TypeSense for all records in each collection         │
│     └── Applies filters (e.g., is_default=false for instructions)   │
│                                                                       │
│  3. COMPUTE NEW EMBEDDINGS                                           │
│     └── For each record:                                             │
│         - Extract text from relevant fields                          │
│         - Call embedding API with new model                          │
│         - Get new embedding vector                                   │
│                                                                       │
│  4. UPDATE RECORDS IN-PLACE                                          │
│     └── For each record:                                             │
│         - Keep same document ID                                      │
│         - Keep all other fields unchanged                            │
│         - Replace embedding field with new vector                    │
│                                                                       │
│  5. REPORT RESULTS                                                   │
│     └── Show success/failure counts per collection                   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

#### What Happens to Existing Records

**The script modifies existing records in-place.**

```
┌─────────────────────────────────── BEFORE ───────────────────────────────────┐
│                                                                              │
│  TypeSense Collection: instructions                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │ Document ID: abc123                                                     │   │
│  │   db_connection_id: "749a5cce..."                                      │   │
│  │   condition: "When querying sales data"                                │   │
│  │   rules: "Always filter by last 12 months"                             │   │
│  │   instruction_embedding: [0.123, 0.456, 0.789, ...]  ← OLD EMBEDDING   │   │
│  │   is_default: false                                                    │   │
│  │   created_at: "2026-02-09T10:00:00"                                    │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          │ Migration runs
                                          ▼
┌─────────────────────────────────── AFTER ────────────────────────────────────┐
│                                                                              │
│  TypeSense Collection: instructions                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │ Document ID: abc123                    ← SAME ID                        │   │
│  │   db_connection_id: "749a5cce..."      ← UNCHANGED                     │   │
│  │   condition: "When querying sales data"← UNCHANGED                     │   │
│  │   rules: "Always filter by last 12 months"← UNCHANGED                  │   │
│  │   instruction_embedding: [0.987, 0.321, 0.654, ...]  ← NEW EMBEDDING  │   │
│  │   is_default: false                    ← UNCHANGED                     │   │
│  │   created_at: "2026-02-09T10:00:00"    ← UNCHANGED                     │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

#### Key Behaviors

| Aspect | Behavior | Explanation |
|--------|----------|-------------|
| **Record ID** | Preserved | Same document ID before and after |
| **Other Fields** | Unchanged | All fields except embedding stay identical |
| **Embedding Field** | Replaced | Old embedding vector is overwritten |
| **Duplicate Records** | None created | No new documents are created |
| **Deleted Records** | None deleted | All records are preserved |

#### Why In-Place Update?

**Advantages:**
- ✅ **No duplicates** - Clean database, no orphaned records
- ✅ **References preserved** - Any external references to document IDs remain valid
- ✅ **Storage efficient** - No additional storage required
- ✅ **Idempotent** - Can safely rerun if migration fails partway
- ✅ **Zero downtime** - Application continues working during migration

**Trade-offs:**
- ⚠️ **No automatic backup** - Old embeddings are lost after update
- ⚠️ **Point-in-time change** - Records update one by one, not atomically

#### Data Flow for Each Collection

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COLLECTION: instructions                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Step 1: Fetch Records                                              │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ SELECT * FROM instructions WHERE is_default = false             │  │
│  │ Returns: 5 records                                              │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                   │                                  │
│  Step 2: For Each Record                                           │
│                                   ▼                                  │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ Record ID: abc123                                               │  │
│  │                                                                  │  │
│  │ Text to embed:                                                  │  │
│  │   "When querying sales data, Always filter by last 12 months"   │  │
│  │                                                                  │  │
│  │ Call: embedding_model.embed_query(text)                         │  │
│  │                                                                  │  │
│  │ Result: [0.987, 0.321, 0.654, ...]  (768 dimensions)            │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                   │                                  │
│  Step 3: Update Record                                              │
│                                   ▼                                  │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ UPDATE instructions                                              │  │
│  │ SET instruction_embedding = [0.987, 0.321, 0.654, ...]          │  │
│  │ WHERE id = "abc123"                                              │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

#### Error Handling

If embedding computation fails for a record:

```
┌─────────────────────────────────────────────────────────────────────┐
│ Record ID: xyz789                                                    │
│ Text: "Some text..."                                                 │
│                                                                       │
│ Try: embedding_model.embed_query(text)                               │
│                                                                       │
│ ❌ ERROR: API timeout / invalid API key / network issue               │
│                                                                       │
│ Result:                                                               │
│   - Record is SKIPPED (not updated)                                  │
│   - Error logged to console                                          │
│   - Failed count incremented                                         │
│   - Migration continues with next record                             │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

**Recovery**: You can safely rerun the script. It will recompute embeddings for:
- All records (if not using idempotency checks)
- Or only failed records (if you implement resume capability)

#### Batch Processing

Records are fetched in pages of **250** to avoid memory issues:

```
Page 1: Records 1-250     → Migrate → Update
Page 2: Records 251-500   → Migrate → Update
Page 3: Records 501-750   → Migrate → Update
...
```

Progress bar shows real-time status:

```
Migrating instructions: 100%|████████| 500/500 [02:15<00:00,  3.67it/s]
```

### What Gets Migrated

| Collection | Embedding Field | Records Migrated |
|------------|-----------------|------------------|
| `context_stores` | `prompt_embedding` | All records |
| `instructions` | `instruction_embedding` | Only `is_default=false` |
| `table_descriptions` | N/A | Skipped (computed dynamically) |

### Prerequisites

Before running the migration, update your `.env` file with the new embedding configuration:

```bash
# Example: Switch to Google embeddings
EMBEDDING_FAMILY="google"
EMBEDDING_MODEL="gemini-embedding-001"
EMBEDDING_DIMENSIONS=768

# Example: Switch to OpenAI embeddings
EMBEDDING_FAMILY="openai"
EMBEDDING_MODEL="text-embedding-3-small"
EMBEDDING_DIMENSIONS=1536
```

### Usage

#### Migrate All Collections

```bash
poetry run python -m migration.embedding_migration
```

#### Migrate Specific Collections

```bash
poetry run python -m migration.embedding_migration --collections instructions context_stores
```

#### Dry Run (Recommended First)

Run without making any changes to see what will be migrated:

```bash
poetry run python -m migration.embedding_migration --dry-run
```

### Output Example

```
============================================================
EMBEDDING MIGRATION
============================================================
New embedding config: {'family': 'google', 'model': 'gemini-embedding-001', 'dimensions': 768}
Collections to migrate: ['context_stores', 'instructions']
============================================================
Starting migration for 'instructions'...
  - Embedding field: instruction_embedding
  - Filter: is_default:=false
  Found 5 documents to migrate
  Migrating instructions: 100%|████████████| 5/5 [00:03<00:00,  1.42it/s]
  Migration complete: 5 succeeded, 0 failed
============================================================
Starting migration for 'context_stores'...
  - Embedding field: prompt_embedding
  Filter: none
  Found 12 documents to migrate
  Migrating context_stores: 100%|█████████| 12/12 [00:05<00:00,  2.15it/s]
  Migration complete: 12 succeeded, 0 failed
============================================================
MIGRATION SUMMARY
============================================================
instructions: {'status': 'completed', 'count': 5, 'success': 5, 'failed': 0}
context_stores: {'status': 'completed', 'count': 12, 'success': 12, 'failed': 0}
============================================================
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--collections` | Specify collections to migrate: `context_stores`, `instructions`, `table_descriptions`, `all` |
| `--dry-run` | Run without making any changes |

### Common Scenarios

#### Scenario 1: Changed Embedding Model

```bash
# 1. Update .env with new model
# 2. Dry run first
poetry run python -m migration.embedding_migration --dry-run

# 3. Run actual migration
poetry run python -m migration.embedding_migration
```

#### Scenario 2: Changed Embedding Dimensions

```bash
# When changing dimensions, TypeSense collections need to be recreated
# The script handles this automatically

poetry run python -m migration.embedding_migration
```

#### Scenario 3: Migration Only Instructions

```bash
poetry run python -m migration.embedding_migration --collections instructions
```

### Troubleshooting

#### Error: "Failed to compute embedding"

- Check your API key is valid
- Verify the embedding model name is correct
- Check network connectivity to the embedding API

#### Error: "Collection not found"

- Ensure TypeSense is running
- Check `TYPESENSE_HOST` and `TYPESENSE_PORT` in `.env`

#### Progress Stuck

- Press `Ctrl+C` to stop
- The script is idempotent - you can safely rerun it

### After Migration

1. **Verify the migration** by checking record counts match
2. **Test semantic search** to ensure embeddings work correctly
3. **Monitor API usage** - recomputing embeddings uses API calls

### Notes

- **Backups**: The script updates embeddings in-place. No automatic backup is created.
- **Downtime**: The application can continue running during migration.
- **Idempotent**: You can safely rerun the script if it fails.
- **API Costs**: Each document requires one embedding API call.
