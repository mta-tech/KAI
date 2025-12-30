# Troubleshooting Guide

Common issues and solutions when working with KAI.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Connection Problems](#connection-problems)
- [API Errors](#api-errors)
- [LLM & Agent Issues](#llm--agent-issues)
- [Database Issues](#database-issues)
- [Performance Problems](#performance-problems)
- [Docker Issues](#docker-issues)

## Installation Issues

### Problem: `uv: command not found`

**Solution:**

Install uv package manager:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart your terminal, then verify:
uv --version
```

### Problem: Python version too old

**Error:** `Python 3.11 or higher is required`

**Solution:**

```bash
# Check current version
python --version

# Install Python 3.11+ from python.org
# Or use pyenv:
pyenv install 3.11.9
pyenv global 3.11.9
```

### Problem: `cryptography` installation fails

**Error:** `Failed to build cryptography`

**Solution:**

Install system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev

# macOS
brew install openssl

# Then retry:
uv sync
```

## Connection Problems

### Problem: Cannot connect to Typesense

**Error:** `Connection refused to localhost:8108`

**Solution:**

1. **Check if Typesense is running:**
   ```bash
   docker compose ps typesense
   ```

2. **Start Typesense if stopped:**
   ```bash
   docker compose up typesense -d
   ```

3. **Verify Typesense health:**
   ```bash
   curl http://localhost:8108/health
   ```

4. **Check TYPESENSE_HOST in .env:**
   ```bash
   # For local dev:
   TYPESENSE_HOST=localhost

   # For Docker compose:
   TYPESENSE_HOST=typesense
   ```

### Problem: Database connection fails

**Error:** `Could not connect to database`

**Solutions:**

1. **Test connection manually:**
   ```bash
   # PostgreSQL
   psql -h localhost -U username -d database

   # MySQL
   mysql -h localhost -u username -p database
   ```

2. **Check connection URI format:**
   ```bash
   # Correct format:
   postgresql://user:password@host:5432/database
   mysql://user:password@host:3306/database
   ```

3. **Verify network connectivity:**
   ```bash
   # Test if database host is reachable
   telnet database-host 5432
   # Or
   nc -zv database-host 5432
   ```

4. **Check firewall rules:**
   - Ensure database port is open
   - Verify database allows remote connections
   - Check database authentication (pg_hba.conf for PostgreSQL)

### Problem: LLM API connection timeout

**Error:** `OpenAI API request timed out`

**Solutions:**

1. **Check API key:**
   ```bash
   # Verify key is set in .env
   echo $OPENAI_API_KEY
   ```

2. **Test API manually:**
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

3. **Increase timeout:**
   ```bash
   # In .env
   DH_ENGINE_TIMEOUT=300  # Increase from default 150
   ```

4. **Check network/proxy:**
   ```bash
   # Test HTTPS connectivity
   curl -I https://api.openai.com
   ```

## API Errors

### Problem: 500 Internal Server Error

**Solutions:**

1. **Check server logs:**
   ```bash
   # Docker logs
   docker compose logs kai_engine -f

   # Local development logs appear in terminal
   ```

2. **Verify all environment variables:**
   ```bash
   # Check .env has all required vars
   grep -E 'CHAT_FAMILY|CHAT_MODEL|ENCRYPT_KEY' .env
   ```

3. **Restart services:**
   ```bash
   docker compose restart
   # or
   uv run python -m app.main
   ```

### Problem: 422 Unprocessable Entity

**Error:** Validation error on API request

**Solution:**

Check request body matches API schema:

```bash
# View API documentation
open http://localhost:8015/docs

# Example correct format:
curl -X POST http://localhost:8015/api/v1/database-connections \
  -H "Content-Type: application/json" \
  -d '{
    "alias": "my_db",
    "connection_uri": "postgresql://localhost/db"
  }'
```

### Problem: 401 Unauthorized (if auth enabled)

**Solution:**

Include auth token in request:

```bash
curl -X GET http://localhost:8015/api/v1/sessions \
  -H "Authorization: Bearer your-token-here"
```

## LLM & Agent Issues

### Problem: Agent produces incorrect SQL

**Solutions:**

1. **Ensure schema is scanned:**
   ```bash
   uv run kai-agent scan-all your_db -d
   ```

2. **Add custom instructions:**
   ```bash
   curl -X POST http://localhost:8015/api/v1/instructions \
     -H "Content-Type: application/json" \
     -d '{
       "instruction": "Use LEFT JOIN instead of INNER JOIN for customer queries",
       "db_connection_id": "your-id"
     }'
   ```

3. **Provide better context:**
   - Add table descriptions
   - Create business glossary terms
   - Include example queries

4. **Try different model:**
   ```bash
   # In .env, switch to more powerful model:
   CHAT_MODEL=gpt-4o  # Instead of gpt-4o-mini
   ```

### Problem: Agent gets stuck in loop

**Error:** `Max iterations exceeded`

**Solutions:**

1. **Increase iteration limit:**
   ```bash
   # In .env
   AGENT_MAX_ITERATIONS=30  # Increase from default 20
   ```

2. **Simplify query:**
   - Break complex queries into smaller parts
   - Provide more specific instructions

3. **Check logs for error patterns:**
   ```bash
   docker compose logs kai_engine | grep ERROR
   ```

### Problem: LLM rate limit exceeded

**Error:** `Rate limit reached for requests`

**Solutions:**

1. **Add retry delay** (automatic in most cases)

2. **Use different model tier:**
   ```bash
   # Upgrade OpenAI plan or use different provider
   CHAT_FAMILY=google
   CHAT_MODEL=gemini-2.0-flash
   ```

3. **Implement caching:**
   - Results are cached in Typesense by default
   - Check if query was already answered

## Database Issues

### Problem: Schema scan fails

**Error:** `Failed to retrieve table information`

**Solutions:**

1. **Check database permissions:**
   ```sql
   -- PostgreSQL: User needs SELECT on information_schema
   GRANT SELECT ON ALL TABLES IN SCHEMA information_schema TO your_user;

   -- MySQL
   GRANT SELECT ON information_schema.* TO 'your_user'@'%';
   ```

2. **Verify table exists:**
   ```sql
   -- List all tables
   SELECT table_name FROM information_schema.tables
   WHERE table_schema = 'public';  -- or your schema
   ```

3. **Try manual scan:**
   ```bash
   # Scan specific tables
   curl -X POST http://localhost:8015/api/v1/table-descriptions/sync-schemas \
     -H "Content-Type: application/json" \
     -d '{
       "db_connection_id": "your-id",
       "table_names": ["users", "orders"]
     }'
   ```

### Problem: SQL execution timeout

**Error:** `Query execution exceeded timeout`

**Solutions:**

1. **Increase SQL timeout:**
   ```bash
   # In .env
   SQL_EXECUTION_TIMEOUT=120  # Increase from default 60
   ```

2. **Optimize query:**
   - Add indexes to frequently queried columns
   - Limit result set size
   - Use WHERE clauses to filter data

3. **Check query execution plan:**
   ```sql
   EXPLAIN ANALYZE your_query;
   ```

### Problem: Encrypted credentials error

**Error:** `Invalid encryption key`

**Solution:**

1. **Verify ENCRYPT_KEY is set:**
   ```bash
   grep ENCRYPT_KEY .env
   ```

2. **Generate new key if missing:**
   ```bash
   uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

3. **Update .env with generated key**

4. **Restart services after updating .env**

## Performance Problems

### Problem: Slow query generation

**Solutions:**

1. **Use faster model:**
   ```bash
   # In .env
   CHAT_MODEL=gpt-4o-mini  # Faster than gpt-4o
   # or
   CHAT_MODEL=gemini-2.0-flash  # Very fast
   ```

2. **Enable caching:**
   - Typesense caches results by default
   - Ensure TYPESENSE_HOST is correctly configured

3. **Reduce context size:**
   - Scan only necessary tables
   - Limit instruction count

### Problem: High memory usage

**Solutions:**

1. **Limit result rows:**
   ```bash
   # In .env
   UPPER_LIMIT_QUERY_RETURN_ROWS=50  # Or lower
   ```

2. **Increase Docker memory:**
   ```bash
   # In docker-compose.yml
   services:
     kai_engine:
       mem_limit: 4g
   ```

3. **Monitor resource usage:**
   ```bash
   docker stats
   ```

## Docker Issues

### Problem: Port already in use

**Error:** `Bind for 0.0.0.0:8015 failed: port is already allocated`

**Solutions:**

1. **Find what's using the port:**
   ```bash
   # macOS/Linux
   lsof -i :8015

   # Windows
   netstat -ano | findstr :8015
   ```

2. **Stop conflicting service or change port:**
   ```bash
   # In .env
   APP_PORT=8016  # Use different port

   # Update docker-compose.yml ports:
   ports:
     - "8016:8015"
   ```

### Problem: Volume permission denied

**Error:** `Permission denied: '/data'`

**Solutions:**

1. **Fix volume permissions:**
   ```bash
   sudo chown -R $(whoami):$(whoami) app/data/dbdata
   ```

2. **Or use Docker user mapping:**
   ```yaml
   # In docker-compose.yml
   services:
     typesense:
       user: "${UID}:${GID}"
   ```

### Problem: Container keeps restarting

**Solutions:**

1. **Check container logs:**
   ```bash
   docker compose logs kai_engine
   ```

2. **Verify environment variables:**
   ```bash
   docker compose config
   ```

3. **Remove and recreate containers:**
   ```bash
   docker compose down -v
   docker compose up -d
   ```

## Getting More Help

If your issue isn't listed here:

1. **Check logs:**
   ```bash
   # Docker
   docker compose logs -f

   # Local development
   # Logs appear in terminal
   ```

2. **Enable debug mode:**
   ```bash
   # In .env
   APP_ENVIRONMENT=DEBUG
   ```

3. **Search existing issues:**
   - [GitHub Issues](https://github.com/your-org/kai/issues)

4. **Create new issue:**
   - Include error message
   - Describe steps to reproduce
   - Share relevant logs (remove sensitive data)
   - Mention your environment (OS, Python version, etc.)

5. **Join discussions:**
   - [GitHub Discussions](https://github.com/your-org/kai/discussions)

---

**Still stuck?** Open an issue with:
- Error message
- Steps to reproduce
- Environment details
- Relevant logs
