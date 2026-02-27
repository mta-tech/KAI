# API Reference

KAI provides a comprehensive REST API with 40+ endpoints for programmatic access.

## Base URL

```
http://localhost:8015/api/v1
```

## Authentication

Currently, KAI uses simple API key authentication (if configured). Future versions will support OAuth2.

## Response Format

All responses are JSON with consistent structure:

```json
{
  "data": { ... },
  "status": "success"
}
```

Error responses:

```json
{
  "error": "Error message",
  "status": "error",
  "code": "ERROR_CODE"
}
```

## API Documentation

| API | Description |
|-----|-------------|
| [Context Platform](context-platform-api.md) | Context assets, benchmarks, feedback |
| Session API | Session management and chat |
| Query API | Query execution |
| Dashboard API | Dashboard creation and management |

## Quick Examples

### List Context Assets

```bash
curl -X GET "http://localhost:8015/api/v1/context/assets?db_connection_id=mydb"
```

### Create Context Asset

```bash
curl -X POST "http://localhost:8015/api/v1/context/assets" \
  -H "Content-Type: application/json" \
  -d '{
    "db_connection_id": "mydb",
    "asset_type": "instruction",
    "canonical_key": "revenue_analysis",
    "name": "Revenue Analysis Rules",
    "content": {"rules": ["Always filter active records"]}
  }'
```

### Run Query

```bash
curl -X POST "http://localhost:8015/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "db_connection_id": "mydb",
    "question": "Show total sales by month"
  }'
```

## Interactive Documentation

Access the full interactive API documentation at:

- **Swagger UI**: http://localhost:8015/docs
- **ReDoc**: http://localhost:8015/redoc
