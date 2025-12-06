# Implementation Plan: MDL & GENBI for KAI

## Executive Summary

This document outlines a comprehensive plan to implement **MDL (Model Definition Language)** and **GENBI (Generative Business Intelligence)** capabilities in KAI, drawing inspiration from WrenAI's architecture while leveraging KAI's existing strengths.

---

## Part 1: Architecture Comparison

### WrenAI Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    WREN AI ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────┤
│  Frontend (wren-ui)          Next.js + Apollo GraphQL       │
│  Backend (wren-ai-service)   FastAPI + Haystack + Hamilton  │
│  Vector DB                   Qdrant                         │
│  LLM Provider                LiteLLM (multi-provider)       │
│  Semantic Layer              MDL (JSON Schema)              │
└─────────────────────────────────────────────────────────────┘
```

### KAI Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     KAI ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────┤
│  Backend                     FastAPI + LangGraph            │
│  Vector DB                   Typesense                      │
│  LLM Provider                Multi-provider (OpenAI/Gemini) │
│  Agent Framework             DeepAgents + LangChain         │
│  Semantic Layer              TableDescription + Glossary    │
└─────────────────────────────────────────────────────────────┘
```

### Key Differences

| Aspect | WrenAI | KAI |
|--------|--------|-----|
| **Semantic Layer** | MDL (comprehensive JSON schema) | Fragmented (TableDescription, BusinessGlossary, Instructions) |
| **Relationships** | Explicit in MDL with join types | Implicit via FK in ColumnDescription |
| **Metrics** | First-class MDL entity with dimensions/measures | BusinessGlossary (SQL templates only) |
| **Calculated Fields** | Expression-based in MDL columns | Not supported |
| **Views** | MDL views with SQL statements | Not supported |
| **Caching** | MDL-level cache configuration | Not supported |
| **Access Control** | Row/Column level in MDL | Not supported |
| **Chart Generation** | Dedicated pipeline with Vega-Lite | ChartRecommendation (basic) |
| **Pipeline Framework** | Haystack + Hamilton (async DAG) | LangGraph + DeepAgents |

---

## Part 2: Gap Analysis

### What KAI Has That Maps to MDL

| KAI Component | MDL Equivalent | Gap |
|---------------|----------------|-----|
| `TableDescription` | `models` | Missing: refSql, calculated fields, caching |
| `ColumnDescription` | `columns` | Missing: expressions, relationship refs, access control |
| `BusinessGlossary` | `metrics` (partial) | Missing: dimensions, measures, timeGrain |
| `ForeignKeyDetail` | `relationships` | Missing: join types, explicit conditions |
| N/A | `views` | **Complete gap** |
| N/A | `enumDefinitions` | **Complete gap** |
| N/A | `accessControls` | **Complete gap** |

### What KAI Has That WrenAI Doesn't

| KAI Feature | Notes |
|-------------|-------|
| Long-term Memory | Session-scoped + shared memory system |
| Skills System | Reusable analysis patterns |
| Autonomous Agents | Multi-step task execution with subagents |
| Interactive Sessions | LangGraph-based multi-turn conversations |
| RAG Documents | Document search integration |
| MCP Integration | External tool connectivity |

---

## Part 3: Implementation Strategy

### Phase 1: MDL Schema & Models (4-6 weeks)

#### 1.1 Create MDL Schema Definition

**File**: `app/modules/mdl/schema/mdl.schema.json`

