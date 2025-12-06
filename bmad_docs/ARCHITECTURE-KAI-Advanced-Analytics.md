# Architecture Document
# KAI Advanced Analytics Platform

**Version:** 1.0
**Date:** 2025-12-06
**Author:** BMad Master (AI-Generated)
**Status:** Draft for Review

---

## 1. Executive Summary

This document defines the technical architecture for evolving KAI into an Advanced Analytics Platform. The architecture builds upon KAI's existing strengths (autonomous agents, persistent memory, semantic layer) while adding new capabilities for data source expansion, interactive visualization, statistical analysis, and workflow automation.

### Architecture Principles

1. **Extensibility First** - Plugin-based connectors, adapters, and tools
2. **CLI/API Parity** - Every feature accessible via both interfaces
3. **Layered Abstraction** - Clear separation of concerns
4. **Async by Default** - Non-blocking operations for scalability
5. **Provider Agnostic** - Flexible LLM, storage, and database support
6. **Backwards Compatible** - Existing functionality preserved

---

## 2. Current Architecture Overview

### 2.1 Existing System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              KAI CURRENT STATE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────────┐  │
│  │   CLI        │    │  REST API    │    │   LangGraph Studio           │  │
│  │  (kai-agent) │    │  (FastAPI)   │    │   (langgraph dev)            │  │
│  └──────┬───────┘    └──────┬───────┘    └──────────────┬───────────────┘  │
│         │                   │                           │                   │
│         └───────────────────┼───────────────────────────┘                   │
│                             ▼                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        SERVICE LAYER                                  │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────────┐ │  │
│  │  │ Autonomous │ │  Session   │ │    SQL     │ │     Analysis       │ │  │
│  │  │   Agent    │ │  Service   │ │ Generation │ │     Service        │ │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────────────┘ │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────────┐ │  │
│  │  │   Memory   │ │   Skill    │ │    MDL     │ │      RAG           │ │  │
│  │  │  Service   │ │  Service   │ │  Service   │ │    Service         │ │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                             │                                               │
│                             ▼                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      AGENT TOOLS (30+)                                │  │
│  │  sql_query, python_execute, generate_chart, write_excel,             │  │
│  │  remember, recall, list_tables, get_business_glossary, etc.          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                             │                                               │
│                             ▼                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │    Typesense    │  │   SQLAlchemy    │  │      LLM Adapters           │ │
│  │    (Storage)    │  │  (PG/MySQL/     │  │  (OpenAI/Gemini/Ollama)     │ │
│  │                 │  │   SQLite)       │  │                             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Current Module Structure

```
app/
├── main.py                    # FastAPI entry point
├── server/
│   ├── config.py              # Pydantic settings
│   ├── middleware.py          # Request middleware
│   └── errors.py              # Exception handlers
├── api/
│   ├── __init__.py            # Route registration (add_api_route)
│   ├── analysis.py            # Analysis endpoints
│   ├── connection.py          # DB connection endpoints
│   └── ... (40+ endpoint modules)
├── modules/
│   ├── autonomous_agent/      # DeepAgents integration
│   │   ├── cli.py             # CLI commands
│   │   ├── services/          # Agent orchestration
│   │   └── tools/             # 30+ agent tools
│   ├── session/               # LangGraph sessions
│   ├── sql_generation/        # NL-to-SQL
│   ├── analysis/              # Query + insights
│   ├── memory/                # Persistent memory
│   ├── skill/                 # Markdown skills
│   ├── mdl/                   # Semantic layer
│   └── ... (18+ modules)
├── utils/
│   ├── model/                 # LLM adapters
│   ├── sql/                   # SQL utilities
│   └── prompts/               # Prompt templates
├── data/db/
│   ├── storage.py             # Typesense wrapper
│   └── schemas.py             # Storage schemas
└── langgraph_server/
    └── graphs.py              # Session + SQL agent graphs
```

---

## 3. Target Architecture

