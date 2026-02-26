# Question Generation API Documentation

API for generating synthetic questions.

**Base URL:** `/api/v1/synthetic-questions`

---

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Generate synthetic questions |

---

## Data Types

### SyntheticQuestionRequest (Request)

```typescript
interface SyntheticQuestionRequest {
  db_connection_id: string;
  llm_config?: LLMConfig;
  instruction?: string;
  questions_per_batch?: number;
  num_batches?: number;
  peeking_context_stores?: boolean;
  evaluate?: boolean;
  metadata?: Record<string, any>;
}
```

### SyntheticQuestionResponse (Response)

```typescript
interface SyntheticQuestionResponse {
  questions: QuestionSQLPair[];
  input_tokens_used?: number;
  output_tokens_used?: number;
  metadata?: Record<string, any>;
}
```

### QuestionSQLPair (Response)

```typescript
interface QuestionSQLPair {
  question: string;
  sql: string;
  status: string;
  error: string;
}```

---

## POST /

Generate synthetic questions.

### Request Body

`SyntheticQuestionRequest`

### Response

`SyntheticQuestionResponse`