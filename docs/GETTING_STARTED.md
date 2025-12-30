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

1. **Python 3.11+**
   ```bash
   python --version  # Should be 3.11 or higher
   ```
   [Download Python](https://www.python.org/downloads/)

2. **uv Package Manager**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   [uv Documentation](https://github.com/astral-sh/uv)

3. **Docker & Docker Compose**
   ```bash
   docker --version
   docker compose version
   ```
   [Install Docker](https://docs.docker.com/get-docker/)

4. **Git**
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

Check that all services are running:

```bash
# API health check
curl http://localhost:8015/health

# Typesense health
curl http://localhost:8108/health

# View API documentation
open http://localhost:8015/docs
```

### 2. Create Your First Database Connection

Using the API:

```bash
curl -X POST http://localhost:8015/api/v1/database-connections \
  -H "Content-Type: application/json" \
  -d '{
    "alias": "my_postgres",
    "connection_uri": "postgresql://user:pass@localhost:5432/mydb",
    "use_ssh": false
  }'
```

Or using the CLI:

```bash
uv run kai-agent create-connection \
  "postgresql://user:pass@localhost:5432/mydb" \
  -a my_postgres
```

### 3. Scan Database Schema

Let KAI learn about your database structure:

```bash
# Scan all tables
uv run kai-agent scan-all my_postgres

# With AI-generated descriptions (recommended)
uv run kai-agent scan-all my_postgres -d
```

This analyzes your tables and generates descriptions to help the AI understand your data.

### 4. Your First Query

#### Via API

```bash
curl -X POST http://localhost:8015/api/v1/prompts/sql-generations/nl-generations \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_text": "Show me the top 10 customers by revenue",
    "db_connection_id": "your-connection-id"
  }'
```

#### Via CLI (Interactive Mode)

```bash
uv run kai-agent interactive --db my_postgres
```

Then ask questions naturally:
```
> Show me total sales by month
> Which products are most popular?
> Forecast sales for next 30 days
```

#### Via CLI (One-Shot)

```bash
uv run kai-agent run "Show top 10 customers by revenue" --db my_postgres
```

### 5. View Results

The response includes:
- **Generated SQL** - The query KAI created
- **Results** - Query execution results
- **Natural Language** - Human-readable explanation

Example response:
```json
{
  "sql": "SELECT customer_name, SUM(amount) as revenue FROM orders GROUP BY customer_name ORDER BY revenue DESC LIMIT 10",
  "results": [...],
  "explanation": "Here are the top 10 customers ranked by total revenue..."
}
```

## Example Workflows

### Workflow 1: Database Analysis

```bash
# 1. Connect to database
uv run kai-agent create-connection \
  "postgresql://localhost:5432/sales" \
  -a sales_db

# 2. Scan schema
uv run kai-agent scan-all sales_db -d

# 3. Ask analytical questions
uv run kai-agent run "What's the distribution of orders by status?" --db sales_db
uv run kai-agent run "Show monthly revenue trend" --db sales_db
uv run kai-agent run "Identify top 5 products by profit margin" --db sales_db
```

### Workflow 2: Dashboard Creation

Using the API to create a dashboard from natural language:

```bash
curl -X POST http://localhost:8015/api/v1/dashboards \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Overview",
    "description": "Create a dashboard showing total revenue, top products, monthly trends, and customer distribution",
    "db_connection_id": "your-connection-id"
  }'
```

### Workflow 3: Advanced Analytics

```bash
# Time series forecasting
curl -X POST http://localhost:8015/api/v1/analytics/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "sql_generation_id": "your-sql-id",
    "periods": 30,
    "confidence_level": 0.95
  }'

# Anomaly detection
curl -X POST http://localhost:8015/api/v1/analytics/detect-anomalies \
  -H "Content-Type: application/json" \
  -d '{
    "sql_generation_id": "your-sql-id",
    "sensitivity": 0.05
  }'

# Statistical analysis
curl -X POST http://localhost:8015/api/v1/analytics/statistical-summary \
  -H "Content-Type: application/json" \
  -d '{
    "sql_generation_id": "your-sql-id"
  }'
```

## Next Steps

### Explore Features

1. **Learn the CLI**
   ```bash
   uv run kai-agent --help
   ```

2. **Try Different LLM Providers**
   - Google Gemini: Set `CHAT_FAMILY=google`
   - Local with Ollama: Set `CHAT_FAMILY=ollama`
   - OpenRouter: Set `CHAT_FAMILY=openrouter`

3. **Enable Long-term Memory**
   ```bash
   # In .env
   MEMORY_BACKEND=letta  # or typesense (default)
   ```

4. **Set Up the Web UI**
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
uv run kai-agent create-connection \
  "mysql://user:pass@localhost:3306/crm" \
  -a crm_db
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

**Ready to build?** Start with `uv run kai-agent interactive --db your_db` and explore! 🚀