Adapt WrenAI's schema with KAI-specific extensions:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://kai.dev/mdl.schema.json",
  "title": "KAI MDL Manifest Schema",
  "type": "object",
  "properties": {
    "catalog": { "type": "string" },
    "schema": { "type": "string" },
    "dataSource": { "type": "string", "enum": ["postgresql", "mysql", "bigquery", "duckdb", "sqlite"] },
    "models": { "$ref": "#/$defs/models" },
    "relationships": { "$ref": "#/$defs/relationships" },
    "metrics": { "$ref": "#/$defs/metrics" },
    "views": { "$ref": "#/$defs/views" },
    "enumDefinitions": { "$ref": "#/$defs/enumDefinitions" }
  },
  "$defs": {
    // ... (full schema definitions)
  }
}
```

#### 1.2 Create MDL Models

**File**: `app/modules/mdl/models/__init__.py`

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class JoinType(str, Enum):
    ONE_TO_ONE = "ONE_TO_ONE"
    ONE_TO_MANY = "ONE_TO_MANY"
    MANY_TO_ONE = "MANY_TO_ONE"
    MANY_TO_MANY = "MANY_TO_MANY"

class MDLColumn(BaseModel):
    name: str
    type: str
    relationship: Optional[str] = None
    is_calculated: bool = False
    not_null: bool = False
    expression: Optional[str] = None
    is_hidden: bool = False
    properties: Dict[str, Any] = {}

class TableReference(BaseModel):
    catalog: Optional[str] = None
    schema: Optional[str] = None
    table: str

class MDLModel(BaseModel):
    name: str
    table_reference: Optional[TableReference] = None
    ref_sql: Optional[str] = None
    columns: List[MDLColumn] = []
    primary_key: Optional[str] = None
    cached: bool = False
    refresh_time: Optional[str] = None
    properties: Dict[str, Any] = {}

class MDLRelationship(BaseModel):
    name: str
    models: List[str]  # Exactly 2 models
    join_type: JoinType
    condition: str
    properties: Dict[str, Any] = {}

class TimeGrain(BaseModel):
    name: str
    ref_column: str
    date_parts: List[str]  # YEAR, QUARTER, MONTH, WEEK, DAY, etc.

class MDLMetric(BaseModel):
    name: str
    base_object: str  # Reference to model
    dimension: List[MDLColumn] = []
    measure: List[MDLColumn] = []
    time_grain: List[TimeGrain] = []
    cached: bool = False
    refresh_time: Optional[str] = None
    properties: Dict[str, Any] = {}

class MDLView(BaseModel):
    name: str
    statement: str  # SQL statement
    properties: Dict[str, Any] = {}

class EnumValue(BaseModel):
    name: str
    value: Optional[str] = None
    properties: Dict[str, Any] = {}

class MDLEnumDefinition(BaseModel):
    name: str
    values: List[EnumValue]
    properties: Dict[str, Any] = {}

class MDLManifest(BaseModel):
    """Complete MDL Manifest for a database connection."""
    id: Optional[str] = None
    db_connection_id: str
    catalog: str
    schema: str
    data_source: str
    models: List[MDLModel] = []
    relationships: List[MDLRelationship] = []
    metrics: List[MDLMetric] = []
    views: List[MDLView] = []
    enum_definitions: List[MDLEnumDefinition] = []
    mdl_hash: Optional[str] = None  # For caching/versioning
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
```

#### 1.3 Create MDL Builder Service

**File**: `app/modules/mdl/services/mdl_builder.py`

```python
class MDLBuilder:
    """Build MDL manifest from KAI's existing data structures."""

    def __init__(
        self,
        table_descriptions: List[TableDescription],
        business_glossaries: List[BusinessGlossary],
        db_connection: DatabaseConnection,
    ):
        self.table_descriptions = table_descriptions
        self.business_glossaries = business_glossaries
        self.db_connection = db_connection
        self.manifest = MDLManifest(
            db_connection_id=db_connection.id,
            catalog=db_connection.alias,
            schema=db_connection.schemas[0] if db_connection.schemas else "public",
            data_source=db_connection.dialect,
        )

    def build(self) -> MDLManifest:
        """Build complete MDL manifest."""
        self._add_models()
        self._add_relationships()
        self._add_metrics()
        self._compute_hash()
        return self.manifest

    def _add_models(self):
        """Convert TableDescriptions to MDL Models."""
        for td in self.table_descriptions:
            model = MDLModel(
                name=td.table_name,
                table_reference=TableReference(
                    schema=td.db_schema,
                    table=td.table_name,
                ),
                columns=[
                    MDLColumn(
                        name=col.name,
                        type=col.data_type,
                        not_null=col.is_primary_key,
                        properties={
                            "description": col.description,
                            "low_cardinality": col.low_cardinality,
                            "categories": col.categories,
                        }
                    )
                    for col in td.columns
                ],
                primary_key=next(
                    (col.name for col in td.columns if col.is_primary_key),
                    None
                ),
                properties={
                    "description": td.table_description,
                    "displayName": td.table_name,
                }
            )
            self.manifest.models.append(model)

    def _add_relationships(self):
        """Extract relationships from foreign keys."""
        for td in self.table_descriptions:
            for col in td.columns:
                if col.foreign_key:
                    rel = MDLRelationship(
                        name=f"{td.table_name}_{col.name}_fk",
                        models=[td.table_name, col.foreign_key.reference_table],
                        join_type=JoinType.MANY_TO_ONE,
                        condition=f'"{td.table_name}".{col.name} = "{col.foreign_key.reference_table}".{col.foreign_key.field_name}'
                    )
                    self.manifest.relationships.append(rel)

    def _add_metrics(self):
        """Convert BusinessGlossary to MDL Metrics."""
        for bg in self.business_glossaries:
            # Parse SQL to extract dimensions/measures (simplified)
            metric = MDLMetric(
                name=bg.metric,
                base_object=self._extract_base_table(bg.sql),
                measure=[
                    MDLColumn(
                        name=bg.metric,
                        type="DECIMAL",
                        is_calculated=True,
                        expression=bg.sql,
                    )
                ],
                properties={
                    "alias": bg.alias,
                    "sql": bg.sql,
                }
            )
            self.manifest.metrics.append(metric)

    def _compute_hash(self):
        """Compute MD5 hash of manifest for caching."""
        import hashlib
        content = self.manifest.model_dump_json()
        self.manifest.mdl_hash = hashlib.md5(content.encode()).hexdigest()
```

