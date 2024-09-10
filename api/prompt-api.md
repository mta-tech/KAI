# Prompt API

The Prompt API allows you to manage prompts that are used to generate SQL queries and natural language responses. This API provides endpoints for creating, retrieving, updating, and deleting prompts.

### Endpoints

#### 1. Create a Prompt

**Endpoint:** `/api/v1/prompts`\
**Method:** `POST`\
**Request Body:**

```json
{
    "text": "string",
    "db_connection_id": "string",
    "schemas": ["string"],
    "context": [{"key": "value"}],
    "metadata": {"key": "value"}
}
```

**Description:** Creates a new prompt with the specified text, database connection ID, optional schemas, context, and metadata.

**Response:**

```json
{
    "id": "string",
    "text": "string",
    "db_connection_id": "string",
    "schemas": ["string"],
    "context": [{"key": "value"}],
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 2. Retrieve All Prompts

**Endpoint:** `/api/v1/prompts`\
**Method:** `GET`\
**Description:** Retrieves a list of all prompts.

**Response:**

```json
[
    {
        "id": "string",
        "text": "string",
        "db_connection_id": "string",
        "schemas": ["string"],
        "context": [{"key": "value"}],
        "metadata": {"key": "value"},
        "created_at": "string"
    }
]
```

#### 3. Retrieve a Specific Prompt

**Endpoint:** `/api/v1/prompts/{prompt_id}`\
**Method:** `GET`\
**Description:** Retrieves the details of a specific prompt identified by `prompt_id`.

**Response:**

```json
{
    "id": "string",
    "text": "string",
    "db_connection_id": "string",
    "schemas": ["string"],
    "context": [{"key": "value"}],
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 4. Update a Prompt

**Endpoint:** `/api/v1/prompts/{prompt_id}`\
**Method:** `PUT`\
**Request Body:**

```json
{
    "text": "string",
    "db_connection_id": "string",
    "schemas": ["string"],
    "context": [{"key": "value"}],
    "metadata": {"key": "value"}
}
```

**Description:** Updates the details of an existing prompt identified by `prompt_id`.

**Response:**

```json
{
    "id": "string",
    "text": "string",
    "db_connection_id": "string",
    "schemas": ["string"],
    "context": [{"key": "value"}],
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 5. Delete a Prompt

**Endpoint:** `/api/v1/prompts/{prompt_id}`\
**Method:** `DELETE`\
**Description:** Deletes a specific prompt identified by `prompt_id`.

**Response:**

```json
{
    "id": "string",
    "text": "string",
    "db_connection_id": "string",
    "schemas": ["string"],
    "context": [{"key": "value"}],
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

### Example Usage

#### Creating a Prompt

To create a new prompt, send a `POST` request to `/api/v1/prompts`:

**Request:**

```http
POST /api/v1/prompts
Content-Type: application/json

{
    "text": "Generate a sales report for the last month",
    "db_connection_id": "db123",
    "schemas": ["public"],
    "context": [{"user": "admin"}],
    "metadata": {"created_by": "admin"}
}
```

**Response:**

```json
{
    "id": "prompt123",
    "text": "Generate a sales report for the last month",
    "db_connection_id": "db123",
    "schemas": ["public"],
    "context": [{"user": "admin"}],
    "metadata": {"created_by": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```

#### Retrieving All Prompts

To retrieve a list of all prompts, send a `GET` request to `/api/v1/prompts`:

**Request:**

```http
GET /api/v1/prompts
```

**Response:**

```json
[
    {
        "id": "prompt123",
        "text": "Generate a sales report for the last month",
        "db_connection_id": "db123",
        "schemas": ["public"],
        "context": [{"user": "admin"}],
        "metadata": {"created_by": "admin"},
        "created_at": "2024-09-09T12:34:56Z"
    }
]
```

#### Retrieving a Specific Prompt

To retrieve a specific prompt, send a `GET` request to `/api/v1/prompts/{prompt_id}`:

**Request:**

```http
GET /api/v1/prompts/prompt123
```

**Response:**

```json
{
    "id": "prompt123",
    "text": "Generate a sales report for the last month",
    "db_connection_id": "db123",
    "schemas": ["public"],
    "context": [{"user": "admin"}],
    "metadata": {"created_by": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```

#### Updating a Prompt

To update a prompt, send a `PUT` request to `/api/v1/prompts/{prompt_id}`:

**Request:**

```http
PUT /api/v1/prompts/prompt123
Content-Type: application/json

{
    "text": "Generate a detailed sales report for the last quarter",
    "db_connection_id": "db123",
    "schemas": ["public"],
    "context": [{"user": "admin"}],
    "metadata": {"updated_by": "admin"}
}
```

**Response:**

```json
{
    "id": "prompt123",
    "text": "Generate a detailed sales report for the last quarter",
    "db_connection_id": "db123",
    "schemas": ["public"],
    "context": [{"user": "admin"}],
    "metadata": {"updated_by": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```

#### Deleting a Prompt

To delete a prompt, send a `DELETE` request to `/api/v1/prompts/{prompt_id}`:

**Request:**

```http
DELETE /api/v1/prompts/prompt123
```

**Response:**

```json
{
    "id": "prompt123",
    "text": "Generate a detailed sales report for the last quarter",
    "db_connection_id": "db123",
    "schemas": ["public"],
    "context": [{"user": "admin"}],
    "metadata": {"updated_by": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```
