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
uv run kai-agent --help

# Database management
uv run kai-agent create-connection "postgresql://user:pass@host:5432/db" -a mydb
uv run kai-agent scan-all mydb -d  # Scan with AI descriptions

# Interactive session
uv run kai-agent interactive --db mydb

# One-shot analysis
uv run kai-agent run "Analyze sales by region" --db mydb
```

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

### LangGraph Graphs

Located in `app/langgraph_server/graphs.py`:
- `session_graph` - Multi-turn conversational sessions with routing
- `sql_agent_graph` - ReAct agent for SQL generation with tools

Configuration in `langgraph.json`.

### Key Patterns

- **Storage**: Typesense wrapper at `app/data/db/storage.py` handles vector search and document storage
- **Settings**: `app/server/config.py` uses `pydantic_settings.BaseSettings` with `@lru_cache` singleton
- **LLM Adapters**: `app/utils/model/` provides unified interface across providers
- **API Registration**: Routes added via `router.add_api_route()` in `app/api/__init__.py`

## Environment Setup

Required `.env` variables:
- `GOOGLE_API_KEY` or `OPENAI_API_KEY` - LLM provider key
- `CHAT_FAMILY` - Provider: `google`, `openai`, `ollama`, `openrouter`
- `CHAT_MODEL` - Model name (e.g., `gemini-2.0-flash`, `gpt-4o-mini`)
- `ENCRYPT_KEY` - Fernet key for credential encryption
- `TYPESENSE_HOST` - Use `localhost` for local dev, `typesense` for Docker

Generate encryption key:
```bash
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Code Style

- Uses `ruff` for linting and `black` for formatting
- Python 3.11+ required
- Async code uses native `async/await` with `asyncio`
- Type hints expected throughout