#### 1.4 Create MDL Repository & Service

**File**: `app/modules/mdl/repositories/__init__.py`

```python
class MDLManifestRepository:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.collection_name = "mdl_manifests"

    def save(self, manifest: MDLManifest) -> MDLManifest:
        """Save or update MDL manifest."""
        data = manifest.model_dump()
        if manifest.id:
            self.storage.update(self.collection_name, manifest.id, data)
        else:
            manifest.id = self.storage.insert(self.collection_name, data)
        return manifest

    def get_by_connection(self, db_connection_id: str) -> Optional[MDLManifest]:
        """Get MDL manifest for a database connection."""
        results = self.storage.find(
            self.collection_name,
            {"db_connection_id": db_connection_id},
            limit=1
        )
        return MDLManifest(**results[0]) if results else None

    def get_by_hash(self, mdl_hash: str) -> Optional[MDLManifest]:
        """Get MDL manifest by hash (for caching)."""
        results = self.storage.find(
            self.collection_name,
            {"mdl_hash": mdl_hash},
            limit=1
        )
        return MDLManifest(**results[0]) if results else None
```

**File**: `app/modules/mdl/services/__init__.py`

```python
class MDLService:
    def __init__(
        self,
        storage: Storage,
        table_description_repo: TableDescriptionRepository,
        business_glossary_service: BusinessGlossaryService,
        database_connection_repo: DatabaseConnectionRepository,
    ):
        self.storage = storage
        self.table_repo = table_description_repo
        self.glossary_service = business_glossary_service
        self.db_conn_repo = database_connection_repo
        self.mdl_repo = MDLManifestRepository(storage)

    def build_mdl(self, db_connection_id: str) -> MDLManifest:
        """Build MDL manifest from existing KAI data."""
        db_conn = self.db_conn_repo.get_by_id(db_connection_id)
        tables = self.table_repo.get_all_tables_by_db({
            "db_connection_id": db_connection_id,
            "sync_status": TableDescriptionStatus.SCANNED.value,
        })
        glossaries = self.glossary_service.get_all_by_connection(db_connection_id)

        builder = MDLBuilder(
            table_descriptions=tables,
            business_glossaries=glossaries,
            db_connection=db_conn,
        )
        manifest = builder.build()
        return self.mdl_repo.save(manifest)

    def get_mdl(self, db_connection_id: str) -> Optional[MDLManifest]:
        """Get cached MDL or build new one."""
        manifest = self.mdl_repo.get_by_connection(db_connection_id)
        if not manifest:
            manifest = self.build_mdl(db_connection_id)
        return manifest

    def refresh_mdl(self, db_connection_id: str) -> MDLManifest:
        """Force rebuild MDL manifest."""
        return self.build_mdl(db_connection_id)

    def to_ddl(self, manifest: MDLManifest) -> str:
        """Convert MDL to DDL string for LLM context."""
        ddl_parts = []
        for model in manifest.models:
            columns = ", ".join([
                f"{col.name} {col.type}" +
                (" PRIMARY KEY" if model.primary_key == col.name else "") +
                (" NOT NULL" if col.not_null else "")
                for col in model.columns
            ])
            ddl = f"CREATE TABLE {model.name} ({columns});"
            if model.properties.get("description"):
                ddl += f"\n-- {model.properties['description']}"
            ddl_parts.append(ddl)

        for rel in manifest.relationships:
            ddl_parts.append(
                f"-- Relationship: {rel.name} ({rel.join_type.value})\n"
                f"-- {rel.condition}"
            )

        return "\n\n".join(ddl_parts)
```

---

### Phase 2: Enhanced Relationship Management (2-3 weeks)

#### 2.1 Extend TableDescription Model

**File**: `app/modules/table_description/models/__init__.py` (update)

```python
class RelationshipType(str, Enum):
    ONE_TO_ONE = "ONE_TO_ONE"
    ONE_TO_MANY = "ONE_TO_MANY"
    MANY_TO_ONE = "MANY_TO_ONE"
    MANY_TO_MANY = "MANY_TO_MANY"

class Relationship(BaseModel):
    name: str
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    join_type: RelationshipType
    condition: Optional[str] = None  # Custom join condition
    inferred: bool = False  # AI-detected vs user-defined

class ColumnDescription(BaseModel):
    name: str
    description: str | None = None
    is_primary_key: bool = False
    data_type: str = "str"
    low_cardinality: bool = False
    categories: list[Any] | None = None
    foreign_key: ForeignKeyDetail | None = None
    # NEW FIELDS
    is_calculated: bool = False
    expression: str | None = None  # SQL expression for calculated fields
    relationship: str | None = None  # Reference to relationship name
```

#### 2.2 Create Relationship Detection Service

**File**: `app/modules/relationship/services/__init__.py`