### 3.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        KAI ADVANCED ANALYTICS PLATFORM                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                          INTERFACE LAYER                                 │   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐  │   │
│   │  │  Enhanced   │  │   REST API  │  │  WebSocket  │  │   LangGraph    │  │   │
│   │  │    CLI      │  │  (FastAPI)  │  │     API     │  │    Studio      │  │   │
│   │  │ (Rich/Click)│  │  + SSE      │  │             │  │                │  │   │
│   │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                         │
│                                        ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                        ORCHESTRATION LAYER                               │   │
│   │  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────────────┐  │   │
│   │  │   Autonomous     │  │    Notebook      │  │     Scheduler         │  │   │
│   │  │   Agent Engine   │  │   Orchestrator   │  │     Service           │  │   │
│   │  │   (DeepAgents)   │  │                  │  │   (APScheduler)       │  │   │
│   │  └──────────────────┘  └──────────────────┘  └───────────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                         │
│                                        ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                         SERVICE LAYER                                    │   │
│   │                                                                          │   │
│   │  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────────┐ │   │
│   │  │  Data Source   │  │ Visualization  │  │    Analytics Engine        │ │   │
│   │  │    Service     │  │    Service     │  │  ┌──────────────────────┐  │ │   │
│   │  │ ┌────────────┐ │  │ ┌────────────┐ │  │  │ Statistical Service  │  │ │   │
│   │  │ │ Connection │ │  │ │   Plotly   │ │  │  ├──────────────────────┤  │ │   │
│   │  │ │  Manager   │ │  │ │  Renderer  │ │  │  │ Forecasting Service  │  │ │   │
│   │  │ ├────────────┤ │  │ ├────────────┤ │  │  ├──────────────────────┤  │ │   │
│   │  │ │   File     │ │  │ │   Theme    │ │  │  │  Anomaly Service     │  │ │   │
│   │  │ │  Handler   │ │  │ │   Engine   │ │  │  └──────────────────────┘  │ │   │
│   │  │ └────────────┘ │  │ └────────────┘ │  │                            │ │   │
│   │  └────────────────┘  └────────────────┘  └────────────────────────────┘ │   │
│   │                                                                          │   │
│   │  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────────┐ │   │
│   │  │   SQL Gen      │  │   Analysis     │  │    Knowledge Services      │ │   │
│   │  │   Service      │  │   Service      │  │  ┌──────────────────────┐  │ │   │
│   │  │  (existing)    │  │  (existing)    │  │  │   Memory Service     │  │ │   │
│   │  │                │  │                │  │  ├──────────────────────┤  │ │   │
│   │  │                │  │                │  │  │   Skill Service      │  │ │   │
│   │  │                │  │                │  │  ├──────────────────────┤  │ │   │
│   │  │                │  │                │  │  │   MDL Service        │  │ │   │
│   │  └────────────────┘  └────────────────┘  └────────────────────────────┘ │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                         │
│                                        ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                        CONNECTOR LAYER                                   │   │
│   │  ┌───────────────────────────────────────────────────────────────────┐  │   │
│   │  │                    Data Source Connectors                          │  │   │
│   │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐  │  │   │
│   │  │  │PostgreSQL│ │  MySQL  │ │ SQLite  │ │BigQuery │ │  Snowflake  │  │  │   │
│   │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────────┘  │  │   │
│   │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐  │  │   │
│   │  │  │Redshift │ │ DuckDB  │ │  CSV    │ │  Excel  │ │   Parquet   │  │  │   │
│   │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────────┘  │  │   │
│   │  └───────────────────────────────────────────────────────────────────┘  │   │
│   │                                                                          │   │
│   │  ┌───────────────────────────────────────────────────────────────────┐  │   │
│   │  │                    Storage Connectors                              │  │   │
│   │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │  │   │
│   │  │  │   GCS    │  │   S3     │  │  Azure   │  │   Local FS       │   │  │   │
│   │  │  │          │  │          │  │  Blob    │  │                  │   │  │   │
│   │  │  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘   │  │   │
│   │  └───────────────────────────────────────────────────────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                         │
│                                        ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                       FOUNDATION LAYER                                   │   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐  │   │
│   │  │  Typesense  │  │    LLM      │  │   Task      │  │   Config       │  │   │
│   │  │  Storage    │  │  Adapters   │  │   Queue     │  │   Manager      │  │   │
│   │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 New Module Structure

```
app/
├── main.py                         # FastAPI entry point (enhanced)
├── server/
│   ├── config.py                   # Extended settings
│   ├── middleware.py               # Request middleware
│   ├── errors.py                   # Exception handlers
│   └── streaming.py                # SSE/WebSocket support (NEW)
├── api/
│   ├── __init__.py                 # Route registration
│   ├── v1/                         # API v1 (existing)
│   └── v2/                         # API v2 (NEW - streaming, batch)
│       ├── analysis.py
│       ├── notebooks.py
│       ├── visualizations.py
│       └── files.py
├── modules/
│   ├── autonomous_agent/           # Enhanced with new tools
│   │   ├── cli.py                  # Enhanced CLI
│   │   ├── services/
│   │   └── tools/
│   │       ├── sql_tools.py        # Existing
│   │       ├── chart_tools.py      # ENHANCED (Plotly)
│   │       ├── stats_tools.py      # NEW
│   │       ├── forecast_tools.py   # NEW
│   │       └── file_tools.py       # NEW
│   ├── data_source/                # NEW MODULE
│   │   ├── __init__.py
│   │   ├── models.py               # DataSource, FileSource models
│   │   ├── services/
│   │   │   ├── connection_manager.py   # Unified connection handling
│   │   │   └── file_handler.py         # File-based data handling
│   │   ├── connectors/             # Database connectors
│   │   │   ├── base.py             # Abstract connector
│   │   │   ├── postgresql.py       # Existing (refactored)
│   │   │   ├── mysql.py            # Existing (refactored)
│   │   │   ├── sqlite.py           # Existing (refactored)
│   │   │   ├── bigquery.py         # NEW
│   │   │   ├── snowflake.py        # NEW
│   │   │   ├── redshift.py         # NEW
│   │   │   └── duckdb.py           # NEW
│   │   └── file_readers/           # File format readers
│   │       ├── base.py             # Abstract reader
│   │       ├── csv_reader.py       # NEW
│   │       ├── excel_reader.py     # NEW (enhanced)
│   │       ├── parquet_reader.py   # NEW
│   │       └── json_reader.py      # NEW
│   ├── visualization/              # NEW MODULE
│   │   ├── __init__.py
│   │   ├── models.py               # Chart, Theme models
│   │   ├── services/
│   │   │   ├── chart_service.py    # Plotly chart generation
│   │   │   ├── theme_service.py    # Theme management
│   │   │   └── export_service.py   # Format export
│   │   ├── charts/                 # Chart type implementations
│   │   │   ├── base.py             # Abstract chart
│   │   │   ├── line.py
│   │   │   ├── bar.py
│   │   │   ├── scatter.py
│   │   │   ├── pie.py
│   │   │   ├── heatmap.py
│   │   │   ├── treemap.py
│   │   │   └── ... (15+ types)
│   │   └── themes/                 # Theme definitions
│   │       ├── default.py
│   │       ├── dark.py
│   │       └── custom.py
│   ├── analytics/                  # NEW MODULE
│   │   ├── __init__.py
│   │   ├── models.py               # StatResult, Forecast models
│   │   ├── services/
│   │   │   ├── statistical_service.py   # Hypothesis tests
│   │   │   ├── forecasting_service.py   # Time series
│   │   │   └── anomaly_service.py       # Outlier detection
│   │   └── algorithms/
│   │       ├── hypothesis_tests.py      # t-test, ANOVA, chi-square
│   │       ├── time_series.py           # Prophet, ARIMA
│   │       └── outlier_detection.py     # IQR, isolation forest
│   ├── notebook/                   # NEW MODULE
│   │   ├── __init__.py
│   │   ├── models.py               # Notebook, Cell models
│   │   ├── services/
│   │   │   ├── notebook_service.py      # CRUD operations
│   │   │   ├── executor_service.py      # Notebook execution
│   │   │   └── scheduler_service.py     # Scheduled runs
│   │   ├── cells/                  # Cell type handlers
│   │   │   ├── query_cell.py
│   │   │   ├── viz_cell.py
│   │   │   ├── text_cell.py
│   │   │   └── code_cell.py
│   │   └── templates/              # Pre-built templates
│   │       ├── sales_analysis.yaml
│   │       ├── customer_cohort.yaml
│   │       └── data_quality.yaml
│   ├── data_prep/                  # NEW MODULE
│   │   ├── __init__.py
│   │   ├── models.py               # Profile, CleaningOp models
│   │   ├── services/
│   │   │   ├── profiling_service.py     # Data profiling
│   │   │   └── cleaning_service.py      # Data cleaning
│   │   └── operations/
│   │       ├── missing_values.py
│   │       ├── type_conversion.py
│   │       └── deduplication.py
│   ├── session/                    # Existing (enhanced)
│   ├── sql_generation/             # Existing
│   ├── analysis/                   # Existing
│   ├── memory/                     # Existing (enhanced)
│   ├── skill/                      # Existing (enhanced)
│   ├── mdl/                        # Existing
│   └── ...
├── utils/
│   ├── model/                      # LLM adapters
│   ├── sql/                        # SQL utilities
│   ├── prompts/                    # Prompt templates
│   └── rich_output/                # NEW - Rich terminal formatting
│       ├── tables.py
│       ├── charts.py
│       └── progress.py
├── data/db/
│   ├── storage.py                  # Typesense wrapper
│   └── schemas.py                  # Storage schemas (extended)
└── cli/                            # NEW - Restructured CLI
    ├── __init__.py
    ├── main.py                     # Entry point
    ├── commands/
    │   ├── connection.py           # DB connection commands
    │   ├── analysis.py             # Analysis commands
    │   ├── notebook.py             # Notebook commands
    │   ├── file.py                 # File commands
    │   ├── skill.py                # Skill commands
    │   └── profile.py              # Profiling commands
    └── output/
        ├── formatter.py            # Output formatting
        └── themes.py               # CLI themes
```

