# Database Connection API

The Database Connection API provides endpoints to manage database connections, including creating, listing, updating, and retrieving database connection details. Below is a guide on how to use these endpoints effectively.

### Endpoints

#### 1. Create a Database Connection

**Endpoint:** `/api/v1/database-connections`\
**Method:** `POST`\
**Request Body:**

```json
{
    "alias": "string",
    "connection_uri": "string",
    "schemas": ["string"],
    "metadata": {"key": "value"}
}
```

**Description:** Creates a new database connection with the provided details.

**Response:**

```json
{
    "id": "string",
    "alias": "string",
    "connection_uri": "string",
    "schemas": ["string"],
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

#### 2. List Database Connections

**Endpoint:** `/api/v1/database-connections`\
**Method:** `GET`\
**Description:** Retrieves a list of all database connections.

**Response:**

```json
[
    {
        "id": "string",
        "alias": "string",
        "connection_uri": "string",
        "schemas": ["string"],
        "metadata": {"key": "value"},
        "created_at": "string"
    }
]
```

#### 3. Update a Database Connection

**Endpoint:** `/api/v1/database-connections/{db_connection_id}`\
**Method:** `PUT`\
**Request Body:**

```json
{
    "alias": "string",
    "connection_uri": "string",
    "schemas": ["string"],
    "metadata": {"key": "value"}
}
```

**Description:** Updates the details of a specific database connection identified by `db_connection_id`.

**Response:**

```json
{
    "id": "string",
    "alias": "string",
    "connection_uri": "string",
    "schemas": ["string"],
    "metadata": {"key": "value"},
    "created_at": "string"
}
```

### Example Usage

#### Creating a Database Connection

To create a new database connection, send a `POST` request to `/api/v1/database-connections` with the required body. For example:

**Request:**

```http
POST /api/v1/database-connections
Content-Type: application/json

{
    "alias": "my_database",
    "connection_uri": "postgresql://user:password@localhost/dbname",
    "schemas": ["public"],
    "metadata": {"type": "postgres"}
}
```

**Response:**

```json
{
    "id": "12345",
    "alias": "my_database",
    "connection_uri": "postgresql://user:password@localhost/dbname",
    "schemas": ["public"],
    "metadata": {"type": "postgres"},
    "created_at": "2024-09-09T12:34:56Z"
}
```

#### Listing Database Connections

To retrieve a list of all database connections, send a `GET` request to `/api/v1/database-connections`:

**Request:**

```http
GET /api/v1/database-connections
```

**Response:**

```json
[
    {
        "id": "12345",
        "alias": "my_database",
        "connection_uri": "postgresql://user:password@localhost/dbname",
        "schemas": ["public"],
        "metadata": {"type": "postgres"},
        "created_at": "2024-09-09T12:34:56Z"
    }
]
```

#### Updating a Database Connection

To update an existing database connection, send a `PUT` request to `/api/v1/database-connections/{db_connection_id}` with the updated details:

**Request:**

```http
PUT /api/v1/database-connections/12345
Content-Type: application/json

{
    "alias": "updated_database",
    "connection_uri": "postgresql://user:password@localhost/updated_dbname",
    "schemas": ["public"],
    "metadata": {"type": "postgres", "version": "12"}
}
```

**Response:**

```json
{
    "id": "12345",
    "alias": "updated_database",
    "connection_uri": "postgresql://user:password@localhost/updated_dbname",
    "schemas": ["public"],
    "metadata": {"type": "postgres", "version": "12"},
    "created_at": "2024-09-09T12:34:56Z"
}
```

### Error Handling

* **400 Bad Request:** The request body is invalid or missing required fields.
* **404 Not Found:** The specified `db_connection_id` does not exist.
* **500 Internal Server Error:** An unexpected error occurred on the server.