```python
class RelationshipDetectionService:
    """AI-powered relationship detection between tables."""

    def __init__(self, llm_adapter, storage: Storage):
        self.llm = llm_adapter
        self.storage = storage

    async def detect_relationships(
        self,
        tables: List[TableDescription]
    ) -> List[Relationship]:
        """Use LLM to detect potential relationships between tables."""
        # Build schema context
        schema_context = self._build_schema_context(tables)

        prompt = f"""
        Analyze the following database schema and identify relationships between tables.
        For each relationship, provide:
        1. The two tables involved
        2. The columns that form the relationship
        3. The join type (ONE_TO_ONE, ONE_TO_MANY, MANY_TO_ONE, MANY_TO_MANY)
        4. Confidence score (0-1)

        Schema:
        {schema_context}

        Output JSON array of relationships.
        """

        response = await self.llm.generate(prompt)
        return self._parse_relationships(response)

    def _build_schema_context(self, tables: List[TableDescription]) -> str:
        lines = []
        for t in tables:
            cols = ", ".join([
                f"{c.name} ({c.data_type})" +
                (" PK" if c.is_primary_key else "") +
                (f" FK->{c.foreign_key.reference_table}" if c.foreign_key else "")
                for c in t.columns
            ])
            lines.append(f"TABLE {t.table_name}: {cols}")
        return "\n".join(lines)
```

---

### Phase 3: GENBI - Chart Generation Pipeline (3-4 weeks)

#### 3.1 Create Chart Generation Models

**File**: `app/modules/chart/models/__init__.py`

```python
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Literal
from enum import Enum

class ChartType(str, Enum):
    LINE = "line"
    MULTI_LINE = "multi_line"
    BAR = "bar"
    PIE = "pie"
    GROUPED_BAR = "grouped_bar"
    STACKED_BAR = "stacked_bar"
    AREA = "area"
    SCATTER = "scatter"
    HEATMAP = "heatmap"

class ChartRequest(BaseModel):
    query: str  # Original user question
    sql: str  # Generated SQL
    data: Optional[List[Dict[str, Any]]] = None  # Query results
    language: str = "en"
    custom_instruction: Optional[str] = None

class ChartResult(BaseModel):
    reasoning: str  # Why this chart type
    chart_type: ChartType
    chart_schema: Dict[str, Any]  # Vega-Lite schema
    data_preview: Optional[List[Dict[str, Any]]] = None

class ChartGeneration(BaseModel):
    id: Optional[str] = None
    sql_generation_id: str
    request: ChartRequest
    result: Optional[ChartResult] = None
    status: Literal["pending", "processing", "completed", "failed"] = "pending"
    error: Optional[str] = None
    created_at: str
```

#### 3.2 Create Chart Generation Service

**File**: `app/modules/chart/services/__init__.py`

```python
class ChartGenerationService:
    """Generate Vega-Lite charts from SQL results."""

    SYSTEM_PROMPT = """
    You are a data visualization expert. Given a user's question, SQL query, and data,
    generate an appropriate Vega-Lite chart specification.

    Guidelines:
    - Choose the most appropriate chart type for the data
    - Use clear labels and titles
    - Consider color schemes for accessibility
    - Handle null/missing values gracefully

    Output JSON with: reasoning, chart_type, chart_schema
    """

    def __init__(self, llm_adapter, sql_database: SQLDatabase):
        self.llm = llm_adapter
        self.database = sql_database

    async def generate_chart(self, request: ChartRequest) -> ChartResult:
        """Generate chart from request."""
        # Execute SQL if data not provided
        if not request.data:
            request.data = await self._execute_sql(request.sql)

        # Preprocess data
        sample_data = self._preprocess_data(request.data)
        sample_columns = self._get_column_samples(request.data)

        prompt = f"""
        Question: {request.query}
        SQL: {request.sql}
        Sample Data: {json.dumps(sample_data[:10])}
        Column Types: {json.dumps(sample_columns)}
        Language: {request.language}
        Custom Instruction: {request.custom_instruction or "None"}

        Generate a Vega-Lite chart specification.
        """

        response = await self.llm.generate(
            self.SYSTEM_PROMPT + "\n\n" + prompt,
            response_format={"type": "json_object"}
        )

        result = json.loads(response)

        # Inject data into schema
        chart_schema = result.get("chart_schema", {})
        chart_schema["data"] = {"values": request.data}

        return ChartResult(
            reasoning=result.get("reasoning", ""),
            chart_type=ChartType(result.get("chart_type", "bar")),
            chart_schema=chart_schema,
            data_preview=sample_data[:5],
        )

    def _preprocess_data(self, data: List[Dict]) -> List[Dict]:
        """Clean and preprocess data for charting."""
        if not data:
            return []

        processed = []
        for row in data:
            clean_row = {}
            for k, v in row.items():
                # Handle datetime
                if isinstance(v, (datetime, date)):
                    clean_row[k] = v.isoformat()
                # Handle Decimal
                elif isinstance(v, Decimal):
                    clean_row[k] = float(v)
                else:
                    clean_row[k] = v
            processed.append(clean_row)

        return processed

    def _get_column_samples(self, data: List[Dict]) -> Dict[str, Any]:
        """Extract column type samples for LLM context."""
        if not data:
            return {}

        samples = {}
        for col in data[0].keys():
            values = [row.get(col) for row in data[:10] if row.get(col) is not None]
            if values:
                samples[col] = {
                    "type": type(values[0]).__name__,
                    "samples": values[:3],
                    "unique_count": len(set(str(v) for v in values)),
                }
        return samples
```