---

## 4. Component Design

### 4.1 Data Source Connector System

#### Abstract Connector Interface

```python
# app/modules/data_source/connectors/base.py

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Optional
from pydantic import BaseModel

class ConnectionConfig(BaseModel):
    """Base configuration for all connectors."""
    alias: str
    connection_type: str
    credentials: dict  # Encrypted
    options: dict = {}

class QueryResult(BaseModel):
    """Unified query result format."""
    columns: list[str]
    rows: list[list[Any]]
    row_count: int
    execution_time_ms: float
    metadata: dict = {}

class BaseConnector(ABC):
    """Abstract base class for all data source connectors."""

    connector_type: str  # e.g., "postgresql", "bigquery"

    def __init__(self, config: ConnectionConfig):
        self.config = config
        self._connection = None

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the data source."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection."""
        pass

    @abstractmethod
    async def execute_query(
        self,
        query: str,
        params: Optional[dict] = None,
        limit: int = 50
    ) -> QueryResult:
        """Execute a query and return results."""
        pass

    @abstractmethod
    async def stream_query(
        self,
        query: str,
        params: Optional[dict] = None,
        batch_size: int = 1000
    ) -> AsyncIterator[QueryResult]:
        """Stream query results in batches."""
        pass

    @abstractmethod
    async def get_schema(self) -> dict:
        """Get database schema information."""
        pass

    @abstractmethod
    async def list_tables(self, schema: Optional[str] = None) -> list[str]:
        """List available tables."""
        pass

    @abstractmethod
    async def get_table_columns(self, table: str) -> list[dict]:
        """Get column information for a table."""
        pass

    async def test_connection(self) -> bool:
        """Test if connection is valid."""
        try:
            await self.connect()
            await self.disconnect()
            return True
        except Exception:
            return False
```

#### BigQuery Connector Example

```python
# app/modules/data_source/connectors/bigquery.py

from google.cloud import bigquery
from google.oauth2 import service_account
from .base import BaseConnector, ConnectionConfig, QueryResult

class BigQueryConnector(BaseConnector):
    connector_type = "bigquery"

    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self._client: Optional[bigquery.Client] = None

    async def connect(self) -> None:
        credentials_info = self.config.credentials.get("service_account")
        if credentials_info:
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info
            )
            self._client = bigquery.Client(
                project=self.config.credentials.get("project_id"),
                credentials=credentials
            )
        else:
            # Use default credentials
            self._client = bigquery.Client(
                project=self.config.credentials.get("project_id")
            )

    async def execute_query(
        self,
        query: str,
        params: Optional[dict] = None,
        limit: int = 50
    ) -> QueryResult:
        import time
        start = time.time()

        # Add LIMIT if not present
        if "LIMIT" not in query.upper():
            query = f"{query} LIMIT {limit}"

        job = self._client.query(query)
        results = job.result()

        columns = [field.name for field in results.schema]
        rows = [list(row.values()) for row in results]

        return QueryResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            execution_time_ms=(time.time() - start) * 1000,
            metadata={
                "bytes_processed": job.total_bytes_processed,
                "cache_hit": job.cache_hit
            }
        )

    async def get_schema(self) -> dict:
        datasets = list(self._client.list_datasets())
        schema = {}
        for dataset in datasets:
            tables = list(self._client.list_tables(dataset.dataset_id))
            schema[dataset.dataset_id] = [t.table_id for t in tables]
        return schema

    # ... other methods
```

#### Connector Factory

