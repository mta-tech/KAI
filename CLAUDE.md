# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KAI (Knowledge Agent for Intelligence Query) is an AI-powered agent for natural language database querying and analysis. Built with FastAPI, LangGraph, and LangChain, it supports multiple LLM providers (OpenAI, Google Gemini, Ollama, OpenRouter).

## Development Commands

```bash
# Install dependencies
uv sync

# Run development server (port 8015)
uv run python -m app.main

# Run with hot reload
APP_ENABLE_HOT_RELOAD=1 uv run python -m app.main

# Start Typesense (required for storage)
docker compose up typesense -d

# Run LangGraph development server
uv run langgraph dev
```

## Docker Deployment

### LangGraph Server (Recommended for Production)

Build and run the LangGraph server with full stack (PostgreSQL, Redis, Typesense):

```bash
# Build the LangGraph container image
uv run langgraph build -t kai-langgraph:latest

# Start the full stack
docker compose -f docker-compose.langgraph.yml up -d
```

Services started:
- **LangGraph API**: http://localhost:8123 (graphs: `session`, `sql_agent`)
- **Typesense**: http://localhost:8108 (vector search)
- **PostgreSQL**: localhost:5433 (state persistence)
- **Redis**: localhost:6379 (streaming)

Health check: `curl http://localhost:8123/ok`

### Alternative: Manual Dockerfile Build

```bash
# Build using Dockerfile.langgraph directly
docker build -f Dockerfile.langgraph -t kai-langgraph .

# Run standalone (requires external Typesense/Redis/PostgreSQL)
docker run -p 8123:8123 --env-file .env kai-langgraph
```

### Typesense Only (Local Development)

```bash
# Start only Typesense for local development
docker compose up typesense -d
```

### Docker Network

The LangGraph stack uses `kai_langgraph_network` bridge network. Services connect via container names:
- `TYPESENSE_HOST=typesense`
- `REDIS_URI=redis://langgraph-redis:6379`
- `DATABASE_URI=postgres://postgres:postgres@langgraph-postgres:5432/postgres`

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/unit/test_deep_agent_adapter.py

# Run single test function
uv run pytest tests/unit/test_deep_agent_adapter.py::test_function_name

# Run specific module tests
uv run pytest tests/modules/session/
```

Tests require a running Typesense instance. The test suite uses `pytest-asyncio` with `asyncio_mode = auto`.

## CLI Commands

```bash
# List CLI commands
uv run kai --help

# Database management
uv run kai connection create "postgresql://user:pass@host:5432/db" -a mydb
uv run kai table scan-all mydb -d  # Scan with AI descriptions

# Interactive session
uv run kai query interactive --db mydb

# One-shot analysis
uv run kai query run "Analyze sales by region" --db mydb
```

CLI entry point: `app/modules/autonomous_agent/main.py` (registered as `kai` in pyproject.toml).

Command groups: `config`, `connection`, `table`, `query`, `session`, `dashboard`, `knowledge` (sub-groups: `glossary`, `instruction`, `skill`, `memory`), `mdl`.

## Architecture

### Layered Structure

```
app/
├── main.py                 # FastAPI entry point
├── server/                 # Config (pydantic_settings), middleware, errors
├── api/                    # REST API layer (40+ endpoints via router.add_api_route)
├── modules/                # Feature modules (service layer)
│   ├── autonomous_agent/   # CLI and DeepAgents-based analysis
│   ├── session/            # LangGraph-based interactive sessions
│   ├── sql_generation/     # NL-to-SQL conversion
│   ├── memory/             # Long-term memory (Typesense/Letta backends)
│   ├── skill/              # Markdown-based reusable analysis patterns
│   ├── analytics/          # Statistical analysis, forecasting, anomaly detection
│   ├── dashboard/          # Natural language dashboard creation
│   ├── visualization/      # Chart generation and theming
│   └── ...                 # Other domain modules
├── utils/                  # Shared utilities (LLM adapters, SQL tools, prompts)
├── data/db/                # Typesense storage wrapper and schemas
└── langgraph_server/       # LangGraph graphs (session_graph, sql_agent_graph)
```

### Module Pattern (Service-Repository-Model)

Each module follows a consistent pattern:
- **models/** - Pydantic BaseModel definitions
- **repositories/** - Data access via Storage (Typesense)
- **services/** - Business logic that uses repositories

When adding new modules, follow this pattern and add services to `app/api/__init__.py` for API exposure.

### LangGraph Graphs

Located in `app/langgraph_server/graphs.py`:
- `session_graph` - Multi-turn conversational sessions with routing
- `sql_agent_graph` - ReAct agent for SQL generation with tools

Configuration in `langgraph.json`. Graphs are exposed as `session` and `sql_agent` assistants.

### Key Patterns

- **Storage**: Typesense wrapper at `app/data/db/storage.py` handles vector search and document storage
- **Settings**: `app/server/config.py` uses `pydantic_settings.BaseSettings` with `@lru_cache` singleton via `get_settings()`
- **LLM Adapters**: `app/utils/model/` provides unified interface across providers (google, openai, ollama, openrouter)
- **API Registration**: Routes added via `router.add_api_route()` in `app/api/__init__.py`. The `API` class receives `Storage` and instantiates all services

### Adding New Features

1. Create module in `app/modules/<feature>/` with `models/`, `repositories/`, `services/` subdirs
2. Add service instantiation in `app/api/__init__.py`
3. Register routes in `_register_routes()` method
4. Add request/response models in `app/api/requests.py` and `app/api/responses.py`

## Environment Setup

Required `.env` variables:
- `GOOGLE_API_KEY` or `OPENAI_API_KEY` - LLM provider key
- `CHAT_FAMILY` - Provider: `google`, `openai`, `ollama`, `openrouter`
- `CHAT_MODEL` - Model name (e.g., `gemini-2.0-flash`, `gpt-4o-mini`)
- `ENCRYPT_KEY` - Fernet key for credential encryption
- `TYPESENSE_HOST` - Use `localhost` for local dev, `typesense` for Docker

Optional:
- `MEMORY_BACKEND` - `typesense` (default) or `letta` for long-term memory
- `MCP_ENABLED` - Enable Model Context Protocol integration
- `AGENT_LANGUAGE` - `en` (English) or `id` (Indonesian)

Generate encryption key:
```bash
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Code Style

- Uses `ruff` for linting and `black` for formatting
- Python 3.11+ required
- Async code uses native `async/await` with `asyncio`
- Type hints expected throughout