#### 3.3 Create Chart API Endpoints

**File**: `app/api/routers/chart.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from app.modules.chart.models import ChartRequest, ChartResult, ChartGeneration
from app.modules.chart.services import ChartGenerationService

router = APIRouter(prefix="/api/v1/charts", tags=["charts"])

@router.post("/", response_model=ChartGeneration)
async def generate_chart(
    request: ChartRequest,
    chart_service: ChartGenerationService = Depends(get_chart_service),
):
    """Generate a chart from SQL query and data."""
    try:
        result = await chart_service.generate_chart(request)
        return ChartGeneration(
            sql_generation_id=request.sql_generation_id,
            request=request,
            result=result,
            status="completed",
            created_at=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/adjust")
async def adjust_chart(
    chart_id: str,
    instruction: str,
    chart_service: ChartGenerationService = Depends(get_chart_service),
):
    """Adjust an existing chart based on user instruction."""
    # Load existing chart, apply modification prompt
    pass
```

---

### Phase 4: Enhanced Ask Pipeline with MDL (3-4 weeks)

#### 4.1 Update SQL Generation to Use MDL

**File**: `app/modules/sql_generation/services/mdl_aware_adapter.py`

```python
class MDLAwareSQLGeneratorAdapter(KaiSqlGeneratorAdapter):
    """SQL Generator that leverages MDL for enhanced context."""

    def __init__(
        self,
        repository: SQLGenerationRepository,
        mdl_service: MDLService,
    ):
        super().__init__(repository)
        self.mdl_service = mdl_service

    def _prepare_tool_context_with_mdl(
        self,
        user_prompt,
        db_connection: DatabaseConnection,
        context: list[dict] | None,
    ) -> tuple[KaiToolContext, list[str], MDLManifest]:
        """Prepare context with MDL enhancement."""

        # Get or build MDL
        mdl = self.mdl_service.get_mdl(db_connection.id)

        # Convert MDL to DDL context
        ddl_context = self.mdl_service.to_ddl(mdl)

        # Extract relationship context
        relationship_context = self._build_relationship_context(mdl)

        # Extract metric context
        metric_context = self._build_metric_context(mdl)

        # Build enhanced instructions
        extra_instructions = [
            "## RELATIONSHIP CONTEXT ##",
            relationship_context,
            "## METRIC DEFINITIONS ##",
            metric_context,
        ]

        tool_context = KaiToolContext(
            database=self.database,
            db_scan=self._mdl_to_table_descriptions(mdl),
            embedding=EmbeddingModel().get_model(),
            context=context,
            few_shot_examples=[],
            business_metrics=self._extract_business_metrics(mdl),
            aliases=[],
            is_multiple_schema=len(db_connection.schemas or []) > 1,
            top_k=50,
            tenant_id="default",
            sql_generation_id="",
        )

        return tool_context, extra_instructions, mdl

    def _build_relationship_context(self, mdl: MDLManifest) -> str:
        """Build relationship context for SQL generation."""
        if not mdl.relationships:
            return "No explicit relationships defined."

        lines = []
        for rel in mdl.relationships:
            lines.append(
                f"- {rel.name}: {rel.models[0]} {rel.join_type.value} {rel.models[1]}"
                f"\n  Condition: {rel.condition}"
            )
        return "\n".join(lines)

    def _build_metric_context(self, mdl: MDLManifest) -> str:
        """Build metric context for SQL generation."""
        if not mdl.metrics:
            return "No metrics defined."

        lines = []
        for metric in mdl.metrics:
            measures = ", ".join([m.name for m in metric.measure])
            dims = ", ".join([d.name for d in metric.dimension])
            lines.append(
                f"- {metric.name}: Measures({measures}), Dimensions({dims})"
                f"\n  Base: {metric.base_object}"
            )
        return "\n".join(lines)
```

#### 4.2 Create Ask Pipeline Service

**File**: `app/modules/ask/services/__init__.py`

