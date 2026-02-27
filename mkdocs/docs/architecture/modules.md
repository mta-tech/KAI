# Modules

KAI is organized into feature modules, each following a consistent pattern.

## Module Structure

```
app/modules/<feature>/
├── __init__.py
├── models/
│   ├── __init__.py
│   └── *.py          # Pydantic models
├── repositories/
│   ├── __init__.py
│   └── *.py          # Data access layer
├── services/
│   ├── __init__.py
│   └── *.py          # Business logic
└── api/
    ├── __init__.py
    └── endpoints.py   # REST endpoints (optional)
```

## Core Modules

### autonomous_agent
CLI and agent-based analysis.

- Natural language query execution
- Interactive sessions
- Mission orchestration
- Artifact management

### context_platform
Context asset lifecycle management.

- **Models**: Asset, Benchmark, Feedback
- **Services**: AssetService, BenchmarkService, TelemetryService
- **API**: 20+ endpoints for assets, benchmarks, feedback

### session
LangGraph-based interactive sessions.

- Multi-turn conversations
- Session persistence
- Export capabilities

### sql_generation
Natural language to SQL conversion.

- Schema-aware generation
- Query validation
- Execution and results

### analytics
Statistical analysis features.

- Correlation analysis
- Time series forecasting
- Anomaly detection
- Automated insights

### dashboard
Natural language dashboard creation.

- Widget generation
- Layout management
- Theme support

### memory
Long-term memory management.

- Typesense backend
- Letta backend (optional)
- Semantic search

## Adding New Modules

1. Create module directory in `app/modules/<feature>/`
2. Add `models/`, `repositories/`, `services/` subdirectories
3. Define Pydantic models for data structures
4. Implement repository for data access
5. Create service for business logic
6. Add API endpoints if needed
7. Register in `app/api/__init__.py`