```python
# app/modules/data_source/services/connection_manager.py

from typing import Type
from ..connectors.base import BaseConnector, ConnectionConfig
from ..connectors.postgresql import PostgreSQLConnector
from ..connectors.mysql import MySQLConnector
from ..connectors.sqlite import SQLiteConnector
from ..connectors.bigquery import BigQueryConnector
from ..connectors.snowflake import SnowflakeConnector
from ..connectors.redshift import RedshiftConnector
from ..connectors.duckdb import DuckDBConnector

class ConnectionManager:
    """Factory and registry for data source connectors."""

    _connectors: dict[str, Type[BaseConnector]] = {
        "postgresql": PostgreSQLConnector,
        "mysql": MySQLConnector,
        "sqlite": SQLiteConnector,
        "bigquery": BigQueryConnector,
        "snowflake": SnowflakeConnector,
        "redshift": RedshiftConnector,
        "duckdb": DuckDBConnector,
    }

    _active_connections: dict[str, BaseConnector] = {}

    @classmethod
    def register_connector(cls, name: str, connector_class: Type[BaseConnector]):
        """Register a new connector type."""
        cls._connectors[name] = connector_class

    @classmethod
    async def create_connection(cls, config: ConnectionConfig) -> BaseConnector:
        """Create and return a connector instance."""
        connector_class = cls._connectors.get(config.connection_type)
        if not connector_class:
            raise ValueError(f"Unknown connector type: {config.connection_type}")

        connector = connector_class(config)
        await connector.connect()
        cls._active_connections[config.alias] = connector
        return connector

    @classmethod
    def get_connection(cls, alias: str) -> Optional[BaseConnector]:
        """Get an existing connection by alias."""
        return cls._active_connections.get(alias)

    @classmethod
    async def close_connection(cls, alias: str) -> None:
        """Close and remove a connection."""
        connector = cls._active_connections.pop(alias, None)
        if connector:
            await connector.disconnect()
```

### 4.2 File Handler System

```python
# app/modules/data_source/file_readers/base.py

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Any
import pandas as pd
from pydantic import BaseModel

class FileMetadata(BaseModel):
    """Metadata about a file."""
    path: str
    size_bytes: int
    format: str
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    columns: Optional[list[str]] = None
    preview_rows: Optional[list[dict]] = None

class BaseFileReader(ABC):
    """Abstract base class for file readers."""

    supported_extensions: list[str]

    @abstractmethod
    async def read(
        self,
        path: Path,
        limit: Optional[int] = None,
        columns: Optional[list[str]] = None
    ) -> pd.DataFrame:
        """Read file into DataFrame."""
        pass

    @abstractmethod
    async def get_metadata(self, path: Path) -> FileMetadata:
        """Get file metadata without full read."""
        pass

    @abstractmethod
    async def get_schema(self, path: Path) -> list[dict]:
        """Get column schema information."""
        pass


# app/modules/data_source/file_readers/parquet_reader.py

class ParquetReader(BaseFileReader):
    supported_extensions = [".parquet", ".pq"]

    async def read(
        self,
        path: Path,
        limit: Optional[int] = None,
        columns: Optional[list[str]] = None
    ) -> pd.DataFrame:
        import pyarrow.parquet as pq

        table = pq.read_table(
            path,
            columns=columns
        )
        df = table.to_pandas()

        if limit:
            df = df.head(limit)

        return df

    async def get_metadata(self, path: Path) -> FileMetadata:
        import pyarrow.parquet as pq

        pf = pq.ParquetFile(path)
        schema = pf.schema_arrow

        return FileMetadata(
            path=str(path),
            size_bytes=path.stat().st_size,
            format="parquet",
            row_count=pf.metadata.num_rows,
            column_count=len(schema),
            columns=[f.name for f in schema]
        )
```

### 4.3 Visualization Service

```python
# app/modules/visualization/services/chart_service.py

from typing import Optional, Any
import plotly.graph_objects as go
import plotly.express as px
from pydantic import BaseModel
import pandas as pd

class ChartConfig(BaseModel):
    """Configuration for chart generation."""
    chart_type: str
    title: Optional[str] = None
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    color_column: Optional[str] = None
    size_column: Optional[str] = None
    theme: str = "default"
    width: int = 800
    height: int = 600
    interactive: bool = True

class ChartResult(BaseModel):
    """Result of chart generation."""
    chart_type: str
    html: Optional[str] = None
    json: Optional[dict] = None
    image_base64: Optional[str] = None
    config: ChartConfig

class ChartService:
    """Service for generating interactive visualizations."""

    CHART_MAPPING = {
        "line": px.line,
        "bar": px.bar,
        "scatter": px.scatter,
        "pie": px.pie,
        "histogram": px.histogram,
        "box": px.box,
        "violin": px.violin,
        "heatmap": px.imshow,
        "treemap": px.treemap,
        "sunburst": px.sunburst,
        "funnel": px.funnel,
        "scatter_3d": px.scatter_3d,
        "parallel_coordinates": px.parallel_coordinates,
    }

    def __init__(self, theme_service: "ThemeService"):
        self.theme_service = theme_service

    async def recommend_chart_type(
        self,
        df: pd.DataFrame,
        intent: Optional[str] = None
    ) -> str:
        """AI-assisted chart type recommendation."""
        # Analyze data characteristics
        num_columns = df.select_dtypes(include=['number']).columns
        cat_columns = df.select_dtypes(include=['object', 'category']).columns
        date_columns = df.select_dtypes(include=['datetime']).columns

        # Rule-based recommendations
        if len(date_columns) > 0 and len(num_columns) > 0:
            return "line"  # Time series
        elif len(cat_columns) == 1 and len(num_columns) == 1:
            return "bar"  # Category comparison
        elif len(num_columns) >= 2:
            return "scatter"  # Correlation
        elif len(cat_columns) == 1 and len(num_columns) == 0:
            return "pie"  # Distribution
        else:
            return "bar"  # Default

    async def generate_chart(
        self,
        df: pd.DataFrame,
        config: ChartConfig
    ) -> ChartResult:
        """Generate a chart from DataFrame."""
        chart_func = self.CHART_MAPPING.get(config.chart_type)
        if not chart_func:
            raise ValueError(f"Unknown chart type: {config.chart_type}")

        # Build chart arguments
        kwargs = {
            "data_frame": df,
            "title": config.title,
        }

        if config.x_column:
            kwargs["x"] = config.x_column
        if config.y_column:
            kwargs["y"] = config.y_column
        if config.color_column:
            kwargs["color"] = config.color_column

        # Create figure
        fig = chart_func(**kwargs)

        # Apply theme
        theme = self.theme_service.get_theme(config.theme)
        fig.update_layout(template=theme.plotly_template)

        # Set dimensions
        fig.update_layout(width=config.width, height=config.height)

        # Generate outputs
        return ChartResult(
            chart_type=config.chart_type,
            html=fig.to_html(include_plotlyjs="cdn") if config.interactive else None,
            json=fig.to_dict(),
            config=config
        )

    async def export_chart(
        self,
        result: ChartResult,
        format: str,
        path: Optional[str] = None
    ) -> bytes:
        """Export chart to various formats."""
        fig = go.Figure(result.json)

        if format == "html":
            return fig.to_html(include_plotlyjs="cdn").encode()
        elif format == "png":
            return fig.to_image(format="png", scale=2)
        elif format == "svg":
            return fig.to_image(format="svg")
        elif format == "pdf":
            return fig.to_image(format="pdf")
        else:
            raise ValueError(f"Unknown export format: {format}")
```

