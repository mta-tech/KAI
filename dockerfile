FROM python:3.11.4

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . /app

ENTRYPOINT ["uv", "run", "python", "-m", "app.main"]
