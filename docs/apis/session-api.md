# Session API

The Session API provides endpoints for managing conversational sessions with KAI. Sessions maintain conversation history, context, and state across multiple queries, enabling multi-turn interactions with the database.

### Endpoints

#### 1. Create a Session

**Endpoint:** `/api/v1/sessions`\
**Method:** `POST`\
**Request Body:**

```json
{
    "db_connection_id": "string",
    "metadata": {"key": "value"}
}
```

**Description:** Creates a new session for the specified database connection.

**Response:**

```json
{
    "session_id": "string"
}
```

#### 2. List Sessions

**Endpoint:** `/api/v1/sessions`\
**Method:** `GET`\
**Request Parameters:**

- `db_connection_id`: (Optional) Filter sessions by database connection ID.
- `status`: (Optional) Filter sessions by status (active, closed).
- `limit`: (Optional) Maximum number of sessions to return (default: 100, max: 1000).
- `offset`: (Optional) Number of sessions to skip (default: 0).

**Description:** Retrieves a list of sessions with optional filtering.

**Response:**

```json
{
    "sessions": [
        {
            "id": "string",
            "db_connection_id": "string",
            "status": "string",
            "messages": [],
            "summary": "string",
            "metadata": {"key": "value"},
            "created_at": "2024-09-09T12:34:56Z",
            "updated_at": "2024-09-09T12:34:56Z"
        }
    ],
    "total": 100,
    "limit": 100,
    "offset": 0
}
```

#### 3. Get Session Details

**Endpoint:** `/api/v1/sessions/{session_id}`\
**Method:** `GET`\
**Description:** Retrieves details of a specific session including conversation history.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "status": "string",
    "messages": [
        {
            "id": "string",
            "role": "string",
            "query": "string",
            "sql": "string",
            "results_summary": "string",
            "analysis": "string",
            "timestamp": "2024-09-09T12:34:56Z"
        }
    ],
    "summary": "string",
    "metadata": {"key": "value"},
    "created_at": "2024-09-09T12:34:56Z",
    "updated_at": "2024-09-09T12:34:56Z"
}
```

#### 4. Delete Session

**Endpoint:** `/api/v1/sessions/{session_id}`\
**Method:** `DELETE`\
**Description:** Deletes a session and its conversation history.

**Response:**

```json
{
    "status": "deleted"
}
```

#### 5. Close Session

**Endpoint:** `/api/v1/sessions/{session_id}/close`\
**Method:** `POST`\
**Description:** Closes a session, marking it as inactive. The session data is preserved but no new queries can be submitted.

**Response:**

```json
{
    "status": "closed"
}
```

#### 6. Query Session (Streaming)

**Endpoint:** `/api/v1/sessions/{session_id}/query/stream`\
**Method:** `POST`\
**Request Body:**

```json
{
    "query": "string"
}
```

**Description:** Sends a natural language query to the session and streams the response via Server-Sent Events (SSE).

**Response:** Stream of Server-Sent Events with the following event types:

- **status**: Processing step updates
- **chunk**: SQL, results, and analysis chunks
- **done**: Final completion signal
- **error**: Error information if failed

### Example Usage

#### Creating a Session

To create a new session, send a `POST` request to `/api/v1/sessions`:

**Request:**

```http
POST /api/v1/sessions
Content-Type: application/json

{
    "db_connection_id": "db123",
    "metadata": {"user_id": "user456"}
}
```

**Response:**

```json
{
    "session_id": "sess789"
}
```

#### Listing Sessions

To list sessions for a database connection:

**Request:**

```http
GET /api/v1/sessions?db_connection_id=db123&status=active&limit=10
```

**Response:**

```json
{
    "sessions": [
        {
            "id": "sess789",
            "db_connection_id": "db123",
            "status": "active",
            "messages": [],
            "summary": null,
            "metadata": {"user_id": "user456"},
            "created_at": "2024-09-09T12:34:56Z",
            "updated_at": "2024-09-09T12:34:56Z"
        }
    ],
    "total": 1,
    "limit": 10,
    "offset": 0
}
```

#### Querying a Session

To send a query to a session:

**Request:**

```http
POST /api/v1/sessions/sess789/query/stream
Content-Type: application/json

{
    "query": "What were our total sales last month?"
}
```

**Response (SSE Stream):**

```
event: status
data: {"step": "generating_sql"}

event: chunk
data: {"type": "sql", "content": "SELECT SUM(amount) FROM sales WHERE date >= '2024-08-01'"}

event: chunk
data: {"type": "results", "content": "Total: $125,000"}

event: chunk
data: {"type": "analysis", "content": "Last month's sales totaled $125,000..."}

event: done
data: {"message_id": "msg123"}
```

### Error Handling

- **404 Not Found:** The specified session ID does not exist.
- **400 Bad Request:** Invalid request parameters or session is closed.
- **500 Internal Server Error:** An unexpected error occurred.