### 4.4 Analytics Engine

```python
# app/modules/analytics/services/statistical_service.py

from typing import Optional, Any
from pydantic import BaseModel
import pandas as pd
import numpy as np
from scipy import stats

class StatisticalTestResult(BaseModel):
    """Result of a statistical test."""
    test_name: str
    statistic: float
    p_value: float
    degrees_of_freedom: Optional[float] = None
    confidence_level: float = 0.95
    is_significant: bool
    interpretation: str
    details: dict = {}

class StatisticalService:
    """Service for statistical analysis."""

    async def t_test(
        self,
        group1: pd.Series,
        group2: pd.Series,
        alternative: str = "two-sided"
    ) -> StatisticalTestResult:
        """Perform independent samples t-test."""
        statistic, p_value = stats.ttest_ind(group1, group2, alternative=alternative)

        is_significant = p_value < 0.05

        interpretation = (
            f"The difference between groups is "
            f"{'statistically significant' if is_significant else 'not statistically significant'} "
            f"(p = {p_value:.4f}). "
        )

        if is_significant:
            mean_diff = group1.mean() - group2.mean()
            interpretation += (
                f"Group 1 mean ({group1.mean():.2f}) is "
                f"{'higher' if mean_diff > 0 else 'lower'} than "
                f"Group 2 mean ({group2.mean():.2f}) by {abs(mean_diff):.2f}."
            )

        return StatisticalTestResult(
            test_name="Independent Samples T-Test",
            statistic=float(statistic),
            p_value=float(p_value),
            degrees_of_freedom=float(len(group1) + len(group2) - 2),
            is_significant=is_significant,
            interpretation=interpretation,
            details={
                "group1_mean": float(group1.mean()),
                "group1_std": float(group1.std()),
                "group2_mean": float(group2.mean()),
                "group2_std": float(group2.std()),
                "effect_size_cohens_d": self._cohens_d(group1, group2)
            }
        )

    async def anova(
        self,
        *groups: pd.Series
    ) -> StatisticalTestResult:
        """Perform one-way ANOVA."""
        statistic, p_value = stats.f_oneway(*groups)
        is_significant = p_value < 0.05

        interpretation = (
            f"There {'is' if is_significant else 'is no'} "
            f"statistically significant difference between groups "
            f"(F = {statistic:.2f}, p = {p_value:.4f})."
        )

        return StatisticalTestResult(
            test_name="One-Way ANOVA",
            statistic=float(statistic),
            p_value=float(p_value),
            degrees_of_freedom=float(len(groups) - 1),
            is_significant=is_significant,
            interpretation=interpretation,
            details={
                "group_means": [float(g.mean()) for g in groups],
                "group_counts": [len(g) for g in groups]
            }
        )

    async def chi_square(
        self,
        observed: pd.DataFrame
    ) -> StatisticalTestResult:
        """Perform chi-square test of independence."""
        statistic, p_value, dof, expected = stats.chi2_contingency(observed)
        is_significant = p_value < 0.05

        interpretation = (
            f"There {'is' if is_significant else 'is no'} "
            f"statistically significant association between variables "
            f"(χ² = {statistic:.2f}, p = {p_value:.4f})."
        )

        return StatisticalTestResult(
            test_name="Chi-Square Test of Independence",
            statistic=float(statistic),
            p_value=float(p_value),
            degrees_of_freedom=float(dof),
            is_significant=is_significant,
            interpretation=interpretation,
            details={
                "expected_frequencies": expected.tolist()
            }
        )

    async def correlation_matrix(
        self,
        df: pd.DataFrame,
        method: str = "pearson"
    ) -> pd.DataFrame:
        """Calculate correlation matrix."""
        return df.corr(method=method)

    def _cohens_d(self, group1: pd.Series, group2: pd.Series) -> float:
        """Calculate Cohen's d effect size."""
        n1, n2 = len(group1), len(group2)
        var1, var2 = group1.var(), group2.var()
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        return float((group1.mean() - group2.mean()) / pooled_std)


# app/modules/analytics/services/forecasting_service.py

class ForecastResult(BaseModel):
    """Result of a forecast."""
    model_name: str
    forecast_values: list[float]
    forecast_dates: list[str]
    lower_bound: list[float]
    upper_bound: list[float]
    confidence_level: float
    metrics: dict = {}
    interpretation: str

class ForecastingService:
    """Service for time series forecasting."""

    async def forecast_prophet(
        self,
        df: pd.DataFrame,
        date_column: str,
        value_column: str,
        periods: int = 30,
        confidence_level: float = 0.95
    ) -> ForecastResult:
        """Forecast using Facebook Prophet."""
        from prophet import Prophet

        # Prepare data for Prophet
        prophet_df = df[[date_column, value_column]].rename(
            columns={date_column: "ds", value_column: "y"}
        )

        # Fit model
        model = Prophet(interval_width=confidence_level)
        model.fit(prophet_df)

        # Make future dataframe
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)

        # Extract forecast period only
        forecast_only = forecast.tail(periods)

        return ForecastResult(
            model_name="Prophet",
            forecast_values=forecast_only["yhat"].tolist(),
            forecast_dates=forecast_only["ds"].dt.strftime("%Y-%m-%d").tolist(),
            lower_bound=forecast_only["yhat_lower"].tolist(),
            upper_bound=forecast_only["yhat_upper"].tolist(),
            confidence_level=confidence_level,
            metrics={
                "trend": "increasing" if forecast_only["yhat"].iloc[-1] > forecast_only["yhat"].iloc[0] else "decreasing"
            },
            interpretation=self._generate_interpretation(forecast_only)
        )

    def _generate_interpretation(self, forecast: pd.DataFrame) -> str:
        """Generate human-readable forecast interpretation."""
        start_val = forecast["yhat"].iloc[0]
        end_val = forecast["yhat"].iloc[-1]
        change_pct = ((end_val - start_val) / start_val) * 100

        return (
            f"The forecast shows a {'positive' if change_pct > 0 else 'negative'} "
            f"trend with an expected change of {abs(change_pct):.1f}% "
            f"over the forecast period."
        )
```