```python
class AskService:
    """
    Unified ask service similar to WrenAI's approach.
    Handles the complete flow: understanding → searching → generating → correcting
    """

    def __init__(
        self,
        mdl_service: MDLService,
        sql_generator_adapter: MDLAwareSQLGeneratorAdapter,
        chart_service: ChartGenerationService,
        memory_service: MemoryService,
    ):
        self.mdl_service = mdl_service
        self.sql_generator = sql_generator_adapter
        self.chart_service = chart_service
        self.memory_service = memory_service
        self._results_cache = TTLCache(maxsize=10000, ttl=120)

    async def ask(
        self,
        query: str,
        db_connection_id: str,
        histories: List[Dict] = None,
        include_chart: bool = False,
        custom_instruction: str = None,
    ) -> AskResult:
        """
        Process a natural language question.

        Flow:
        1. Understanding - intent classification, query rephrasing
        2. Searching - retrieve relevant schema, examples
        3. Planning - generate SQL approach
        4. Generating - create SQL
        5. Correcting - fix errors if any
        6. Charting (optional) - generate visualization
        """
        query_id = str(uuid.uuid4())
        self._results_cache[query_id] = AskResultResponse(status="understanding")

        try:
            # Phase 1: Understanding
            intent = await self._classify_intent(query, histories)
            self._results_cache[query_id] = AskResultResponse(
                status="understanding",
                type=intent.type,
            )

            # Phase 2: Searching
            mdl = self.mdl_service.get_mdl(db_connection_id)
            relevant_tables = await self._search_relevant_tables(query, mdl)
            self._results_cache[query_id] = AskResultResponse(
                status="searching",
                retrieved_tables=relevant_tables,
            )

            # Phase 3: Planning
            reasoning = await self._generate_reasoning(query, mdl, relevant_tables)
            self._results_cache[query_id] = AskResultResponse(
                status="planning",
                sql_generation_reasoning=reasoning,
            )

            # Phase 4: Generating
            sql_result = await self._generate_sql(
                query=query,
                mdl=mdl,
                tables=relevant_tables,
                reasoning=reasoning,
                custom_instruction=custom_instruction,
            )
            self._results_cache[query_id] = AskResultResponse(
                status="generating",
                sql=sql_result.sql,
            )

            # Phase 5: Correcting (if needed)
            if sql_result.status == "INVALID":
                sql_result = await self._correct_sql(sql_result, mdl)

            # Phase 6: Charting (optional)
            chart = None
            if include_chart and sql_result.status == "VALID":
                chart = await self.chart_service.generate_chart(
                    ChartRequest(
                        query=query,
                        sql=sql_result.sql,
                    )
                )

            # Final result
            self._results_cache[query_id] = AskResultResponse(
                status="finished",
                response=[AskResult(sql=sql_result.sql)],
                chart=chart,
            )

            return self._results_cache[query_id]

        except Exception as e:
            self._results_cache[query_id] = AskResultResponse(
                status="failed",
                error=AskError(code="OTHERS", message=str(e)),
            )
            raise
```

---

### Phase 5: Semantics Preparation Pipeline (2-3 weeks)

#### 5.1 Create Semantics Indexing Service

**File**: `app/modules/semantics/services/__init__.py`

```python
class SemanticsPreparationService:
    """
    Index MDL to vector store for semantic search.
    Similar to WrenAI's semantics-preparations endpoint.
    """

    def __init__(
        self,
        storage: Storage,
        embedding_model: EmbeddingModel,
        mdl_service: MDLService,
    ):
        self.storage = storage
        self.embedder = embedding_model
        self.mdl_service = mdl_service
        self._status_cache = TTLCache(maxsize=1000, ttl=300)

    async def prepare(self, db_connection_id: str) -> str:
        """
        Prepare semantics (index MDL to vector store).
        Returns preparation_id for status tracking.
        """
        prep_id = str(uuid.uuid4())
        self._status_cache[prep_id] = {
            "status": "indexing",
            "progress": 0,
        }

        # Run indexing in background
        asyncio.create_task(self._run_indexing(prep_id, db_connection_id))

        return prep_id

    async def _run_indexing(self, prep_id: str, db_connection_id: str):
        """Background indexing task."""
        try:
            mdl = self.mdl_service.get_mdl(db_connection_id)

            # Index models/tables
            self._status_cache[prep_id]["progress"] = 20
            await self._index_models(mdl)

            # Index columns
            self._status_cache[prep_id]["progress"] = 40
            await self._index_columns(mdl)

            # Index relationships
            self._status_cache[prep_id]["progress"] = 60
            await self._index_relationships(mdl)

            # Index metrics
            self._status_cache[prep_id]["progress"] = 80
            await self._index_metrics(mdl)

            # Done
            self._status_cache[prep_id] = {
                "status": "finished",
                "progress": 100,
                "mdl_hash": mdl.mdl_hash,
            }

        except Exception as e:
            self._status_cache[prep_id] = {
                "status": "failed",
                "error": str(e),
            }

    async def _index_models(self, mdl: MDLManifest):
        """Index model descriptions to vector store."""
        for model in mdl.models:
            text = f"Table {model.name}"
            if model.properties.get("description"):
                text += f": {model.properties['description']}"

            embedding = await self.embedder.embed(text)

            self.storage.insert("mdl_model_embeddings", {
                "mdl_hash": mdl.mdl_hash,
                "model_name": model.name,
                "text": text,
                "embedding": embedding,
            })

    async def _index_columns(self, mdl: MDLManifest):
        """Index column descriptions to vector store."""
        for model in mdl.models:
            for col in model.columns:
                text = f"Column {model.name}.{col.name} ({col.type})"
                if col.properties.get("description"):
                    text += f": {col.properties['description']}"

                embedding = await self.embedder.embed(text)

                self.storage.insert("mdl_column_embeddings", {
                    "mdl_hash": mdl.mdl_hash,
                    "model_name": model.name,
                    "column_name": col.name,
                    "text": text,
                    "embedding": embedding,
                })
```

