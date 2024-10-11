# SQL Generation API

The SQL Generation API allows you to manage SQL queries generated from natural language prompts or predefined SQL queries. This API provides endpoints for creating, retrieving, updating, and executing SQL generations.

### Endpoints

#### 1. Create SQL Generation

**Endpoint:** `/api/v1/sql-generations`\
**Method:** `POST`\
**Request Body:**

```json
{
    "llm_config": {
        "model_name": "string",
        "temperature": 0.7,
        "max_tokens": 150
    },
    "evaluate": false,
    "sql": "string",
    "metadata": {"key": "value"}
}
```

**Description:** Creates a new SQL generation configuration with optional LLM settings, SQL query, evaluation flag, and metadata.

**Response:**

```json
{
    "id": "string",
    "prompt_id": "string",
    "status": "string",
    "llm_config": {
        "model_name": "string",
        "temperature": 0.7,
        "max_tokens": 150
    },
    "intermediate_steps": [
        {
            "step_description": "string",
            "step_result": "string"
        }
    ],
    "sql": "string",
    "tokens_used": 123,
    "confidence_score": 0.9,
    "completed_at": "string",
    "error": "string",
    "created_at": "string"
}
```

#### 2. Retrieve All SQL Generations

**Endpoint:** `/api/v1/sql-generations`\
**Method:** `GET`\
**Description:** Retrieves a list of all SQL generations.

**Response:**

```json
[
    {
        "id": "string",
        "prompt_id": "string",
        "status": "string",
        "llm_config": {
            "model_name": "string",
            "temperature": 0.7,
            "max_tokens": 150
        },
        "intermediate_steps": [
            {
                "step_description": "string",
                "step_result": "string"
            }
        ],
        "sql": "string",
        "tokens_used": 123,
        "confidence_score": 0.9,
        "completed_at": "string",
        "error": "string",
        "created_at": "string"
    }
]
```

#### 3. Retrieve a Specific SQL Generation

**Endpoint:** `/api/v1/sql-generations/{sql_generation_id}`\
**Method:** `GET`\
**Description:** Retrieves the details of a specific SQL generation identified by `sql_generation_id`.

**Response:**

```json
{
    "id": "string",
    "prompt_id": "string",
    "status": "string",
    "llm_config": {
        "model_name": "string",
        "temperature": 0.7,
        "max_tokens": 150
    },
    "intermediate_steps": [
        {
            "step_description": "string",
            "step_result": "string"
        }
    ],
    "sql": "string",
    "tokens_used": 123,
    "confidence_score": 0.9,
    "completed_at": "string",
    "error": "string",
    "created_at": "string"
}
```

#### 4. Update a SQL Generation

**Endpoint:** `/api/v1/sql-generations/{sql_generation_id}`\
**Method:** `PUT`\
**Request Body:**

```json
{
    "llm_config": {
        "model_name": "string",
        "temperature": 0.7,
        "max_tokens": 150
    },
    "evaluate": false,
    "sql": "string",
    "metadata": {"key": "value"}
}
```

**Description:** Updates the details of an existing SQL generation identified by `sql_generation_id`.

**Response:**

```json
{
    "id": "string",
    "prompt_id": "string",
    "status": "string",
    "llm_config": {
        "model_name": "string",
        "temperature": 0.7,
        "max_tokens": 150
    },
    "intermediate_steps": [
        {
            "step_description": "string",
            "step_result": "string"
        }
    ],
    "sql": "string",
    "tokens_used": 123,
    "confidence_score": 0.9,
    "completed_at": "string",
    "error": "string",
    "created_at": "string"
}
```

#### 5. Execute SQL Query

**Endpoint:** `/api/v1/sql-generations/{sql_generation_id}/execute`\
**Method:** `GET`\
**Description:** Executes the SQL query associated with the specified SQL generation.

**Response:**

```json
{
    "id": "string",
    "sql": "string",
    "result": "string",
    "status": "string",
    "tokens_used": 123,
    "confidence_score": 0.9,
    "completed_at": "string",
    "error": "string",
    "created_at": "string"
}
```

### Example Usage

#### Creating a SQL Generation