### 4.5 Notebook System

```python
# app/modules/notebook/models.py

from typing import Optional, Any, Union
from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class CellType(str, Enum):
    QUERY = "query"
    VISUALIZATION = "visualization"
    TEXT = "text"
    CODE = "code"
    USER_INPUT = "user_input"

class CellStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Cell(BaseModel):
    """A single cell in a notebook."""
    id: str
    type: CellType
    name: str
    prompt: Optional[str] = None
    code: Optional[str] = None
    depends_on: Optional[list[str]] = None
    output: Optional[Any] = None
    status: CellStatus = CellStatus.PENDING
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None

class Parameter(BaseModel):
    """A notebook parameter."""
    name: str
    type: str  # date, select, text, number
    default: Optional[Any] = None
    options: Optional[list[str]] = None
    description: Optional[str] = None

class Notebook(BaseModel):
    """A reusable analysis notebook."""
    id: str
    name: str
    description: Optional[str] = None
    parameters: list[Parameter] = []
    cells: list[Cell] = []
    created_at: datetime
    updated_at: datetime
    tags: list[str] = []
    database_alias: Optional[str] = None

class NotebookRun(BaseModel):
    """A single execution of a notebook."""
    id: str
    notebook_id: str
    parameters: dict[str, Any]
    status: str  # pending, running, completed, failed
    started_at: datetime
    completed_at: Optional[datetime] = None
    results: dict[str, Any] = {}
    error: Optional[str] = None


# app/modules/notebook/services/executor_service.py

class NotebookExecutor:
    """Service for executing notebooks."""

    def __init__(
        self,
        sql_service: "SQLGenerationService",
        analysis_service: "AnalysisService",
        chart_service: "ChartService",
        agent_service: "AutonomousAgentService"
    ):
        self.sql_service = sql_service
        self.analysis_service = analysis_service
        self.chart_service = chart_service
        self.agent_service = agent_service

    async def execute_notebook(
        self,
        notebook: Notebook,
        parameters: dict[str, Any],
        database_alias: str
    ) -> NotebookRun:
        """Execute a notebook with given parameters."""
        run = NotebookRun(
            id=generate_id(),
            notebook_id=notebook.id,
            parameters=parameters,
            status="running",
            started_at=datetime.utcnow()
        )

        # Build execution context
        context = {
            "parameters": parameters,
            "results": {},
            "database_alias": database_alias
        }

        # Execute cells in dependency order
        execution_order = self._resolve_dependencies(notebook.cells)

        try:
            for cell in execution_order:
                result = await self._execute_cell(cell, context)
                context["results"][cell.name] = result
                run.results[cell.name] = result

            run.status = "completed"
        except Exception as e:
            run.status = "failed"
            run.error = str(e)

        run.completed_at = datetime.utcnow()
        return run

    async def _execute_cell(
        self,
        cell: Cell,
        context: dict
    ) -> Any:
        """Execute a single cell."""
        # Interpolate parameters in prompt
        prompt = self._interpolate(cell.prompt, context)

        if cell.type == CellType.QUERY:
            # Use autonomous agent for SQL generation and execution
            result = await self.agent_service.run(
                prompt=prompt,
                database_alias=context["database_alias"]
            )
            return result

        elif cell.type == CellType.VISUALIZATION:
            # Get data from dependent cell
            data = context["results"].get(cell.depends_on[0]) if cell.depends_on else None
            result = await self.chart_service.generate_from_prompt(
                prompt=prompt,
                data=data
            )
            return result

        elif cell.type == CellType.TEXT:
            # Use LLM for text generation
            result = await self.agent_service.generate_text(
                prompt=prompt,
                context=context["results"]
            )
            return result

        elif cell.type == CellType.CODE:
            # Execute Python code
            result = await self._execute_code(cell.code, context)
            return result

    def _interpolate(self, template: str, context: dict) -> str:
        """Interpolate parameters into template."""
        import re

        def replace(match):
            key = match.group(1)
            if key in context["parameters"]:
                return str(context["parameters"][key])
            elif key in context["results"]:
                return str(context["results"][key])
            return match.group(0)

        return re.sub(r"\{\{(\w+)\}\}", replace, template)

    def _resolve_dependencies(self, cells: list[Cell]) -> list[Cell]:
        """Topological sort of cells by dependencies."""
        # ... implementation
        pass
```

---

## 5. API Design

