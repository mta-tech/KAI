# Welcome to KAI

<div align="center">

**Knowledge Agent for Intelligence Query**

*Transform natural language into powerful data insights*

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-00a393.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-purple.svg)](https://github.com/langchain-ai/langgraph)

[Get Started](getting-started/quick-start.md){ .md-button .md-button--primary }
[View on GitHub](https://github.com/mta-tech/kai){ .md-button }

</div>

---

## What is KAI?

KAI is an **AI-powered data agent** that transforms how you interact with databases. Using natural language, you can:

- :material-database-search: **Query databases** without writing SQL
- :material-chart-line: **Generate insights** with advanced analytics (forecasting, anomaly detection, statistical analysis)
- :material-view-dashboard: **Create dashboards** from natural language descriptions
- :material-brain: **Remember context** across sessions with long-term memory
- :material-book-open: **Manage knowledge** with context assets and benchmarks

## Key Features

### Context Platform :material-new-box:

The Context Platform provides reliable autonomous analytics through:

- **Context Assets**: Reusable knowledge artifacts (table descriptions, glossaries, instructions, skills)
- **Lifecycle Management**: Draft → Verified → Published → Deprecated
- **Benchmarks**: Severity-weighted scoring for quality evaluation
- **Telemetry**: KPI tracking for asset reuse (≥70% target)

[Learn about Context Platform →](tutorials/context-platform-tutorial.md){ .md-button }

### Natural Language Querying

Ask questions in plain English—no SQL knowledge required:

```bash
uv run kai query run "Show total sales by month for 2024" --db mydb
```

### Multi-LLM Support

Flexible LLM provider support:

- OpenAI (GPT-4, GPT-3.5)
- Google Gemini
- Ollama (local models)
- OpenRouter

### Access Options

| Option | Description |
|--------|-------------|
| **Web UI** | Modern Next.js interface for visual interaction |
| **REST API** | 40+ endpoints for programmatic access |
| **CLI** | Command-line tool for terminal-based workflows |

## Quick Links

<div class="grid cards" markdown>

-   :material-rocket-launch: __Getting Started__

    ---

    Get KAI running in 5 minutes with Docker

    [:octicons-arrow-right-24: Quick Start](getting-started/quick-start.md)

-   :material-school: __Tutorials__

    ---

    Step-by-step guides for common use cases

    [:octicons-arrow-right-24: View Tutorials](tutorials/index.md)

-   :material-api: __API Reference__

    ---

    Complete REST API documentation with examples

    [:octicons-arrow-right-24: API Docs](apis/index.md)

-   :material-console: __CLI Reference__

    ---

    Command-line interface documentation

    [:octicons-arrow-right-24: CLI Docs](cli/index.md)

</div>

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                 FastAPI REST API                     │
├─────────────────────────────────────────────────────┤
│                 Service Layer                        │
│  ┌──────────┬──────────┬──────────┬──────────┐     │
│  │ Session  │   SQL    │Analytics │Dashboard │     │
│  │  Module  │ Module   │  Module  │  Module  │     │
│  └──────────┴──────────┴──────────┴──────────┘     │
├─────────────────────────────────────────────────────┤
│             Repository Layer (Typesense)             │
├─────────────────────────────────────────────────────┤
│      LangGraph Agents & LLM Adapters                │
└─────────────────────────────────────────────────────┘
```

[Learn more about the architecture →](architecture/index.md){ .md-button }

## Built With

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [Typesense](https://typesense.org/) - Vector search engine

## License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](../LICENSE) file for details.
