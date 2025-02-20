# Context Store API

&#x20;The Context Store API allows you to manage context stores, which are used to store and retrieve SQL prompts and associated metadata. This API provides endpoints for creating, retrieving, updating, and deleting context stores.

### Endpoints

#### 1. Create a Context Store

**Endpoint:** `/api/v1/context-stores`\
**Method:** `POST`\
**Request Body:**

```json
{
    "db_connection_id": "string",
    "prompt": "string",
    "sql": "string",
    "metadata": {"key": "value"}
}
```

**Description:** Creates a new context store entry with the specified database connection ID, prompt, SQL query, and optional metadata.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "prompt": "string",
    "sql": "string",
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 2. Retrieve All Context Stores

**Endpoint:** `/api/v1/context-stores`\
**Method:** `GET`\
**Description:** Retrieves a list of all context stores.

**Response:**

```json
[
    {
        "id": "string",
        "db_connection_id": "string",
        "prompt": "string",
        "sql": "string",
        "metadata": {"key": "value"},
        "created_at": "string"
    }
]
```

#### 3. Retrieve a Specific Context Store

**Endpoint:** `/api/v1/context-stores/{context_store_id}`\
**Method:** `GET`\
**Description:** Retrieves the details of a specific context store entry identified by `context_store_id`.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "prompt": "string",
    "sql": "string",
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 4. Retrieve Similar Context Stores

**Endpoint:** `/api/v1/context-stores/semantic-search`\
**Method:** `POST`\
**Description:** Retrieves the details of `top k` most similar context store entries.

**Response:**

```json
{
    "db_connection_id": "string",
    "prompt": "string",
    "top_k": "int"
}
```

#### 5. Update a Context Store

**Endpoint:** `/api/v1/context-stores/{context_store_id}`\
**Method:** `PUT`\
**Request Body:**

```json
{
    "prompt": "string",
    "sql": "string",
    "metadata": {"key": "value"}
}
```

**Description:** Updates the details of an existing context store entry identified by `context_store_id`.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "prompt": "string",
    "sql": "string",
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 6. Delete a Context Store

**Endpoint:** `/api/v1/context-stores/{context_store_id}`\
**Method:** `DELETE`\
**Description:** Deletes a specific context store entry identified by `context_store_id`.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "prompt": "string",
    "sql": "string",
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

### Example Usage

#### Creating a Context Store

To create a new context store, send a `POST` request to `/api/v1/context-stores`:

**Request:**

```http
POST /api/v1/context-stores
Content-Type: application/json

{
    "db_connection_id": "db123",
    "prompt": "What is the total revenue?",
    "sql": "SELECT SUM(amount) AS revenue FROM sales",
    "metadata": {"created_by": "admin"}
}
```

**Response:**

```json
{
    "id": "ctx123",
    "db_connection_id": "db123",
    "prompt": "What is the total revenue?",
    "sql": "SELECT SUM(amount) AS revenue FROM sales",
    "metadata": {"created_by": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```

#### Retrieving All Context Stores

To retrieve a list of all context stores, send a `GET` request to `/api/v1/context-stores`:

**Request:**

```http
GET /api/v1/context-stores
```

**Response:**

```json
[
    {
        "id": "ctx123",
        "db_connection_id": "db123",
        "prompt": "What is the total revenue?",
        "sql": "SELECT SUM(amount) AS revenue FROM sales",
        "metadata": {"created_by": "admin"},
        "created_at": "2024-09-09T12:34:56Z"
    }
]
```

#### Retrieving a Specific Context Store

To retrieve a specific context store, send a `GET` request to `/api/v1/context-stores/{context_store_id}`:

**Request:**

```http
GET /api/v1/context-stores/ctx123
```

**Response:**

```json
{
    "id": "ctx123",
    "db_connection_id": "db123",
    "prompt": "What is the total revenue?",
    "sql": "SELECT SUM(amount) AS revenue FROM sales",
    "metadata": {"created_by": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```

#### Retrieving Similar Context Stores

To retrieve a specific context store, send a `POST` request to `/api/v1/context-stores/semantic-search`:

**Request:**

```http
POST /api/v1/context-stores/semantic-search
Content-Type: application/json

{
    "db_connection_id": "db123"
    "prompt": How many regency in,
    "top_k": 3
}
```

**Response:**

```json
[
    {
        "prompt_text": "How many regency in Kutai?",
        "sql": "SELECT SUM(amount) AS revenue FROM sales",
        "score": "0.8117260634899139"
    }
]
```

#### Updating a Context Store

To update a context store, send a `PUT` request to `/api/v1/context-stores/{context_store_id}`:

**Request:**

```http
PUT /api/v1/context-stores/ctx123
Content-Type: application/json

{
    "prompt": "What is the total revenue from Q1?",
    "sql": "SELECT SUM(amount) AS revenue FROM sales WHERE quarter = 'Q1'",
    "metadata": {"updated_by": "admin"}
}
```

**Response:**

```json
{
    "id": "ctx123",
    "db_connection_id": "db123",
    "prompt": "What is the total revenue from Q1?",
    "sql": "SELECT SUM(amount) AS revenue FROM sales WHERE quarter = 'Q1'",
    "metadata": {"updated_by": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```

#### Deleting a Context Store

To delete a context store, send a `DELETE` request to `/api/v1/context-stores/{context_store_id}`:

**Request:**

```http
DELETE /api/v1/context-stores/ctx123
```

**Response:**

```json
{
    "id": "ctx123",
    "db_connection_id": "db123",
    "prompt": "What is the total revenue from Q1?",
    "sql": "SELECT SUM(amount) AS revenue FROM sales WHERE quarter = 'Q1'",
    "metadata": {"updated_by": "admin"},
    "created_at": "2024-09-09T12:34:56Z"
}
```