### 5.1 New API Endpoints

#### Data Source API

```yaml
# File Analysis
POST /api/v2/files/upload
  - Upload a file for analysis
  - Returns: file_id, metadata, schema

GET /api/v2/files/{file_id}
  - Get file metadata and preview

POST /api/v2/files/{file_id}/analyze
  - Analyze file with natural language query
  - Body: { "prompt": "...", "output_format": "json|chart" }

POST /api/v2/files/{file_id}/query
  - Query file using DuckDB SQL
  - Body: { "sql": "SELECT * FROM data WHERE..." }

# Cloud Connections
POST /api/v2/connections/bigquery
POST /api/v2/connections/snowflake
POST /api/v2/connections/redshift
POST /api/v2/connections/duckdb
```

#### Visualization API

```yaml
POST /api/v2/visualizations/generate
  - Generate chart from data
  - Body: {
      "data": [...] or "query_result_id": "...",
      "chart_type": "line|bar|scatter|...",
      "config": { ... }
    }

POST /api/v2/visualizations/recommend
  - Get chart type recommendation
  - Body: { "data": [...], "intent": "compare|trend|distribute" }

GET /api/v2/visualizations/{viz_id}
  - Get visualization by ID

POST /api/v2/visualizations/{viz_id}/export
  - Export to format (html, png, svg, pdf)
  - Body: { "format": "png", "dpi": 300 }

GET /api/v2/visualizations/themes
  - List available themes

POST /api/v2/visualizations/themes
  - Create custom theme
```

#### Analytics API

```yaml
POST /api/v2/analytics/statistics
  - Run statistical tests
  - Body: {
      "test_type": "t_test|anova|chi_square|correlation",
      "data": [...],
      "groups": ["group1", "group2"]
    }

POST /api/v2/analytics/forecast
  - Generate time series forecast
  - Body: {
      "data": [...],
      "date_column": "date",
      "value_column": "sales",
      "periods": 30
    }

POST /api/v2/analytics/anomalies
  - Detect anomalies
  - Body: {
      "data": [...],
      "method": "zscore|iqr|isolation_forest",
      "threshold": 3.0
    }

POST /api/v2/analytics/profile
  - Profile dataset
  - Body: { "data": [...] }
```

#### Notebook API

```yaml
POST /api/v2/notebooks
  - Create notebook
  - Body: { "name": "...", "cells": [...], "parameters": [...] }

GET /api/v2/notebooks
  - List notebooks
  - Query: ?tags=sales&limit=10

GET /api/v2/notebooks/{notebook_id}
  - Get notebook details

PUT /api/v2/notebooks/{notebook_id}
  - Update notebook

DELETE /api/v2/notebooks/{notebook_id}
  - Delete notebook

POST /api/v2/notebooks/{notebook_id}/run
  - Execute notebook
  - Body: { "parameters": { "start_date": "2025-01-01" } }

GET /api/v2/notebooks/{notebook_id}/runs
  - List notebook runs

GET /api/v2/notebooks/{notebook_id}/runs/{run_id}
  - Get run details and results

# Templates
GET /api/v2/notebooks/templates
  - List available templates

POST /api/v2/notebooks/from-template
  - Create notebook from template
  - Body: { "template_id": "sales-analysis" }
```

#### Streaming API

```yaml
# Server-Sent Events
GET /api/v2/analysis/{task_id}/stream
  - Stream analysis progress and results
  - Content-Type: text/event-stream

# WebSocket
WS /api/v2/sessions/{session_id}/ws
  - Interactive session via WebSocket
  - Messages: { "type": "query", "content": "..." }
```

### 5.2 API Response Formats

```python
# Standard response wrapper
class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: dict = {}

# Paginated response
class PaginatedResponse(APIResponse):
    total: int
    page: int
    page_size: int
    has_more: bool

# Streaming event
class StreamEvent(BaseModel):
    event: str  # progress, result, error, complete
    data: Any
    timestamp: datetime
```

---

## 6. CLI Design

### 6.1 Enhanced CLI Structure

```bash
kai-agent
├── connection          # Database connections
│   ├── create          # Create new connection
│   ├── list            # List connections
│   ├── test            # Test connection
│   └── delete          # Remove connection
├── file                # File operations (NEW)
│   ├── upload          # Upload file
│   ├── list            # List uploaded files
│   ├── analyze         # Analyze file
│   ├── query           # Query file with SQL
│   └── delete          # Remove file
├── run                 # One-shot analysis
├── interactive         # Interactive session
├── notebook            # Notebook operations (NEW)
│   ├── create          # Create notebook
│   ├── list            # List notebooks
│   ├── run             # Execute notebook
│   ├── schedule        # Schedule notebook
│   └── export          # Export results
├── visualize           # Visualization (NEW)
│   ├── generate        # Generate chart
│   ├── themes          # Manage themes
│   └── export          # Export chart
├── stats               # Statistical analysis (NEW)
│   ├── describe        # Descriptive statistics
│   ├── test            # Statistical tests
│   └── correlate       # Correlation analysis
├── forecast            # Forecasting (NEW)
│   ├── predict         # Generate forecast
│   └── detect          # Anomaly detection
├── profile             # Data profiling (NEW)
│   ├── run             # Profile data
│   └── report          # Generate report
├── skill               # Skill management
│   ├── list
│   ├── search
│   └── create
├── memory              # Memory management
│   ├── list
│   ├── search
│   └── clear
└── mdl                 # Semantic layer
    ├── generate
    ├── validate
    └── export
```

### 6.2 CLI Examples

