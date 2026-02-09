# KAI Cookbook

Welcome to the KAI (Knowledge Agent for Intelligence Query) Cookbook! This collection of Python scripts demonstrates how to use the KAI API for natural language database querying and analysis.

## Prerequisites

1. **KAI Server Running**
   ```bash
   # Start the KAI server
   uv run python -m app.main
   ```
   The server will be available at `http://localhost:8015`

2. **Required Environment Variables**
   - `GOOGLE_API_KEY` or `OPENAI_API_KEY` - For LLM operations
   - `ENCRYPT_KEY` - For credential encryption
   - `TYPESENSE_HOST` - Vector search backend

3. **Python Dependencies**
   ```bash
   uv sync
   ```

4. **Optional: Typesense for Storage**
   ```bash
   docker compose up typesense -d
   ```

## Getting Started

### Quick Start

1. Ensure the KAI server is running at `http://localhost:8015`
2. Configure the sample database (optional - scripts use it by default):
   ```bash
   # Already configured in .env:
   SAMPLE_DB_URI=postgresql://neondb_owner:npg_6Lua4kAFJnhg@ep-blue-bar-a1ptyhib-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
   SAMPLE_DB_ALIAS=kemenkop_sample
   ```
3. Run scripts in order:
   ```bash
   # Basic functionality - run without cleanup to preserve resources
   python cookbook/basic/01_create_database_connection.py --no-cleanup
   python cookbook/basic/02_list_table_descriptions.py --no-cleanup
   python cookbook/basic/03_sync_schemas.py --no-cleanup
   # ... etc
   ```

### Command-Line Arguments

All cookbook scripts support the `--no-cleanup` flag:

- **Default behavior** (without flag): Resources are deleted at the end of each script
- **`--no-cleanup` flag**: Resources are preserved for use by subsequent scripts

```bash
# Preserve resources between runs (recommended for learning)
python cookbook/basic/01_create_database_connection.py --no-cleanup

# Clean up resources after each script (default)
python cookbook/basic/01_create_database_connection.py
```

Each script includes:
- Clear explanations of API endpoints
- Step-by-step demonstrations
- "Press any key to continue" pauses for multi-endpoint flows
- Idempotent operations where possible
- Full error handling
- Optional cleanup control via command-line flag

## Cookbook Structure

```
cookbook/
├── utils/
│   └── __init__.py          # Shared utilities and API client
├── basic/                   # Basic API functionality
│   ├── 01_create_database_connection.py
│   ├── 02_list_table_descriptions.py
│   ├── 03_sync_schemas.py
│   ├── 04_create_instructions.py
│   ├── 05_create_context_stores.py
│   ├── 06_create_business_glossaries.py
│   ├── 07_create_prompts.py
│   ├── 08_sql_generation.py
│   └── 09_aliases.py
└── advanced/                # Advanced features
    ├── 01_nl_generation.py
    ├── 02_comprehensive_analysis.py
    └── 03_rag_documents.py
```

## Basic Functionality

### 1. Create Database Connection (`01_create_database_connection.py`)
- Create and manage database connections
- Supports PostgreSQL, MySQL, and other databases
- Connection testing and validation

### 2. List Table Descriptions (`02_list_table_descriptions.py`)
- View synced table metadata
- Browse column definitions
- Understand table relationships

### 3. Sync Schemas (`03_sync_schemas.py`)
- Scan database structure
- Create table descriptions
- Optionally use AI to generate descriptions

### 4. Create Instructions (`04_create_instructions.py`)
- Define rules for SQL generation
- Set query-specific conditions
- Configure default behaviors

### 5. Create Context Stores (`05_create_context_stores.py`)
- Store example prompt-SQL pairs
- Enable few-shot learning
- Improve SQL generation accuracy

### 6. Create Business Glossaries (`06_create_business_glossaries.py`)
- Define business metrics
- Map business terms to SQL
- Standardize metric calculations

### 7. Create Prompts (`07_create_prompts.py`)
- Save natural language queries
- Associate with database connections
- Add context for better results

### 8. SQL Generation (`08_sql_generation.py`)
- Convert natural language to SQL
- Execute generated queries
- View and store results

