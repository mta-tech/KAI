# Getting Started with KAI

This guide will walk you through setting up KAI for development, from zero to your first query.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [First Steps](#first-steps)
- [Example Workflows](#example-workflows)
- [Next Steps](#next-steps)

## Prerequisites

Before you begin, ensure you have the following installed:

### Required

1.  **Python 3.11+**
    ```bash
    python --version  # Should be 3.11 or higher
    ```    [Download Python](https://www.python.org/downloads/)

2.  **uv Package Manager**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
    [uv Documentation](https://github.com/astral-sh/uv)

3.  **Docker & Docker Compose**
    ```bash
    docker --version
    docker compose version
    ```
    [Install Docker](https://docs.docker.com/get-docker/)

4.  **Git**
    ```bash
    git --version
    ```

### Optional

- **Node.js 18+** (for Web UI)
- **PostgreSQL/MySQL** (if connecting to databases)

## Installation

### Method 1: Quick Start with Docker (Recommended)

This is the fastest way to get KAI running:

```bash
# 1. Clone the repository
git clone https://github.com/your-org/kai.git
cd kai

# 2. Set up environment
cp .env.example .env

# 3. Generate encryption key
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy the output and paste into .env as ENCRYPT_KEY

# 4. Add your LLM API key to .env
# For OpenAI:
# OPENAI_API_KEY=sk-your-key-here
# CHAT_FAMILY=openai
# CHAT_MODEL=gpt-4o-mini

# 5. Start all services
docker compose up -d

# 6. Verify services are running
docker compose ps

# 7. Check API health
curl http://localhost:8015/health
# Expected: {"status":"healthy"}
```

**Access Points:**
- API: http://localhost:8015
- API Docs: http://localhost:8015/docs
- Typesense: http://localhost:8108

### Method 2: Local Development Setup

For active development with hot reload:

```bash
# 1. Clone and enter directory
git clone https://github.com/your-org/kai.git
cd kai

# 2. Install Python dependencies
uv sync

# 3. Start Typesense in Docker
docker compose up typesense -d

# 4. Configure environment
cp .env.example .env
# Edit .env:
#   - Set TYPESENSE_HOST=localhost
#   - Add LLM API key
#   - Generate and set ENCRYPT_KEY

# 5. Run development server
uv run python -m app.main

# Or with hot reload:
APP_ENABLE_HOT_RELOAD=1 uv run python -m app.main
```

## Configuration

### Required Environment Variables

Edit your `.env` file with these values:

```bash
# LLM Provider Configuration
CHAT_FAMILY=openai                    # or: google, ollama, openrouter
CHAT_MODEL=gpt-4o-mini               # Model name
OPENAI_API_KEY=sk-your-key-here      # Your API key

# Typesense Configuration
TYPESENSE_HOST=localhost              # Use 'typesense' for Docker
TYPESENSE_PORT=8108
TYPESENSE_API_KEY=kai_typesense

# Security
ENCRYPT_KEY=your-fernet-key-here     # Generated key
```

### Optional Variables

```bash
# Advanced Settings
AGENT_MAX_ITERATIONS=20               # Max agent steps
DH_ENGINE_TIMEOUT=150                 # Timeout (seconds)
SQL_EXECUTION_TIMEOUT=60              # SQL timeout
UPPER_LIMIT_QUERY_RETURN_ROWS=50      # Result row limit

# Memory
MEMORY_BACKEND=typesense              # or: letta

# Language
AGENT_LANGUAGE=en                     # or: id (Indonesian)
```

### Generating Encryption Key

The `ENCRYPT_KEY` is required for securely storing database credentials:

```bash
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output (e.g., `4Mbe2GYx0Hk94o_f-irVHk1fKkCGAt1R7LLw5wHVghI=`) and set it in `.env`.

## First Steps

### 1. Verify Installation

Check that the API and Typesense services are running:

```bash
# API health check
curl http://localhost:8015/health

# Typesense health
curl http://localhost:8108/health

# View API documentation
open http://localhost:8015/docs
```

### 2. Create a Database Connection

All interactions with KAI require a database connection. You can create one via the API.

```bash
# Example for PostgreSQL
DB_ID="my_postgres_db"
curl -X POST http://localhost:8015/api/v1/database-connections \
  -H "Content-Type: application/json" \
  -d '{
    "id": "'"$DB_ID"'",
    "alias": "My PostgreSQL DB",
    "connection_uri": "postgresql://user:pass@localhost:5432/mydb",
    "schemas": ["public"]
  }'
```
**Note:** Replace `"id"`, `"alias"`, `"connection_uri"`, and `"schemas"` with your actual database details. The `id` you provide will be used in subsequent CLI commands.

### 3. Using the KAI Agent CLI

The `kai-agent` CLI is the primary way to interact with the autonomous agent.

#### List Connections
Verify that your newly created connection is available:
```bash
uv run kai-agent list-connections
```You should see `my_postgres_db` (or the ID you chose) in the output.

#### Interactive Mode
Start an interactive session to ask questions conversationally:
```bash
uv run kai-agent interactive --db my_postgres_db
```
Once in the session, you can ask questions like:
```
> Show me total sales by month.
> Which products are the most popular?
> Analyze customer churn patterns.
```

#### Run a Single Task
Execute a single, one-off analysis task:
```bash
uv run kai-agent run "Show top 10 customers by revenue" --db my_postgres_db
```

You can specify different modes for the agent:
- `full_autonomy` (default): The agent has full control to achieve the goal.
- `analysis`: The agent focuses on generating insights and visualizations.
- `query`: The agent primarily generates and executes SQL queries.
- `script`: The agent writes and executes scripts (e.g., for data cleaning).

Example with a specific mode:
```bash
uv run kai-agent run "Analyze customer churn patterns" --db my_postgres_db --mode analysis
```

### 4. Starting the Temporal Worker

The Temporal worker is required for certain asynchronous background tasks.
```bash
uv run kai-agent worker
```

## Example Workflows

### Workflow 1: Quick Analysis with the CLI

This workflow is ideal for developers and analysts who want to quickly get insights from their data.

```bash
# 1. List available database connections
uv run kai-agent list-connections

# 2. Start an interactive session with your desired database
uv run kai-agent interactive --db your_db_id

# 3. Ask analytical questions within the interactive session
> What's the distribution of orders by status?
> Show the monthly revenue trend for the last year.
> Identify the top 5 products by profit margin.
```

### Workflow 2: Integrating with Applications via API

This workflow is for developers building KAI into their own applications.

```bash
# 1. Create a database connection via API
curl -X POST http://localhost:8015/api/v1/database-connections -d '{...}'

# 2. Trigger an autonomous agent task via API
curl -X POST http://localhost:8015/api/v2/agent/execute -d '{
  "prompt": "Create a dashboard showing total revenue, top products, and monthly trends.",
  "db_connection_id": "your_db_id"
}'

# 3. The API will stream back events, including the final result,
# which could be a dashboard configuration, a chart, or a natural language answer.
```

## Next Steps

### Explore Features

1.  **Learn the CLI**
    ```bash
    uv run kai-agent --help
    ```

2.  **Try Different LLM Providers**
    - Google Gemini: Set `CHAT_FAMILY=google`
    - Local with Ollama: Set `CHAT_FAMILY=ollama`
    - OpenRouter: Set `CHAT_FAMILY=openrouter`

3.  **Enable Long-term Memory**
    ```bash
    # In .env
    MEMORY_BACKEND=letta  # or typesense (default)
    ```

4.  **Set Up the Web UI**
    ```bash
    cd ui
    npm install
    npm run dev
    ```

### Learn More

- **[Architecture Documentation](../ARCHITECTURE.md)** - Understand system design
- **[API Reference](apis/README.md)** - Complete API documentation
- **[Tutorials](tutorials/)** - Step-by-step guides
- **[Contributing](../CONTRIBUTING.md)** - Join development

### Common Tasks

**Add More Databases**
```bash
# This should be done via the API as shown in the "First Steps" section.
```

**Update Table Descriptions**
```bash
# Refresh specific table
curl -X POST http://localhost:8015/api/v1/table-descriptions/refresh \
  -H "Content-Type: application/json" \
  -d '{"db_connection_id": "your-id", "table_names": ["customers"]}'
```

**Create Custom Instructions**
```bash
curl -X POST http://localhost:8015/api/v1/instructions \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "Always use UTC timezone for date comparisons",
    "db_connection_id": "your-id"
  }'
```

## Troubleshooting

If you encounter issues, see:
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Common problems and solutions
- **[GitHub Issues](https://github.com/your-org/kai/issues)** - Report bugs

## Getting Help

- **Documentation**: Check docs in `docs/` directory
- **API Docs**: http://localhost:8015/docs
- **GitHub Discussions**: Ask questions
- **Examples**: See `docs/tutorials/` for more examples

---

**Ready to build?** Start with `uv run kai-agent interactive --db your_db` and explore!