```bash
# File Analysis
kai-agent file upload ./sales_data.csv
kai-agent file analyze sales_data.csv "What are the top 10 products?"
kai-agent file query sales_data.csv "SELECT region, SUM(revenue) FROM data GROUP BY region"

# BigQuery Connection
kai-agent connection create bigquery://my-project \
  --credentials ./service-account.json \
  --alias my-bigquery

# Visualization
kai-agent run "Show monthly revenue trend" --db mydb --chart line --output revenue.html
kai-agent visualize generate --data results.json --type treemap --theme dark

# Statistical Analysis
kai-agent stats test "Is there a significant difference in sales between North and South?" --db mydb
kai-agent stats correlate --db mydb --table orders --columns price,quantity,discount

# Forecasting
kai-agent forecast predict "Forecast next 30 days of orders" --db mydb
kai-agent forecast detect "Find anomalies in transaction amounts" --db mydb

# Notebooks
kai-agent notebook create monthly-review --from-template sales-analysis
kai-agent notebook run monthly-review --param start_date=2025-11-01
kai-agent notebook schedule monthly-review --cron "0 8 1 * *"
kai-agent notebook export monthly-review --format pdf --output ./reports/

# Data Profiling
kai-agent profile run --db mydb --table customers --output profile.html
kai-agent profile run --file ./data.csv
```

---

## 7. Data Flow Diagrams

### 7.1 File Analysis Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   User       │     │   CLI/API    │     │    File      │
│   uploads    │────▶│   receives   │────▶│   Handler    │
│   CSV file   │     │   file       │     │   reads file │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Return     │     │   Agent      │     │   DuckDB     │
│   results    │◀────│   analyzes   │◀────│   creates    │
│   to user    │     │   data       │     │   in-memory  │
└──────────────┘     └──────────────┘     │   table      │
                                          └──────────────┘
```

### 7.2 Notebook Execution Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   User       │     │   Notebook   │     │   Parameter  │
│   triggers   │────▶│   Executor   │────▶│   Resolution │
│   notebook   │     │   starts     │     │              │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
        ┌─────────────────────────────────────────┘
        │
        ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Cell 1     │     │   Cell 2     │     │   Cell N     │
│   Query      │────▶│   Viz        │────▶│   Text       │
│   executes   │     │   generates  │     │   summarizes │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
                                          ┌──────────────┐
                                          │   Results    │
                                          │   assembled  │
                                          │   & exported │
                                          └──────────────┘
```

---

## 8. Security Considerations

### 8.1 Credential Management

```python
# All credentials encrypted at rest
class CredentialManager:
    def __init__(self, encryption_key: str):
        self.fernet = Fernet(encryption_key.encode())

    def encrypt(self, credential: str) -> str:
        return self.fernet.encrypt(credential.encode()).decode()

    def decrypt(self, encrypted: str) -> str:
        return self.fernet.decrypt(encrypted.encode()).decode()
```

### 8.2 Query Safety

```python
# Prevent destructive queries by default
class QuerySafetyChecker:
    DANGEROUS_PATTERNS = [
        r"\bDROP\b",
        r"\bDELETE\b",
        r"\bTRUNCATE\b",
        r"\bALTER\b",
        r"\bUPDATE\b",
        r"\bINSERT\b",
    ]

    def is_safe(self, query: str) -> bool:
        query_upper = query.upper()
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, query_upper):
                return False
        return True
```

### 8.3 File Isolation

- Uploaded files stored with user-specific prefixes
- Temporary files cleaned after session
- No cross-user file access

---

## 9. Performance Considerations

### 9.1 Caching Strategy

```python
# Query result caching
class QueryCache:
    def __init__(self, ttl_seconds: int = 300):
        self.cache = TTLCache(maxsize=1000, ttl=ttl_seconds)

    def cache_key(self, query: str, params: dict) -> str:
        return hashlib.md5(
            f"{query}:{json.dumps(params, sort_keys=True)}".encode()
        ).hexdigest()

    async def get_or_execute(
        self,
        key: str,
        executor: Callable
    ) -> QueryResult:
        if key in self.cache:
            return self.cache[key]
        result = await executor()
        self.cache[key] = result
        return result
```

### 9.2 Connection Pooling

- SQLAlchemy connection pools for relational DBs
- Lazy connection initialization
- Connection health checks

### 9.3 Streaming for Large Results

- Server-Sent Events for progress updates
- Chunked query result streaming
- Background task processing for long analyses

---

## 10. Testing Strategy

### 10.1 Test Categories

| Category | Description | Tools |
|----------|-------------|-------|
| Unit Tests | Individual components | pytest, pytest-asyncio |
| Integration Tests | Service interactions | pytest, testcontainers |
| Connector Tests | Data source connectors | pytest, mocked clients |
| CLI Tests | Command-line interface | click.testing |
| API Tests | REST endpoints | httpx, pytest |

### 10.2 Test Data

- Sample CSV/Excel/Parquet files
- Mock database schemas
- Notebook templates for testing

---

## 11. Migration Plan

### Phase 1: Non-Breaking Additions
- Add new modules without modifying existing
- New API version (v2) alongside v1
- CLI commands additive

### Phase 2: Connector Refactoring
- Abstract existing PostgreSQL/MySQL/SQLite behind BaseConnector
- No user-facing changes initially

### Phase 3: Visualization Upgrade
- Add Plotly alongside matplotlib
- Gradual deprecation of matplotlib-only paths

### Phase 4: Full Integration
- Unify all data sources under ConnectionManager
- Complete notebook system
- Statistical/forecasting services active

---

## 12. Dependencies

### New Dependencies

```toml
# pyproject.toml additions

[project.dependencies]
# Data Sources
google-cloud-bigquery = "^3.0"
snowflake-connector-python = "^3.0"
redshift-connector = "^2.0"
duckdb = "^0.9"

# Visualization
plotly = "^5.18"
kaleido = "^0.2"  # For static export

# Analytics
prophet = "^1.1"
statsmodels = "^0.14"
scipy = "^1.11"

# CLI Enhancement
rich = "^13.0"
click = "^8.1"

# Scheduling
apscheduler = "^3.10"

# File Handling
pyarrow = "^14.0"
openpyxl = "^3.1"
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-06 | BMad Master | Initial architecture document |

---

*This Architecture Document was generated by BMad Master as part of the YOLO workflow execution.*