---

### Phase 6: API Endpoints & Integration (2-3 weeks)

#### 6.1 Create MDL API Endpoints

**File**: `app/api/routers/mdl.py`

```python
router = APIRouter(prefix="/api/v1/mdl", tags=["mdl"])

@router.post("/build/{db_connection_id}")
async def build_mdl(
    db_connection_id: str,
    mdl_service: MDLService = Depends(get_mdl_service),
):
    """Build MDL manifest from database schema."""
    manifest = mdl_service.build_mdl(db_connection_id)
    return {"mdl_hash": manifest.mdl_hash, "manifest": manifest.model_dump()}

@router.get("/{db_connection_id}")
async def get_mdl(
    db_connection_id: str,
    mdl_service: MDLService = Depends(get_mdl_service),
):
    """Get MDL manifest for a database connection."""
    manifest = mdl_service.get_mdl(db_connection_id)
    if not manifest:
        raise HTTPException(404, "MDL not found")
    return manifest.model_dump()

@router.post("/{db_connection_id}/refresh")
async def refresh_mdl(
    db_connection_id: str,
    mdl_service: MDLService = Depends(get_mdl_service),
):
    """Force refresh MDL manifest."""
    manifest = mdl_service.refresh_mdl(db_connection_id)
    return {"mdl_hash": manifest.mdl_hash}

@router.put("/{db_connection_id}/relationships")
async def update_relationships(
    db_connection_id: str,
    relationships: List[MDLRelationship],
    mdl_service: MDLService = Depends(get_mdl_service),
):
    """Update relationships in MDL."""
    pass

@router.put("/{db_connection_id}/metrics")
async def update_metrics(
    db_connection_id: str,
    metrics: List[MDLMetric],
    mdl_service: MDLService = Depends(get_mdl_service),
):
    """Update metrics in MDL."""
    pass
```

#### 6.2 Create Ask API Endpoints

**File**: `app/api/routers/ask.py`

```python
router = APIRouter(prefix="/api/v1/asks", tags=["asks"])

@router.post("/")
async def create_ask(
    request: AskRequest,
    ask_service: AskService = Depends(get_ask_service),
):
    """Submit a natural language question."""
    query_id = await ask_service.ask(
        query=request.query,
        db_connection_id=request.db_connection_id,
        histories=request.histories,
        include_chart=request.include_chart,
        custom_instruction=request.custom_instruction,
    )
    return {"query_id": query_id}

@router.get("/{query_id}/result")
async def get_ask_result(
    query_id: str,
    ask_service: AskService = Depends(get_ask_service),
):
    """Get result of an ask query."""
    return ask_service.get_result(query_id)

@router.get("/{query_id}/streaming-result")
async def stream_ask_result(
    query_id: str,
    ask_service: AskService = Depends(get_ask_service),
):
    """Stream ask result via SSE."""
    async def event_generator():
        while True:
            result = ask_service.get_result(query_id)
            yield f"data: {result.model_dump_json()}\n\n"
            if result.status in ["finished", "failed", "stopped"]:
                break
            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
```

#### 6.3 Create Semantics API Endpoints

**File**: `app/api/routers/semantics.py`

```python
router = APIRouter(prefix="/api/v1/semantics-preparations", tags=["semantics"])

@router.post("/")
async def create_preparation(
    db_connection_id: str,
    semantics_service: SemanticsPreparationService = Depends(get_semantics_service),
):
    """Start semantics preparation (indexing)."""
    prep_id = await semantics_service.prepare(db_connection_id)
    return {"preparation_id": prep_id}

@router.get("/{preparation_id}/status")
async def get_preparation_status(
    preparation_id: str,
    semantics_service: SemanticsPreparationService = Depends(get_semantics_service),
):
    """Get preparation status."""
    return semantics_service.get_status(preparation_id)
```

---

## Part 4: Migration Strategy

### Step 1: Data Migration (Non-Breaking)

```python
# app/scripts/migrate_to_mdl.py

async def migrate_existing_data():
    """Migrate existing KAI data to MDL format."""
    storage = Storage(Settings())

    # Get all database connections
    db_conn_repo = DatabaseConnectionRepository(storage)
    connections = db_conn_repo.get_all()

    for conn in connections:
        # Build MDL from existing data
        mdl_service = MDLService(storage, ...)
        mdl = mdl_service.build_mdl(conn.id)

        # Index to vector store
        semantics_service = SemanticsPreparationService(storage, ...)
        await semantics_service.prepare(conn.id)

        print(f"Migrated {conn.alias}: {mdl.mdl_hash}")
```

