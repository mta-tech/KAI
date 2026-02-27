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
- [Context Platform Issues](#context-platform-issues)

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

### Problem: Context Platform LifecyclePolicyError

**Error:** `Lifecycle policy error`

**Solutions:**

1. **Check current asset state:**
   ```bash
   curl -X GET "http://localhost:8015/api/v1/context-assets/{db_id}/{asset_type}/{key}"
   ```

2. **Follow valid lifecycle transitions:**
   - Only DRAFT assets can be updated
   - Only DRAFT assets can be deleted
   - Only DRAFT assets can be promoted to VERIFIED
   - Only VERIFIED assets can be promoted to PUBLISHED
   - Only PUBLISHED assets can be deprecated

3. **Create revision for editing published assets:**
   ```bash
   curl -X POST "http://localhost:8015/api/v1/context-assets/{asset_id}/revision" \
     -H "Content-Type: application/json" \
     -d '{"author": "your-email@example.com"}'
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

## Context Platform Issues

### Problem: Asset not found

**Error:** `Asset not found: {asset_type}/{canonical_key}@{version}`

**Solutions:**

1. **Verify asset identifier:**
   ```bash
   # List all assets for a database connection
   curl -X GET "http://localhost:8015/api/v1/context-assets?db_connection_id=your-db"
   ```

2. **Check asset type spelling:**
   ```bash
   # Valid asset types:
   # - table_description
   # - glossary
   # - instruction
   # - skill
   ```

3. **Use "latest" version:**
   ```bash
   # If unsure of version, use latest
   curl -X GET "http://localhost:8015/api/v1/context-assets/db123/glossary/monthly_active_users?version=latest"
   ```

### Problem: Cannot update asset in non-DRAFT state

**Error:** `Cannot update asset in 'verified' state. Only DRAFT assets can be updated.`

**Solutions:**

1. **Create a draft revision:**
   ```bash
   curl -X POST "http://localhost:8015/api/v1/context-assets/{asset_id}/revision" \
     -H "Content-Type: application/json" \
     -d '{
       "author": "your-email@example.com"
     }'
   ```

2. **Or deprecate and recreate:**
   ```bash
   # If the asset should be completely replaced
   curl -X POST "http://localhost:8015/api/v1/context-assets/{asset_id}/deprecate" \
     -H "Content-Type: application/json" \
     -d '{
       "promoted_by": "your-email@example.com",
       "reason": "Replacing with new version"
     }'
   ```

### Problem: Invalid lifecycle transition

**Error:** `Invalid lifecycle transition from {current_state} to {target_state}`

**Solutions:**

1. **Understand valid transitions:**
   - `draft -> verified` (requires promotion)
   - `verified -> published` (requires promotion)
   - `published -> deprecated` (requires deprecation)
   - `Any state -> draft` (create revision)

2. **Follow proper promotion flow:**
   ```bash
   # Step 1: Create draft (automatic on creation)
   curl -X POST "http://localhost:8015/api/v1/context-assets" \
     -H "Content-Type: application/json" \
     -d '{
       "db_connection_id": "db123",
       "asset_type": "glossary",
       "canonical_key": "my_metric",
       "name": "My Metric",
       "content": {},
       "content_text": "Description"
     }'

   # Step 2: Promote to verified
   curl -X POST "http://localhost:8015/api/v1/context-assets/{asset_id}/promote/verified" \
     -H "Content-Type: application/json" \
     -d '{
       "promoted_by": "domain-expert@example.com",
       "change_note": "Reviewed and approved"
     }'

   # Step 3: Promote to published
   curl -X POST "http://localhost:8015/api/v1/context-assets/{asset_id}/promote/published" \
     -H "Content-Type: application/json" \
     -d '{
       "promoted_by": "approver@example.com",
       "change_note": "Approved for reuse"
     }'
   ```

### Problem: Invalid asset type

**Error:** `'invalid_type' is not a valid ContextAssetType`

**Solution:**

Use only valid asset types:

| Asset Type | Description | Example Content |
|-------------|-------------|------------------|
| `table_description` | Descriptive metadata about database tables | Column descriptions, keys, relationships |
| `glossary` | Business terminology and definitions | Metric definitions, business terms |
| `instruction` | Domain-specific analysis instructions | SQL patterns, analysis rules |
| `skill` | Reusable analysis patterns and templates | Analysis templates, workflows |

### Problem: Search returns no results

**Solutions:**

1. **Verify assets exist:**
   ```bash
   curl -X GET "http://localhost:8015/api/v1/context-assets?db_connection_id=your-db"
   ```

2. **Check search query:**
   ```bash
   # Use broader search terms
   curl -X POST "http://localhost:8015/api/v1/context-assets/search" \
     -H "Content-Type: application/json" \
     -d '{
       "db_connection_id": "your-db",
       "query": "user",  # More generic term
       "limit": 20
     }'
   ```

3. **Verify Typesense is running:**
   ```bash
   curl http://localhost:8108/health
   docker compose ps typesense
   ```

4. **Check content_text field:**
   - Search uses the `content_text` field for indexing
   - Ensure this field has meaningful content when creating assets

### Problem: Canonical key already exists

**Error:** `Asset with canonical_key '{key}' already exists`

**Solutions:**

1. **Use a different canonical key:**
   ```bash
   # Canonical keys must be unique per db_connection_id + asset_type
   # Use descriptive, unique names
   "canonical_key": "monthly_active_users_v2"
   ```

2. **Or update existing asset:**
   ```bash
   # If the asset exists, update it instead
   curl -X PUT "http://localhost:8015/api/v1/context-assets/{existing_asset_id}" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Updated Name",
       "description": "Updated description"
     }'
   ```

### Problem: Cannot delete published asset

**Error:** `Cannot delete asset in 'published' state`

**Solution:**

Only DRAFT assets can be deleted. For published assets:

1. **Deprecate instead:**
   ```bash
   curl -X POST "http://localhost:8015/api/v1/context-assets/{asset_id}/deprecate" \
     -H "Content-Type: application/json" \
     -d '{
       "promoted_by": "your-email@example.com",
       "reason": "No longer applicable"
     }'
   ```

2. **Or create a revision and delete the draft:**
   ```bash
   # Create draft revision
   curl -X POST "http://localhost:8015/api/v1/context-assets/{asset_id}/revision" \
     -H "Content-Type: application/json" \
     -d '{"author": "your-email@example.com"}'

   # The new draft can be deleted if needed
   ```

### Problem: Tags not showing up

**Solutions:**

1. **Check tags are properly formatted:**
   ```bash
   # Tags should be an array of strings
   "tags": ["metrics", "kpi", "user-engagement"]
   ```

2. **View all available tags:**
   ```bash
   curl -X GET "http://localhost:8015/api/v1/context-assets/tags"
   ```

3. **Filter by category:**
   ```bash
   curl -X GET "http://localhost:8015/api/v1/context-assets/tags?category=domain"
   ```

### Problem: Version history not available

**Error:** `No version history found for asset`

**Solutions:**

1. **Verify asset ID:**
   ```bash
   # Get the correct asset ID first
   curl -X GET "http://localhost:8015/api/v1/context-assets/{db_id}/{asset_type}/{canonical_key}"
   ```

2. **Check if asset has versions:**
   - New assets start at version "1.0.0"
   - Versions are created when promoting or creating revisions

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