To create a new SQL generation, send a `POST` request to `/api/v1/sql-generations`:

**Request:**

```http
POST /api/v1/sql-generations
Content-Type: application/json

{
    "llm_config": {
        "model_name": "gpt-4",
        "temperature": 0.6,
        "max_tokens": 200
    },
    "evaluate": true,
    "sql": "SELECT * FROM users WHERE age > 30;",
    "metadata": {"requestor": "admin"}
}
```

**Response:**

```json
{
    "id": "sqlgen456",
    "prompt_id": "prompt789",
    "status": "pending",
    "llm_config": {
        "model_name": "gpt-4",
        "temperature": 0.6,
        "max_tokens": 200
    },
    "intermediate_steps": [],
    "sql": "SELECT * FROM users WHERE age > 30;",
    "tokens_used": 150,
    "confidence_score": 0.85,
    "completed_at": null,
    "error": null,
    "created_at": "2024-09-09T12:45:00Z"
}
```

#### Retrieving All SQL Generations

To retrieve a list of all SQL generations, send a `GET` request to `/api/v1/sql-generations`:

**Request:**

```http
GET /api/v1/sql-generations
```

**Response:**

```json
[
    {
        "id": "sqlgen456",
        "prompt_id": "prompt789",
        "status": "pending",
        "llm_config": {
            "model_name": "gpt-4",
            "temperature": 0.6,
            "max_tokens": 200
        },
        "intermediate_steps": [],
        "sql": "SELECT * FROM users WHERE age > 30;",
        "tokens_used": 150,
        "confidence_score": 0.85,
        "completed_at": null,
        "error": null,
        "created_at": "2024-09-09T12:45:00Z"
    }
]
```

#### Retrieving a Specific SQL Generation

To retrieve a specific SQL generation, send a `GET` request to `/api/v1/sql-generations/{sql_generation_id}`:

**Request:**

```http
GET /api/v1/sql-generations/sqlgen456
```

**Response:**

```json
{
    "id": "sqlgen456",
    "prompt_id": "prompt789",
    "status": "pending",
    "llm_config": {
        "model_name": "gpt-4",
        "temperature": 0.6,
        "max_tokens": 200
    },
    "intermediate_steps": [],
    "sql": "SELECT * FROM users WHERE age > 30;",
    "tokens_used": 150,
    "confidence_score": 0.85,
    "completed_at": null,
    "error": null,
    "created_at": "2024-09-09T12:45:00Z"
}
```

#### Updating a SQL Generation

To update a SQL generation, send a `PUT` request to `/api/v1/sql-generations/{sql_generation_id}`:

**Request:**

```http
PUT /api/v1/sql-generations/sqlgen456
Content-Type: application/json

{
    "llm_config": {
        "model_name": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 250
    },
    "evaluate": true,
    "sql": "SELECT name, email FROM users WHERE age > 40;",
    "metadata": {"updated_by": "admin"}
}
```

**Response:**

```json
{
    "id": "sqlgen456",
    "prompt_id": "prompt789",
    "status": "pending",
    "llm_config": {
        "model_name": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 250
    },
    "intermediate_steps": [],
    "sql": "SELECT name, email FROM users WHERE age > 40;",
    "tokens_used": 175,
    "confidence_score": 0.87,
    "completed_at": null,
    "error": null,
    "created_at": "2024-09-09T12:45:00Z"
}
```

#### Executing a SQL Query

To execute the SQL query associated with a specific SQL generation, send a `GET` request to `/api/v1/sql-generations/{sql_generation_id}/execute`:

**Request:**

```http
GET /api/v1/sql-generations/sqlgen456/execute
```

**Response:**

```json
{
    "id": "sqlgen456",
    "sql": "SELECT name, email FROM users WHERE age > 40;",
    "result": "name, email\nJohn Doe, john@example.com\nJane Smith, jane@example.com",
    "status": "completed",
    "tokens_used": 175,
    "confidence_score": 0.87,
    "completed_at": "2024-09-09T12:50:00Z",
    "error": null,
    "created_at": "2024-09-09T12:45:00Z"
}
```

This guide provides a comprehensive overview of how to use the SQL Generation API to handle SQL queries and their results effectively.
