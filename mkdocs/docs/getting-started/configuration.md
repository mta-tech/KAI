# Configuration

## Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `CHAT_FAMILY` | LLM provider | `openai`, `google`, `ollama` |
| `CHAT_MODEL` | Model name | `gpt-4o-mini`, `gemini-2.0-flash` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `ENCRYPT_KEY` | Fernet encryption key | Generate with command below |
| `TYPESENSE_HOST` | Typesense server host | `localhost` (dev), `typesense` (Docker) |

## Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MEMORY_BACKEND` | Memory backend | `typesense` |
| `MCP_ENABLED` | Enable Model Context Protocol | `false` |
| `AGENT_LANGUAGE` | Agent language | `en` |
| `AGENT_MAX_ITERATIONS` | Max agent iterations | `20` |
| `DH_ENGINE_TIMEOUT` | Engine timeout (seconds) | `150` |
| `SQL_EXECUTION_TIMEOUT` | SQL timeout (seconds) | `60` |
| `UPPER_LIMIT_QUERY_RETURN_ROWS` | Max query rows | `50` |

## Generate Encryption Key

```bash
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Docker Configuration

For Docker deployments, use these host values:

| Service | Host Value |
|---------|------------|
| Typesense | `typesense` |
| Redis | `langgraph-redis` |
| PostgreSQL | `langgraph-postgres` |

See `.env.example` for a complete configuration template.
