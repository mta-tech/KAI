# Deployment Guide

This guide covers deploying KAI in production environments.

## Table of Contents

- [Production Checklist](#production-checklist)
- [Docker Deployment](#docker-deployment)
- [LangGraph Production Server](#langgraph-production-server)
- [Environment Configuration](#environment-configuration)
- [Scaling Strategies](#scaling-strategies)
- [Monitoring & Logging](#monitoring--logging)
- [Security Best Practices](#security-best-practices)
- [Backup & Recovery](#backup--recovery)

## Production Checklist

Before deploying to production:

- [ ] All environment variables configured
- [ ] Encryption key generated and secured
- [ ] Database credentials encrypted
- [ ] LLM API keys configured with rate limits
- [ ] Typesense data directory backed up
- [ ] Firewall rules configured
- [ ] HTTPS/TLS enabled
- [ ] Monitoring and logging set up
- [ ] Backup strategy in place
- [ ] Health checks configured
- [ ] Resource limits defined

## Docker Deployment

### Standard Docker Compose

Basic production deployment with Docker Compose:

```bash
# 1. Clone repository
git clone https://github.com/your-org/kai.git
cd kai

# 2. Create production .env
cp .env.example .env.production

# Edit .env.production with production values:
# - Secure ENCRYPT_KEY
# - Production LLM API keys
# - Production database URLs
# - TYPESENSE_HOST=typesense

# 3. Deploy
docker compose -f docker-compose.yml --env-file .env.production up -d

# 4. Verify deployment
docker compose ps
curl http://localhost:8015/health
```

### Production docker-compose.yml

Example production configuration:

```yaml
version: '3.8'

services:
  typesense:
    image: typesense/typesense:26.0
    container_name: kai_typesense
    restart: always
    ports:
      - "8108:8108"
    volumes:
      - ./typesense-data:/data
    environment:
      TYPESENSE_API_KEY: ${TYPESENSE_API_KEY}
      TYPESENSE_DATA_DIR: /data
    command: '--data-dir /data --api-key=${TYPESENSE_API_KEY} --enable-cors'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8108/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  kai_engine:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: kai_api
    restart: always
    ports:
      - "8015:8015"
    depends_on:
      typesense:
        condition: service_healthy
    environment:
      - APP_ENVIRONMENT=PRODUCTION
      - TYPESENSE_HOST=typesense
    env_file:
      - .env.production
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8015/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  # Optional: Nginx reverse proxy
  nginx:
    image: nginx:alpine
    container_name: kai_nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - kai_engine

networks:
  default:
    name: kai_network

volumes:
  typesense-data:
    driver: local
```

## LangGraph Production Server

For production deployments, use the LangGraph server for better agent orchestration:

### Build LangGraph Image

```bash
# Build the LangGraph container
uv run langgraph build -t kai-langgraph:latest

# Verify image
docker images | grep kai-langgraph
```

### Deploy Full LangGraph Stack

```bash
# Start LangGraph with PostgreSQL, Redis, and Typesense
docker compose -f docker-compose.langgraph.yml up -d

# Services started:
# - LangGraph API (port 8123)
# - PostgreSQL (port 5433)
# - Redis (port 6379)
# - Typesense (port 8108)

# Health check
curl http://localhost:8123/ok
```

### LangGraph Configuration

The `langgraph.json` file configures the graphs:

```json
{
  "graphs": {
    "session": "./app/langgraph_server/graphs.py:session_graph",
    "sql_agent": "./app/langgraph_server/graphs.py:sql_agent_graph"
  },
  "env": ".env",
  "python_version": "3.11",
  "pip_config_file": "pyproject.toml"
}
```

### Production Environment for LangGraph

```bash
# .env for LangGraph
TYPESENSE_HOST=typesense
REDIS_URI=redis://langgraph-redis:6379
DATABASE_URI=postgres://postgres:postgres@langgraph-postgres:5432/postgres

# LLM Configuration
OPENAI_API_KEY=your-key
CHAT_FAMILY=openai
CHAT_MODEL=gpt-4o-mini

# Security
ENCRYPT_KEY=your-fernet-key
```

## Environment Configuration

### Production .env Template

```bash
# Application
APP_NAME="KAI API"
APP_ENVIRONMENT=PRODUCTION
APP_HOST=0.0.0.0
APP_PORT=8015
APP_ENABLE_HOT_RELOAD=0

# LLM Configuration
CHAT_FAMILY=openai
CHAT_MODEL=gpt-4o-mini
OPENAI_API_KEY=your-production-key

# Typesense
TYPESENSE_API_KEY=secure-random-key
TYPESENSE_HOST=typesense
TYPESENSE_PORT=8108
TYPESENSE_PROTOCOL=HTTP
TYPESENSE_TIMEOUT=5

# Security
ENCRYPT_KEY=your-secure-fernet-key

# Performance
AGENT_MAX_ITERATIONS=20
DH_ENGINE_TIMEOUT=150
SQL_EXECUTION_TIMEOUT=60
UPPER_LIMIT_QUERY_RETURN_ROWS=100

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Optional: Memory
MEMORY_BACKEND=typesense

# Optional: MCP
MCP_ENABLED=false
```

### Secrets Management

**Option 1: Docker Secrets**

```yaml
services:
  kai_engine:
    secrets:
      - openai_api_key
      - encrypt_key

secrets:
  openai_api_key:
    file: ./secrets/openai_key.txt
  encrypt_key:
    file: ./secrets/encrypt_key.txt
```

**Option 2: Environment Variable Files**

```bash
# Create secure .env file
touch .env.production
chmod 600 .env.production

# Load from secure vault (e.g., HashiCorp Vault)
vault kv get -field=value secret/kai/openai_key > .env.production
```

## Scaling Strategies

### Horizontal Scaling

KAI is stateless and can be horizontally scaled:

```yaml
services:
  kai_engine:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        max_attempts: 3
```

### Load Balancer Configuration

**Nginx Example:**

```nginx
upstream kai_backend {
    least_conn;
    server kai_1:8015 weight=1;
    server kai_2:8015 weight=1;
    server kai_3:8015 weight=1;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://kai_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 300s;
    }

    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://kai_backend/health;
    }
}
```

### Typesense Clustering

For high availability, deploy Typesense cluster:

```yaml
services:
  typesense-1:
    image: typesense/typesense:26.0
    command: >
      --data-dir /data
      --api-key=${TYPESENSE_API_KEY}
      --nodes=typesense-1:8108,typesense-2:8108,typesense-3:8108

  typesense-2:
    image: typesense/typesense:26.0
    command: >
      --data-dir /data
      --api-key=${TYPESENSE_API_KEY}
      --nodes=typesense-1:8108,typesense-2:8108,typesense-3:8108

  typesense-3:
    image: typesense/typesense:26.0
    command: >
      --data-dir /data
      --api-key=${TYPESENSE_API_KEY}
      --nodes=typesense-1:8108,typesense-2:8108,typesense-3:8108
```

## Monitoring & Logging

### Health Checks

KAI provides health check endpoints:

```bash
# API health
curl http://localhost:8015/health
# Returns: {"status":"healthy"}

# Typesense health
curl http://localhost:8108/health
# Returns: {"ok":true}
```

### Prometheus Metrics

Add Prometheus metrics (optional):

```python
# app/server/middleware.py
from prometheus_client import Counter, Histogram

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
```

### Logging Configuration

```python
# app/server/config.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/kai.log'),
        logging.StreamHandler()
    ]
)
```

### Log Aggregation

**Using Docker logs:**

```bash
# View logs
docker compose logs -f kai_engine

# Export logs
docker compose logs kai_engine > kai_logs.txt
```

**Using ELK Stack:**

```yaml
services:
  filebeat:
    image: docker.elastic.co/beats/filebeat:8.11.0
    volumes:
      - ./logs:/app/logs:ro
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
```

## Security Best Practices

### 1. Use HTTPS

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}
```

### 2. Encrypt Sensitive Data

- Use `ENCRYPT_KEY` for database credentials
- Store API keys in secrets management
- Never commit `.env` files

### 3. Network Security

```yaml
services:
  kai_engine:
    networks:
      - internal  # No external access

  nginx:
    networks:
      - internal
      - external

networks:
  internal:
    internal: true
  external:
```

### 4. Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api/ {
    limit_req zone=api_limit burst=20;
    proxy_pass http://kai_backend;
}
```

### 5. Input Validation

- Pydantic validates all inputs
- SQL injection prevented by parameterized queries
- Implement API authentication if needed

## Backup & Recovery

### Typesense Backup

```bash
# Backup Typesense data
docker cp kai_typesense:/data ./backups/typesense-$(date +%Y%m%d)

# Restore
docker cp ./backups/typesense-20240101 kai_typesense:/data
docker compose restart typesense
```

### Database Connection Backup

```bash
# Export connections (encrypted)
curl http://localhost:8015/api/v1/database-connections > connections_backup.json

# Restore (re-import after setup)
# Manual process via API
```

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/kai"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup Typesense
docker cp kai_typesense:/data $BACKUP_DIR/typesense_$DATE

# Backup configuration
cp .env.production $BACKUP_DIR/env_$DATE

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} \;

echo "Backup completed: $DATE"
```

### Disaster Recovery

1. **Restore Typesense data**
2. **Restore .env configuration**
3. **Restart services**
4. **Verify health checks**
5. **Re-scan database schemas if needed**

## Deployment Checklist

Final checklist before going live:

- [ ] Production .env configured
- [ ] HTTPS enabled
- [ ] Firewall configured
- [ ] Resource limits set
- [ ] Health checks passing
- [ ] Monitoring enabled
- [ ] Logs aggregated
- [ ] Backup script running
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Team trained on operations

---

**Need help?** Check [Troubleshooting](TROUBLESHOOTING.md) or open an issue on GitHub.
