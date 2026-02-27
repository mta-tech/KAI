# Installation

For local development without Docker.

## Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **uv** package manager ([Install uv](https://github.com/astral-sh/uv))

## Installation

### 1. Install dependencies

```bash
uv sync
```

### 2. Start Typesense (required)

```bash
docker compose up typesense -d
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your settings (use TYPESENSE_HOST=localhost for local dev)
```

### 4. Run the development server

```bash
uv run python -m app.main
```

Or with hot reload:

```bash
APP_ENABLE_HOT_RELOAD=1 uv run python -m app.main
```

### 5. Access the API

- API: http://localhost:8015
- API Docs: http://localhost:8015/docs

## LangGraph Development

For working with LangGraph agents:

```bash
uv run langgraph dev
```

This starts the LangGraph Studio interface for debugging agent workflows.
