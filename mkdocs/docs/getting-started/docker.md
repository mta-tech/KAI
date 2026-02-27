# Docker Deployment

## LangGraph Server (Recommended for Production)

Build and run the LangGraph server with full stack (PostgreSQL, Redis, Typesense):

```bash
# Build the LangGraph container image
uv run langgraph build -t kai-langgraph:latest

# Start the full stack
docker compose -f docker-compose.langgraph.yml up -d
```

### Services Started

| Service | URL | Description |
|---------|-----|-------------|
| LangGraph API | http://localhost:8123 | Graphs: `session`, `sql_agent` |
| Typesense | http://localhost:8108 | Vector search |
| PostgreSQL | localhost:5433 | State persistence |
| Redis | localhost:6379 | Streaming |

### Health Check

```bash
curl http://localhost:8123/ok
```

## Typesense Only (Local Development)

```bash
# Start only Typesense for local development
docker compose up typesense -d
```

## Docker Network

The LangGraph stack uses `kai_langgraph_network` bridge network. Services connect via container names:

- `TYPESENSE_HOST=typesense`
- `REDIS_URI=redis://langgraph-redis:6379`
- `DATABASE_URI=postgres://postgres:postgres@langgraph-postgres:5432/postgres`

## Alternative: Manual Dockerfile Build

```bash
# Build using Dockerfile.langgraph directly
docker build -f Dockerfile.langgraph -t kai-langgraph .

# Run standalone (requires external Typesense/Redis/PostgreSQL)
docker run -p 8123:8123 --env-file .env kai-langgraph
```
