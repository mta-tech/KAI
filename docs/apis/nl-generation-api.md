# NL Generation API

The NL Generation API allows you to manage the generation of natural language responses based on SQL queries. This API provides endpoints for creating, retrieving, and updating natural language generations.

### Endpoints

#### 1. Create Natural Language Generation

**Endpoint:** `/api/v1/nl-generations`\
**Method:** `POST`\
**Request Body:**

```json
{
    "llm_config": {
        "model_name": "string",
        "temperature": 0.7,
        "max_tokens": 150
    },
    "max_rows": 100,
    "metadata": {"key": "value"}
}
```

**Description:** Creates a new natural language generation configuration with optional LLM settings, maximum rows for response, and metadata.

**Response:**

```json
{
    "id": "string",
    "llm_config": {
        "model_name": "string",
        "temperature": 0.7,
        "max_tokens": 150
    },
    "max_rows": 100,
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 2. Retrieve All Natural Language Generations

**Endpoint:** `/api/v1/nl-generations`\
**Method:** `GET`\
**Description:** Retrieves a list of all natural language generations.

**Response:**

```json
[
    {
        "id": "string",
        "llm_config": {
            "model_name": "string",
            "temperature": 0.7,
            "max_tokens": 150
        },
        "max_rows": 100,
        "metadata": {"key": "value"},
        "created_at": "string"
    }
]
```

#### 3. Retrieve a Specific Natural Language Generation

**Endpoint:** `/api/v1/nl-generations/{nl_generation_id}`\
**Method:** `GET`\
**Description:** Retrieves the details of a specific natural language generation identified by `nl_generation_id`.

**Response:**

```json
{
    "id": "string",
    "llm_config": {
        "model_name": "string",
        "temperature": 0.7,
        "max_tokens": 150
    },
    "max_rows": 100,
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 4. Update a Natural Language Generation

**Endpoint:** `/api/v1/nl-generations/{nl_generation_id}`\
**Method:** `PUT`\
**Request Body:**

```json
{
    "llm_config": {
        "model_name": "string",
        "temperature": 0.7,
        "max_tokens": 150
    },
    "max_rows": 100,
    "metadata": {"key": "value"}
}
```

**Description:** Updates the details of an existing natural language generation identified by `nl_generation_id`.

**Response:**

```json
{
    "id": "string",
    "llm_config": {
        "model_name": "string",
        "temperature": 0.7,
        "max_tokens": 150
    },
    "max_rows": 100,
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

### Example Usage

#### Creating a Natural Language Generation

To create a new natural language generation configuration, send a `POST` request to `/api/v1/nl-generations`:

**Request:**

```http
POST /api/v1/nl-generations
Content-Type: application/json

{
    "llm_config": {
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.5,
        "max_tokens": 100
    },
    "max_rows": 50,
    "metadata": {"creator": "admin"}
}
```

**Response:**

```json
{
    "id": "nlgen123",
    "llm_config": {
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.5,
        "max_tokens": 100
    },
    "max_rows": 50,
    "metadata": {"creator": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```

#### Retrieving All Natural Language Generations

To retrieve a list of all natural language generations, send a `GET` request to `/api/v1/nl-generations`:

**Request:**

```http
GET /api/v1/nl-generations
```

**Response:**

```json
[
    {
        "id": "nlgen123",
        "llm_config": {
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.5,
            "max_tokens": 100
        },
        "max_rows": 50,
        "metadata": {"creator": "admin"},
        "created_at": "2024-09-09T12:34:56Z"
    }
]
```

#### Retrieving a Specific Natural Language Generation

To retrieve a specific natural language generation, send a `GET` request to `/api/v1/nl-generations/{nl_generation_id}`:

**Request:**

```http
GET /api/v1/nl-generations/nlgen123
```

**Response:**

```json
{
    "id": "nlgen123",
    "llm_config": {
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.5,
        "max_tokens": 100
    },
    "max_rows": 50,
    "metadata": {"creator": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```

#### Updating a Natural Language Generation

To update a natural language generation, send a `PUT` request to `/api/v1/nl-generations/{nl_generation_id}`:

**Request:**

```http
PUT /api/v1/nl-generations/nlgen123
Content-Type: application/json

{
    "llm_config": {
        "model_name": "gpt-4",
        "temperature": 0.6,
        "max_tokens": 150
    },
    "max_rows": 100,
    "metadata": {"updated_by": "admin"}
}
```

**Response:**

```json
{
    "id": "nlgen123",
    "llm_config": {
        "model_name": "gpt-4",
        "temperature": 0.6,
        "max_tokens": 150
    },
    "max_rows": 100,
    "metadata": {"updated_by": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```
