# Analysis API Documentation

API for performing analysis on SQL generation results.

**Base URL:** `/api/v1/analysis`

---

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/comprehensive` | Create a comprehensive analysis |
| POST | `/sql-generations/{sql_generation_id}/analysis` | Create an analysis for a SQL generation |
| GET | `/{analysis_id}` | Get an analysis |

---

## Data Types

### ComprehensiveAnalysisRequest (Request)

```typescript
interface ComprehensiveAnalysisRequest {
  prompt: PromptRequest;
  llm_config?: LLMConfig;
  max_rows?: number;
  use_deep_agent?: boolean;
  metadata?: Record<string, any>;
}
```

### ComprehensiveAnalysisResponse (Response)

```typescript
interface ComprehensiveAnalysisResponse {
  prompt_id: string;
  sql_generation_id: string;
  analysis_id?: string;
  sql?: string;
  sql_status: string;
  summary: string;
  insights: Record<string, any>[];
  chart_recommendations: Record<string, any>[];
  row_count?: number;
  column_count?: number;
  input_tokens_used?: number;
  output_tokens_used?: number;
  error?: string;
  execution_time: Record<string, any>;
}
```

### AnalysisRequest (Request)

```typescript
interface AnalysisRequest {
  llm_config?: LLMConfig;
  max_rows?: number;
  metadata?: Record<string, any>;
}
```

### AnalysisResponse (Response)

```typescript
interface AnalysisResponse {
  id: string;
  sql_generation_id: string;
  prompt_id?: string;
  summary: string;
  insights: InsightResponse[];
  chart_recommendations: ChartRecommendationResponse[];
  row_count?: number;
  column_count?: number;
  llm_config?: LLMConfig;
  input_tokens_used?: number;
  output_tokens_used?: number;
  completed_at?: string;
  error?: string;
  metadata?: Record<string, any>;
  created_at: string;
}
```

---

## POST /comprehensive

Create a comprehensive analysis.

### Request Body

`ComprehensiveAnalysisRequest`

### Response

`ComprehensiveAnalysisResponse`

---

## POST /sql-generations/{sql_generation_id}/analysis

Create an analysis for a SQL generation.

### Path Parameters

- `sql_generation_id` (string, required)

### Request Body

`AnalysisRequest`

### Response

`AnalysisResponse`

---

## GET /{analysis_id}

Get an analysis.

### Path Parameters

- `analysis_id` (string, required)

### Response

`AnalysisResponse`