### Step 2: Feature Flag Rollout

```python
# app/server/config.py

class Settings:
    # MDL Feature Flags
    USE_MDL_CONTEXT: bool = os.getenv("USE_MDL_CONTEXT", "false").lower() == "true"
    USE_GENBI_CHARTS: bool = os.getenv("USE_GENBI_CHARTS", "false").lower() == "true"
    USE_ASK_PIPELINE: bool = os.getenv("USE_ASK_PIPELINE", "false").lower() == "true"
```

### Step 3: Gradual API Migration

1. **v1 APIs** - Current KAI APIs (unchanged)
2. **v2 APIs** - New MDL/GENBI APIs (parallel deployment)
3. **Deprecation** - Mark v1 APIs as deprecated after v2 stabilizes
4. **Sunset** - Remove v1 APIs in major version bump

---

## Part 5: File Structure

```
app/
├── modules/
│   ├── mdl/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   └── __init__.py          # MDL Pydantic models
│   │   ├── repositories/
│   │   │   └── __init__.py          # MDL repository
│   │   ├── services/
│   │   │   ├── __init__.py          # MDL service
│   │   │   └── mdl_builder.py       # MDL builder
│   │   └── schema/
│   │       └── mdl.schema.json      # JSON Schema
│   │
│   ├── ask/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   └── __init__.py          # Ask models
│   │   └── services/
│   │       └── __init__.py          # Ask service (WrenAI-style)
│   │
│   ├── chart/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   └── __init__.py          # Chart models
│   │   └── services/
│   │       └── __init__.py          # Chart generation service
│   │
│   ├── semantics/
│   │   ├── __init__.py
│   │   └── services/
│   │       └── __init__.py          # Semantics preparation service
│   │
│   └── relationship/
│       ├── __init__.py
│       ├── models/
│       │   └── __init__.py          # Relationship models
│       └── services/
│           └── __init__.py          # Relationship detection
│
├── api/
│   └── routers/
│       ├── mdl.py                   # MDL API endpoints
│       ├── ask.py                   # Ask API endpoints
│       ├── chart.py                 # Chart API endpoints
│       └── semantics.py             # Semantics API endpoints
│
└── scripts/
    └── migrate_to_mdl.py            # Migration script
```

---

## Part 6: Timeline & Resources

| Phase | Duration | Dependencies | Resources |
|-------|----------|--------------|-----------|
| Phase 1: MDL Schema & Models | 4-6 weeks | None | 1 Backend Engineer |
| Phase 2: Relationship Management | 2-3 weeks | Phase 1 | 1 Backend Engineer |
| Phase 3: Chart Generation | 3-4 weeks | Phase 1 | 1 Backend Engineer |
| Phase 4: Ask Pipeline | 3-4 weeks | Phase 1, 2 | 1-2 Backend Engineers |
| Phase 5: Semantics Pipeline | 2-3 weeks | Phase 1, 4 | 1 Backend Engineer |
| Phase 6: API & Integration | 2-3 weeks | All above | 1 Backend Engineer |

**Total Estimated Duration**: 16-23 weeks (4-6 months)

---

## Part 7: Key Decisions & Trade-offs

### Decision 1: MDL as Primary Semantic Layer
- **Choice**: Create MDL as the single source of truth
- **Rationale**: Consolidates fragmented data (TableDescription, BusinessGlossary, etc.)
- **Trade-off**: Migration effort required

### Decision 2: Keep Existing Modules
- **Choice**: MDL builds on top of existing modules, not replace them
- **Rationale**: Backward compatibility, gradual migration
- **Trade-off**: Some data duplication

### Decision 3: Separate Ask Pipeline
- **Choice**: Create dedicated Ask service separate from existing SQL generation
- **Rationale**: Clean architecture, easier to maintain
- **Trade-off**: Code duplication initially

### Decision 4: Vega-Lite for Charts
- **Choice**: Use Vega-Lite (same as WrenAI) instead of custom chart formats
- **Rationale**: Industry standard, flexible, well-documented
- **Trade-off**: Learning curve for team

---

## Part 8: Success Metrics

1. **MDL Coverage**: % of databases with complete MDL manifests
2. **Chart Generation Accuracy**: User acceptance rate for auto-generated charts
3. **Query Accuracy**: % of valid SQL generated on first attempt
4. **Response Time**: Time to generate SQL + chart (target: <5s)
5. **User Adoption**: % of queries using new Ask pipeline vs legacy

---

## Appendix A: MDL Schema (Full)

See separate file: `mdl.schema.json`

## Appendix B: API Reference

See separate file: `api-reference.md`

## Appendix C: Migration Guide

See separate file: `migration-guide.md`