### 9. Aliases (`09_aliases.py`)
- Map business terms to schema names
- Improve query understanding
- Bridge terminology gaps

## Advanced Functionality

### 1. Natural Language Generation (`01_nl_generation.py`)
- Generate insights from SQL results
- Create human-readable summaries
- Explain data patterns

### 2. Comprehensive Analysis (`02_comprehensive_analysis.py`)
- End-to-end: prompt → SQL → analysis
- Statistical analysis of results
- Chart recommendations

### 3. RAG Documents (`03_rag_documents.py`)
- Upload and index documents
- Semantic search on content
- Knowledge-based Q&A

## Common Usage Patterns

### End-to-End Query Flow

```python
from utils import KAIAPIClient

client = KAIAPIClient()

# 1. Create connection
conn = client.post("/database-connections", json_data={
    "alias": "my_db",
    "connection_uri": "postgresql://user:pass@host/db"
})

# 2. Sync schemas
tables = client.post("/table-descriptions/sync-schemas", json_data={
    "db_connection_id": conn["id"]
})

# 3. Generate SQL
prompt = client.post("/prompts", json_data={
    "text": "Show me total sales by month",
    "db_connection_id": conn["id"]
})

sql_gen = client.post(f"/prompts/{prompt['id']}/sql-generations", json_data={
    "llm_config": {"provider": "google", "model": "gemini-2.0-flash-exp"}
})

# 4. Execute SQL
results = client.get(f"/sql-generations/{sql_gen['id']}/execute")
```

### One-Call Comprehensive Analysis

```python
# Everything in one call
analysis = client.post("/analysis/comprehensive", json_data={
    "prompt": {
        "text": "Analyze revenue trends",
        "db_connection_id": conn["id"]
    },
    "llm_config": {"provider": "google", "model": "gemini-2.0-flash-exp"}
})
```

## Configuration

### Sample Database

The cookbook uses a sample Kementerian Koperasi database hosted on Neon PostgreSQL. This is configured via environment variables in `.env`:

```env
SAMPLE_DB_URI=postgresql://neondb_owner:npg_6Lua4kAFJnhg@ep-blue-bar-a1ptyhib-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
SAMPLE_DB_ALIAS=kemenkop_sample
```

All scripts automatically use this database connection. You can modify these values in your `.env` file to use your own database.

### API Client

The `KAIAPIClient` class in `utils/__init__.py` provides a simple HTTP client:

```python
from utils import KAIAPIClient

# Custom base URL
client = KAIAPIClient(base_url="http://localhost:8015")

# Make requests
result = client.get("/database-connections")
data = client.post("/prompts", json_data={...})
```

### LLM Configuration

Most operations accept `llm_config`:

```python
llm_config = {
    "provider": "google",  # or "openai", "ollama", "openrouter"
    "model": "gemini-2.0-flash-exp"
}
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure KAI server is running: `uv run python -m app.main`

2. **LLM Errors**
   - Check API keys are set in `.env`
   - Verify LLM provider is configured

3. **Database Connection Failures**
   - Verify database is running
   - Check connection URI format
   - Ensure credentials are correct

4. **Type Check Warnings**
   - These are from isolated validator environments
   - Scripts will work correctly when run
   - Can be safely ignored

## API Reference

Full API documentation is available at `/docs` when the server is running.

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/database-connections` | POST | Create connection |
| `/api/v1/table-descriptions/sync-schemas` | POST | Sync schemas |
| `/api/v1/prompts` | POST | Create prompt |
| `/api/v1/prompts/{id}/sql-generations` | POST | Generate SQL |
| `/api/v1/sql-generations/{id}/execute` | GET | Execute SQL |
| `/api/v1/analysis/comprehensive` | POST | Full analysis |

## Contributing

To add a new cookbook entry:

1. Create a new file in `basic/` or `advanced/`
2. Follow the naming convention: `##_description.py`
3. Import shared utilities from `utils`
4. Include comprehensive docstrings
5. Add step-by-step execution with pauses
6. Make operations idempotent where possible

## License

This cookbook is part of the KAI project.
