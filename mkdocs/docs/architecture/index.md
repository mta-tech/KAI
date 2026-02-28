# Architecture Overview

KAI follows a modular, layered architecture designed for scalability and maintainability.

## System Architecture

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
│  ┌──────────────────────────────────────────┐       │
│  │         Context Platform Module          │       │
│  │  Assets │ Benchmarks │ Feedback │ Telemetry │   │
│  └──────────────────────────────────────────┘       │
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

## Key Components

### FastAPI Server
- REST API with 40+ endpoints
- Automatic OpenAPI documentation
- Async request handling

### Service Modules
Domain-specific business logic organized by feature:
- **Session**: Conversational state management
- **SQL**: Query generation and execution
- **Analytics**: Statistical analysis, forecasting, anomaly detection
- **Dashboard**: Natural language dashboard creation
- **Context Platform**: Asset lifecycle, benchmarks, telemetry

### LangGraph Agents
Agent orchestration for complex workflows:
- `session_graph`: Multi-turn conversations
- `sql_agent_graph`: SQL generation with tools

### Typesense
Vector search and document storage for:
- Session history
- Knowledge base
- Context assets

### LLM Adapters
Unified interface across providers:
- OpenAI (GPT-4, GPT-3.5)
- Google Gemini
- Ollama (local)
- OpenRouter

## Module Pattern

Each module follows a consistent pattern:

```
app/modules/<feature>/
├── models/          # Pydantic BaseModel definitions
├── repositories/    # Data access via Storage (Typesense)
├── services/        # Business logic
└── api/             # REST endpoints (optional)
```

## Detailed Documentation

- [System Design](system-design.md) - Full architecture details
- [Modules](modules.md) - Module documentation
