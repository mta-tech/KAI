# KAI Architecture Documentation

This document provides a comprehensive overview of KAI's architecture, design patterns, and technical decisions.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Layered Structure](#layered-structure)
- [Core Components](#core-components)
- [Module Pattern](#module-pattern)
- [LangGraph Agents](#langgraph-agents)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Design Patterns](#design-patterns)
- [Scalability & Performance](#scalability--performance)
- [Security](#security)

## Overview

KAI (Knowledge Agent for Intelligence Query) is built on a **modular, layered architecture** that separates concerns and enables easy extension. The system follows modern Python async patterns and integrates multiple AI/ML frameworks.

### Core Principles

1. **Modularity**: Features organized in self-contained modules
2. **Async-First**: All I/O operations use async/await
3. **Type Safety**: Comprehensive type hints throughout
4. **Testability**: Clear separation enables easy testing
5. **Extensibility**: New modules and LLM providers easily added

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Web UI     │  │  CLI Client  │  │  API Client  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI REST API Layer                       │
│                       (app/api/)                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  40+ REST Endpoints: /database-connections, /sessions,   │  │
│  │  /prompts, /sql-generations, /analytics, /dashboards     │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Service Layer                             │
│                      (app/modules/*/services/)                   │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐      │
│  │ Session  │   SQL    │Analytics │Dashboard │MemoryMgr │      │
│  │ Service  │ Service  │ Service  │ Service  │ Service  │      │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘      │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐      │
│  │  Skill   │  Visual  │ Context  │Business  │   RAG    │      │
│  │ Service  │ Service  │ Service  │Glossary  │ Service  │      │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘      │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Repository Layer                            │
│                   (app/modules/*/repositories/)                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Data Access Layer - Abstracts Typesense operations      │  │
│  │  CRUD operations, vector search, filtering               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Agent & LLM Layer                           │
│             (app/langgraph_server/, app/utils/model/)            │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │  Session Graph   │  │ SQL Agent Graph  │                    │
│  │ (Multi-turn chat)│  │ (ReAct SQL gen)  │                    │
│  └──────────────────┘  └──────────────────┘                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │   LLM Adapters (OpenAI, Google, Ollama, OpenRouter)     │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Storage & External Services                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Typesense   │  │   User DB    │  │   LLM APIs   │         │
│  │ (Vector DB)  │  │ (PostgreSQL/ │  │ (OpenAI/etc) │         │
│  │              │  │  MySQL/etc)  │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Layered Structure

### 1. API Layer (`app/api/`)

**Purpose**: HTTP request/response handling, routing, validation

**Key Files**:
- `__init__.py` - Main API router and endpoint registration
- `requests.py` - Pydantic request models
- `responses.py` - Pydantic response models

**Responsibilities**:
- Route HTTP requests to services
- Validate input/output with Pydantic
- Handle authentication/authorization
- Error handling and HTTP status codes

### 2. Service Layer (`app/modules/*/services/`)

**Purpose**: Business logic implementation

**Examples**:
- `SessionService` - Manages conversational sessions
- `SqlGenerationService` - Orchestrates SQL generation
- `AnalyticsService` - Statistical analysis and forecasting
- `DashboardService` - Dashboard creation from NL
- `MemoryService` - Long-term memory management

**Responsibilities**:
- Implement business rules
- Coordinate between repositories
- Call LLM agents when needed
- Transform data between layers

### 3. Repository Layer (`app/modules/*/repositories/`)

**Purpose**: Data access abstraction

**Pattern**:
```python
class SessionRepository:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.collection = "sessions"

    async def create(self, session: Session) -> str:
        """Create new session in storage."""
        return await self.storage.create(
            collection=self.collection,
            document=session.dict()
        )

    async def find_by_id(self, session_id: str) -> Optional[Session]:
        """Find session by ID."""
        doc = await self.storage.get(self.collection, session_id)
        return Session(**doc) if doc else None
```

**Responsibilities**:
- CRUD operations
- Query composition
- Data mapping (storage ↔ domain models)

### 4. Model Layer (`app/modules/*/models/`)

**Purpose**: Domain object definitions

**Pattern**:
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Session(BaseModel):
    """Interactive session model."""
    id: Optional[str] = None
    db_alias: str
    user_id: str
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = {}
```

## Core Components

### FastAPI Server (`app/main.py`)

Entry point that:
- Initializes FastAPI application
- Sets up middleware (CORS, logging, error handling)
- Registers API routes
- Configures Typesense connection
- Starts Uvicorn server

### Storage Abstraction (`app/data/db/storage.py`)

Unified interface to Typesense:

```python
class Storage:
    """Typesense wrapper for vector search and document storage."""

    async def create(self, collection: str, document: dict) -> str:
        """Create document, return ID."""

    async def get(self, collection: str, doc_id: str) -> Optional[dict]:
        """Retrieve document by ID."""

    async def search(
        self,
        collection: str,
        query: str,
        query_by: str,
        filter_by: str = "",
    ) -> List[dict]:
        """Vector/text search."""

    async def update(self, collection: str, doc_id: str, updates: dict):
        """Update document fields."""

    async def delete(self, collection: str, doc_id: str):
        """Delete document."""
```

### Configuration (`app/server/config.py`)

Settings management with `pydantic_settings`:

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Server
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8015

    # LLM
    CHAT_FAMILY: str  # openai, google, ollama, openrouter
    CHAT_MODEL: str
    OPENAI_API_KEY: Optional[str] = None

    # Typesense
    TYPESENSE_HOST: str = "localhost"
    TYPESENSE_PORT: int = 8108

    # Security
    ENCRYPT_KEY: str  # Fernet key for DB credentials

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
```

## Module Pattern

Each feature module follows this structure:

```
app/modules/<feature>/
├── __init__.py
├── models/
│   ├── __init__.py
│   └── <feature>.py       # Pydantic models
├── repositories/
│   ├── __init__.py
│   └── <feature>_repository.py
├── services/
│   ├── __init__.py
│   └── <feature>_service.py
└── utils/                  # Optional
    └── helpers.py
```

### Adding a New Module

1. **Create module structure**:
   ```bash
   mkdir -p app/modules/my_feature/{models,repositories,services}
   ```

2. **Define model** (`app/modules/my_feature/models/my_feature.py`):
   ```python
   from pydantic import BaseModel

   class MyFeature(BaseModel):
       id: str
       name: str
       description: str
   ```

3. **Implement repository** (`app/modules/my_feature/repositories/my_feature_repository.py`):
   ```python
   class MyFeatureRepository:
       def __init__(self, storage: Storage):
           self.storage = storage
           self.collection = "my_features"

       async def create(self, feature: MyFeature) -> str:
           return await self.storage.create(
               self.collection,
               feature.dict()
           )
   ```

4. **Implement service** (`app/modules/my_feature/services/my_feature_service.py`):
   ```python
   class MyFeatureService:
       def __init__(self, repository: MyFeatureRepository):
           self.repository = repository

       async def create_feature(self, name: str, description: str) -> MyFeature:
           feature = MyFeature(name=name, description=description)
           feature_id = await self.repository.create(feature)
           feature.id = feature_id
           return feature
   ```

5. **Register in API** (`app/api/__init__.py`):
   ```python
   class API:
       def __init__(self, storage: Storage):
           # Initialize service
           my_feature_repo = MyFeatureRepository(storage)
           self.my_feature_service = MyFeatureService(my_feature_repo)

       def _register_routes(self):
           # Add route
           self.router.add_api_route(
               "/api/v1/my-features",
               self._create_my_feature,
               methods=["POST"]
           )

       async def _create_my_feature(self, request: CreateMyFeatureRequest):
           feature = await self.my_feature_service.create_feature(
               request.name,
               request.description
           )
           return {"id": feature.id, "name": feature.name}
   ```

## LangGraph Agents

### Session Graph (`app/langgraph_server/graphs.py`)

**Purpose**: Multi-turn conversational sessions

**Flow**:
```
User Input
    ↓
Route Decision (determine intent)
    ↓
  ┌─────────────┬──────────────┬──────────────┐
  │             │              │              │
SQL Query    Analytics    Dashboard      General
  │             │              │              │
  └─────────────┴──────────────┴──────────────┘
                ↓
          Response Generation
                ↓
            User Output
```

**Key Nodes**:
- `route_query` - Classifies user intent
- `generate_sql` - Creates SQL from NL
- `execute_query` - Runs SQL, handles errors
- `analyze_data` - Statistical analysis
- `generate_response` - Natural language response

### SQL Agent Graph

**Purpose**: Robust SQL generation with self-correction

**Flow**:
```
User Question
    ↓
Plan Generation (ReAct reasoning)
    ↓
SQL Generation
    ↓
Validation (syntax, schema)
    ↓
  Valid? ──No──> Reflect & Retry
    │
   Yes
    ↓
Execute & Return Results
```

**Tools Available**:
- `get_schema` - Retrieve table schemas
- `execute_sql` - Run SQL query
- `analyze_error` - Parse SQL errors
- `get_similar_queries` - Retrieve past queries

## Data Flow

### Example: Natural Language Query

```
1. User: "Show top 10 customers by revenue"
        ↓
2. API Endpoint: POST /api/v1/prompts/sql-generations
        ↓
3. SqlGenerationService.create_sql_generation()
        ↓
4. LangGraph SQL Agent:
   - Analyze question
   - Retrieve schema
   - Generate SQL
   - Validate syntax
        ↓
5. Execute SQL on user database
        ↓
6. Store results in Typesense
        ↓
7. Return SQL + Results to user
```

### Example: Analytics Pipeline

```
1. User: "Forecast sales for next 30 days"
        ↓
2. API: POST /api/v1/analytics/forecast
        ↓
3. AnalyticsService.forecast()
        ↓
4. Fetch historical data
        ↓
5. Apply time series model (Prophet/ARIMA)
        ↓
6. Generate predictions
        ↓
7. Create visualization spec
        ↓
8. Return forecast data + chart config
```

## Technology Stack

### Core Framework
- **FastAPI** - Async web framework
- **Pydantic** - Data validation and settings
- **Uvicorn** - ASGI server

### AI/ML
- **LangGraph** - Agent orchestration
- **LangChain** - LLM framework
- **OpenAI/Google SDKs** - LLM APIs

### Storage
- **Typesense** - Vector search and document store
- **User Databases** - PostgreSQL, MySQL, SQLite (via connectors)

### Development
- **uv** - Fast package manager
- **pytest** - Testing framework
- **ruff** - Linting
- **black** - Code formatting

## Design Patterns

### 1. Repository Pattern
Abstracts data access logic from business logic.

### 2. Service Layer Pattern
Encapsulates business logic separate from API and data layers.

### 3. Dependency Injection
Services receive dependencies via constructor:
```python
class SessionService:
    def __init__(
        self,
        repository: SessionRepository,
        llm_adapter: LLMAdapter,
    ):
        self.repository = repository
        self.llm_adapter = llm_adapter
```

### 4. Factory Pattern
For LLM adapter creation:
```python
def get_llm_adapter(family: str, model: str) -> LLMAdapter:
    if family == "openai":
        return OpenAIAdapter(model)
    elif family == "google":
        return GoogleAdapter(model)
    # ...
```

### 5. Async Context Managers
For resource management:
```python
async with get_db_connection(conn_id) as conn:
    results = await conn.execute(sql)
```

## Scalability & Performance

### Async Architecture
- All I/O operations are async (DB, LLM API, file I/O)
- Non-blocking request handling
- Concurrent request processing

### Caching Strategy
- LLM responses cached in Typesense
- Schema metadata cached
- Frequently used queries cached

### Horizontal Scaling
- Stateless API design
- Session state in Typesense (shared)
- Can deploy multiple FastAPI instances behind load balancer

### Resource Limits
- Configurable timeouts (DH_ENGINE_TIMEOUT, SQL_EXECUTION_TIMEOUT)
- Max query iterations (AGENT_MAX_ITERATIONS)
- Row limits (UPPER_LIMIT_QUERY_RETURN_ROWS)

## Security

### Data Encryption
- Database credentials encrypted with Fernet (ENCRYPT_KEY)
- Stored encrypted in Typesense
- Decrypted only when needed

### Input Validation
- Pydantic models validate all inputs
- SQL injection prevention (parameterized queries)
- Schema validation before execution

### API Security
- CORS configured
- Rate limiting (optional)
- API key authentication (optional)

### LLM Security
- Prompt injection detection
- Output filtering
- Sandboxed SQL execution

---

## Further Reading

- [Module Documentation](docs/apis/README.md)
- [LangGraph Concepts](https://github.com/langchain-ai/langgraph)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Typesense Guide](https://typesense.org/docs/)
