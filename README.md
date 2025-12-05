# KAI

<p align="center">
    <b>Knowledge Agent for Intelligence Query</b> <br />
</p>

**KAI (Knowledge Agent for Intelligence Query)** is an AI-powered agent that lets you query and analyze your database using natural language. Simply ask questions in plain natural language—KAI handles the rest.

No SQL expertise required. Just connect your database and start asking.

## Table of Contents

- [Key Features](#key-features)
- [Architecture Overview](#architecture-overview)
- [Quickstart](#quickstart)
- [CLI Reference](#cli-reference)
- [Environment Variables](#environment)
- [API Overview](#api-overview)
- [Skills System](#skills-system)
- [LangGraph Deployment](#langgraph-server-deployment)
- [Development](#development)

## Key Features

| Feature | Description |
|---------|-------------|
| **Natural Language Querying** | Query databases in plain English or Indonesian—no SQL required |
| **Autonomous Agents** | Multi-step analysis with 40+ tools for SQL, analysis, and reporting |
| **Multi-Provider LLM** | OpenAI, Google Gemini, Ollama (local), OpenRouter support |
| **Long-Term Memory** | Persistent memory with Typesense or Letta backends |
| **Skills System** | Reusable analysis patterns as Markdown with semantic search |
| **Business Glossary** | Define metrics and KPIs with SQL for consistent analytics |
| **RAG Document Search** | Hybrid vector + full-text search via Typesense |
| **Interactive Sessions** | LangGraph-powered conversations with streaming |
| **MCP Integration** | Connect external tools via Model Context Protocol |
| **Multi-Database** | PostgreSQL, MySQL, SQLite, BigQuery support |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FastAPI Server (:8015)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐  │
│  │  REST API   │  │  Sessions   │  │  KAI-Agent  │  │  MCP Client   │  │
│  │  (40+ eps)  │  │ (LangGraph) │  │ (DeepAgents)│  │  (External)   │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └───────┬───────┘  │
│         │                │                │                  │          │
│  ┌──────┴────────────────┴────────────────┴──────────────────┴──────┐  │
│  │                        Core Modules                               │  │
│  ├───────────────────────────────────────────────────────────────────┤  │
│  │ SQL Gen │ Analysis │ RAG │ Memory │ Skills │ Glossary │ Context  │  │
│  └──────────────────────────────────┬────────────────────────────────┘  │
│                                     │                                   │
└─────────────────────────────────────┼───────────────────────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
    ┌─────────▼─────────┐   ┌─────────▼─────────┐   ┌─────────▼─────────┐
    │     Typesense     │   │   Your Database   │   │   LLM Providers   │
    │  (Vector + Search)│   │ (PG/MySQL/SQLite) │   │ (OpenAI/Gemini/..)│
    └───────────────────┘   └───────────────────┘   └───────────────────┘
```

**Core Modules:**

| Module | Purpose |
|--------|---------|
| `session` | LangGraph-based interactive query sessions with streaming |
| `autonomous_agent` | Fully autonomous analysis via DeepAgents |
| `sql_generation` | Natural language to SQL conversion |
| `analysis` | Query execution and data analysis |
| `memory` | Long-term persistent memory (Typesense/Letta) |
| `skill` | Reusable analysis patterns with semantic search |
| `business_glossary` | Metric definitions and lookups |
| `rag` | Document embedding and semantic search |
| `context_store` | Rich context storage for sessions |
| `mcp` | External tool integration via MCP |

## Quickstart

### Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** - Fast Python package manager
- **Docker** - For running Typesense

### Setup

```bash
# Clone and enter the project
git clone <repo-url> && cd KAI

# Install dependencies
uv sync

# Copy environment template
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
GOOGLE_API_KEY=AIza...         # Required
CHAT_FAMILY=google
CHAT_MODEL=gemini-2.0-flash
EMBEDDING_FAMILY=google
EMBEDDING_MODEL=text-embedding-004

# Generate encryption key (paste output into .env)
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Run

```bash
# Start Typesense (required for storage)
docker compose up typesense -d

# Start KAI server
uv run python -m app.main
```

Visit http://localhost:8015/docs to access the API.

### Using the CLI

```bash
# List available commands
uv run kai-agent --help

# Add a PostgreSQL database connection (only needed once)
uv run kai-agent create-connection "postgresql://user:pass@localhost:5432/mydb" -a mypg

# Scan the database schema with AI-generated descriptions
uv run kai-agent scan-all mypg -d

# Start interactive analysis session
uv run kai-agent interactive --db mypg
```

### Docker Deployment (Alternative)

For full containerized deployment:

```bash
docker compose up -d
```

This starts both Typesense and KAI engine. Data persists in `./app/data/dbdata`.

## CLI Reference

KAI includes a powerful CLI for database management and autonomous analysis.

### Core Commands

| Command | Description |
|---------|-------------|
| `run <prompt> --db <id>` | Execute a one-shot analysis |
| `interactive --db <id>` | Start interactive chat session |
| `create-connection <uri> -a <alias>` | Add a database connection |
| `list-connections` | List all connections |
| `scan-all <conn_id> -d` | Scan tables with AI descriptions |

### Database Management

```bash
# Test a connection string
uv run kai-agent test-connection "postgresql://user:pass@host:5432/db"

# Create connection with specific schemas
uv run kai-agent create-connection "postgresql://..." -a mydb -s public -s analytics

# View connection details
uv run kai-agent show-connection <connection_id>

# Refresh and scan tables
uv run kai-agent scan-all <connection_id> -d
```

### Business Glossary

```bash
# Add a metric definition
uv run kai-agent add-glossary <conn_id> --metric "Revenue" --sql "SELECT SUM(amount) FROM orders"

# List all glossary entries
uv run kai-agent list-glossaries <conn_id>
```

### Custom Instructions

```bash
# Add a default instruction
uv run kai-agent add-instruction <conn_id> -c "Always" -r "Format currency with $" --default

# List instructions
uv run kai-agent list-instructions <conn_id>
```

### Skills Management

```bash
# Discover skills from directory
uv run kai-agent discover-skills <conn_id> --path ./.skills

# List and search skills
uv run kai-agent list-skills <conn_id>
uv run kai-agent search-skills <conn_id> "revenue analysis"
```

### Memory Management

```bash
# Store a memory
uv run kai-agent add-memory <conn_id> user_preferences date_format "Use YYYY-MM-DD"

# List and search memories
uv run kai-agent list-memories <conn_id>
uv run kai-agent search-memories <conn_id> "date format"
```

### Session Management

```bash
# List all sessions
uv run kai-agent list-sessions

# Export session to file
uv run kai-agent export-session <session_id> -f markdown -o chat.md
```

### Example Session

```bash
$ uv run kai-agent interactive --db mydb

KAI> What tables contain sales data?
# Agent explores schema...

KAI> Analyze sales performance by region for Q4
# Agent generates SQL, executes, analyzes results...

KAI> Create an Excel report with monthly breakdown
# Agent generates Excel file...

KAI> exit
```

Sessions are automatically persisted with human-readable IDs (e.g., `brave-falcon-42`). Resume anytime:

```bash
uv run kai-agent interactive --db mydb --session brave-falcon-42
```

## Environment

KAI relies on several environment variables to configure and control its behavior. Below is a detailed description of each environment variable used in the project:

```bash
# Server Configuration
APP_HOST=0.0.0.0
APP_PORT=8015
APP_ENVIRONMENT=LOCAL
APP_ENABLE_HOT_RELOAD=0

# Typesense Configuration
TYPESENSE_API_KEY=kai_typesense
TYPESENSE_HOST=typesense   # Use 'localhost' for local dev
TYPESENSE_PORT=8108
TYPESENSE_PROTOCOL=HTTP
TYPESENSE_TIMEOUT=2

# LLM Provider Configuration
CHAT_FAMILY=google         # openai, google, ollama, openrouter, model_garden
CHAT_MODEL=gemini-2.0-flash
EMBEDDING_FAMILY=google
EMBEDDING_MODEL=text-embedding-004
EMBEDDING_DIMENSIONS=768

# API Keys (set based on your CHAT_FAMILY)
OPENAI_API_KEY=
GOOGLE_API_KEY=            # Required for google family
OLLAMA_API_BASE=http://localhost:11434
OPENROUTER_API_KEY=
OPENROUTER_API_BASE=https://openrouter.ai/api/v1

# Agent Configuration
AGENT_MAX_ITERATIONS=20
AGENT_LANGUAGE=en          # en or id (Indonesian)
DH_ENGINE_TIMEOUT=150
SQL_EXECUTION_TIMEOUT=60
UPPER_LIMIT_QUERY_RETURN_ROWS=50
ENCRYPT_KEY=               # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Long-term Memory Configuration
MEMORY_BACKEND=typesense   # typesense or letta
LETTA_API_KEY=
LETTA_BASE_URL=

# Automatic Learning (Agentic-Learning SDK)
ENABLE_AUTO_LEARNING=false
AUTO_LEARNING_CAPTURE_ONLY=false
AUTO_LEARNING_MEMORY_BLOCKS=human,context,user_preferences,corrections
AUTO_LEARNING_SHARED_MEMORY_BLOCK=shared_knowledge

# MCP Integration
MCP_ENABLED=false
MCP_SERVERS_CONFIG=mcp-servers.json
```

### **Server Configuration**

* **`APP_HOST`**\
  _Description:_ The host address on which the application will run.\
  _Example:_ `"0.0.0.0"`
* **`APP_PORT`**\
  _Description:_ The port number on which the application will listen for incoming requests.\
  _Example:_ `"8015"`
* **`APP_ENABLE_HOT_RELOAD`**\
  _Description:_ Enables or disables hot reloading of the application. Set to `1` to enable hot reload, or `0` to disable it.\
  _Example:_ `"0"`

### **Typesense Configuration**

* **`TYPESENSE_API_KEY`**\
  _Description:_ The API key used to authenticate requests to the Typesense server.\
  _Example:_ `"kai_typesense"`
* **`TYPESENSE_HOST`**\
  _Description:_ The host address of the Typesense server.\
  _Example:_ `"localhost"`
* **`TYPESENSE_PORT`**\
  _Description:_ The port number on which the Typesense server listens.\
  _Example:_ `"8108"`
* **`TYPESENSE_PROTOCOL`**\
  _Description:_ The protocol used to communicate with the Typesense server.\
  _Example:_ `"HTTP"`
* **`TYPESENSE_TIMEOUT`**\
  _Description:_ The timeout value (in seconds) for requests to the Typesense server.\
  _Example:_ `"2"`

### **LLM Provider Configuration**

KAI supports multiple LLM providers. Configure your preferred provider using these variables:

* **`CHAT_FAMILY`**\
  _Description:_ The LLM provider family for chat models.\
  _Options:_ `openai`, `google`, `ollama`, `openrouter`, `model_garden`\
  _Example:_ `"openai"`

* **`CHAT_MODEL`**\
  _Description:_ The model used for chat and natural language understanding tasks.\
  _Example:_ `"gpt-4o-mini"` (OpenAI), `"gemini-2.0-flash"` (Google), `"llama3"` (Ollama)

* **`EMBEDDING_FAMILY`**\
  _Description:_ The LLM provider family for embedding models.\
  _Options:_ `openai`, `google`, `ollama`\
  _Example:_ `"openai"`

* **`EMBEDDING_MODEL`**\
  _Description:_ The model used for generating embeddings from text data.\
  _Example:_ `"text-embedding-003-small"`

* **`EMBEDDING_DIMENSIONS`**\
  _Description:_ The dimension size for embeddings (must match the model).\
  _Example:_ `768`

### **API Keys**

Set the API key(s) for your chosen LLM provider(s):

* **`OPENAI_API_KEY`**\
  _Description:_ API key for OpenAI services. Required when `CHAT_FAMILY=openai`.\
  _Example:_ `"sk-..."`

* **`GOOGLE_API_KEY`**\
  _Description:_ API key for Google Gemini. Required when `CHAT_FAMILY=google`.\
  _Example:_ `"AIza..."`

* **`OLLAMA_API_BASE`**\
  _Description:_ Base URL for Ollama API (local models).\
  _Example:_ `"http://localhost:11434"`

* **`OPENROUTER_API_KEY`** / **`OPENROUTER_API_BASE`**\
  _Description:_ API key and base URL for OpenRouter (multi-provider access).\
  _Example:_ `"sk-or-..."`, `"https://openrouter.ai/api/v1"`

### **Agent Configuration**

* **`AGENT_MAX_ITERATIONS`**\
  _Description:_ The maximum number of iterations the agent will perform. This is useful for controlling resource usage.\
  _Example:_ `20`

* **`AGENT_LANGUAGE`**\
  _Description:_ Language for agent responses and prompts.\
  _Options:_ `"en"` (English), `"id"` (Indonesian)\
  _Example:_ `"en"`
* **`DH_ENGINE_TIMEOUT`**\
  _Description:_ The timeout value (in seconds) for the engine to return a response.\
  _Example:_ `"150"`
* **`SQL_EXECUTION_TIMEOUT`**\
  _Description:_ The timeout (in seconds) for executing SQL queries. This is important for recovering from errors during execution.\
  _Example:_ `"60"`
* **`UPPER_LIMIT_QUERY_RETURN_ROWS`**\
  _Description:_ The upper limit on the number of rows returned from the query engine. This acts similarly to the `LIMIT` clause in SQL.\
  _Example:_ `"50"`
* **`ENCRYPT_KEY`**\
  _Description:_ The encryption key used for securely storing database connection data in Typesense. Use Fernet Generated key for this.\
  _Example:_ `"f0KVMZHZPgdMStBmVIn2XD049e6Mun7ZEDhf1W7MRnw="`

### **Long-Term Memory Configuration**

KAI supports multiple backends for long-term memory storage. By default, it uses TypeSense, but you can optionally use Letta AI for more sophisticated memory management.

* **`MEMORY_BACKEND`**\
  _Description:_ The backend to use for long-term memory storage. Options are `"typesense"` (default) or `"letta"`.\
  _Example:_ `"typesense"`

* **`LETTA_API_KEY`**\
  _Description:_ The API key for Letta AI services. Required when `MEMORY_BACKEND` is set to `"letta"`.\
  _Example:_ `""` _(To be provided)_

* **`LETTA_BASE_URL`**\
  _Description:_ Optional base URL for self-hosted Letta instances. Leave empty to use the default Letta cloud service.\
  _Example:_ `""` _(Optional)_

### **Automatic Learning (Agentic-Learning SDK)**

KAI can optionally use Letta's agentic-learning SDK for automatic memory injection and conversation capture. When enabled, memory is automatically injected into LLM calls at the SDK level, and conversations are captured for future learning.

* **`ENABLE_AUTO_LEARNING`**\
  _Description:_ Enable automatic memory learning via agentic-learning SDK. When enabled, memory is automatically injected into LLM calls and conversations are captured.\
  _Default:_ `False`

* **`AUTO_LEARNING_CAPTURE_ONLY`**\
  _Description:_ When True, captures conversations without injecting memory (useful for gradual rollout).\
  _Default:_ `False`

* **`AUTO_LEARNING_MEMORY_BLOCKS`**\
  _Description:_ Comma-separated list of memory block labels to inject for session-specific memory.\
  _Default:_ `"human,context,user_preferences,corrections"`

* **`AUTO_LEARNING_SHARED_MEMORY_BLOCK`**\
  _Description:_ Shared memory block visible across all sessions (e.g., business facts, data insights).\
  _Default:_ `"shared_knowledge"`

**Configuration Matrix:**

| ENABLE_AUTO_LEARNING | LETTA_API_KEY | Behavior |
|---------------------|---------------|----------|
| False | Any | Manual memory (existing behavior) |
| True | Not set | Falls back to manual memory with warning |
| True | Set | Automatic learning via agentic-learning |

### **MCP (Model Context Protocol) Configuration**

KAI supports the Model Context Protocol for integrating external tools and services into agents.

* **`MCP_ENABLED`**\
  _Description:_ Enable MCP integration to dynamically load tools from external MCP servers.\
  _Default:_ `false`

* **`MCP_SERVERS_CONFIG`**\
  _Description:_ Path to MCP servers configuration file.\
  _Example:_ `"mcp-servers.json"`

**Example `mcp-servers.json`:**

```json
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-filesystem", "./data"]
    },
    "github": {
      "type": "streamable_http",
      "url": "http://localhost:3001/mcp"
    }
  }
}
```

**Supported Transport Types:**
- `stdio` - Launch MCP server as subprocess
- `streamable_http` - Connect to HTTP-based MCP server
- `sse` - Connect via Server-Sent Events

## API Overview

KAI exposes a comprehensive REST API on port 8015. Access the interactive documentation at `/docs` (Swagger UI).

### Key Endpoint Groups

| Endpoint Group | Base Path | Description |
|----------------|-----------|-------------|
| Database Connections | `/api/v1/database-connections` | Manage database connections |
| Table Descriptions | `/api/v1/table-descriptions` | Schema discovery and description |
| SQL Generation | `/api/v1/sql-generations` | Natural language to SQL |
| Analysis | `/api/v1/analyses` | Query execution and analysis |
| Business Glossary | `/api/v1/business-glossaries` | Metric definitions |
| Instructions | `/api/v1/instructions` | Custom query instructions |
| Context Store | `/api/v1/context-stores` | Rich context storage |
| Sessions | `/api/v1/sessions` | Interactive query sessions |
| Agent Sessions | `/api/v1/agent-sessions` | Autonomous agent tasks |
| Documents | `/api/v1/documents` | RAG document management |

### Common Workflows

**1. Set up a database connection:**
```bash
curl -X POST http://localhost:8015/api/v1/database-connections \
  -H "Content-Type: application/json" \
  -d '{"alias": "prod_db", "driver": "postgresql", "host": "...", "database": "..."}'
```

**2. Scan and describe tables:**
```bash
curl -X POST http://localhost:8015/api/v1/table-descriptions/sync-schemas \
  -d '{"db_connection_id": "<connection_id>"}'
```

**3. Generate SQL from natural language:**
```bash
curl -X POST http://localhost:8015/api/v1/sql-generations \
  -d '{"prompt": "Show top 10 customers by revenue", "db_connection_id": "<id>"}'
```

**4. Start an interactive session:**
```bash
curl -X POST http://localhost:8015/api/v1/sessions \
  -d '{"db_connection_id": "<id>"}'
```

## Skills System

Skills are reusable analysis patterns stored as Markdown files. They encode domain expertise and can be discovered and composed by agents.

### Skill Structure

Skills are stored in `.skills/` directories with the following format:

```markdown
---
name: Revenue Analysis
category: financial
tags: [revenue, analysis, trends]
description: Analyze revenue patterns and trends
version: 1.0.0
---

# Revenue Analysis Skill

## Overview
This skill provides patterns for analyzing revenue data.

## SQL Patterns
...

## Analysis Steps
...
```

### Managing Skills

**Via CLI:**
```bash
# Discover skills from a directory
uv run kai-agent discover-skills <connection_id> --path ./.skills

# List all skills
uv run kai-agent list-skills <connection_id>

# Search skills semantically
uv run kai-agent search-skills <connection_id> "cohort analysis"
```

**Via API:**
```bash
# List skills
curl http://localhost:8015/api/v1/skills?db_connection_id=<id>

# Search skills semantically
curl http://localhost:8015/api/v1/skills/search?query=revenue&db_connection_id=<id>
```

Agents automatically discover and use relevant skills during analysis based on the user's query.

## LangGraph Server Deployment

KAI-Agent's session and SQL generation capabilities are built on LangGraph and can be deployed to:
- **Self-hosted LangGraph server** using Docker
- **LangGraph Platform** (cloud) for managed hosting
- **LangGraph Studio** for development and debugging

### Available Graphs

KAI includes deployable LangGraph graphs in `app/langgraph_server/`:

| Graph | Entry Point | Description |
|-------|-------------|-------------|
| Session Graph | `app.langgraph_server:session_graph` | Multi-turn conversational sessions with context management |
| SQL Agent | `app.langgraph_server:sql_agent_graph` | Tool-using ReAct agent for SQL generation |

### Graph Architecture

**Session Graph Flow:**
```
START → route_query → [process_database | process_reasoning] → save_response → END
```

**SQL Agent Pattern:**
```
START → agent → conditional(tools|END) → tools → agent (loop)
```

### Self-Hosted Deployment (Docker)

Deploy KAI graphs to a self-hosted LangGraph server using Docker:

```bash
# Build the LangGraph container
docker build -f Dockerfile.langgraph -t kai-langgraph .

# Run with Docker Compose (includes Typesense + Redis)
docker compose -f docker-compose.langgraph.yml up -d

# Access LangGraph Studio
open http://localhost:8123
```

**Services started:**
- **LangGraph Server**: http://localhost:8123 (Studio UI + API)
- **Typesense**: http://localhost:8108 (vector search, checkpointing)
- **Redis**: localhost:6379 (state persistence)

### Quick Start with langgraph CLI

For local development without Docker:

```bash
# Install dependencies
uv sync

# Start LangGraph development server
uv run langgraph dev

# Or run in production mode
uv run langgraph up --host 0.0.0.0 --port 8123
```

### Invoking Graphs via API

Once the server is running, invoke graphs via the LangGraph API:

```bash
# Create a new thread (session)
curl -X POST http://localhost:8123/threads \
  -H "Content-Type: application/json" \
  -d '{}'

# Run the session graph
curl -X POST http://localhost:8123/threads/{thread_id}/runs \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "session",
    "input": {
      "current_query": "What tables contain customer data?",
      "db_connection_id": "your-connection-id"
    }
  }'

# Stream responses
curl -X POST http://localhost:8123/threads/{thread_id}/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "sql_agent",
    "input": {
      "messages": [{"role": "user", "content": "Show top 10 customers by revenue"}],
      "question": "Show top 10 customers by revenue",
      "dialect": "postgresql"
    }
  }'
```

### Using LangGraph SDK

```python
from langgraph_sdk import get_client

# Connect to self-hosted server
client = get_client(url="http://localhost:8123")

# List available graphs
assistants = await client.assistants.list()

# Create a thread
thread = await client.threads.create()

# Run the session graph
result = await client.runs.create(
    thread_id=thread["thread_id"],
    assistant_id="session",
    input={
        "current_query": "Analyze monthly revenue trends",
        "db_connection_id": "prod_db"
    }
)

# Stream responses
async for event in client.runs.stream(
    thread_id=thread["thread_id"],
    assistant_id="sql_agent",
    input={"messages": [{"role": "user", "content": "List all tables"}]}
):
    print(event)
```

### LangGraph Configuration

The `langgraph.json` file configures which graphs are exposed:

```json
{
  "python_version": "3.11",
  "dependencies": ["."],
  "graphs": {
    "session": "./app/langgraph_server:session_graph",
    "sql_agent": "./app/langgraph_server:sql_agent_graph"
  },
  "env": ".env"
}
```

### Deploy to LangGraph Platform (Cloud)

For managed cloud deployment:

```bash
# Login to LangGraph Platform
uv run langgraph auth login

# Deploy to cloud
uv run langgraph deploy
```

### LangGraph Studio

LangGraph Studio provides visual debugging:

1. **Graph Visualization** - See execution flow in real-time
2. **State Inspection** - Examine state at each node
3. **Checkpoint History** - Browse conversation threads
4. **Thread Management** - Manage active sessions

Access Studio at http://localhost:8123 after starting the server.

### State Persistence Options

KAI supports multiple checkpointing strategies:

| Backend | Use Case | Configuration |
|---------|----------|---------------|
| MemorySaver | Development/testing | Default (no config needed) |
| Redis | Production self-hosted | `LANGGRAPH_REDIS_URL=redis://...` |
| Typesense | KAI-native persistence | Use `get_session_graph_with_typesense()` |
| LangGraph Platform | Cloud deployment | Automatic |

```python
from app.langgraph_server.graphs import (
    create_session_graph,
    get_session_graph_with_typesense
)

# Memory-based (default)
graph = create_session_graph()

# Typesense-based (production)
graph = get_session_graph_with_typesense()
```

### Environment Variables for LangGraph

```bash
# LangGraph Server
LANGGRAPH_HOST=0.0.0.0
LANGGRAPH_PORT=8123
LANGGRAPH_REDIS_URL=redis://localhost:6379  # Optional: persistent state

# LangSmith Tracing (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langchain-api-key
LANGCHAIN_PROJECT=kai-langgraph
```

### Architecture: LangGraph Server + KAI API

For full functionality, run both services:

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
┌─────────▼─────────┐         ┌───────────▼───────────┐
│  LangGraph Server │         │     KAI FastAPI       │
│    (:8123)        │         │       (:8015)         │
│                   │         │                       │
│ • Session Graph   │◄───────►│ • Database Connections│
│ • SQL Agent       │         │ • Table Descriptions  │
│ • Streaming       │         │ • Business Glossary   │
│ • State Mgmt      │         │ • Skills & RAG        │
└─────────┬─────────┘         └───────────┬───────────┘
          │                               │
          └───────────────┬───────────────┘
                          │
              ┌───────────▼───────────┐
              │      Typesense        │
              │       (:8108)         │
              │                       │
              │ • Vector Search       │
              │ • Checkpointing       │
              │ • Schema Storage      │
              └───────────────────────┘
```

## Development

### Running Tests

```bash
uv run pytest                          # Run all tests
uv run pytest --cov=app                # With coverage
uv run pytest tests/modules/session/   # Specific module
```

### Project Structure

```
KAI/
├── app/
│   ├── main.py              # FastAPI application entry
│   ├── server/              # Server configuration
│   ├── api/                 # REST API routes
│   ├── modules/             # Feature modules
│   │   ├── autonomous_agent/  # KAI-Agent CLI & service
│   │   ├── session/           # Interactive sessions
│   │   ├── sql_generation/    # NL-to-SQL
│   │   ├── analysis/          # Query analysis
│   │   ├── memory/            # Long-term memory
│   │   ├── skill/             # Skills system
│   │   ├── rag/               # Document search
│   │   └── ...
│   └── data/                # Database schemas
├── tests/                   # Test suite
├── docs/                    # Documentation
├── docker-compose.yml       # Container orchestration
└── pyproject.toml          # Dependencies
```

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](./LICENSE) file for details.