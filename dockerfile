# Dockerfile for KAI Text2SQL Agent Service
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (including PostgreSQL dev libs for psycopg2)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install uv

# Copy dependency files first for layer caching
COPY pyproject.toml ./
COPY uv.lock* ./

# Install dependencies with pre-release support for letta-client
# The uv.lock already contains resolved pre-release versions
RUN uv sync --frozen 2>/dev/null || uv sync --prerelease=allow

# Copy application code
COPY app/ ./app/

# Copy environment template (actual .env should be mounted or passed via --env-file)
COPY .env.example ./.env.example

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# KAI API port
EXPOSE 8005

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8005/health || exit 1

# Run KAI API server
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
