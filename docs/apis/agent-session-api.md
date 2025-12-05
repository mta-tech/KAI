# Agent Session API

The Agent Session API provides endpoints for managing autonomous agent sessions in KAI. Agent sessions enable fully autonomous data analysis with different operational modes, supporting complex multi-step analysis tasks.

### Endpoints

#### 1. Create an Agent Session

**Endpoint:** `/api/v1/agent-sessions`\
**Method:** `POST`\
**Request Body:**

```json
{
    "db_connection_id": "string",
    "mode": "full_autonomy",
    "recursion_limit": 100,
    "title": "string",
    "metadata": {"key": "value"}
}
```

**Fields:**
- `db_connection_id` (required): Database connection ID for this session.
- `mode` (optional): Agent operation mode. Options: `analysis`, `query`, `script`, `full_autonomy` (default: `full_autonomy`).
- `recursion_limit` (optional): Maximum recursion depth for LangGraph (default: 100, range: 1-500).
- `title` (optional): Session title for identification.
- `metadata` (optional): Custom metadata for the session.

**Description:** Creates a new autonomous agent session.

**Response:**

```json
{
    "session_id": "string"
}
```

#### 2. List Agent Sessions

**Endpoint:** `/api/v1/agent-sessions`\
**Method:** `GET`\
**Request Parameters:**

- `db_connection_id`: (Optional) Filter by database connection ID.
- `status`: (Optional) Filter by session status.
- `limit`: (Optional) Maximum sessions to return (default: 100, max: 1000).
- `offset`: (Optional) Number of sessions to skip (default: 0).

**Description:** Retrieves a list of agent sessions with optional filtering.

**Response:**

```json
{
    "sessions": [
        {
            "id": "string",
            "db_connection_id": "string",
            "status": "active",
            "mode": "full_autonomy",
            "recursion_limit": 100,
            "title": "string",
            "created_at": "2024-09-09T12:34:56Z",
            "updated_at": "2024-09-09T12:34:56Z",
            "metadata": {"key": "value"}
        }
    ],
    "total": 100,
    "limit": 100,
    "offset": 0
}
```

#### 3. Get Agent Session Details

**Endpoint:** `/api/v1/agent-sessions/{session_id}`\
**Method:** `GET`\
**Description:** Retrieves details of a specific agent session.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "status": "active",
    "mode": "full_autonomy",
    "recursion_limit": 100,
    "title": "string",
    "created_at": "2024-09-09T12:34:56Z",
    "updated_at": "2024-09-09T12:34:56Z",
    "metadata": {"key": "value"}
}
```

#### 4. Update Agent Session

**Endpoint:** `/api/v1/agent-sessions/{session_id}`\
**Method:** `PATCH`\
**Request Body:**

```json
{
    "title": "string",
    "status": "active",
    "metadata": {"key": "value"}
}
```

**Description:** Updates an agent session's title, status, or metadata.

**Response:**

```json
{
    "id": "string",
    "db_connection_id": "string",
    "status": "active",
    "mode": "full_autonomy",
    "recursion_limit": 100,
    "title": "string",
    "created_at": "2024-09-09T12:34:56Z",
    "updated_at": "2024-09-09T12:34:56Z",
    "metadata": {"key": "value"}
}
```

#### 5. Delete Agent Session

**Endpoint:** `/api/v1/agent-sessions/{session_id}`\
**Method:** `DELETE`\
**Description:** Deletes an agent session.

**Response:**

```json
{
    "status": "deleted"
}
```

#### 6. Pause Agent Session

**Endpoint:** `/api/v1/agent-sessions/{session_id}/pause`\
**Method:** `POST`\
**Description:** Pauses an active or running agent session.

**Response:**

```json
{
    "status": "paused"
}
```

#### 7. Resume Agent Session

**Endpoint:** `/api/v1/agent-sessions/{session_id}/resume`\
**Method:** `POST`\
**Description:** Resumes a paused agent session.

**Response:**

```json
{
    "status": "active"
}
```

### Agent Modes

The agent supports different operational modes:

| Mode | Description |
|------|-------------|
| `analysis` | Focus on data analysis and insights generation |
| `query` | Simple question-answering with SQL generation |
| `script` | Script execution and automation tasks |
| `full_autonomy` | Full autonomous operation with all capabilities |

### Session Status

Agent sessions can have the following statuses:

| Status | Description |
|--------|-------------|
| `active` | Session is active and ready to accept tasks |
| `paused` | Session is paused; can be resumed |
| `running` | Session is currently executing a task |
| `completed` | Session has completed all tasks |
| `failed` | Session encountered an error |

### Example Usage

#### Creating an Agent Session

**Request:**

```http
POST /api/v1/agent-sessions
Content-Type: application/json

{
    "db_connection_id": "db123",
    "mode": "full_autonomy",
    "recursion_limit": 150,
    "title": "Monthly Sales Analysis",
    "metadata": {"department": "finance"}
}
```

**Response:**

```json
{
    "session_id": "agent_sess_456"
}
```

#### Listing Agent Sessions

**Request:**

```http
GET /api/v1/agent-sessions?db_connection_id=db123&status=active&limit=10
```

**Response:**

```json
{
    "sessions": [
        {
            "id": "agent_sess_456",
            "db_connection_id": "db123",
            "status": "active",
            "mode": "full_autonomy",
            "recursion_limit": 150,
            "title": "Monthly Sales Analysis",
            "created_at": "2024-09-09T12:34:56Z",
            "updated_at": "2024-09-09T12:34:56Z",
            "metadata": {"department": "finance"}
        }
    ],
    "total": 1,
    "limit": 10,
    "offset": 0
}
```

#### Pausing and Resuming a Session

**Pause Request:**

```http
POST /api/v1/agent-sessions/agent_sess_456/pause
```

**Response:**

```json
{
    "status": "paused"
}
```

**Resume Request:**

```http
POST /api/v1/agent-sessions/agent_sess_456/resume
```

**Response:**

```json
{
    "status": "active"
}
```

### Error Handling

- **404 Not Found:** The specified agent session ID does not exist.
- **400 Bad Request:** Invalid request (e.g., cannot pause a session that is not active/running).
- **500 Internal Server Error:** An unexpected error occurred.
