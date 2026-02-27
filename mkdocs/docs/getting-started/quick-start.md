# Quick Start

Get KAI running in **5 minutes** with Docker Compose!

## Prerequisites

- **Docker** & **Docker Compose** ([Install Docker](https://docs.docker.com/get-docker/))
- **API Key** from OpenAI, Google, or other LLM provider

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/mta-tech/kai.git
cd kai
```

### 2. Create environment configuration

```bash
cp .env.example .env
```

### 3. Configure your LLM provider

Edit `.env` and set your LLM configuration:

```bash
# Choose your LLM provider
CHAT_FAMILY=openai  # or: google, ollama, openrouter
CHAT_MODEL=gpt-4o-mini
OPENAI_API_KEY=your-api-key-here

# Required: Generate encryption key for database credentials
ENCRYPT_KEY=  # See below
```

### 4. Generate encryption key

```bash
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output and paste it as `ENCRYPT_KEY` in your `.env` file.

## Running with Docker

### Start all services

```bash
docker compose up -d
```

### Verify services are running

```bash
docker compose ps
```

Expected output:

```
NAME         IMAGE                      STATUS          PORTS
kai_engine   kai-kai_engine             Up 2 minutes    0.0.0.0:8015->8015/tcp
typesense    typesense/typesense:26.0   Up 2 minutes    0.0.0.0:8108->8108/tcp
```

### Access the application

| Service | URL |
|---------|-----|
| API | http://localhost:8015 |
| API Documentation | http://localhost:8015/docs |
| Typesense | http://localhost:8108 |

### Test the API

```bash
curl http://localhost:8015/health
# Expected: {"status":"healthy"}
```

## Next Steps

Now that KAI is running, explore these options:

- [Web UI](#) - Visual interface with dashboard builder
- [CLI Tutorial](../cli/index.md) - Terminal-based workflows
- [Context Platform Tutorial](../tutorials/context-platform-tutorial.md) - Learn about context assets
- [API Documentation](http://localhost:8015/docs) - Programmatic access

## Stopping Services

```bash
docker compose down
```

!!! note "Data Persistence"
    Data in `./app/data/dbdata` persists across restarts.
