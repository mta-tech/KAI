<div align="center">

# KAI
### Knowledge Agent for Intelligence Query

**Transform natural language into powerful data insights**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-00a393.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-purple.svg)](https://github.com/langchain-ai/langgraph)

[Documentation](https://mta-3.gitbook.io/kai) • [Getting Started](#quickstart) • [Contributing](CONTRIBUTING.md) • [Architecture](ARCHITECTURE.md)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Quickstart](#quickstart)
- [Development Setup](#development-setup)
- [Architecture](#architecture)
- [CLI Usage & Tutorial](#cli-usage)
- [Environment Configuration](#environment-configuration)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Overview

KAI (Knowledge Agent for Intelligence Query) is an **AI-powered data agent** that transforms how you interact with databases. Using natural language, you can:

- **Query databases** without writing SQL
- **Generate insights** with advanced analytics (forecasting, anomaly detection, statistical analysis)
- **Create dashboards** from natural language descriptions
- **Search documents** across large datasets
- **Remember context** across sessions with long-term memory

Built with **FastAPI**, **LangGraph**, and **LangChain**, KAI supports multiple LLM providers (OpenAI, Google Gemini, Ollama, OpenRouter) and integrates seamlessly with your existing data infrastructure.

## Key Features

<table>
<tr>
<td width="50%">

### Natural Language Querying
Ask questions in plain English—no SQL knowledge required. KAI translates your intent into optimized database queries.

### Advanced Analytics
- Statistical analysis (correlation, regression)
- Time series forecasting
- Anomaly detection
- Automated insights generation

### Dashboard Creation
Generate interactive dashboards from natural language descriptions using natural language.

</td>
<td width="50%">

### Long-term Memory
Persistent memory across sessions using Typesense or Letta backends to maintain context.

### Multi-LLM Support
Flexible LLM provider support:
- OpenAI (GPT-4, GPT-3.5)
- Google Gemini
- Ollama (local models)
- OpenRouter

### Production-Ready
- LangGraph-based agent architecture
- FastAPI for high-performance APIs
- Docker deployment support
- Comprehensive testing suite

</td>
</tr>
</table>

## Quickstart

Get KAI running in **5 minutes** with Docker Compose!

### Prerequisites

- **Docker** & **Docker Compose** ([Install Docker](https://docs.docker.com/get-docker/))
- **API Key** from OpenAI, Google, or other LLM provider

### Setup

**1. Clone the repository**

```bash
git clone https://github.com/your-org/kai.git
cd kai
```

**2. Create environment configuration**

```bash
cp .env.example .env
```

**3. Configure your LLM provider**

Edit `.env` and set your LLM configuration:

```bash
# Choose your LLM provider
CHAT_FAMILY=openai  # or: google, ollama, openrouter
CHAT_MODEL=gpt-4o-mini
OPENAI_API_KEY=your-api-key-here

# Required: Generate encryption key for database credentials
ENCRYPT_KEY=  # See below
```

**4. Generate encryption key**

```bash
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output and paste it as `ENCRYPT_KEY` in your `.env` file.

### Running with Docker

**Start all services:**

```bash
docker compose up -d
```

**Verify services are running:**

```bash
docker compose ps
```

Expected output:
```
NAME         IMAGE                      STATUS          PORTS
kai_engine   kai-kai_engine             Up 2 minutes    0.0.0.0:8015->8015/tcp
typesense    typesense/typesense:26.0   Up 2 minutes    0.0.0.0:8108->8108/tcp
```

**Access the application:**

- **API Documentation**: http://localhost:8015/docs
- **Typesense**: http://localhost:8108

**Test the API:**

```bash
curl http://localhost:8015/health
# Expected: {"status":"healthy"}
```

### Stopping Services

```bash
docker compose down
```

> **Note**: Data in `./app/data/dbdata` persists across restarts.

### Next Steps

Now that KAI is running, try the **[CLI Tutorial](#quick-cli-tutorial)** below to:
- Connect to your first database
- Run natural language queries
- Explore interactive analysis mode

---

## Development Setup

For local development without Docker:

### Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **uv** package manager ([Install uv](https://github.com/astral-sh/uv))

### Installation

**1. Install dependencies**

```bash
uv sync
```

**2. Start Typesense (required)**

```bash
docker compose up typesense -d
```

**3. Configure environment**

```bash
cp .env.example .env
# Edit .env with your settings (use TYPESENSE_HOST=localhost for local dev)
```

**4. Run the development server**

```bash
uv run python -m app.main
```

Or with hot reload:

```bash
APP_ENABLE_HOT_RELOAD=1 uv run python -m app.main
```

**5. Access the API**

- API: http://localhost:8015
- API Docs: http://localhost:8015/docs

### LangGraph Development

For working with LangGraph agents:

```bash
uv run langgraph dev
```

This starts the LangGraph Studio interface for debugging agent workflows.

---

## Architecture

KAI follows a modular, layered architecture:

```
┌─────────────────────────────────────────────────────┐
│                 FastAPI REST API                     │
│                  (app/api/)                          │
├─────────────────────────────────────────────────────┤
│                 Service Layer                        │
│  ┌──────────┬──────────┬──────────┬──────────┐     │
│  │ Session  │   SQL    │Analytics │Dashboard │     │
│  │  Module  │ Module   │  Module  │  Module  │     │
│  └──────────┴──────────┴──────────┴──────────┘     │
├─────────────────────────────────────────────────────┤
│             Repository Layer                         │
│        (Data Access via Typesense)                   │
├─────────────────────────────────────────────────────┤
│      LangGraph Agents & LLM Adapters                │
│   ┌────────────────┬──────────────────┐            │
│   │ Session Graph  │  SQL Agent Graph │            │
│   └────────────────┴──────────────────┘            │
├─────────────────────────────────────────────────────┤
│            Storage & External Services               │
│   ┌──────────┬───────────┬──────────────┐          │
│   │Typesense │  Database │  LLM APIs    │          │
│   │ (Vector) │ (User DB) │ (OpenAI/etc) │          │
│   └──────────┴───────────┴──────────────┘          │
└─────────────────────────────────────────────────────┘
```

### Key Components

- **FastAPI Server**: REST API with 40+ endpoints
- **LangGraph Agents**: Conversational session management and SQL generation
- **Service Modules**: Domain-specific business logic (analytics, dashboards, visualization)
- **Typesense**: Vector search and document storage
- **LLM Adapters**: Unified interface for multiple LLM providers

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Testing

Run the test suite:

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=app

# Specific module
uv run pytest tests/modules/session/

# Single test
uv run pytest tests/unit/test_deep_agent_adapter.py::test_function_name
```

> **Note**: Tests require a running Typesense instance. Start it with:
> ```bash
> docker compose up typesense -d
> ```

---

## CLI Usage

KAI provides a powerful command-line interface for database management and natural language analysis.

### Quick CLI Tutorial

Here's a complete workflow from connecting to your database to running queries:

**Step 1: Connect to your database**

```bash
# PostgreSQL
uv run kai-agent create-connection \
  "postgresql://user:password@localhost:5432/sales_db" \
  -a sales

# MySQL
uv run kai-agent create-connection \
  "mysql://user:password@localhost:3306/crm_db" \
  -a crm

# SQLite
uv run kai-agent create-connection \
  "sqlite:///path/to/database.db" \
  -a local_db
```

**Step 2: Scan your database schema**

Let KAI understand your database structure:

```bash
# Basic scan
uv run kai-agent scan-all sales

# With AI-generated descriptions (recommended)
uv run kai-agent scan-all sales -d
```

This analyzes your tables, columns, and relationships, generating descriptions to help the AI understand your data model.

**Step 3: Run your first query**

Try these example queries:

```bash
# One-shot query
uv run kai-agent run "Show total sales by month for 2024" --db sales

# Another example
uv run kai-agent run "List top 10 customers by revenue" --db sales

# Complex analytics
uv run kai-agent run "Analyze correlation between price and quantity sold" --db sales
```

**Step 4: Interactive mode**

For back-and-forth conversations:

```bash
uv run kai-agent interactive --db sales
```

Then ask questions naturally:

```
> Show me total revenue this quarter
> Which products are underperforming?
> Create a forecast for next month's sales
> What's the average order value by customer segment?
```

Type `exit` or press Ctrl+D to quit.

### Available Commands

```bash
# Connection management
kai-agent create-connection <uri> -a <alias>    # Add database
kai-agent list-connections                       # List all connections
kai-agent delete-connection <alias>              # Remove connection

# Schema management
kai-agent scan-all <alias>                       # Scan all tables
kai-agent scan-all <alias> -d                    # Scan with AI descriptions
kai-agent scan-table <alias> <table_name>        # Scan specific table

# Query execution
kai-agent run "<question>" --db <alias>          # One-shot query
kai-agent interactive --db <alias>               # Interactive session

# Help
kai-agent --help                                 # Show all commands
kai-agent <command> --help                       # Command-specific help
```

### Advanced CLI Features

**Custom instructions:**

```bash
# Add domain-specific guidance
uv run kai-agent add-instruction \
  "Always use fiscal year (July-June) for financial queries" \
  --db sales
```

**Export results:**

```bash
# Run query and save to CSV
uv run kai-agent run "Show monthly sales" --db sales --output sales.csv

# JSON format
uv run kai-agent run "Show top products" --db sales --format json
```

**Verbose mode:**

```bash
# See detailed SQL generation process
uv run kai-agent run "Show revenue" --db sales --verbose
```

---

## Environment Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `CHAT_FAMILY` | LLM provider | `openai`, `google`, `ollama` |
| `CHAT_MODEL` | Model name | `gpt-4o-mini`, `gemini-2.0-flash` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `ENCRYPT_KEY` | Fernet encryption key | Generate with command above |
| `TYPESENSE_HOST` | Typesense server host | `localhost` (dev), `typesense` (Docker) |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MEMORY_BACKEND` | Memory backend | `typesense` |
| `MCP_ENABLED` | Enable Model Context Protocol | `false` |
| `AGENT_LANGUAGE` | Agent language | `en` |
| `AGENT_MAX_ITERATIONS` | Max agent iterations | `20` |
| `DH_ENGINE_TIMEOUT` | Engine timeout (seconds) | `150` |
| `SQL_EXECUTION_TIMEOUT` | SQL timeout (seconds) | `60` |
| `UPPER_LIMIT_QUERY_RETURN_ROWS` | Max query rows | `50` |

See `.env.example` for a complete configuration template.

---

## Documentation

- **[API Documentation](docs/apis/README.md)** - Complete REST API reference
- **[Architecture Guide](ARCHITECTURE.md)** - System design and patterns
- **[Getting Started](docs/GETTING_STARTED.md)** - Detailed setup guide
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment
- **[Tutorials](docs/tutorials/)** - Step-by-step guides

---

## Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details on:

- Development workflow
- Code style guidelines
- Testing requirements
- Pull request process

### Quick Start for Contributors

```bash
# Fork and clone the repository
git clone https://github.com/your-username/kai.git
cd kai

# Create a feature branch
git checkout -b feature/amazing-feature

# Install dependencies
uv sync

# Make your changes and test
uv run pytest

# Commit and push
git commit -m "Add amazing feature"
git push origin feature/amazing-feature

# Open a pull request
```

---

## License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

---

## Star History

If you find KAI useful, please consider giving it a star on GitHub!

---

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [Typesense](https://typesense.org/) - Vector search engine

---

<div align="center">

**Made with love by MTA**

[Report Bug](https://github.com/your-org/kai/issues) • [Request Feature](https://github.com/your-org/kai/issues) • [Join Discussion](https://github.com/your-org/kai/discussions)

</div>