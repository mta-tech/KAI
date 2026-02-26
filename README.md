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
- [Web UI](#web-ui)
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

**Access Options:**
- **Web UI** - Modern Next.js interface for visual interaction
- **REST API** - 40+ endpoints for programmatic access
- **CLI** - Command-line tool for terminal-based workflows

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
git clone https://github.com/mta-tech/KAI.git
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

Now that KAI is running, explore these options:
- **[Web UI](#web-ui)** - Visual interface with dashboard builder
- **[Dashboard Tutorial](#creating-dashboards-tutorial)** - Create dashboards from natural language
- **[CLI Tutorial](#quick-cli-tutorial)** - Terminal-based workflows
- **[API Documentation](http://localhost:8015/docs)** - Programmatic access

---

## Web UI

KAI includes a **modern web interface** built with Next.js for visual, interactive data analysis.

### Features

- **Interactive Chat** - Natural language conversations with your data
- **Dashboard Builder** - Create visual dashboards from text descriptions
- **SQL Query Interface** - Write and execute queries with visual results
- **Analytics Visualizations** - View forecasts, trends, and statistical analysis
- **Database Management** - Configure connections and settings through UI

### Quick Start

**1. Ensure the backend is running**

```bash
docker compose up -d
# Backend available at http://localhost:8015
```

**2. Navigate to UI directory**

```bash
cd ui
```

**3. Install dependencies**

```bash
npm install
# or
yarn install
```

**4. Configure environment**

Create `ui/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8015
NEXT_PUBLIC_API_BASE_PATH=/api/v1
```

**5. Start the UI**

```bash
npm run dev
```

**6. Open in browser**

Visit [http://localhost:3000](http://localhost:3000)

### Using the Web UI

**Create a session:**
1. Navigate to "New Session"
2. Select your database connection
3. Start asking questions in natural language

**Example interactions:**
- "Show me total sales by month"
- "Create a dashboard with revenue trends and top products"
- "What are the customer demographics?"
- "Forecast sales for next quarter"

**View results:**
- SQL queries are shown with syntax highlighting
- Results displayed in interactive tables
- Charts auto-generated for time series and distributions
- Download results as CSV or JSON

### Creating Dashboards Tutorial

KAI can automatically generate interactive dashboards from natural language descriptions.

**Step 1: Access Dashboard Builder**

Navigate to the "Dashboards" section in the Web UI.

**Step 2: Describe your dashboard**

Enter a natural language description of what you want to see:

```
Create a sales dashboard showing:
- Total revenue this month
- Top 5 products by sales
- Revenue trend over the last 12 months
- Customer distribution by region
```

**Step 3: Select database**

Choose the database connection to query from.

**Step 4: Generate**

Click "Generate Dashboard" and KAI will:
1. Analyze your description
2. Generate appropriate SQL queries
3. Execute queries against your database
4. Create visualizations (charts, tables, KPIs)
5. Arrange components in a responsive layout

**Step 5: Customize**

- Rearrange dashboard components via drag-and-drop
- Adjust chart types (bar, line, pie, etc.)
- Modify time ranges and filters
- Save dashboard for future use

**Via API:**

You can also create dashboards programmatically:

```bash
curl -X POST http://localhost:8015/api/v1/dashboards \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Overview",
    "description": "Show total revenue, top products, and monthly trends",
    "db_connection_id": "your-connection-id"
  }'
```

**Via CLI:**

```bash
uv run kai create-dashboard \
  "Sales dashboard with revenue trends and top products" \
  --db sales
```

For detailed UI documentation and advanced features, see [ui/README.md](ui/README.md).

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

KAI provides a powerful command-line interface organized into logical command groups for database management, knowledge curation, and natural language analysis.

### Quick CLI Tutorial

Here's a complete workflow from connecting to your database to running queries:

**Step 1: Connect to your database**

```bash
# PostgreSQL
uv run kai connection create \
  "postgresql://user:password@localhost:5432/sales_db" \
  -a sales

# MySQL
uv run kai connection create \
  "mysql://user:password@localhost:3306/crm_db" \
  -a crm

# SQLite
uv run kai connection create \
  "sqlite:///path/to/database.db" \
  -a local_db
```

**Step 2: Scan your database schema**

Let KAI understand your database structure:

```bash
# Basic scan
uv run kai table scan-all sales

# With AI-generated descriptions (recommended)
uv run kai table scan-all sales -d

# With MDL semantic layer generation
uv run kai table scan-all sales -d --generate-mdl
```

This analyzes your tables, columns, and relationships, generating descriptions to help the AI understand your data model.

**Step 3: Run your first query**

Try these example queries:

```bash
# One-shot query
uv run kai query run "Show total sales by month for 2024" --db sales

# Another example
uv run kai query run "List top 10 customers by revenue" --db sales

# Complex analytics
uv run kai query run "Analyze correlation between price and quantity sold" --db sales
```

**Step 4: Interactive mode**

For back-and-forth conversations:

```bash
uv run kai query interactive --db sales
```

Then ask questions naturally:

```
> Show me total revenue this quarter
> Which products are underperforming?
> Create a forecast for next month's sales
> What's the average order value by customer segment?
```

Type `exit` or press Ctrl+D to quit.

### Command Reference

The CLI is organized into 8 command groups:

```
kai
├── config              # Configuration and system utilities
├── connection          # Database connection management
├── table               # Table management and schema scanning
├── query               # Query execution and interactive sessions
├── session             # Session management and export
├── dashboard           # Dashboard creation and management
├── knowledge           # Knowledge management
│   ├── glossary        #   Business metric definitions
│   ├── instruction     #   SQL generation rules
│   ├── skill           #   Reusable analysis patterns
│   └── memory          #   Long-term memory store
└── mdl                 # Semantic layer (MDL) management
```

**Connection management:**

```bash
kai connection create <uri> -a <alias>     # Add database connection
kai connection list                        # List all connections
kai connection show <id_or_alias>          # Show connection details
kai connection test <uri>                  # Test without saving
kai connection update <id> --alias <name>  # Update connection
kai connection delete <id> [-f]            # Remove connection
```

**Table management:**

```bash
kai table list <connection_id>             # List tables
kai table show <table_id>                  # Show table details
kai table scan <connection_id> -d          # Scan with AI descriptions
kai table scan-all <connection_id> -d      # Scan all tables
kai table search <connection_id> "pattern" # Search tables/columns
kai table context <connection_id>          # Display database context
```

**Query and analysis:**

```bash
kai query run "<question>" --db <alias>    # One-shot analysis
kai query interactive --db <alias>         # Interactive session
kai query resume <session_id> "<prompt>" --db <alias>  # Resume session
```

**Session management:**

```bash
kai session list [--db <alias>]            # List sessions
kai session show <session_id>              # Show session details
kai session export <session_id> -f markdown -o chat.md  # Export session
kai session delete <session_id> [-f]       # Delete session
```

**Dashboard management:**

```bash
kai dashboard create "Sales overview" --db <alias>      # Create from NL
kai dashboard list --db <alias>                         # List dashboards
kai dashboard execute <dashboard_id> --save             # Run all widgets
kai dashboard render <dashboard_id> -f html -o report.html  # Render to HTML
kai dashboard refine <dashboard_id> "Add revenue chart" # Refine with NL
```

**Knowledge management:**

```bash
# Business glossary (metric definitions)
kai knowledge glossary add <conn_id> -m "Revenue" -s "SELECT SUM(amount) FROM orders"
kai knowledge glossary list <conn_id>

# Business instructions (SQL generation rules)
kai knowledge instruction add <conn_id> -c "General" -r "Exclude test accounts"
kai knowledge instruction list <conn_id>

# Skills (reusable analysis patterns)
kai knowledge skill discover <conn_id> --path ./skills
kai knowledge skill list <conn_id>

# Long-term memory
kai knowledge memory list <conn_id>
kai knowledge memory search "date format" -d <conn_id>
kai knowledge memory add <conn_id> user_preferences date_format "Use YYYY-MM-DD"
```

**MDL (semantic layer):**

```bash
kai mdl list [--db <alias>]                # List MDL manifests
kai mdl show <manifest_id> [--summary]     # Show manifest details
kai mdl show <manifest_id> -f json         # Export as JSON
```

**Configuration:**

```bash
kai config show [--json]                   # Show current settings
kai config check                           # Check environment/API keys
kai config version                         # Show version info
```

**Help:**

```bash
kai --help                                 # Show all command groups
kai <group> --help                         # Group-specific help
kai <group> <command> --help               # Command-specific help
```

### Common Workflows

**Setup workflow** (connection, scan, query):

```bash
uv run kai connection create "postgresql://user:pass@host:5432/db" -a mydb
uv run kai table scan-all mydb -d
uv run kai query run "Show top customers" --db mydb
```

**Knowledge workflow** (teach KAI your business context):

```bash
uv run kai knowledge glossary add mydb -m "MRR" -s "SELECT SUM(amount) FROM subscriptions WHERE status='active'"
uv run kai knowledge instruction add mydb -c "Revenue" -r "Always filter by active subscriptions"
uv run kai knowledge skill discover mydb --path ./skills
uv run kai query run "What's our MRR?" --db mydb  # Now uses business context
```

**Dashboard workflow** (create, execute, export):

```bash
uv run kai dashboard create "Sales performance dashboard" --db mydb --theme ocean
uv run kai dashboard execute <dashboard_id> --save
uv run kai dashboard render <dashboard_id> -f html -o dashboard.html
```

### Advanced CLI Features

**Session management:**

```bash
# Resume a previous conversation
uv run kai query resume <session_id> "Break it down by region" --db sales

# Export session to markdown
uv run kai session export <session_id> -f markdown -o conversation.md
```

**Search and exploration:**

```bash
# Search tables and columns by pattern
uv run kai table search mydb "revenue"
uv run kai table search mydb "*_id" -i columns

# Display full database context
uv run kai table context mydb -s -d -f markdown -o context.md
```

**Memory management:**

```bash
# Store preferences the AI remembers across sessions
uv run kai knowledge memory add mydb user_preferences date_format "Use YYYY-MM-DD"
uv run kai knowledge memory search "preferences" -d mydb
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

[Report Bug](https://github.com/mta-tech/KAI/issues) • [Request Feature](https://github.com/mta-tech/KAI/issues) • [Join Discussion](https://github.com/mta-tech/KAI/discussions)

</div>